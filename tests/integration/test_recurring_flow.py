from tests.integration.conftest import client


def test_create_and_cancel_recurring_booking():

    response = client.post(
        "/bookings/recurring",
        json={
            "room_id": 1,
            "user": "Integration",
            "start_time": "2026-12-07T09:00:00",
            "end_time": "2026-12-07T10:00:00",
            "repeat_until": "2027-01-31",
        },
    )

    assert response.status_code == 201

    recurring = response.json()

    cancel = client.delete(
        f"/bookings/recurring/{recurring['recurring_series_id']}"
    )

    assert cancel.status_code == 200