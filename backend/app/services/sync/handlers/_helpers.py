# backend/app/services/sync/handlers/_helpers.py

"""
Responsibilities:
- Sync handler for helpers entities.
- Implement pull and push operations.
"""

#backend/app/services/sync/handlers/_helpers.py

from typing import Any


def json_id_to_int(value: Any) -> int:
    """
    Converte valores JSON vindos do Supabase para int de forma segura.
    Lança erro se o valor não for conversível.
    """
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    raise TypeError(f"Valor inválido para ID: {value!r}")
