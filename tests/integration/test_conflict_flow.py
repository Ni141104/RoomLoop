from tests.integration.conftest import client


def test_overlapping_booking_is_rejected():

    booking = {
        "room_id": 1,
        "user": "Conflict",
        "start_time": "2026-12-20T09:00:00",
        "end_time": "2026-12-20T10:00:00",
    }

    assert client.post("/bookings", json=booking).status_code == 201

    conflict = client.post("/bookings", json=booking)

    assert conflict.status_code == 409