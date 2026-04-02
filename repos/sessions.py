from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.auth import Session
from datetime import datetime, timezone, timedelta
from core.constants import REFRESH_TOKEN_EXPIRE_DAYS
from core.security import hash_password, verify_password



class SessionRepo:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
            self,
            user_id: str,
            refresh_token: str,
            user_agent: str | None = None,
            ip_address: str | None = None,
            device_id: str | None = None,
            epires_at: datetime | None = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )->Session:
        new_session = Session(
            user_id=user_id,
            refresh_token=hash_password(refresh_token),
            user_agent=user_agent,
            ip_address=ip_address,
            device_id=device_id,
            expires_at=epires_at
        )
        self.db.add(new_session)
        await self.db.refresh(new_session)
        return new_session
    
    async def get_by_refresh_token(self, refresh_token: str) -> Session | None:
        result = await self.db.execute(
            select(Session).where(Session.refresh_token == hash_password(refresh_token))
        )
        session = result.scalar_one_or_none()
        if session and not session.is_revoked and session.expires_at > datetime.now(timezone.utc):
            return session
        return None
    
    async def revoke_by_refresh_token(self, refresh_token: str) -> None:
        session = await self.get_by_refresh_token(refresh_token)
        if session:
            session.is_revoked = True
            self.db.add(session)
            await self.db.flush()

    async def get_active_user_sessions(self, user_id: str) -> list[Session]:
        result = await self.db.execute(
            select(Session).where(Session.user_id == user_id, Session.is_revoked == False, Session.expires_at > datetime.now(timezone.utc))
        )
        return result.scalars().all()
    
    async def revoke_all_user_sessions(self, user_id: str) -> None:
        await self.db.execute(
            update(Session).where(Session.user_id == user_id, Session.is_revoked == False).values(is_revoked=True)
        )
        await self.db.flush()