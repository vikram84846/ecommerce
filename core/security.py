import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from core.config import get_settings
from core.constants import (
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINS,
    REFRESH_TOKEN_EXPIRE_DAYS
)

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)


def create_jwt_token(data: dict, token_type: str = "access") -> str:
    to_encode = data.copy()

    if token_type == "access":
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINS)
    elif token_type == "refresh":
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        raise ValueError(f"Invalid token_type: {token_type}")

    to_encode.update({
        "exp": expires_at,
        "type": token_type  # dono tokens mein type claim
    })

    return jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise
    except InvalidTokenError:
        raise