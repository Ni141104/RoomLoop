from __future__ import annotations

import os
from datetime import date, datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("APP_NAME", "RoomLoop")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("HOST", "127.0.0.1")
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("DATABASE_HOST", "localhost")
os.environ.setdefault("DATABASE_PORT", "3306")
os.environ.setdefault("DATABASE_NAME", "roomloop")
os.environ.setdefault("DATABASE_USER", "root")
os.environ.setdefault("DATABASE_PASSWORD", "pass")
os.environ.setdefault("TIMEZONE_DEFAULT", "UTC")

from app.core.exceptions import BookingConflictError, InvalidTimeRangeError, RecurringSeriesNotFoundError, RoomNotFoundError
from app.models import Base, Booking, RecurringSeries, Room
from app.services.booking_service import BookingService
from app.services.recurring_service import RecurringService
from app.services.room_service import RoomService

ROOT = Path("/Users/nikhilprajapati/Desktop/RoomLoop/RoomLoop")
FIXED_NOW = datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc)


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    session.add_all(
        [
            Room(id=1, name="Aurora", capacity=8, timezone="UTC"),
            Room(id=2, name="Summit", capacity=12, timezone="America/Denver"),
            Room(id=3, name="Berlin", capacity=10, timezone="Europe/Berlin"),
        ]
    )
    session.commit()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def booking_service(session):
    return BookingService(session)


@pytest.fixture()
def recurring_service(session):
    return RecurringService(session)


@pytest.fixture()
def room_service(session):
    return RoomService(session)


@pytest.fixture()
def frozen_recurring_now(monkeypatch):
    class FrozenDateTime:
        @staticmethod
        def now(tz=None):
            if tz is None:
                return FIXED_NOW.replace(tzinfo=None)
            return FIXED_NOW.astimezone(tz)

    monkeypatch.setattr("app.services.recurring_service.datetime", FrozenDateTime)


def booking_count(session) -> int:
    return session.scalar(select(func.count(Booking.id))) or 0


def recurring_series_count(session) -> int:
    return session.scalar(select(func.count(RecurringSeries.id))) or 0


def test_1_validate_single_booking_overlap_predicate(session, booking_service):
    session.add(
        Booking(
            room_id=1,
            user="alice",
            start_time=datetime(2026, 7, 6, 9, 0),
            end_time=datetime(2026, 7, 6, 10, 0),
            status="active",
        )
    )
    session.commit()

    with pytest.raises(BookingConflictError):
        booking_service.create_booking(
            1,
            "bob",
            datetime(2026, 7, 6, 9, 30),
            datetime(2026, 7, 6, 10, 30),
        )

    booking = booking_service.create_booking(
        1,
        "carol",
        datetime(2026, 7, 6, 10, 0),
        datetime(2026, 7, 6, 11, 0),
    )

    assert booking.status == "active"
    assert booking.room_id == 1


def test_2_validate_different_room_isolation(session, booking_service):
    session.add(
        Booking(
            room_id=1,
            user="alice",
            start_time=datetime(2026, 7, 6, 9, 0),
            end_time=datetime(2026, 7, 6, 10, 0),
            status="active",
        )
    )
    session.commit()

    booking = booking_service.create_booking(
        2,
        "bob",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )

    assert booking.room_id == 2
    assert booking.status == "active"


def test_5_validate_cancelled_booking_exclusion_from_conflicts(session, booking_service):
    booking = booking_service.create_booking(
        1,
        "alice",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )
    booking_service.cancel_booking(booking.id)

    reused = booking_service.create_booking(
        1,
        "bob",
        datetime(2026, 7, 6, 9, 15),
        datetime(2026, 7, 6, 9, 45),
    )

    assert reused.status == "active"
    assert reused.room_id == 1


def test_8_create_single_booking_successfully(session, booking_service):
    booking = booking_service.create_booking(
        1,
        "alice",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )

    assert booking.id is not None
    assert booking.status == "active"
    assert booking.room_id == 1
    assert booking.start_time == datetime(2026, 7, 6, 9, 0)
    assert booking.end_time == datetime(2026, 7, 6, 10, 0)


def test_9_reject_single_booking_for_missing_room(booking_service):
    with pytest.raises(RoomNotFoundError):
        booking_service.create_booking(
            999,
            "alice",
            datetime(2026, 7, 6, 9, 0),
            datetime(2026, 7, 6, 10, 0),
        )


