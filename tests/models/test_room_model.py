from __future__ import annotations

from app.models.room import Room


def test_room_model_can_be_created():
    room = Room(
        name="Conference Room",
        capacity=12,
        timezone="Europe/Berlin",
    )

    assert room.name == "Conference Room"
    assert room.capacity == 12
    assert room.timezone == "Europe/Berlin"


def test_room_relationships_exist():
    """
    Room should expose ORM relationships.
    """

    room = Room()

    assert hasattr(room, "bookings")
    assert hasattr(room, "recurring_series")