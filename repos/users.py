# user_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.auth import UserModel
from schemas.enums import Role


class UserRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email_or_phone(
        self,
        email: str | None = None,
        phone: str | None = None
    ) -> UserModel | None:
        if not email and not phone:
            raise ValueError("email or phone required")

        if email:
            stmt = select(UserModel).where(
                UserModel.email == email,
                UserModel.is_deleted == False
            )
        else:
            stmt = select(UserModel).where(
                UserModel.phone == phone,
                UserModel.is_deleted == False
            )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> UserModel | None:
        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str | None = None,
        phone: str | None = None,
        role: Role = Role.consumer
    ) -> UserModel:
        user = UserModel(email=email, phone=phone, role=role)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user