def test_10_reject_single_booking_for_invalid_time_range(booking_service):
    with pytest.raises(InvalidTimeRangeError):
        booking_service.create_booking(
            1,
            "alice",
            datetime(2026, 7, 6, 10, 0),
            datetime(2026, 7, 6, 9, 0),
        )


def test_11_reject_overlapping_single_booking_in_same_room(session, booking_service):
    session.add(
        Booking(
            room_id=1,
            user="alice",
            start_time=datetime(2026, 7, 6, 9, 0),
            end_time=datetime(2026, 7, 6, 10, 0),
            status="active",
        )
    )
    session.commit()

    with pytest.raises(BookingConflictError):
        booking_service.create_booking(
            1,
            "bob",
            datetime(2026, 7, 6, 9, 30),
            datetime(2026, 7, 6, 10, 30),
        )


def test_12_allow_back_to_back_single_bookings(booking_service):
    booking_service.create_booking(
        1,
        "alice",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )
    booking = booking_service.create_booking(
        1,
        "bob",
        datetime(2026, 7, 6, 10, 0),
        datetime(2026, 7, 6, 11, 0),
    )

    assert booking.room_id == 1
    assert booking.start_time == datetime(2026, 7, 6, 10, 0)


def test_13_cancel_a_single_booking(session, booking_service):
    booking = booking_service.create_booking(
        1,
        "alice",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )
    other = booking_service.create_booking(
        2,
        "bob",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )

    cancelled = booking_service.cancel_booking(booking.id)

    session.refresh(booking)
    session.refresh(other)

    assert cancelled.status == "cancelled"
    assert booking.status == "cancelled"
    assert other.status == "active"


def test_14_cancel_already_cancelled_booking_idempotently(session, booking_service):
    booking = booking_service.create_booking(
        1,
        "alice",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )

    first = booking_service.cancel_booking(booking.id)
    second = booking_service.cancel_booking(booking.id)

    session.refresh(booking)

    assert first.status == "cancelled"
    assert second.status == "cancelled"
    assert booking.status == "cancelled"


def test_15_create_recurring_booking_successfully(recurring_service):
    series, bookings = recurring_service.create_recurring_booking(
        1,
        "alice",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
        date(2026, 7, 20),
    )

    assert series.id is not None
    assert len(bookings) == 3
    assert [booking.start_time for booking in bookings] == [
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 13, 9, 0),
        datetime(2026, 7, 20, 9, 0),
    ]


def test_16_reject_recurring_booking_when_any_occurrence_conflicts(session, recurring_service):
    session.add(
        Booking(
            room_id=1,
            user="seed",
            start_time=datetime(2026, 7, 13, 9, 0),
            end_time=datetime(2026, 7, 13, 10, 0),
            status="active",
        )
    )
    session.commit()

    with pytest.raises(BookingConflictError):
        recurring_service.create_recurring_booking(
            1,
            "alice",
            datetime(2026, 7, 6, 9, 0),
            datetime(2026, 7, 6, 10, 0),
            date(2026, 7, 20),
        )

    assert booking_count(session) == 1
    assert recurring_series_count(session) == 0


def test_17_reject_recurring_booking_when_every_occurrence_conflicts(session, recurring_service):
    session.add_all(
        [
            Booking(
                room_id=1,
                user="seed1",
                start_time=datetime(2026, 7, 6, 9, 0),
                end_time=datetime(2026, 7, 6, 10, 0),
                status="active",
            ),
            Booking(
                room_id=1,
                user="seed2",
                start_time=datetime(2026, 7, 13, 9, 0),
                end_time=datetime(2026, 7, 13, 10, 0),
                status="active",
            ),
            Booking(
                room_id=1,
                user="seed3",
                start_time=datetime(2026, 7, 20, 9, 0),
                end_time=datetime(2026, 7, 20, 10, 0),
                status="active",
            ),
        ]
    )
    session.commit()

    with pytest.raises(BookingConflictError):
        recurring_service.create_recurring_booking(
            1,
            "alice",
            datetime(2026, 7, 6, 9, 0),
            datetime(2026, 7, 6, 10, 0),
            date(2026, 7, 20),
        )

    assert booking_count(session) == 3
    assert recurring_series_count(session) == 0


