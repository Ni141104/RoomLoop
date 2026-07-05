from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.recurring_series import RecurringSeries


class RecurringRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_recurring_series(self, recurring_series: RecurringSeries) -> RecurringSeries:
        self._session.add(recurring_series)
        return recurring_series

    def get_series_by_id(self, series_id: int) -> RecurringSeries | None:
        statement: Select[tuple[RecurringSeries]] = select(RecurringSeries).where(
            RecurringSeries.id == series_id,
        )
        return self._session.scalars(statement).one_or_none()

    def get_series(self) -> list[RecurringSeries]:
        statement: Select[tuple[RecurringSeries]] = select(RecurringSeries).order_by(
            RecurringSeries.id.asc(),
        )
        return list(self._session.scalars(statement).all())

    def get_bookings_by_series(self, series_id: int) -> list[Booking]:
        statement: Select[tuple[Booking]] = select(Booking).where(
            Booking.recurring_series_id == series_id,
        )
        return list(self._session.scalars(statement).all())