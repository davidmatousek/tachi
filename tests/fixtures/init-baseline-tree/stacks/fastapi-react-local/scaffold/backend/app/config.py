"""Application configuration via Pydantic BaseSettings.

All configuration is loaded from environment variables or a .env file.
Never read os.environ directly -- use settings.VARIABLE_NAME instead.

SQLite is the default database. No external services required.
"""

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

    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"
    SECRET_KEY: str  # Required — set via environment variable or .env file
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    DEBUG: bool = False


settings = Settings()
