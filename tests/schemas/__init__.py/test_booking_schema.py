from __future__ import annotations

from pydantic import ValidationError
import pytest
from app.schemas.booking import (
    BookingCancellationResponse,
    BookingCreateRequest,
    BookingResponse,
    RecurringBookingCreateRequest,
    RecurringBookingResponse,
)


def test_booking_create_request():
    request = BookingCreateRequest(
        room_id=1,
        user="Nikhil",
        start_time="2026-01-01T09:00:00",
        end_time="2026-01-01T10:00:00",
    )

    assert request.room_id == 1


def test_booking_create_rejects_extra_fields():
    try:
        BookingCreateRequest(
            room_id=1,
            user="Nikhil",
            start_time="2026-01-01T09:00:00",
            end_time="2026-01-01T10:00:00",
            invalid=True,
        )
        assert False
    except ValidationError:
        pass


def test_booking_response():
    response = BookingResponse(
        id=1,
        room_id=1,
        user="Nikhil",
        start_time="2026-01-01T09:00:00",
        end_time="2026-01-01T10:00:00",
        recurring_series_id=None,
        status="active",
    )

    assert response.status == "active"


def test_booking_cancel_response():
    response = BookingCancellationResponse(
        id=10,
        status="cancelled",
    )

    assert response.status == "cancelled"


def test_recurring_booking_request():
    request = RecurringBookingCreateRequest(
        room_id=1,
        user="Nikhil",
        start_time="2026-01-01T09:00:00",
        end_time="2026-01-01T10:00:00",
        repeat_until="2026-06-01",
    )

    assert request.repeat_until.year == 2026


def test_recurring_booking_response():
    response = RecurringBookingResponse(
        recurring_series_id=5,
        created_count=3,
        bookings=[],
    )

    assert response.created_count == 3


def test_negative_identifier_rejected():
    with pytest.raises(ValidationError):
        BookingCreateRequest(
            room_id=-1,
            user="Nikhil",
            start_time="2026-01-01T09:00:00",
            end_time="2026-01-01T10:00:00",
        )