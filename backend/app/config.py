from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Pydantic automatically reads from the .env file and validates types.
    """

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/inventory_db"

    # ── Application ───────────────────────────────────────────────────────
    APP_NAME: str = "Inventory & Order Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── Security ──────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-this-in-production"

    # ── CORS ──────────────────────────────────────────────────────────────
    # Stored as a comma-separated string in .env, converted to a list here
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def origins_list(self) -> List[str]:
        """Convert comma-separated ALLOWED_ORIGINS string into a Python list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    model_config = SettingsConfigDict(
        env_file="backend/.env",   # Path relative to where uvicorn is launched
        env_file_encoding="utf-8",
        extra="ignore",            # Ignore unknown variables in .env
    )


# ── Singleton instance ────────────────────────────────────────────────────────
# Import this object anywhere in the app: from app.config import settings
settings = Settings()