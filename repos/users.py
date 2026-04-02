from models.auth import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select



class UserRepo:
    def __init__(self, db:AsyncSession):
        self.db = db
    
    async def get_user_by_email_or_phone(
            self,
            email:str | None = None,
            phone:str | None = None
    ):
        if email:
            stmt = select(UserModel).where(UserModel.email == email)
        if phone:
            stmt = select(UserModel).where(UserModel.phone == phone)
        
        result = await self.db.execute(stmt)
        record = result.scalar_one_or_none()
        return record
    
    async def get_user_by_id(self, user_id: str):
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.db.execute(stmt)
        record = result.scalar_one_or_none()
        return record
    
    async def create(
            self,
            email:str | None = None,
            phone:str | None = None,
            role: str = "consumer"
             )-> UserModel:
        record = UserModel(
            email=email,
            phone=phone,
            role=role
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record
