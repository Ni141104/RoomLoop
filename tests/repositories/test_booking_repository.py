from __future__ import annotations

from datetime import datetime

from app.models.booking import Booking
from app.models.room import Room
from app.repositories.booking_repository import BookingRepository


def test_create_booking(db):
    room = db.get(Room, 1)

    repository = BookingRepository(db)

    booking = Booking(
        room=room,
        user="Repository Test",
        start_time=datetime(2026, 12, 1, 9, 0),
        end_time=datetime(2026, 12, 1, 10, 0),
        status="active",
    )

    repository.create_booking(booking)

    db.flush()

    assert booking.id is not None


def test_get_booking_by_id(db):
    repository = BookingRepository(db)

    booking = repository.get_booking_by_id(1)

    assert booking is not None


def test_get_invalid_booking_returns_none(db):
    repository = BookingRepository(db)

    booking = repository.get_booking_by_id(999999)

    assert booking is None


def test_find_conflicting_bookings(db):
    repository = BookingRepository(db)

    conflicts = repository.find_conflicting_active_bookings(
        room_id=1,
        start_time=datetime(2025, 1, 1, 9, 0),
        end_time=datetime(2025, 1, 1, 10, 0),
    )

    assert isinstance(conflicts, list)


def test_update_booking_status(db):
    repository = BookingRepository(db)

    booking = repository.get_booking_by_id(1)

    repository.update_booking_status(
        booking,
        "cancelled",
    )

    assert booking.status == "cancelled"