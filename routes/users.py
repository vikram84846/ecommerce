from fastapi import HTTPException, status, APIRouter, BackgroundTasks, Depends
from services.user_service import UserRepo
from sqlalchemy.ext.asyncio import AsyncSession
from dependency.common import get_db

router = APIRouter(prefix="/users",tags="user")


@router.post("/forget-password")
async def forget_email_password(bg_tasks:BackgroundTasks,db: AsyncSession =Depends(get_db)):
    user_service = UserRepo(db)
    

    