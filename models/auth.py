# auth.py
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimeStampMixin, SoftDeleteMixin, UUIDMixin
from schemas.enums import Provider, Role, OTPPurpose


class UserModel(Base, TimeStampMixin, UUIDMixin, SoftDeleteMixin):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "(email IS NOT NULL) OR (phone IS NOT NULL)",
            name="ck_email_or_phone_not_null"
        ),
    )

    email: Mapped[str | None] = mapped_column(index=True, unique=True)
    phone: Mapped[str | None] = mapped_column(index=True, unique=True)
    is_active: Mapped[bool] = mapped_column(server_default="true")
    is_verified: Mapped[bool] = mapped_column(server_default="false")
    role: Mapped[Role] = mapped_column(default=Role.consumer)

    auth_identities: Mapped[list["AuthIdentity"]] = relationship(back_populates="user")
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")


class AuthIdentity(Base, TimeStampMixin, UUIDMixin):
    __tablename__ = "auth_identities"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_user"),
        UniqueConstraint("user_id", "provider", name="uq_user_provider"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    provider: Mapped[Provider] = mapped_column()
    provider_user_id: Mapped[str] = mapped_column()
    password_hash: Mapped[str | None] = mapped_column()

    user: Mapped["UserModel"] = relationship(back_populates="auth_identities")


class Session(Base, TimeStampMixin, UUIDMixin):
    __tablename__ = "sessions"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    refresh_token: Mapped[str] = mapped_column(unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_revoked: Mapped[bool] = mapped_column(server_default="false")
    user_agent: Mapped[str | None] = mapped_column()
    ip_address: Mapped[str | None] = mapped_column()
    device_id: Mapped[str | None] = mapped_column()

    user: Mapped["UserModel"] = relationship(back_populates="sessions")


class OTPVerification(Base, UUIDMixin, TimeStampMixin):
    __tablename__ = "otp_verifications"
    __table_args__ = (
        Index("idx_target_purpose", "target", "purpose"),  
    )

    target: Mapped[str] = mapped_column(index=True)
    otp_hash: Mapped[str] = mapped_column()
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_used: Mapped[bool] = mapped_column(server_default="false")
    purpose: Mapped[OTPPurpose] = mapped_column()
