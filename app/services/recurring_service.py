from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import (
    BookingConflictError,
    DomainError,
    InvalidRecurringDateRangeError,
    InvalidTimeRangeError,
    RecurringSeriesNotFoundError,
    RoomNotFoundError,
)
from app.core.timezone import (
    convert_timezone_aware_datetime_to_naive_local_datetime,
    determine_recurring_weekday,
    generate_weekly_occurrences,
    load_timezone,
)
from app.models.booking import Booking
from app.models.recurring_series import RecurringSeries
from app.repositories.booking_repository import BookingRepository
from app.repositories.recurring_repository import RecurringRepository
from app.repositories.room_repository import RoomRepository


class RecurringService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._booking_repository = BookingRepository(session)
        self._recurring_repository = RecurringRepository(session)
        self._room_repository = RoomRepository(session)

    def create_recurring_booking(
        self,
        room_id: int,
        user: str,
        start_time: datetime,
        end_time: datetime,
        repeat_until: date,
    ) -> tuple[RecurringSeries, list[Booking]]:
        self._validate_time_range(start_time, end_time)

        try:
            room = self._room_repository.get_room_by_id(room_id)
            if room is None:
                raise RoomNotFoundError(f"Room {room_id} was not found.")

            if repeat_until < start_time.date():
                raise InvalidRecurringDateRangeError(
                    "repeat_until must not be earlier than the first occurrence date.",
                )

            occurrences = generate_weekly_occurrences(start_time, end_time, repeat_until, load_timezone(room.timezone))
            repeat_weekday = determine_recurring_weekday(start_time)

            self._ensure_no_conflicts(room.id, occurrences)

            recurring_series = RecurringSeries(
                room=room,
                user=user,
                repeat_weekday=repeat_weekday,
                repeat_until=repeat_until,
                start_time=start_time.time(),
                end_time=end_time.time(),
            )
            self._recurring_repository.create_recurring_series(recurring_series)

            bookings: list[Booking] = []
            for occurrence_start, occurrence_end in occurrences:
                booking = Booking(
                    room=room,
                    recurring_series=recurring_series,
                    user=user,
                    start_time=occurrence_start,
                    end_time=occurrence_end,
                    status="active",
                )
                self._booking_repository.create_booking(booking)
                bookings.append(booking)

            self._session.commit()
            return recurring_series, bookings
        except DomainError:
            self._session.rollback()
            raise
        except Exception:
            self._session.rollback()
            raise

    def cancel_recurring_series(self, series_id: int) -> tuple[RecurringSeries, list[Booking]]:
        try:
            recurring_series = self._recurring_repository.get_series_by_id(series_id)
            if recurring_series is None:
                raise RecurringSeriesNotFoundError(f"Recurring series {series_id} was not found.")

            room = recurring_series.room
            room_timezone = load_timezone(room.timezone)
            current_local_datetime = convert_timezone_aware_datetime_to_naive_local_datetime(
                datetime.now(room_timezone),
            )

            future_bookings = self._booking_repository.get_future_bookings_by_recurring_series(
                recurring_series.id,
                current_local_datetime,
            )
            active_future_bookings = [booking for booking in future_bookings if booking.status == "active"]

            for booking in active_future_bookings:
                self._booking_repository.update_booking_status(booking, "cancelled")

            self._session.commit()
            return recurring_series, active_future_bookings
        except DomainError:
            self._session.rollback()
            raise
        except Exception:
            self._session.rollback()
            raise

    def _ensure_no_conflicts(
        self,
        room_id: int,
        occurrences: list[tuple[datetime, datetime]],
    ) -> None:
        for occurrence_start, occurrence_end in occurrences:
            conflicts = self._booking_repository.find_conflicting_active_bookings(
                room_id,
                occurrence_start,
                occurrence_end,
            )
            if conflicts:
                raise BookingConflictError(
                    "A recurring booking conflict exists for at least one generated occurrence.",
                )

    @staticmethod
    def _validate_time_range(start_time: datetime, end_time: datetime) -> None:
        if start_time >= end_time:
            raise InvalidTimeRangeError("Start time must be earlier than end time.")