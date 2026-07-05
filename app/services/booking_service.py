from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import (
    BookingConflictError,
    BookingNotFoundError,
    DomainError,
    InvalidTimeRangeError,
    RoomNotFoundError,
)
from app.models.booking import Booking
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository


class BookingService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._booking_repository = BookingRepository(session)
        self._room_repository = RoomRepository(session)

    def create_booking(
        self,
        room_id: int,
        user: str,
        start_time: datetime,
        end_time: datetime,
    ) -> Booking:
        self._validate_time_range(start_time, end_time)

        try:
            room = self._room_repository.get_room_by_id(room_id)
            if room is None:
                raise RoomNotFoundError(f"Room {room_id} was not found.")

            conflicts = self._booking_repository.find_conflicting_active_bookings(
                room.id,
                start_time,
                end_time,
            )
            if conflicts:
                raise BookingConflictError("A booking conflict exists for the selected room and time range.")

            booking = Booking(
                room=room,
                user=user,
                start_time=start_time,
                end_time=end_time,
                status="active",
            )
            self._booking_repository.create_booking(booking)
            self._session.commit()
            return booking
        except DomainError:
            self._session.rollback()
            raise
        except Exception:
            self._session.rollback()
            raise

    def cancel_booking(self, booking_id: int) -> Booking:
        try:
            booking = self._booking_repository.get_booking_by_id(booking_id)
            if booking is None:
                raise BookingNotFoundError(f"Booking {booking_id} was not found.")

            if booking.status != "cancelled":
                self._booking_repository.update_booking_status(booking, "cancelled")

            self._session.commit()
            return booking
        except DomainError:
            self._session.rollback()
            raise
        except Exception:
            self._session.rollback()
            raise

    @staticmethod
    def _validate_time_range(start_time: datetime, end_time: datetime) -> None:
        if start_time >= end_time:
            raise InvalidTimeRangeError("Start time must be earlier than end time.")