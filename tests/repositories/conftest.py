from __future__ import annotations

import pytest

from app.database.session import SessionLocal


@pytest.fixture
def db():
    session = SessionLocal()

    try:
        yield session
        session.rollback()
    finally:
        session.close()