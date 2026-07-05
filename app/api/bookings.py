from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.booking import (
    BookingCancellationResponse,
    BookingCreateRequest,
    BookingResponse,
    RecurringBookingCreateRequest,
    RecurringBookingResponse,
    RecurringCancellationResponse,
)
from app.services.booking_service import BookingService
from app.services.recurring_service import RecurringService

router = APIRouter(tags=["Bookings"])


@router.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    request: BookingCreateRequest,
    db: Session = Depends(get_db),
) -> BookingResponse:
    booking = BookingService(db).create_booking(
        room_id=request.room_id,
        user=request.user,
        start_time=request.start_time,
        end_time=request.end_time,
    )

    return BookingResponse.model_validate(booking)


@router.delete(
    "/bookings/{booking_id}",
    response_model=BookingCancellationResponse,
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
) -> BookingCancellationResponse:
    booking = BookingService(db).cancel_booking(booking_id)

    return BookingCancellationResponse(
        id=booking.id,
        status="cancelled",
    )


@router.post(
    "/bookings/recurring",
    response_model=RecurringBookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recurring_booking(
    request: RecurringBookingCreateRequest,
    db: Session = Depends(get_db),
) -> RecurringBookingResponse:

    series, bookings = RecurringService(db).create_recurring_booking(
        room_id=request.room_id,
        user=request.user,
        start_time=request.start_time,
        end_time=request.end_time,
        repeat_until=request.repeat_until,
    )

    return RecurringBookingResponse(
        recurring_series_id=series.id,
        created_count=len(bookings),
        bookings=[
            BookingResponse.model_validate(booking)
            for booking in bookings
        ],
    )


@router.delete(
    "/bookings/recurring/{series_id}",
    response_model=RecurringCancellationResponse,
)
def cancel_recurring_booking(
    series_id: int,
    db: Session = Depends(get_db),
) -> RecurringCancellationResponse:

    series, cancelled = RecurringService(db).cancel_recurring_series(
        series_id,
    )

    return RecurringCancellationResponse(
        recurring_series_id=series.id,
        cancelled_count=len(cancelled),
        preserved_count=len(series.bookings) - len(cancelled),
    )