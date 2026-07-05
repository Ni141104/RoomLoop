from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.room import Room


class RoomRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_room_by_id(self, room_id: int) -> Room | None:
        statement: Select[tuple[Room]] = select(Room).where(Room.id == room_id)
        return self._session.scalars(statement).one_or_none()

    def list_rooms(self) -> list[Room]:
        statement: Select[tuple[Room]] = select(Room).order_by(Room.id.asc())
        return list(self._session.scalars(statement).all())