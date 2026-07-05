from pathlib import Path

API_DIR = Path("app/api")


def test_routes_do_not_commit_transactions():
    for file in API_DIR.glob("*.py"):

        source = file.read_text()

        assert ".commit(" not in source
        assert ".rollback(" not in source


def test_routes_do_not_execute_sql():
    for file in API_DIR.glob("*.py"):

        source = file.read_text().lower()

        assert "select " not in source
        assert "insert " not in source
        assert "update " not in source
        assert "delete from" not in source


def test_rooms_route_uses_room_service():
    source = Path("app/api/rooms.py").read_text()

    assert "RoomService" in source


def test_bookings_route_uses_booking_service():
    source = Path("app/api/bookings.py").read_text()

    assert "BookingService" in source


def test_bookings_route_uses_recurring_service():
    source = Path("app/api/bookings.py").read_text()

    assert "RecurringService" in source