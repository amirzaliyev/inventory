from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from sqlalchemy.engine.url import URL

BOT_DIR = Path(__file__).absolute().parent
MEDIA_DIR = Path(BOT_DIR, "media")
LOCALES_DIR = Path.joinpath(BOT_DIR, "locales")
I18N_DOMAIN = "messages"
DEFAULT_LOCALE = "en"


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class BotSettings(EnvBaseSettings):
    BOT_TOKEN: str
    SUPPORT_URL: str | None = None
    RATE_LIMIT: int | float = 0.5  # for throttling control


class DBSettings(EnvBaseSettings):
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str | None = None
    DB_NAME: str = "postgres"

    @property
    def database_url(self) -> URL | str:
        if self.DB_PASS:
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"postgresql+asyncpg://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def database_url_psycopg2(self) -> str:
        if self.DB_PASS:
            return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return (
            f"postgresql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


class Settings(BotSettings, DBSettings):
    SUPER_ADMIN: int
    DEBUG: bool = False


settings = Settings()  # type: ignore
