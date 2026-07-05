from __future__ import annotations

from datetime import datetime

from app.models.booking import Booking
from app.models.room import Room


def test_booking_model_can_be_created():
    room = Room(
        name="Room A",
        capacity=8,
        timezone="UTC",
    )

    booking = Booking(
        room=room,
        user="Nikhil",
        start_time=datetime(2026, 1, 5, 9, 0),
        end_time=datetime(2026, 1, 5, 10, 0),
        status="active",
    )

    assert booking.room == room
    assert booking.user == "Nikhil"
    assert booking.status == "active"


def test_booking_supports_cancelled_status():
    booking = Booking(status="cancelled")

    assert booking.status == "cancelled"


def test_booking_has_required_relationships():
    booking = Booking()

    assert hasattr(booking, "room")
    assert hasattr(booking, "recurring_series")