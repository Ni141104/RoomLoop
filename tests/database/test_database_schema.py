from __future__ import annotations

from sqlalchemy import inspect

from app.database.session import engine


def test_rooms_table_exists():
    inspector = inspect(engine)

    assert "rooms" in inspector.get_table_names()


def test_bookings_table_exists():
    inspector = inspect(engine)

    assert "bookings" in inspector.get_table_names()


def test_recurring_series_table_exists():
    inspector = inspect(engine)

    assert "recurring_series" in inspector.get_table_names()