"""Application configuration via Pydantic BaseSettings.

All configuration is loaded from environment variables or a .env file.
Never read os.environ directly -- use settings.VARIABLE_NAME instead.
"""

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Priority (highest to lowest):
      1. Environment variables
      2. .env file values
      3. Field defaults
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    DATABASE_URL: PostgresDsn
    SECRET_KEY: str
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    DEBUG: bool = False


settings = Settings()  # type: ignore[call-arg]
