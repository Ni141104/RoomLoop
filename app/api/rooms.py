from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.room import RoomResponse
from app.services.room_service import RoomService

router = APIRouter(tags=["Rooms"])


@router.get(
    "/rooms",
    response_model=list[RoomResponse],
)
def list_rooms(
    db: Session = Depends(get_db),
) -> list[RoomResponse]:
    service = RoomService(db)

    rooms = service.list_rooms()

    return [RoomResponse.model_validate(room) for room in rooms]