from __future__ import annotations

from fastapi import FastAPI

from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name)

    @application.get("/")
    def health_check() -> dict[str, str]:
        return {"message": "RoomLoop API is running."}

    return application


app = create_app()