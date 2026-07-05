from __future__ import annotations

from app.models.booking import Booking
from app.models.recurring_series import RecurringSeries
from app.models.room import Room


def test_room_has_booking_relationship():
    assert "bookings" in Room.__mapper__.relationships


def test_room_has_recurring_series_relationship():
    assert "recurring_series" in Room.__mapper__.relationships


def test_booking_has_room_relationship():
    assert "room" in Booking.__mapper__.relationships


def test_booking_has_recurring_series_relationship():
    assert "recurring_series" in Booking.__mapper__.relationships


def test_recurring_series_has_room_relationship():
    assert "room" in RecurringSeries.__mapper__.relationships


def test_recurring_series_has_bookings_relationship():
    assert "bookings" in RecurringSeries.__mapper__.relationships