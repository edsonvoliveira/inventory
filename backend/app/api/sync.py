from fastapi import APIRouter, Depends
from app.core.security import get_current_user, CurrentUser
from app.services.sync_service import bootstrap_sync

router = APIRouter(
    prefix="/sync",
    tags=["Sync"]
)

@router.get("/bootstrap")
async def bootstrap(user: CurrentUser = Depends(get_current_user)):
    return await bootstrap_sync(user)

