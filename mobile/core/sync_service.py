# mobile/core/sync_service.py

"""
Responsibilities:
- Service layer for sync workflows.
- Coordinate related operations and dependencies.
"""

from dataclasses import dataclass
from typing import Optional
import logging
import threading
from pathlib import Path
from uuid import uuid4

from mobile.app_core_container import build_services
from mobile.core.auth_session import AuthSession
from mobile.bootstrap.bootstrap import wipe_local_database
from mobile.data.repositories.app_meta_repo import get_meta, set_meta

logger = logging.getLogger(__name__)


def _get_sync_logger() -> logging.Logger:
    sync_logger = logging.getLogger("sync_client")
    if any(isinstance(h, logging.FileHandler) for h in sync_logger.handlers):
        return sync_logger

    base_dir = Path(__file__).resolve().parents[2]
    log_dir = base_dir / "z_files" / "tests_results"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "sync_client.log"

    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(message)s")
    handler.setFormatter(formatter)
    sync_logger.addHandler(handler)
    sync_logger.setLevel(logging.INFO)
    return sync_logger


@dataclass
class SyncResult:
    did_bootstrap: bool
    push_accepted: int
    push_failed: int
    pulled: bool
    error: Optional[str] = None


class SyncService:
    def run(self) -> SyncResult:
        correlation_id = str(uuid4())
        services = build_services()
        result = services.sync.run(correlation_id=correlation_id)
        status = "ok" if not result.error else "error"
        sync_logger = _get_sync_logger()
        logger.info(
            "event=sync_cycle action=sync status=%s did_bootstrap=%s push_accepted=%s push_failed=%s pulled=%s error=%s",
            status,
            result.did_bootstrap,
            result.push_accepted,
            result.push_failed,
            result.pulled,
            result.error,
        )
        sync_logger.info(
            "event=sync_cycle status=%s correlation_id=%s did_bootstrap=%s push_accepted=%s push_failed=%s pulled=%s error=%s",
            status,
            correlation_id,
            result.did_bootstrap,
            result.push_accepted,
            result.push_failed,
            result.pulled,
            result.error,
        )
        return SyncResult(
            did_bootstrap=result.did_bootstrap,
            push_accepted=result.push_accepted,
            push_failed=result.push_failed,
            pulled=result.pulled,
            error=result.error,
        )


def ensure_bootstrap_for_company(company_id: int, company_uuid: str) -> bool:
    correlation_id = str(uuid4())
    stored_company_id = get_meta("company_id")
    bootstrap_done = get_meta("bootstrap_done") in {"1", "true"}

    if stored_company_id is None:
        _prepare_bootstrap(company_id, company_uuid)
        build_services().bootstrap.run(correlation_id=correlation_id)
        return True

    if stored_company_id != str(company_id):
        wipe_local_database()
        _prepare_bootstrap(company_id, company_uuid)
        build_services().bootstrap.run(correlation_id=correlation_id)
        return True

    if not bootstrap_done:
        set_meta("company_server_id", str(company_id))
        build_services().bootstrap.run(correlation_id=correlation_id)
        return True

    return False


def _prepare_bootstrap(company_id: int, company_uuid: str) -> None:
    set_meta("company_id", str(company_id))
    set_meta("company_uuid", company_uuid)
    set_meta("company_server_id", str(company_id))
    set_meta("bootstrap_done", "false")


class SyncScheduler:
    def __init__(self, interval_seconds: int = 180) -> None:
        self._interval = interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            token = AuthSession().get_valid_access_token()
            if token:
                SyncService().run()
            self._stop_event.wait(self._interval)
