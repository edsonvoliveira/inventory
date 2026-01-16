from __future__ import annotations

from mobile.core.auth_session import AuthSession
from mobile.core.result import Result


class AuthService:
    def authenticate(self, email: str, password: str) -> Result[None]:
        try:
            AuthSession().login(email, password)
        except Exception as exc:
            message = str(exc)
            if "401" in message or "403" in message:
                return Result(
                    ok=False,
                    message="Login invalido! Verifique as credenciais e tente novamente.",
                    error_code="AUTH_INVALID",
                )
            return Result(ok=False, message="Nao foi possivel conectar ao servidor.", error_code="AUTH_ERROR")
        return Result(ok=True)

    def logout(self) -> Result[None]:
        try:
            AuthSession().logout()
        except Exception:
            return Result(ok=False, message="Nao foi possivel sair agora.", error_code="AUTH_LOGOUT_ERROR")
        return Result(ok=True)
