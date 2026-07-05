from tests.integration.conftest import client


def test_rooms_endpoint_returns_success():
    response = client.get("/rooms")

    assert response.status_code == 200


def test_rooms_endpoint_returns_list():
    response = client.get("/rooms")

    assert isinstance(response.json(), list)


def test_rooms_have_required_fields():
    rooms = client.get("/rooms").json()

    if rooms:
        room = rooms[0]

        assert "id" in room
        assert "name" in room
        assert "capacity" in room