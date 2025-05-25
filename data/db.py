from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings

if TYPE_CHECKING:
    from sqlalchemy import URL, Engine
    from sqlalchemy.orm import Session


def get_engine(url: URL | str = settings.database_url) -> Engine:
    return create_engine(url, echo=settings.DEBUG)


def get_sessionmaker(engine: Engine) -> "sessionmaker[Session]":
    return sessionmaker(engine)
