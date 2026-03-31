from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):

    #data base 
    DB_URL: str

    #security 
    SECRET: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINS: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    #TWILIO
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_VERIFY_SERVICE_ID: str 


    model_config = SettingsConfigDict(env_file=".env")

    


@lru_cache
def get_settings()->Settings:
    return Settings()

app_settings = get_settings()
