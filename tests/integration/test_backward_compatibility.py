from tests.integration.conftest import client


def test_rooms_response_contract():

    response = client.get("/rooms")

    room = response.json()[0]

    assert "id" in room
    assert "name" in room
    assert "capacity" in room

    assert "timezone" not in room


def test_timestamp_format():

    booking = client.post(
        "/bookings",
        json={
            "room_id": 1,
            "user": "Timestamp",
            "start_time": "2026-11-10T09:00:00",
            "end_time": "2026-11-10T10:00:00",
        },
    ).json()

    assert "Z" not in booking["start_time"]
    assert "+" not in booking["start_time"]