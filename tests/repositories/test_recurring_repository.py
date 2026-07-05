from __future__ import annotations

from datetime import date, datetime, time

from app.core.timezone import determine_recurring_weekday
from app.models.recurring_series import RecurringSeries
from app.models.room import Room
from app.repositories.recurring_repository import RecurringRepository


def test_create_recurring_series(db):
    room = db.get(Room, 1)

    repository = RecurringRepository(db)

    series = RecurringSeries(
        room=room,
        user="Repository Test",
        repeat_weekday=determine_recurring_weekday(
            datetime(2026, 12, 1, 9, 0)
        ),
        repeat_until=date(2026, 12, 31),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    repository.create_recurring_series(series)

    db.flush()

    assert series.id is not None


def test_get_series_by_id(db):
    repository = RecurringRepository(db)

    series = repository.get_series_by_id(1)

    assert series is not None
    assert series.id == 1


def test_get_invalid_series_returns_none(db):
    repository = RecurringRepository(db)

    series = repository.get_series_by_id(999999)

    assert series is None