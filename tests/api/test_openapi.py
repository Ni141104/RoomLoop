from __future__ import annotations

from tests.api.conftest import client


def test_openapi_contains_rooms():
    schema = client.get("/openapi.json").json()

    assert "/rooms" in schema["paths"]


def test_openapi_contains_bookings():
    schema = client.get("/openapi.json").json()

    assert "/bookings" in schema["paths"]


def test_openapi_contains_recurring():
    schema = client.get("/openapi.json").json()

    assert "/bookings/recurring" in schema["paths"]