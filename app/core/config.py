from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str
    app_env: str
    host: str
    port: int
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str
    timezone_default: str


def _require_env(name: str, *, allow_empty: bool = False) -> str:
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")

    value = value.strip()

    if not allow_empty and value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


def _require_int_env(name: str) -> int:
    raw_value = _require_env(name)
    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be an integer") from exc


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=_require_env("APP_NAME"),
        app_env=_require_env("APP_ENV"),
        host=_require_env("HOST"),
        port=_require_int_env("PORT"),
        database_host=_require_env("DATABASE_HOST"),
        database_port=_require_int_env("DATABASE_PORT"),
        database_name=_require_env("DATABASE_NAME"),
        database_user=_require_env("DATABASE_USER"),
        database_password=_require_env(
                "DATABASE_PASSWORD",
                allow_empty=True,
            ),
        timezone_default=_require_env("TIMEZONE_DEFAULT"),
    )