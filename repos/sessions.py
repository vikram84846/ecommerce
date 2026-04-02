# session_repo.py
import hashlib
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.auth import Session
from core.constants import REFRESH_TOKEN_EXPIRE_DAYS


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


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
        expires_at: datetime | None = None      
    ) -> Session:
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        session = Session(
            user_id=user_id,
            refresh_token=_hash_token(refresh_token),  
            user_agent=user_agent,
            ip_address=ip_address,
            device_id=device_id,
            expires_at=expires_at
        )
        self.db.add(session)
        await self.db.flush()       
        await self.db.refresh(session)
        return session

    async def get_by_refresh_token(self, refresh_token: str) -> Session | None:
        result = await self.db.execute(
            select(Session).where(
                Session.refresh_token == _hash_token(refresh_token),  
                Session.is_revoked == False,
                Session.expires_at > datetime.now(timezone.utc)
            )
        )
        return result.scalar_one_or_none()

    async def revoke_by_refresh_token(self, refresh_token: str) -> None:
        session = await self.get_by_refresh_token(refresh_token)
        if session:
            session.is_revoked = True
            await self.db.flush()

    async def get_active_sessions(self, user_id: str) -> list[Session]:
        result = await self.db.execute(
            select(Session).where(
                Session.user_id == user_id,
                Session.is_revoked == False,
                Session.expires_at > datetime.now(timezone.utc)
            )
        )
        return result.scalars().all()

    async def revoke_all(self, user_id: str) -> None:
        await self.db.execute(
            update(Session)
            .where(Session.user_id == user_id, Session.is_revoked == False)
            .values(is_revoked=True)
        )
        await self.db.flush()