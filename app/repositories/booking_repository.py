from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, and_, select
from sqlalchemy.orm import Session

from app.models.booking import Booking


class BookingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_booking(self, booking: Booking) -> Booking:
        self._session.add(booking)
        return booking

    def get_booking_by_id(self, booking_id: int) -> Booking | None:
        statement: Select[tuple[Booking]] = select(Booking).where(Booking.id == booking_id)
        return self._session.scalars(statement).one_or_none()

    def get_active_booking_by_id(self, booking_id: int) -> Booking | None:
        statement: Select[tuple[Booking]] = select(Booking).where(
            Booking.id == booking_id,
            Booking.status == "active",
        )
        return self._session.scalars(statement).one_or_none()

    def update_booking_status(self, booking: Booking, status: str) -> Booking:
        booking.status = status
        return booking

    def find_conflicting_active_bookings(
        self,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: int | None = None,
    ) -> list[Booking]:
        conditions = [
            Booking.room_id == room_id,
            Booking.status == "active",
            Booking.start_time < end_time,
            start_time < Booking.end_time,
        ]
        if exclude_booking_id is not None:
            conditions.append(Booking.id != exclude_booking_id)

        statement: Select[tuple[Booking]] = select(Booking).where(and_(*conditions))
        return list(self._session.scalars(statement).all())

    def get_bookings_by_recurring_series(self, recurring_series_id: int) -> list[Booking]:
        statement: Select[tuple[Booking]] = select(Booking).where(
            Booking.recurring_series_id == recurring_series_id,
        )
        return list(self._session.scalars(statement).all())

    def get_future_bookings_by_recurring_series(
        self,
        recurring_series_id: int,
        reference_time: datetime,
    ) -> list[Booking]:
        statement: Select[tuple[Booking]] = select(Booking).where(
            Booking.recurring_series_id == recurring_series_id,
            Booking.start_time >= reference_time,
        )
        return list(self._session.scalars(statement).all())

    def get_bookings_by_room(self, room_id: int) -> list[Booking]:
        statement: Select[tuple[Booking]] = select(Booking).where(
            Booking.room_id == room_id,
        )
        return list(self._session.scalars(statement).all())