from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.auth import OTPVerification
from schemas.enums import OTPPurpose
from core.security import hash_password, verify_password
from core.constants import OTP_EXPIRE_MINUTES


class OTPRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        target: str,
        otp: str,
        purpose: OTPPurpose,
        expires_in_minutes: int = OTP_EXPIRE_MINUTES
    ) -> OTPVerification:
        record = OTPVerification(
            target=target,
            otp_hash=hash_password(otp),       
            purpose=purpose,                    
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def verify(
        self,
        target: str,
        otp: str,
        purpose: OTPPurpose
    ) -> OTPVerification | None:
        stmt = select(OTPVerification).where(
            OTPVerification.target == target,
            OTPVerification.purpose == purpose,         
            OTPVerification.is_used == False,
            OTPVerification.expires_at > datetime.now(timezone.utc)  
        )
        result = await self.db.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        if not verify_password(otp, record.otp_hash):  
            return None

        record.is_used = True
        await self.db.flush()
        return record

    async def invalidate_previous(
        self,
        target: str,
        purpose: OTPPurpose
    ) -> None:
        """Naya OTP bhejne se pehle purane invalidate karo"""
        stmt = select(OTPVerification).where(
            OTPVerification.target == target,
            OTPVerification.purpose == purpose,
            OTPVerification.is_used == False
        )
        result = await self.db.execute(stmt)
        records = result.scalars().all()
        for record in records:
            record.is_used = True
        await self.db.flush()