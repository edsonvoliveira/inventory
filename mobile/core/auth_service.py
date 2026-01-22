from __future__ import annotations

from mobile.core.auth_session import AuthSession
from mobile.core.result import Result
from mobile.data.repositories.app_meta_repo import get_meta, set_meta
import requests


class AuthService:
    def authenticate(self, email: str, password: str) -> Result[None]:
        try:
            AuthSession().login(email, password)
            token = get_meta("jwt_token") or ""
            if not token:
                return Result(ok=False, message="Token nao disponivel.", error_code="AUTH_TOKEN_MISSING")
            base_url = (get_meta("dv_server_base_url") or "http://127.0.0.1:8000").rstrip("/")
            resp = requests.get(
                f"{base_url}/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            if not resp.ok:
                return Result(
                    ok=False,
                    message="Nao foi possivel carregar o contexto do usuario.",
                    error_code="AUTH_CONTEXT_ERROR",
                )
            context = resp.json()
            user_id = context.get("user_id")
            company_id = context.get("company_id")
            if user_id is None or company_id is None:
                return Result(
                    ok=False,
                    message="Nao foi possivel carregar o contexto do usuario.",
                    error_code="AUTH_CONTEXT_ERROR",
                )
            set_meta("user_server_id", str(user_id))
            set_meta("company_server_id", str(company_id))
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
