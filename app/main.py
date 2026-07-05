from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api import bookings_router, rooms_router
from app.core.config import get_settings
from app.core.exceptions import (
    ConflictError,
    DomainError,
    NotFoundError,
    ValidationError,
)


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
    )

    @application.get("/")
    def health_check() -> dict[str, str]:
        return {"message": "RoomLoop API is running."}

    application.include_router(rooms_router)
    application.include_router(bookings_router)

    @application.exception_handler(ValidationError)
    async def validation_exception_handler(_, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    @application.exception_handler(NotFoundError)
    async def not_found_exception_handler(_, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    @application.exception_handler(ConflictError)
    async def conflict_exception_handler(_, exc: ConflictError):
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    @application.exception_handler(DomainError)
    async def domain_exception_handler(_, exc: DomainError):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    return application


app = create_app()