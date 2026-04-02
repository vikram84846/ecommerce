from repos.users import UserRepo
from repos.sessions import SessionRepo
from repos.auth_identity import AuthIdentityRepo
from repos.otp_verification import OTPRepo
from schemas.enums import Provider, OTPPurpose
from schemas.auth import UserCreate,UserRead
from models.auth import UserModel, AuthIdentity
from fastapi import BackgroundTasks
from utils.twilio import twilio_verify_client
import secrets
from core.constants import OTP_LENGTH
from utils.email_clinet import mail_service


def _generate_otp(length: int = OTP_LENGTH) -> str:
    return "".join([str(secrets.randbelow(10)) for _ in range(length)])




class UserFactory:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepo(db)
        self.identity_repo = AuthIdentityRepo(db)

    async def create_email_user(self,data: UserCreate)-> tuple[UserModel, AuthIdentity]:
        user = await self.user_repo.create(
            email=data.email,
            role=data.role
        )
        identity = await self.identity_repo.create(
            user_id=user.id,
            provider= Provider.email,
            provider_user_id=data.email,
            password=data.password
        )
        return user, identity
    
    async def create_phone_user(self,data:UserCreate)-> tuple[UserModel,AuthIdentity]:
        user = await self.user_repo.create(
            phone = data.phone,
            role= data.role
        )
        identity = await self.identity_repo.create(
            user_id= user.id,
            provider= Provider.phone,
            provider_user_id= user.phone
        )

        return user, identity
    
    async def create_oauth_user(self,data: UserCreate, provider: Provider, provider_user_id: str)-> tuple[UserModel,AuthIdentity]:
        user = await self.user_repo.create(
            email= data.email,
            role= data.role
        )
        identity = await self.identity_repo.create(
            user_id= user.id,
            provider= provider,
            provider_user_id= provider_user_id
        )

        return user, identity


class UserService:
    def __init__(self, db,background_tasks:BackgroundTasks):
        self.db = db
        self.user_repo = UserRepo(db)
        self.otp_repo = OTPRepo(db)
        self.background_tasks = background_tasks
        self.user_factory = UserFactory(db)

    async def register(
            self,
            data: UserCreate,
    )-> UserRead:
        # check if user already exists
        if data.email:
            existing_user = await self.user_repo.get_by_email_or_phone(email=data.email)
            if existing_user:
                raise ValueError("User already exists.")
        if data.phone:
            existing_user = await self.user_repo.get_by_email_or_phone(phone=data.phone)
            if existing_user:
                raise ValueError("User already exists.")
        
        # create user and auth identity
        if data.email and data.password:
            user, _ = await self.user_factory.create_email_user(data)
            await self._handle_email_verification(data.email)
        elif data.phone:
            user, _ = await self.user_factory.create_phone_user(data)
            #phone verification handled by twillio
            await twilio_verify_client.send_otp(number=data.phone)
        else:
            raise ValueError("Invalid registration data.")
        
        return UserRead.model_validate(user)
    
    async def _handle_email_verification(self,email:str):
        # generate OTP
        otp = _generate_otp()

        #invalidate old OTPs
        await self.otp_repo.invalidate_previous(target=email, purpose=OTPPurpose.signup)

        #new OTP entry
        await self.otp_repo.create(
            target=email,
            otp=otp,
            purpose= OTPPurpose.signup
        )
        # send otp via email in background
        self.background_tasks.add_task(
            mail_service.send_otp_mail,
            email=email,
            code=otp
        )