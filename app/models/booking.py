from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

if TYPE_CHECKING:
    from app.models.recurring_series import RecurringSeries
    from app.models.room import Room


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    recurring_series_id: Mapped[int | None] = mapped_column(
        ForeignKey("recurring_series.id"),
        nullable=True,
    )
    user: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    room: Mapped[Room] = relationship(back_populates="bookings")
    recurring_series: Mapped[RecurringSeries | None] = relationship(back_populates="bookings")