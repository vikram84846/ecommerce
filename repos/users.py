from schemas.auth import UserCreate, UserRead
from models.auth import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def get_user_by_email_or_phone(db: AsyncSession, email: str | None = None, phone: str | None = None) -> UserModel | None:
    stmt = select(UserModel).where(
        (UserModel.email == email) | (UserModel.phone == phone)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_create: UserCreate) -> UserModel:
    user = UserModel(
        email=user_create.email,
        phone=user_create.phone,
        role=user_create.role
    )
    db.add(user)
    await db.flush()
    return user

async def get_user_by_id(db: AsyncSession, user_id: str) -> UserModel | None:
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
