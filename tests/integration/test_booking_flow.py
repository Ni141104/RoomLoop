from tests.integration.conftest import client


def test_complete_booking_lifecycle():

    create = client.post(
        "/bookings",
        json={
            "room_id": 1,
            "user": "Integration Test",
            "start_time": "2026-12-01T09:00:00",
            "end_time": "2026-12-01T10:00:00",
        },
    )

    assert create.status_code == 201

    booking = create.json()

    cancel = client.delete(
        f"/bookings/{booking['id']}"
    )

    assert cancel.status_code == 200

    recreate = client.post(
        "/bookings",
        json={
            "room_id": 1,
            "user": "Integration Test",
            "start_time": "2026-12-01T09:00:00",
            "end_time": "2026-12-01T10:00:00",
        },
    )

    assert recreate.status_code == 201