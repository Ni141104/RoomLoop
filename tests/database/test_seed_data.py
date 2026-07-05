from __future__ import annotations

from sqlalchemy import text

from app.database.session import SessionLocal


def test_seed_contains_rooms():
    session = SessionLocal()

    try:
        count = session.execute(
            text("SELECT COUNT(*) FROM rooms")
        ).scalar()

        assert count > 0
    finally:
        session.close()


def test_seed_contains_room_timezones():
    session = SessionLocal()

    try:
        count = session.execute(
            text(
                """
                SELECT COUNT(*)
                FROM rooms
                WHERE timezone IS NOT NULL
                """
            )
        ).scalar()

        assert count > 0
    finally:
        session.close()