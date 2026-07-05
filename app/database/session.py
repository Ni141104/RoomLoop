from __future__ import annotations

from collections.abc import Generator
from typing import Final
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def _build_database_url() -> str:
    settings = get_settings()
    password = quote_plus(settings.database_password)
    return (
        f"mysql+pymysql://{settings.database_user}:{password}"
        f"@{settings.database_host}:{settings.database_port}/{settings.database_name}"
        "?charset=utf8mb4"
    )


DATABASE_URL: Final[str] = _build_database_url()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()