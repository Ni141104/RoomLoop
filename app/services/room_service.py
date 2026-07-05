from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.room import Room
from app.repositories.room_repository import RoomRepository


class RoomService:
    def __init__(self, session: Session) -> None:
        self._room_repository = RoomRepository(session)

    def list_rooms(self) -> list[Room]:
        return self._room_repository.list_rooms()