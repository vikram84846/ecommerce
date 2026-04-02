from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from services.user_service import UserService
from dependency.common import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.auth import UserCreate, UserRead


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead)
async def register(
    data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db, background_tasks)
    try:
        user = await user_service.register(data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))