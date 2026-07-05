from __future__ import annotations

from pydantic import ValidationError

from app.schemas.room import RoomResponse


def test_room_response_schema():
    room = RoomResponse(
        id=1,
        name="Conference Room",
        capacity=12,
    )

    assert room.id == 1
    assert room.name == "Conference Room"
    assert room.capacity == 12


def test_extra_fields_are_rejected():
    try:
        RoomResponse(
            id=1,
            name="Room",
            capacity=5,
            timezone="UTC",
        )
        assert False
    except ValidationError:
        pass