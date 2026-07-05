from __future__ import annotations

from app.database.session import Base


def test_all_tables_registered():
    tables = Base.metadata.tables

    assert "rooms" in tables
    assert "bookings" in tables
    assert "recurring_series" in tables