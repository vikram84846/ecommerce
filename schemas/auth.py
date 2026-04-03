from pydantic import BaseModel, EmailStr, field_validator, model_validator, ConfigDict
from pydantic_core.core_schema import FieldValidationInfo
from datetime import datetime
import phonenumbers
from phonenumbers import NumberParseException
from schemas.enums import Role, OTPPurpose
import re
from uuid import UUID

def _lowercase_email(v):
    return v.lower() if v else v

def _validate_phone(v, info: FieldValidationInfo):
    if v is None:
        return v
    country_code = info.data.get("country_code")
    if not country_code:
        raise ValueError("country_code is required when phone is provided")
    try:
        parsed = phonenumbers.parse(v, country_code)
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Invalid phone number")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException:
        raise ValueError("Invalid phone number format")

def _validate_password(v):
    if v is None:
        return v
    if len(v) < 8:
        raise ValueError("At least 8 characters required")
    if not re.search(r'[A-Z]', v):
        raise ValueError("At least one uppercase letter required")
    if not re.search(r'[a-z]', v):
        raise ValueError("At least one lowercase letter required")
    if not re.search(r'[0-9]', v):
        raise ValueError("At least one digit required")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
        raise ValueError("At least one special character required")
    return v

class UserCreate(BaseModel):
    email: EmailStr | None = None
    country_code: str | None = None
    phone: str | None = None
    role: Role = Role.consumer
    password: str | None = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,

    )

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, v):
        return _lowercase_email(v)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v, info: FieldValidationInfo):
        return _validate_phone(v, info)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        return _validate_password(v)


    @model_validator(mode="after")
    def check_email_or_phone(self):
        if not self.email and not self.phone:
            raise ValueError("Email or phone required")
        return self  


class UserUpdate(BaseModel):
    """PATCH — sirf jo change karna hai"""
    email: EmailStr | None = None
    phone: str | None = None
    country_code: str | None = None
    role: Role | None = None

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, v):
        return _lowercase_email(v)

    # Phone validation same as UserCreate
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v, info: FieldValidationInfo):
        return _validate_phone(v, info)


class UserRead(BaseModel):
    id: UUID
    email: EmailStr | None = None
    phone: str | None = None
    is_active: bool
    is_verified: bool
    role: Role
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


#----------------------Token Schemas----------------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

#----------------------Passwords---------------------------------

class ForgetPasswordRequest(BaseModel):
    email: EmailStr
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True,str_to_lower=True)

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        return _validate_password(v)
    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, v):
        return _lowercase_email(v)

#-----------------------------Login Schemas-----------------------------

class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, v):
        return _lowercase_email(v)

    

class PhoneLoginRequest(BaseModel):
    country_code: str
    phone: str
    otp: str

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v, info: FieldValidationInfo):
        return _validate_phone(v, info)

#-----------------------------OTP Schemas-----------------------------
class verifyOTPRequest(BaseModel):
    target: str
    otp: str
    purpose: OTPPurpose
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class ResendOTPRequest(BaseModel):
    target: str
    purpose: OTPPurpose
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)