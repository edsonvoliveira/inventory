# backend/app/api/sync.py

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.security import CurrentUser, get_current_user
from app.schemas.sync import SyncPushRequest, SyncPushResponse, SyncBootstrapResponse
from app.services.sync.pull_orchestrator import PullOrchestrator
from app.services.sync.push_orchestrator import PushOrchestrator

router = APIRouter(prefix="/sync", tags=["Sync"])


def _get_company_id(user: CurrentUser) -> int:
    # padrão: CurrentUser.company_id
    # fallback: company_server_id (se existir em alguma versão antiga)
    return int(getattr(user, "company_id", getattr(user, "company_server_id")))

@router.get("/pull")
async def sync_pull(
    since: Optional[datetime] = Query(None),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Pull incremental. Se since=None, tratamos como bootstrap/full pull.
    """
    company_id = _get_company_id(user)

    if since is None:
        since = datetime(1970, 1, 1, tzinfo=timezone.utc)
    elif since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)

    return PullOrchestrator().run(
        since=since,
        company_id=company_id,
        user=user,
    )


@router.post("/push", response_model=SyncPushResponse)
async def sync_push(
    data: SyncPushRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Push de dados do cliente para o servidor.
    """
    accepted, failed = PushOrchestrator().run(
        items=data.items,
        user=user,
    )
    return {"accepted": accepted, "failed": failed}
