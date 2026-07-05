from __future__ import annotations

from app.repositories.room_repository import RoomRepository


def test_list_rooms_returns_rooms(db):
    repository = RoomRepository(db)

    rooms = repository.list_rooms()

    assert isinstance(rooms, list)
    assert len(rooms) > 0


def test_get_room_by_id_returns_room(db):
    repository = RoomRepository(db)

    room = repository.get_room_by_id(1)

    assert room is not None
    assert room.id == 1


def test_get_invalid_room_returns_none(db):
    repository = RoomRepository(db)

    room = repository.get_room_by_id(999999)

    assert room is None