from models.auth import AuthIdentity, Provider
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import hash_password
from sqlalchemy import select


async def create_auth_identity(db: AsyncSession, user_id:str, provider:Provider, provider_user_id:str, password:str | None = None) -> AuthIdentity:
    password_hash = hash_password(password) if password else None
    auth_identity = AuthIdentity(
        user_id=user_id,
        provider=provider,
        provider_user_id=provider_user_id,
        password_hash=password_hash
    )

    await db.add(auth_identity)
    return auth_identity

async def get_auth_identity(db: AsyncSession, provider: Provider, provider_user_id: str) -> AuthIdentity | None:
    stmt = select(AuthIdentity).where(
        AuthIdentity.provider == provider,
        AuthIdentity.provider_user_id == provider_user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

