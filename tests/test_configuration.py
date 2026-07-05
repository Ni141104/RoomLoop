from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

REQUIRED_ENV = {
    "APP_NAME": "RoomLoop",
    "APP_ENV": "development",
    "HOST": "127.0.0.1",
    "PORT": "8000",
    "DATABASE_HOST": "localhost",
    "DATABASE_PORT": "3306",
    "DATABASE_NAME": "roomloop",
    "DATABASE_USER": "root",
    "DATABASE_PASSWORD": "",
    "TIMEZONE_DEFAULT": "UTC",
}


def set_required_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)


# ----------------------------------------------------------------------
# Configuration Tests
# ----------------------------------------------------------------------


def test_get_settings_loads_all_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Configuration should load successfully from environment variables."""

    set_required_environment(monkeypatch)
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.app_name == "RoomLoop"
    assert settings.app_env == "development"
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000

    assert settings.database_host == "localhost"
    assert settings.database_port == 3306
    assert settings.database_name == "roomloop"
    assert settings.database_user == "root"

    # Empty password should now be accepted
    assert settings.database_password == ""

    assert settings.timezone_default == "UTC"


def test_missing_required_environment_variable_raises_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing required environment variables should fail fast."""

    set_required_environment(monkeypatch)

    monkeypatch.delenv("DATABASE_HOST")

    get_settings.cache_clear()

    with pytest.raises(RuntimeError, match="DATABASE_HOST"):
        get_settings()


def test_empty_database_password_is_allowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Local MySQL installations commonly use an empty root password.
    The configuration should allow this.
    """

    set_required_environment(monkeypatch)

    monkeypatch.setenv("DATABASE_PASSWORD", "")

    get_settings.cache_clear()

    settings = get_settings()

    assert settings.database_password == ""


def test_invalid_port_raises_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PORT must be an integer."""

    set_required_environment(monkeypatch)

    monkeypatch.setenv("PORT", "abc")

    get_settings.cache_clear()

    with pytest.raises(RuntimeError, match="PORT"):
        get_settings()


# ----------------------------------------------------------------------
# FastAPI Application Tests
# ----------------------------------------------------------------------


def test_application_can_be_created(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Application factory should successfully create a FastAPI app."""

    set_required_environment(monkeypatch)
    get_settings.cache_clear()

    app = create_app()

    assert app.title == "RoomLoop"


def test_health_endpoint_returns_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Health endpoint should return HTTP 200."""

    set_required_environment(monkeypatch)
    get_settings.cache_clear()

    app = create_app()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "RoomLoop API is running."
    }


def test_application_title_comes_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Changing APP_NAME should change the FastAPI title."""

    set_required_environment(monkeypatch)

    monkeypatch.setenv("APP_NAME", "RoomLoop Test")

    get_settings.cache_clear()

    app = create_app()

    assert app.title == "RoomLoop Test"