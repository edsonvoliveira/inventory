# desktop/core/auth_service.py

"""
Responsibilities:
- Service layer for auth workflows.
- Coordinate related operations and dependencies.
"""

from desktop.core.auth_session import AuthSession
from desktop.core.result import Result
from desktop.core.session_service import SessionService
from desktop.core import http_client
from desktop.core.http_client import DVServerError
from desktop.core.strings import LOGIN_INVALID


class AuthService:
    def authenticate(self, email: str, password: str) -> Result[None]:
        try:
            AuthSession().login(email, password)
            token = SessionService.get_jwt_token()
            if not token:
                return Result(ok=False, message="Falha ao autenticar. Tente novamente.", error_code="AUTH_ERROR")
            context = http_client.get("/v1/auth/me", jwt_token=token)
            user_id = context.get("user_id")
            company_id = context.get("company_id")
            if user_id is None or company_id is None:
                return Result(
                    ok=False,
                    message="Nao foi possivel carregar o contexto do usuario.",
                    error_code="AUTH_CONTEXT_ERROR",
                )
            SessionService.set_user_server_id(int(user_id))
            SessionService.set_company_server_id(int(company_id))
        except DVServerError as exc:
            message = str(exc)
            if "401" in message or "403" in message:
                return Result(ok=False, message=LOGIN_INVALID, error_code="AUTH_INVALID")
            return Result(
                ok=False,
                message="Nao foi possivel conectar ao servidor.",
                error_code="AUTH_ERROR",
            )
        except Exception as exc:
            message = str(exc).lower()
            if "database is locked" in message:
                return Result(
                    ok=False,
                    message="Banco de dados em uso. Feche o DB Browser e tente novamente.",
                    error_code="AUTH_DB_LOCKED",
                )
            return Result(ok=False, message="Falha ao autenticar. Tente novamente.", error_code="AUTH_ERROR")
        return Result(ok=True)
