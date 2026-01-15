# backend/app/clients/supabase_client.py

"""
Responsibilities:
- Client factory for supabase client services.
- Provide configured client instances.
"""

from supabase import create_client, Client
from app.core.config import settings

# Singleton do cliente Supabase com service role
_supabase_service: Client | None = None


def get_supabase_service_client() -> Client:
    """
    Retorna um cliente Supabase configurado com a SERVICE ROLE KEY.
    Usado exclusivamente pelo DV Server (nunca por Desktop/Mobile).
    """
    global _supabase_service

    if _supabase_service is None:
        _supabase_service = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )

    return _supabase_service
