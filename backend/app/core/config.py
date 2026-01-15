from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    PROJECT_NAME: str = "Inventario DV Server"
    API_V1_PREFIX: str = "/v1"

    APP_ENV: str = "local"
    DEBUG: bool = False
    API_BASE_URL: str = "http://127.0.0.1:8000"

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    JWT_VERIFY_SIGNATURE: bool = True
    JWT_AUTH_HEADER: str = "Authorization"
    JWT_AUTH_SCHEME: str = "Bearer"

    LOG_LEVEL: str = "INFO"
    BACKEND_CORS_ORIGINS: str = ""

    def cors_list(self) -> list[str]:
        return [x.strip() for x in self.BACKEND_CORS_ORIGINS.split(",") if x.strip()]


settings = Settings() # type: ignore[call-arg]
