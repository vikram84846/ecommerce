# base.py
from sqlalchemy import func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime
from uuid import UUID, uuid4


class Base(DeclarativeBase):
    pass


class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class UUIDMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(server_default="false")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))