def test_18_cancel_recurring_booking_future_occurrences_only(session, recurring_service, frozen_recurring_now):
    series, bookings = recurring_service.create_recurring_booking(
        1,
        "alice",
        datetime(2026, 6, 22, 9, 0),
        datetime(2026, 6, 22, 10, 0),
        date(2026, 7, 13),
    )

    cancelled_series, cancelled_bookings = recurring_service.cancel_recurring_series(series.id)

    session.refresh(cancelled_series)
    for booking in bookings:
        session.refresh(booking)

    assert cancelled_series.id == series.id
    assert len(cancelled_bookings) == 2
    assert [booking.status for booking in bookings] == ["active", "active", "cancelled", "cancelled"]


def test_19_cancel_recurring_booking_with_mixed_past_and_future_occurrences(session, recurring_service, frozen_recurring_now):
    series, bookings = recurring_service.create_recurring_booking(
        1,
        "alice",
        datetime(2026, 6, 22, 9, 0),
        datetime(2026, 6, 22, 10, 0),
        date(2026, 7, 13),
    )

    recurring_service.cancel_recurring_series(series.id)

    for booking in bookings:
        session.refresh(booking)

    assert [booking.status for booking in bookings] == ["active", "active", "cancelled", "cancelled"]


def test_20_reuse_slot_after_cancellation(booking_service):
    booking = booking_service.create_booking(
        1,
        "alice",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )
    booking_service.cancel_booking(booking.id)

    reused = booking_service.create_booking(
        1,
        "bob",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )

    assert reused.room_id == 1
    assert reused.status == "active"


def test_27_same_room_conflict_rejection_across_create_flows(session, recurring_service):
    session.add(
        Booking(
            room_id=1,
            user="seed",
            start_time=datetime(2026, 7, 6, 9, 0),
            end_time=datetime(2026, 7, 6, 10, 0),
            status="active",
        )
    )
    session.commit()

    with pytest.raises(BookingConflictError):
        recurring_service.create_recurring_booking(
            1,
            "alice",
            datetime(2026, 7, 6, 9, 30),
            datetime(2026, 7, 6, 10, 30),
            date(2026, 7, 20),
        )


def test_28_different_room_non_conflict(session, booking_service):
    session.add(
        Booking(
            room_id=1,
            user="seed",
            start_time=datetime(2026, 7, 6, 9, 0),
            end_time=datetime(2026, 7, 6, 10, 0),
            status="active",
        )
    )
    session.commit()

    booking = booking_service.create_booking(
        2,
        "bob",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )

    assert booking.room_id == 2
    assert booking.status == "active"


def test_29_cancelled_booking_does_not_block_conflicts(session, booking_service):
    booking = booking_service.create_booking(
        1,
        "alice",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )
    booking_service.cancel_booking(booking.id)

    reused = booking_service.create_booking(
        1,
        "bob",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
    )

    assert reused.status == "active"


def test_30_recurrence_uses_the_first_occurrence_weekday(session, recurring_service):
    session.add(
        Room(id=4, name="Calendar", capacity=6, timezone="Europe/Berlin")
    )
    session.commit()

    series, bookings = recurring_service.create_recurring_booking(
        4,
        "alice",
        datetime(2026, 3, 16, 9, 0),
        datetime(2026, 3, 16, 10, 0),
        date(2026, 4, 13),
    )

    assert series.repeat_weekday == 0
    assert [booking.start_time.weekday() for booking in bookings] == [0, 0, 0, 0, 0]
    assert [booking.start_time.hour for booking in bookings] == [9, 9, 9, 9, 9]
    assert [booking.end_time.hour for booking in bookings] == [10, 10, 10, 10, 10]


def test_31_recurrence_stores_all_generated_occurrences_upfront(session, recurring_service):
    series, bookings = recurring_service.create_recurring_booking(
        1,
        "alice",
        datetime(2026, 7, 6, 9, 0),
        datetime(2026, 7, 6, 10, 0),
        date(2026, 7, 20),
    )

    assert recurring_series_count(session) == 1
    assert booking_count(session) == 3
    assert len(bookings) == 3
    assert session.scalar(
        select(func.count(Booking.id)).where(Booking.recurring_series_id == series.id)
    ) == 3


