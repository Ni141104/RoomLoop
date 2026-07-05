from __future__ import annotations

from tests.api.conftest import client


def test_get_rooms_returns_success():
    response = client.get("/rooms")

    assert response.status_code == 200


def test_rooms_returns_array():
    response = client.get("/rooms")

    assert isinstance(response.json(), list)


def test_room_contains_expected_fields():
    response = client.get("/rooms")

    if response.json():
        room = response.json()[0]

        assert "id" in room
        assert "name" in room
        assert "capacity" in room


def test_room_response_does_not_expose_timezone():
    response = client.get("/rooms")

    if response.json():
        room = response.json()[0]

        assert "timezone" not in room