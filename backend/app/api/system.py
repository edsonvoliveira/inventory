#backend/app/api/system.py

from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/debug-env")
def debug_env():
    from app.core.config import settings
    return {
        "project": settings.PROJECT_NAME,
        "supabase_url": settings.SUPABASE_URL[:20] + "...",
    }