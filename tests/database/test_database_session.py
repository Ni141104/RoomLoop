from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.session import (
    DATABASE_URL,
    SessionLocal,
    engine,
    get_db,
)
from sqlalchemy import text

def test_database_url_uses_mysql():
    """
    The application must use MySQL through PyMySQL.
    """
    assert DATABASE_URL.startswith("mysql+pymysql://")


def test_engine_is_created():
    """
    SQLAlchemy engine should be initialized.
    """
    assert engine is not None


def test_session_factory_creates_session():
    """
    SessionLocal should return a SQLAlchemy Session.
    """
    session = SessionLocal()

    try:
        assert isinstance(session, Session)
    finally:
        session.close()


def test_get_db_returns_session():
    """
    FastAPI dependency should yield a Session instance.
    """
    generator = get_db()

    session = next(generator)

    try:
        assert isinstance(session, Session)
    finally:
        generator.close()


def test_multiple_sessions_are_distinct():
    """
    Every call to SessionLocal should create a new session.
    """
    session1 = SessionLocal()
    session2 = SessionLocal()

    try:
        assert session1 is not session2
    finally:
        session1.close()
        session2.close()


def test_session_can_execute_simple_query():
    """
    Database connection should be usable.
    """
    session = SessionLocal()

    try:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        session.close()