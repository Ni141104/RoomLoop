from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


def load_timezone(timezone_name: str) -> ZoneInfo:
    return ZoneInfo(timezone_name)


def _coerce_timezone(timezone_value: str | ZoneInfo) -> ZoneInfo:
    if isinstance(timezone_value, ZoneInfo):
        return timezone_value
    return load_timezone(timezone_value)


def determine_recurring_weekday(value: date | datetime) -> int:
    if isinstance(value, datetime):
        return value.date().weekday()
    return value.weekday()


def convert_naive_local_datetime_to_timezone_aware_datetime(
    local_datetime: datetime,
    timezone_value: str | ZoneInfo,
) -> datetime:
    timezone_object = _coerce_timezone(timezone_value)
    if local_datetime.tzinfo is not None:
        return local_datetime.astimezone(timezone_object)

    aware_datetime = datetime(
        local_datetime.year,
        local_datetime.month,
        local_datetime.day,
        local_datetime.hour,
        local_datetime.minute,
        local_datetime.second,
        local_datetime.microsecond,
        tzinfo=timezone_object,
        fold=0,
    )
    return aware_datetime.astimezone(timezone.utc).astimezone(timezone_object)


def convert_timezone_aware_datetime_to_naive_local_datetime(
    aware_datetime: datetime,
) -> datetime:
    if aware_datetime.tzinfo is None:
        return aware_datetime
    return aware_datetime.astimezone(aware_datetime.tzinfo).replace(tzinfo=None)


def _combine_local_date_and_time(
    local_date: date,
    local_time: time,
    timezone_value: str | ZoneInfo,
) -> datetime:
    timezone_object = _coerce_timezone(timezone_value)
    naive_datetime = datetime.combine(local_date, local_time)
    aware_datetime = datetime(
        naive_datetime.year,
        naive_datetime.month,
        naive_datetime.day,
        naive_datetime.hour,
        naive_datetime.minute,
        naive_datetime.second,
        naive_datetime.microsecond,
        tzinfo=timezone_object,
        fold=0,
    )
    return aware_datetime.astimezone(timezone.utc).astimezone(timezone_object)


def generate_weekly_recurrence_dates(
    first_occurrence_date: date,
    repeat_until: date,
) -> list[date]:
    if repeat_until < first_occurrence_date:
        return []

    recurring_dates: list[date] = []
    current_date = first_occurrence_date
    while current_date <= repeat_until:
        recurring_dates.append(current_date)
        current_date += timedelta(days=7)
    return recurring_dates


def generate_weekly_occurrences(
    start_datetime: datetime,
    end_datetime: datetime,
    repeat_until: date,
    timezone_value: str | ZoneInfo,
) -> list[tuple[datetime, datetime]]:
    recurring_dates = generate_weekly_recurrence_dates(start_datetime.date(), repeat_until)
    if not recurring_dates:
        return []

    recurring_start_time = start_datetime.time()
    recurring_end_time = end_datetime.time()

    occurrences: list[tuple[datetime, datetime]] = []
    for recurring_date in recurring_dates:
        start_aware = _combine_local_date_and_time(
            recurring_date,
            recurring_start_time,
            timezone_value,
        )
        end_aware = _combine_local_date_and_time(
            recurring_date,
            recurring_end_time,
            timezone_value,
        )
        occurrences.append(
            (
                convert_timezone_aware_datetime_to_naive_local_datetime(start_aware),
                convert_timezone_aware_datetime_to_naive_local_datetime(end_aware),
            )
        )

    return occurrences


__all__ = [
    "convert_naive_local_datetime_to_timezone_aware_datetime",
    "convert_timezone_aware_datetime_to_naive_local_datetime",
    "determine_recurring_weekday",
    "generate_weekly_occurrences",
    "generate_weekly_recurrence_dates",
    "load_timezone",
]