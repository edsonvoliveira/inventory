# backend/app/api/sync.py

"""
Responsibilities:
- API routes for sync endpoints.
- Handle request validation and responses.
"""

# backend/app/api/sync.py

from datetime import datetime, timezone
from typing import Optional

import logging
from fastapi import APIRouter, Depends, Query, Header

from app.core.security import CurrentUser, get_current_user
from app.core.sync_logging import ensure_correlation_id, log_sync_event
from app.schemas.sync import SyncPushRequest, SyncPushResponse, SyncBootstrapResponse
from app.services.sync.pull_orchestrator import PullOrchestrator
from app.services.sync.push_orchestrator import PushOrchestrator

router = APIRouter(prefix="/sync", tags=["Sync"])
logger = logging.getLogger(__name__)


def _get_company_id(user: CurrentUser) -> int:
    # padrão: CurrentUser.company_id
    # fallback: company_server_id (se existir em alguma versão antiga)
    return int(getattr(user, "company_id", getattr(user, "company_server_id")))

@router.get("/pull")
async def sync_pull(
    since: Optional[datetime] = Query(None),
    user: CurrentUser = Depends(get_current_user),
    correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id"),
):
    """
    Pull incremental. Se since=None, tratamos como bootstrap/full pull.
    """
    company_id = _get_company_id(user)

    if since is None:
        since = datetime(1970, 1, 1, tzinfo=timezone.utc)
    elif since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    else:
        since = since.astimezone(timezone.utc)

    corr_id = ensure_correlation_id(correlation_id)
    log_sync_event(
        logger,
        "sync_pull_request",
        {
            "correlation_id": corr_id,
            "company_id": company_id,
            "user_id": getattr(user, "id", getattr(user, "db_user_id", None)),
            "since": since.isoformat(),
        },
    )

    payload = PullOrchestrator().run(
        since=since,
        company_id=company_id,
        user=user,
    )
    counts = {
        key: len(value)
        for key, value in payload.items()
        if isinstance(value, list)
    }
    log_sync_event(
        logger,
        "sync_pull_response",
        {
            "correlation_id": corr_id,
            "company_id": company_id,
            "user_id": getattr(user, "id", getattr(user, "db_user_id", None)),
            "counts": counts,
            "server_now": payload.get("server_now") or payload.get("server_ts"),
        },
    )
    return payload


@router.post("/push", response_model=SyncPushResponse)
async def sync_push(
    data: SyncPushRequest,
    user: CurrentUser = Depends(get_current_user),
    correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id"),
):
    """
    Push de dados do cliente para o servidor.
    """
    corr_id = ensure_correlation_id(correlation_id)
    accepted, failed, rejected, server_ids = PushOrchestrator().run(
        items=data.items,
        user=user,
        origin="desktop",
        correlation_id=corr_id,
    )
    log_sync_event(
        logger,
        "sync_push_summary",
        {
            "correlation_id": corr_id,
            "origin": "desktop",
            "company_id": _get_company_id(user),
            "user_id": getattr(user, "id", getattr(user, "db_user_id", None)),
            "accepted": len(accepted),
            "failed": len(failed),
        },
    )
    return {
        "accepted": accepted,
        "failed": failed,
        "rejected": rejected,
        "server_ids": server_ids,
    }


@router.post("/desktop/push", response_model=SyncPushResponse)
async def sync_push_desktop(
    data: SyncPushRequest,
    user: CurrentUser = Depends(get_current_user),
    correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id"),
):
    """
    Push de dados do desktop para o servidor.
    """
    corr_id = ensure_correlation_id(correlation_id)
    accepted, failed, rejected, server_ids = PushOrchestrator().run(
        items=data.items,
        user=user,
        origin="desktop",
        correlation_id=corr_id,
    )
    log_sync_event(
        logger,
        "sync_push_summary",
        {
            "correlation_id": corr_id,
            "origin": "desktop",
            "company_id": _get_company_id(user),
            "user_id": getattr(user, "id", getattr(user, "db_user_id", None)),
            "accepted": len(accepted),
            "failed": len(failed),
        },
    )
    return {
        "accepted": accepted,
        "failed": failed,
        "rejected": rejected,
        "server_ids": server_ids,
    }


@router.post("/mobile/push", response_model=SyncPushResponse)
async def sync_push_mobile(
    data: SyncPushRequest,
    user: CurrentUser = Depends(get_current_user),
    correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id"),
):
    """
    Push de dados do mobile para o servidor.
    """
    corr_id = ensure_correlation_id(correlation_id)
    accepted, failed, rejected, server_ids = PushOrchestrator().run(
        items=data.items,
        user=user,
        origin="mobile",
        correlation_id=corr_id,
    )
    log_sync_event(
        logger,
        "sync_push_summary",
        {
            "correlation_id": corr_id,
            "origin": "mobile",
            "company_id": _get_company_id(user),
            "user_id": getattr(user, "id", getattr(user, "db_user_id", None)),
            "accepted": len(accepted),
            "failed": len(failed),
        },
    )
    return {
        "accepted": accepted,
        "failed": failed,
        "rejected": rejected,
        "server_ids": server_ids,
    }
