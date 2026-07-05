from __future__ import annotations

from tests.api.conftest import client


def test_invalid_recurring_payload():
    response = client.post(
        "/bookings/recurring",
        json={}
    )

    assert response.status_code == 422


def test_invalid_repeat_until():
    response = client.post(
        "/bookings/recurring",
        json={
            "room_id": 1,
            "user": "Nikhil",
            "start_time": "2026-01-01T09:00:00",
            "end_time": "2026-01-01T10:00:00",
            "repeat_until": "abc"
        }
    )

    assert response.status_code == 422


def test_delete_unknown_series():
    response = client.delete(
        "/bookings/recurring/999999"
    )

    assert response.status_code in (404, 400)


def test_recurring_endpoint_exists():
    response = client.options("/bookings/recurring")

    assert response.status_code != 404