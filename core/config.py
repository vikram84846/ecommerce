from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import PostgresDsn
class Settings(BaseSettings):

    #data base 
    DB_URL: PostgresDsn

    #security 
    SECRET: str

    #TWILIO
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_VERIFY_SERVICE_ID: str 

    #Mail configuration
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    model_config = SettingsConfigDict(env_file=".env")
    
    #debug true for development and false for production
    DEBUG: bool = True

    


@lru_cache
def get_settings()->Settings:
    return Settings()