def test_32_r1_rollback_on_partial_recurring_conflict(session, recurring_service):
    session.add(
        Booking(
            room_id=1,
            user="seed",
            start_time=datetime(2026, 7, 13, 9, 0),
            end_time=datetime(2026, 7, 13, 10, 0),
            status="active",
        )
    )
    session.commit()

    with pytest.raises(BookingConflictError):
        recurring_service.create_recurring_booking(
            1,
            "alice",
            datetime(2026, 7, 6, 9, 0),
            datetime(2026, 7, 6, 10, 0),
            date(2026, 7, 20),
        )

    assert recurring_series_count(session) == 0
    assert booking_count(session) == 1


def test_33_r1_rollback_on_full_recurring_conflict(session, recurring_service):
    session.add_all(
        [
            Booking(
                room_id=1,
                user="seed1",
                start_time=datetime(2026, 7, 6, 9, 0),
                end_time=datetime(2026, 7, 6, 10, 0),
                status="active",
            ),
            Booking(
                room_id=1,
                user="seed2",
                start_time=datetime(2026, 7, 13, 9, 0),
                end_time=datetime(2026, 7, 13, 10, 0),
                status="active",
            ),
            Booking(
                room_id=1,
                user="seed3",
                start_time=datetime(2026, 7, 20, 9, 0),
                end_time=datetime(2026, 7, 20, 10, 0),
                status="active",
            ),
        ]
    )
    session.commit()

    with pytest.raises(BookingConflictError):
        recurring_service.create_recurring_booking(
            1,
            "alice",
            datetime(2026, 7, 6, 9, 0),
            datetime(2026, 7, 6, 10, 0),
            date(2026, 7, 20),
        )

    assert recurring_series_count(session) == 0
    assert booking_count(session) == 3


def test_34_future_recurring_occurrences_are_cancelled(session, recurring_service, frozen_recurring_now):
    series, bookings = recurring_service.create_recurring_booking(
        1,
        "alice",
        datetime(2026, 6, 22, 9, 0),
        datetime(2026, 6, 22, 10, 0),
        date(2026, 7, 13),
    )

    _, cancelled_bookings = recurring_service.cancel_recurring_series(series.id)

    for booking in bookings:
        session.refresh(booking)

    assert len(cancelled_bookings) == 2
    assert [booking.status for booking in bookings] == ["active", "active", "cancelled", "cancelled"]


def test_35_past_recurring_occurrences_are_preserved(session, recurring_service, frozen_recurring_now):
    series, bookings = recurring_service.create_recurring_booking(
        1,
        "alice",
        datetime(2026, 6, 22, 9, 0),
        datetime(2026, 6, 22, 10, 0),
        date(2026, 7, 13),
    )

    recurring_service.cancel_recurring_series(series.id)

    for booking in bookings:
        session.refresh(booking)

    assert bookings[0].status == "active"
    assert bookings[1].status == "active"


def test_services_own_transactions_and_repositories_stay_persistence_only():
    booking_service_source = (ROOT / "app/services/booking_service.py").read_text()
    recurring_service_source = (ROOT / "app/services/recurring_service.py").read_text()
    booking_repository_source = (ROOT / "app/repositories/booking_repository.py").read_text()
    recurring_repository_source = (ROOT / "app/repositories/recurring_repository.py").read_text()
    room_repository_source = (ROOT / "app/repositories/room_repository.py").read_text()

    assert "commit(" in booking_service_source
    assert "rollback(" in booking_service_source
    assert "commit(" in recurring_service_source
    assert "rollback(" in recurring_service_source

    for source in (booking_repository_source, recurring_repository_source, room_repository_source):
        assert "commit(" not in source
        assert "rollback(" not in source
        assert "flush(" not in source

    for source in (booking_repository_source, recurring_repository_source, room_repository_source):
        assert "BookingConflictError" not in source
        assert "InvalidTimeRangeError" not in source
        assert "RoomNotFoundError" not in source
        assert "RecurringSeriesNotFoundError" not in source


def test_no_http_or_fastapi_logic_exists_inside_services():
    booking_service_source = (ROOT / "app/services/booking_service.py").read_text()
    recurring_service_source = (ROOT / "app/services/recurring_service.py").read_text()
    room_service_source = (ROOT / "app/services/room_service.py").read_text()

    for source in (booking_service_source, recurring_service_source, room_service_source):
        assert "FastAPI" not in source
        assert "APIRouter" not in source
        assert "HTTPException" not in source
        assert "Request" not in source
        assert "Response" not in source
        assert "status.HTTP_" not in source
