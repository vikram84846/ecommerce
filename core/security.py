from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from core.config import app_settings

ACCESS_TOKEN_EXIPRY = datetime.now(timezone.utc) + timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINS)

REFRESH_TOKEN_EXPIRY = datetime.now(timezone.utc) + timedelta(days=app_settings.REFRESH_TOKEN_EXPIRE_DAYS)

pwd_context = CryptContext(["bcrypt"])


def hash_passwd(raw_passwd:str)->str:
    return pwd_context.hash(raw_passwd)


def verify_pwd(raw_pwd:str, hash_pwd:str)->bool:
    return pwd_context.verify(raw_pwd,hash_passwd)



def create_jwt_token(data:dict,type:str="access")->str:
    to_encode = data.copy()
    if not isinstance(type,str):
        raise TypeError
    if type.lower() == "access":
        to_encode.update({
            "exp":ACCESS_TOKEN_EXIPRY
        })
    elif type.lower() == "refresh":
        to_encode.update({
            "exp":REFRESH_TOKEN_EXPIRY,
            "type":"refresh"
        })
    else:
        raise ValueError("Invalid token type")
    return jwt.encode(to_encode,app_settings.SECRET,algorithm=app_settings.ALGORITHM)


def decode_jwt_token(token:str)->dict:
    try:
            payload =jwt.decode(token=token,key=app_settings.SECRET,algorithms=[app_settings.ALGORITHM])
            return payload
    except JWTError:
        return None


        
