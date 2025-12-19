# backend/app/api/sync.py

from fastapi import APIRouter, Depends, Query
from datetime import datetime


from app.core.security import get_current_user, CurrentUser
from app.schemas.sync import (
    SyncPushRequest,
    SyncPushResponse,
    SyncBootstrapResponse,
)
from app.services.sync.pull_service import pull_sync
from app.services.sync_service import (
    process_sync_items,
    bootstrap_sync,
)

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.get("/bootstrap", response_model=SyncBootstrapResponse)
async def bootstrap(
    user: CurrentUser = Depends(get_current_user),
):
    """
    Envia todos os dados iniciais necessários
    para inicialização do Desktop/Mobile.
    """
    return await bootstrap_sync(user)


@router.post("/push", response_model=SyncPushResponse)
async def sync_push(
    data: SyncPushRequest,
    user: CurrentUser = Depends(get_current_user),
):
    accepted, failed = process_sync_items(data.items, user)
    return {
        "accepted": accepted,
        "failed": failed,
    }

@router.get("/pull")
async def sync_pull(
    since: datetime = Query(...),
    user: CurrentUser = Depends(get_current_user),
):
    return await pull_sync(since, user)
