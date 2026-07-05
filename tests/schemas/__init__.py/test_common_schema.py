from __future__ import annotations

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from app.schemas.common import ISODate, NaiveDateTime, SchemaModel


class DateTimeModel(SchemaModel):
    value: NaiveDateTime


class DateModel(SchemaModel):
    value: ISODate


def test_naive_datetime_is_accepted():
    model = DateTimeModel(
        value="2026-01-10T09:30:00",
    )

    assert model.value == datetime(2026, 1, 10, 9, 30)


def test_timezone_datetime_is_rejected():
    with pytest.raises(ValidationError):
        DateTimeModel(
            value="2026-01-10T09:30:00+05:30",
        )


def test_fractional_seconds_are_rejected():
    with pytest.raises(ValidationError):
        DateTimeModel(
            value="2026-01-10T09:30:00.123",
        )


def test_iso_date_is_accepted():
    model = DateModel(
        value="2026-12-31",
    )

    assert model.value == date(2026, 12, 31)


def test_invalid_date_is_rejected():
    with pytest.raises(ValidationError):
        DateModel(
            value="31-12-2026",
        )


def test_serialization_keeps_naive_datetime():
    model = DateTimeModel(
        value=datetime(2026, 1, 1, 10, 0),
    )

    dumped = model.model_dump()

    assert dumped["value"] == "2026-01-01T10:00:00"