from pydantic import BaseModel, EmailStr, field_validator, model_validator, ConfigDict
from pydantic_core.core_schema import FieldValidationInfo
from datetime import datetime
import phonenumbers
from phonenumbers import NumberParseException
from models.auth import Role
import re

class UserCreate(BaseModel):
    email: EmailStr | None = None
    country_code: str | None = None
    phone: str | None = None
    role: str = Role.consumer.value
    password: str | None = None
    model_config = ConfigDict(extra="forbid",str_strip_whitespace=True,str_to_lower=True)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v,info: FieldValidationInfo):
        if v is None:
            return v
        country_code = info.data.get("country_code")
        if not country_code:
            raise ValueError("country code is required when phone numeber is provided")
        try:
            parsed_number = phonenumbers.parse(v,country_code)
            
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("invalid phone number")
            return phonenumbers.format_number(parsed_number,phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            raise ValueError("invalid phone number format")
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters long")
        #check for atleast one uppercase letter, one lowercase letter, one digit and one special character
        if not re.search(r'[A-Z]',v):
            raise ValueError("password must contain at least one uppercase letter")
        if not re.search(r'[a-z]',v):
            raise ValueError("password must contain at least one lowercase letter")
        if not re.search(r'[0-9]',v):
            raise ValueError("password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]',v):
            raise ValueError("password must contain at least one special character")
        return v

    
    @model_validator(mode="after")
    def check_email_or_phone(self):
        if not self.phone and not self.email:
            raise ValueError("either email or phone number must be provided")
    
        
class UserRead(BaseModel):
    id: str
    email: EmailStr | None = None
    phone: str | None = None
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
    