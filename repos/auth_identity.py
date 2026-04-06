from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.auth import AuthIdentity
from schemas.enums import Provider
from core.security import hash_password


class AuthIdentityRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: str,
        provider: Provider,
        provider_user_id: str,
        password: str | None = None
    ) -> AuthIdentity:
        identity = AuthIdentity(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            password_hash=hash_password(password) if password else None
        )
        self.db.add(identity)
        await self.db.flush()
        await self.db.refresh(identity)
        return identity

    async def get_by_provider(
        self,
        provider: Provider,
        provider_user_id: str
    ) -> AuthIdentity | None:
        stmt = select(AuthIdentity).where(
            AuthIdentity.provider == provider,
            AuthIdentity.provider_user_id == provider_user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_provider(
        self,
        user_id: str,
        provider: Provider
    ) -> AuthIdentity | None:
        stmt = select(AuthIdentity).where(
            AuthIdentity.user_id == user_id,
            AuthIdentity.provider == provider
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update(
            self,
            user_id:str,
            provider: Provider,
            password: str| None
    ):
        identity = self.get_by_user_and_provider(
            user_id=user_id,
            provider=provider
        )
        if identity and password:
            identity.password_hash = hash_password(password)
            self.db.add(identity)
            await self.db.flush()
            await self.db.refresh(identity)
            return identity
        raise ValueError("Auth identity not found")
        