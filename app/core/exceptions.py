from __future__ import annotations


class DomainError(Exception):
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(DomainError):
    code = "BAD_REQUEST"


class NotFoundError(DomainError):
    code = "NOT_FOUND"


class ConflictError(DomainError):
    code = "BOOKING_CONFLICT"


class RoomNotFoundError(NotFoundError):
    pass


class BookingNotFoundError(NotFoundError):
    pass


class RecurringSeriesNotFoundError(NotFoundError):
    pass


class InvalidTimeRangeError(ValidationError):
    pass


class InvalidRecurringDateRangeError(ValidationError):
    pass


class BookingConflictError(ConflictError):
    pass
