import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, Request

from repos.users import UserRepo
from repos.otp_verification import OTPRepo
from repos.sessions import SessionRepo
from repos.auth_identity import AuthIdentityRepo
from utils.twilio import twilio_verify_client

from schemas.auth import (
    UserRead,
    verifyOTPRequest,
    ResendOTPRequest,
    EmailLoginRequest,
    PhoneLoginRequest,
)
from schemas.enums import Provider, OTPPurpose

from core.security import verify_password, create_jwt_token
from core.constants import OTP_LENGTH
from core.exceptions import (
    UserNotFoundError,
    UserNotVerifiedError,
    UserInactiveError,
    InvalidCredentialsError,
    InvalidOTPError,
    SessionNotFoundError,
)

from utils.email_clinet import mail_service
from utils.twilio import twilio_verify_client


def _generate_otp(length: int = OTP_LENGTH) -> str:
    return "".join([str(secrets.randbelow(10)) for _ in range(length)])


class AuthService:
    def __init__(self, db: AsyncSession, background_tasks: BackgroundTasks | None = None):
        self.db = db
        self.background_tasks = background_tasks
        self.user_repo = UserRepo(db)
        self.otp_repo = OTPRepo(db)
        self.session_repo = SessionRepo(db)
        self.identity_repo = AuthIdentityRepo(db)

    # ------------------------------------------------------------------ #
    #  VERIFY OTP                                                          #
    # ------------------------------------------------------------------ #

    async def verify_otp(self, data: verifyOTPRequest) -> UserRead:
        is_email = "@" in data.target

        # 🔹 Step 1: Verify OTP
        if is_email:
            # Email → DB verification
            record = await self.otp_repo.verify(
                target=data.target,
                otp=data.otp,
                purpose=data.purpose
            )

            if not record:
                raise InvalidOTPError("Invalid or expired OTP")

            user = await self.user_repo.get_by_email_or_phone(email=data.target)

        else:
            # Phone → Twilio verification
            is_valid = await twilio_verify_client.verify_otp(
                number=data.target,
                code=data.otp
            )

            if not is_valid:
                raise InvalidOTPError("Invalid or expired OTP")

            user = await self.user_repo.get_by_email_or_phone(phone=data.target)

        # 🔹 Step 2: Check user
        if not user:
            raise UserNotFoundError("User not found")

        # 🔹 Step 3: Mark verified (idempotent)
        if not user.is_verified:
            user.is_verified = True
            await self.db.flush()
            await self.db.refresh(user)

        return UserRead.model_validate(user)

    # ------------------------------------------------------------------ #
    #  RESEND OTP                                                          #
    # ------------------------------------------------------------------ #

    async def resend_otp(self, data: ResendOTPRequest) -> None:
        is_email = "@" in data.target

        if is_email:
            user = await self.user_repo.get_by_email_or_phone(email=data.target)
        else:
            user = await self.user_repo.get_by_email_or_phone(phone=data.target)

        if not user:
            raise UserNotFoundError("User not found")

        if not user.is_active:
            raise UserInactiveError("Account is inactive")

        if is_email:
            # Invalidate old OTPs, create new one, send via email
            otp = _generate_otp()
            await self.otp_repo.invalidate_previous(target=data.target, purpose=data.purpose)
            await self.otp_repo.create(target=data.target, otp=otp, purpose=data.purpose)
            self.background_tasks.add_task(
                mail_service.send_otp_mail,
                email=data.target,
                code=otp
            )
        else:
            # Phone OTPs are handled by Twilio
            await twilio_verify_client.send_otp(number=data.target)

    # ------------------------------------------------------------------ #
    #  LOGIN — EMAIL                                                       #
    # ------------------------------------------------------------------ #

    async def login_email(self, data: EmailLoginRequest, request: Request):
        user = await self.user_repo.get_by_email_or_phone(email=data.email)
        if not user:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UserInactiveError("Account is inactive")

        if not user.is_verified:
            raise UserNotVerifiedError("Please verify your email before logging in")

        # Fetch email identity and verify password
        identity = await self.identity_repo.get_by_user_and_provider(
            user_id=user.id,
            provider=Provider.email
        )
        if not identity or not identity.password_hash:
            raise InvalidCredentialsError()

        if not verify_password(data.password, identity.password_hash):
            raise InvalidCredentialsError()

        return await self._create_session_and_tokens(user, request)

    # ------------------------------------------------------------------ #
    #  LOGIN — PHONE                                                       #
    # ------------------------------------------------------------------ #

    async def login_phone(self, data: PhoneLoginRequest, request: Request):
        user = await self.user_repo.get_by_email_or_phone(phone=data.phone)
        if not user:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UserInactiveError("Account is inactive")

        # Verify OTP via Twilio
        is_valid = await twilio_verify_client.verify_otp(number=data.phone, code=data.otp)
        if not is_valid:
            raise InvalidOTPError("Invalid or expired OTP")

        # Phone OTP verification implicitly verifies the user
        if not user.is_verified:
            user.is_verified = True
            await self.db.flush()
            await self.db.refresh(user)

        return await self._create_session_and_tokens(user, request)

    # ------------------------------------------------------------------ #
    #  REFRESH TOKEN                                                       #
    # ------------------------------------------------------------------ #

    async def refresh_tokens(self, refresh_token: str):
        session = await self.session_repo.get_by_refresh_token(refresh_token)
        if not session:
            raise SessionNotFoundError("Session not found or expired")

        user = await self.user_repo.get_by_id(str(session.user_id))
        if not user:
            raise UserNotFoundError("User not found")

        if not user.is_active:
            raise UserInactiveError("Account is inactive")

        # Rotate refresh token — revoke old, issue new
        await self.session_repo.revoke_by_refresh_token(refresh_token)
        new_refresh_token = create_jwt_token(
            data={"sub": str(user.id), "role": user.role},
            token_type="refresh"
        )
        await self.session_repo.create(
            user_id=str(user.id),
            refresh_token=new_refresh_token,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
            device_id=session.device_id,
        )

        access_token = create_jwt_token(
            data={"sub": str(user.id), "role": user.role},
            token_type="access"
        )

        return {"access_token": access_token, "refresh_token": new_refresh_token}

    # ------------------------------------------------------------------ #
    #  LOGOUT                                                              #
    # ------------------------------------------------------------------ #

    async def logout(self, refresh_token: str) -> None:
        session = await self.session_repo.get_by_refresh_token(refresh_token)
        if not session:
            raise SessionNotFoundError("Session not found or already revoked")

        await self.session_repo.revoke_by_refresh_token(refresh_token)

    # ------------------------------------------------------------------ #
    #  INTERNAL HELPER                                                     #
    # ------------------------------------------------------------------ #

    async def _create_session_and_tokens(self, user, request: Request):
        refresh_token = create_jwt_token(
            data={"sub": str(user.id),"role": user.role},
            token_type="refresh"
        )


        await self.session_repo.create(
            user_id=str(user.id),
            refresh_token=refresh_token,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )

        access_token = create_jwt_token(
            data={"sub": str(user.id), "role": user.role},
            token_type="access"
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }