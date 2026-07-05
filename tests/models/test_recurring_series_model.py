from __future__ import annotations

from datetime import date, time

from app.models.recurring_series import RecurringSeries
from app.models.room import Room


def test_recurring_series_can_be_created():
    room = Room(
        name="Conference",
        capacity=20,
        timezone="UTC",
    )

    series = RecurringSeries(
        room=room,
        user="Office Manager",
        repeat_weekday="MONDAY",
        repeat_until=date(2026, 12, 31),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    assert series.room == room
    assert series.user == "Office Manager"
    assert series.repeat_weekday == "MONDAY"


def test_recurring_series_has_relationships():
    series = RecurringSeries()

    assert hasattr(series, "room")
    assert hasattr(series, "bookings")