from __future__ import annotations

from app.schemas.common import PositiveIdentifier, SchemaModel


class RoomResponse(SchemaModel):
    id: PositiveIdentifier
    name: str
    capacity: int