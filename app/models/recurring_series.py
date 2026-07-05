from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String, Time, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.room import Room


class RecurringSeries(Base):
    __tablename__ = "recurring_series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    user: Mapped[str] = mapped_column(String(255), nullable=False)
    repeat_weekday: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    repeat_until: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    room: Mapped[Room] = relationship(back_populates="recurring_series")
    bookings: Mapped[list[Booking]] = relationship(back_populates="recurring_series")