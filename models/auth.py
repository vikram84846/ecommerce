from .base import Base, TimeStampMixin, SoftDeleteMixin, UUIDMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime
from enum import Enum
from datetime import datetime

class Provider(Enum,str):
    email = "email"
    phonne = "phone"
    google = "goolge"

class Role(Enum,str):
    consumer = "consumer"
    retailer = "retailer"
    admin = "admin"

class UserModel(Base,TimeStampMixin,UUIDMixin,SoftDeleteMixin):
    email:Mapped[str | None] = mapped_column(index=True,unique=True)
    phone: Mapped[str | None] = mapped_column(index=True, unique=True)
    is_active: Mapped[bool] = mapped_column(server_default="true")
    is_verified: Mapped[bool] = mapped_column(server_default="false")
    role: Mapped[Role] = mapped_column(default=Role.consumer)


class AuthIdentity(Base,TimeStampMixin,UUIDMixin):
    __tablename__="auth_identites"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    provider: Mapped[Provider] = mapped_column()
    provider_user_id: Mapped[str] = mapped_column()
    password_hash: Mapped[str | None] = mapped_column()


class Session(Base,TimeStampMixin,UUIDMixin):
    __tablename__= "sessions"
    refresh_token: Mapped[str] = mapped_column()
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    is_revoked: Mapped[bool] = mapped_column(server_default="false")
    user_agent: Mapped[str] = mapped_column()
    ip_address: Mapped[str] = mapped_column()


class OTPVerification(Base,UUIDMixin,TimeStampMixin):
    __tablename__ = "otp_verifications"
    opt_code:Mapped[str] = mapped_column()
    exipres_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_used: Mapped[bool] = mapped_column(server_default="false")
    target: Mapped[str] = mapped_column()