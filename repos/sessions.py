from models.auth import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone, timedelta


async def create_session(db: AsyncSession, user_id: str, refresh_token: str, expires_at: datetime, user_agent: str, ip_address: str) -> Session:
    session = Session(
        user_id=user_id,
        refresh_token=refresh_token,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address
    )
    db.add(session)
    await db.flush()
    return session

async def revoke_session(db: AsyncSession, refresh_token: str):
    stmt = select(Session).where(Session.refresh_token == refresh_token)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if session:
        session.is_revoked = True
        await db.commit()
    return session

async def get_session_by_refresh_token(db: AsyncSession, refresh_token: str) -> Session | None:
    stmt = select(Session).where(Session.refresh_token == refresh_token)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if session and not session.is_revoked and session.expires_at > datetime.now(timezone.utc):
        return session
    return None