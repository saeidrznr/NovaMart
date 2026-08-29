from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    COOKIE_SECURE: bool = False
    REFRESH_TOKEN_IDLE_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_ABSOLUTE_EXPIRE_DAYS: int = 30
    ENVIRONMENT: str
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
