from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response, Request
from services.user_service import UserService
from dependency.common import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.auth import UserCreate, UserRead, verifyOTPRequest, ResendOTPRequest, EmailLoginRequest, PhoneLoginRequest
from services.auth_service import AuthService
from core.config import get_settings
from core.constants import REFRESH_TOKEN_EXPIRE_DAYS
settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_token(response:Response,refresh_token:str):
    response.set_cookie(
        key= "refresh_token",
        value = refresh_token,
        httponly=True,
        samesite="strict",
        max_age= REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600

    )

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
    

@router.post("/verify-otp")
async def verify_otp(
    data: verifyOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    await auth_service.verify_otp(data)
    return {"message": "OTP verified successfully"}

@router.post("/resend-otp")
async def resend_otp(
    data: ResendOTPRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db, background_tasks)
    await auth_service.resend_otp(data)
    return {"message": "OTP resent successfully"}

@router.post("/login/email")
async def email_login(
    data: EmailLoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    tokens = await auth_service.login_email(data,request)
    access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]
    # Set HttpOnly cookie for refresh token
    _set_refresh_token(response,refresh_token)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/phone")
async def phone_login(
    data: PhoneLoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    tokens = await auth_service.login_phone(data,request)
    access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]
    # Set HttpOnly cookie for refresh token
    _set_refresh_token(response,refresh_token)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh_tokens(request:Request,response:Response,db:AsyncSession= Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    auth_service = AuthService(db)
    if refresh_token:
        tokens = await auth_service.refresh_tokens(refresh_token=refresh_token)
        access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]
        #set refresh_token 
        _set_refresh_token(response, refresh_token)
        return {
            "access_token": access_token, "token_type":"bearer"
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "token missing"
    )

@router.post("/logout")
async def logout(request:Request,db:AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await auth_service.logout(refresh_token)
        return {
            "success":"ok",
            "detail":"user loged out successfuly"
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token missing"
    )