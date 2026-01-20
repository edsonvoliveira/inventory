from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Mapping


def _get_sync_logger() -> logging.Logger:
    sync_logger = logging.getLogger("sync")
    if sync_logger.handlers:
        return sync_logger
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    sync_logger.addHandler(handler)
    sync_logger.setLevel(logging.INFO)
    return sync_logger


def ensure_correlation_id(value: str | None) -> str:
    return value or str(uuid4())


def log_sync_event(logger: logging.Logger, event: str, fields: Mapping[str, Any]) -> None:
    if not logger.handlers:
        logger = _get_sync_logger()
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    logger.info(json.dumps(payload, ensure_ascii=True, default=str))
