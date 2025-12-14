from fastapi import APIRouter, Depends
from app.core.security import get_current_user, CurrentUser

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.get("/me")
async def me(user: CurrentUser = Depends(get_current_user)):
    return {
        "auth_uid": user.auth_uid,
        "email": user.email,
    }

