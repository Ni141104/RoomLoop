from __future__ import annotations

import re
from datetime import date, datetime
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, PlainSerializer

_NAIVE_DATETIME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
_ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _validate_naive_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed_value = value
    elif isinstance(value, str):
        if not _NAIVE_DATETIME_PATTERN.fullmatch(value):
            raise ValueError("Datetime values must use YYYY-MM-DDTHH:MM:SS without timezone information.")
        parsed_value = datetime.fromisoformat(value)
    else:
        raise TypeError("Datetime values must be provided as strings or datetime instances.")

    if parsed_value.tzinfo is not None and parsed_value.utcoffset() is not None:
        raise ValueError("Datetime values must not include timezone information.")
    if parsed_value.microsecond != 0:
        raise ValueError("Datetime values must not include fractional seconds.")

    return parsed_value.replace(tzinfo=None, microsecond=0)


def _serialize_naive_datetime(value: datetime) -> str:
    return value.replace(tzinfo=None, microsecond=0).isoformat(timespec="seconds")


def _validate_iso_date(value: Any) -> date:
    if isinstance(value, datetime):
        raise TypeError("Date values must not include time information.")
    if isinstance(value, date):
        parsed_value = value
    elif isinstance(value, str):
        if not _ISO_DATE_PATTERN.fullmatch(value):
            raise ValueError("Date values must use YYYY-MM-DD format.")
        parsed_value = date.fromisoformat(value)
    else:
        raise TypeError("Date values must be provided as strings or date instances.")

    return parsed_value


def _serialize_iso_date(value: date) -> str:
    return value.isoformat()


class SchemaModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


PositiveIdentifier = Annotated[int, Field(gt=0)]
NonEmptyString = Annotated[str, Field(min_length=1)]
NaiveDateTime = Annotated[
    datetime,
    BeforeValidator(_validate_naive_datetime),
    PlainSerializer(_serialize_naive_datetime, return_type=str),
]
ISODate = Annotated[
    date,
    BeforeValidator(_validate_iso_date),
    PlainSerializer(_serialize_iso_date, return_type=str),
]