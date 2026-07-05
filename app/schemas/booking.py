from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.schemas.common import ISODate, NaiveDateTime, NonEmptyString, PositiveIdentifier, SchemaModel


class BookingBase(SchemaModel):
    room_id: PositiveIdentifier
    user: NonEmptyString
    start_time: NaiveDateTime
    end_time: NaiveDateTime


class BookingCreateRequest(BookingBase):
    pass


class BookingResponse(BookingBase):
    id: PositiveIdentifier
    recurring_series_id: PositiveIdentifier | None = None
    status: Literal["active", "cancelled"]


class BookingCancellationResponse(SchemaModel):
    id: PositiveIdentifier
    status: Literal["cancelled"]


class RecurringBookingCreateRequest(BookingBase):
    repeat_until: ISODate


class RecurringBookingResponse(SchemaModel):
    recurring_series_id: PositiveIdentifier
    created_count: int = Field(ge=0)
    bookings: list[BookingResponse]


class RecurringCancellationResponse(SchemaModel):
    recurring_series_id: PositiveIdentifier
    cancelled_count: int = Field(ge=0)
    preserved_count: int = Field(ge=0)