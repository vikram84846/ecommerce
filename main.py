from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import auth
from utils.twilio import twilio_verify_client
from core.database import init_db
from core.exceptions import (
    UserNotFoundError, UserAlreadyExistsError, UserNotVerifiedError, UserInactiveError,InvalidCredentialsError, TokenExpiredError, InvalidTokenError, SessionNotFoundError, SessionRevokedError, InvalidOTPError, OTPExpiredError, OTPAlreadyUsedError,AppException
)
from fastapi.responses import JSONResponse
from core.exceptions import AppException

STATUS_MAP = {
    UserAlreadyExistsError: 409,
    UserNotFoundError: 404,
    UserNotVerifiedError: 403,
    UserInactiveError: 403,
    InvalidCredentialsError: 401,
    InvalidTokenError: 401,
    TokenExpiredError: 401,
    InvalidOTPError: 400,
    OTPAlreadyUsedError: 400,
    OTPExpiredError: 400,
    SessionNotFoundError: 404,
    SessionRevokedError: 401,
}

async def app_exception_handler(request, exc: AppException):
    status_code = STATUS_MAP.get(type(exc), 500)
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.detail}
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await twilio_verify_client.close()


app = FastAPI(lifespan=lifespan)


app.add_exception_handler(AppException, app_exception_handler)



app.include_router(auth.router)