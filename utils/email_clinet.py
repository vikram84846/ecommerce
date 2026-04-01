from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from core.config import app_settings
import asyncio

def get_configuration():
    config = ConnectionConfig(
        MAIL_USERNAME= app_settings.MAIL_USERNAME,
        MAIL_PASSWORD=app_settings.MAIL_PASSWORD,
        MAIL_FROM= app_settings.MAIL_USERNAME,
        MAIL_PORT=app_settings.MAIL_PORT,
        MAIL_SERVER=app_settings.MAIL_SERVER,
        MAIL_STARTTLS=app_settings.MAIL_TLS,
        MAIL_SSL_TLS= app_settings.MAIL_SSL,

    )
    return config





class EmailService:
    def __init__(self):
        self.clinet = FastMail(config=get_configuration())

    async def send_otp_mail(self,email:str,code:str):
        html = f"""
        <h3>Your OTP Code</h3>
        <div style="padding: 10px; background-color: #f2f2f2; border-radius: 5px; display: block; max-width: 100%; margin: 20px auto; text-align: center;">
            <p style="font-size: 18px; font-weight: bold; color: #333;">{code}</p>
        </div>
"""
        message = MessageSchema(
            recipients=[email],
            subject="Your OTP Code",
            body=html,
            subtype=MessageType.html
        )
        await self.clinet.send_message(message)


    async def welcome_mail(self,email:str):
        html = f"""
        <h3>Welcome to our service</h3>
        <div style="padding: 10px; background-color: #f2f2f2; border-radius: 5px; display: block; max-width: 100%; margin: 20px auto;">
            <p style="font-size: 18px; color: #333;">Dear User,</p>
        <p>Thank you for signing up! We're excited to have you on board. If you have any questions or need assistance, feel free to reach out to our support team.</p>
        <p>Best regards,<br>Hari Om bikaneri</p>
        </div>
        """
        message = MessageSchema(
            recipients=[email],
            subject="Welcome to our service",
            body=html,
            subtype=MessageType.html
        )
        await self.clinet.send_message(message)
mailSerivce = EmailService()