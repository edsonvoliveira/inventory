# backend/app/core/user_context.py

"""
Responsibilities:
- Core module for user context.
- Provide shared application logic.
"""

#backend/app/core/user_context.py

from typing import Protocol

class UserContext(Protocol):
    company_server_id: int
    db_user_id: int
    role: str
