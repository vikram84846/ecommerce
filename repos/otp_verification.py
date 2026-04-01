from sqlalchemy.ext.asyncio import AsyncSession
from models.auth import OTPVerification
from datetime import datetime, timedelta, timezone
from sqlalchemy import select


async def create_otp_verification(db:AsyncSession,target:str,otp_code:str,expires_in_minutes:int=5):
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    otp_verification = OTPVerification(
        target=target,
        opt_code=otp_code,
        exipres_at=expires_at
    )
    db.add(otp_verification)
    await db.commit()
    await db.refresh(otp_verification)
    return otp_verification

async def mark_otp_as_used(db:AsyncSession,target:str,otp_code:str):
    stmt = select(OTPVerification).where(
        OTPVerification.otp_code == otp_code,
        OTPVerification.target == target
    ).order_by(OTPVerification.created_at.desc())
    result = await db.execute(stmt).scalars().first()
    if result:
        result.is_used = True
        await db.commit()
    return result

