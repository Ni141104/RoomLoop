from __future__ import annotations

from tests.api.conftest import client


def test_invalid_booking_payload_returns_validation_error():
    response = client.post(
        "/bookings",
        json={}
    )

    assert response.status_code == 422


def test_invalid_booking_time_format():
    response = client.post(
        "/bookings",
        json={
            "room_id": 1,
            "user": "Nikhil",
            "start_time": "invalid",
            "end_time": "invalid"
        }
    )

    assert response.status_code == 422


def test_delete_unknown_booking():
    response = client.delete("/bookings/999999")

    assert response.status_code in (404, 400)


def test_post_endpoint_exists():
    response = client.options("/bookings")

    assert response.status_code != 404