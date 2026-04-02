from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from core.config import get_settings
from core.constants import OTP_EXPIRE_MINUTES

settings = get_settings()

_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
)

_client = FastMail(config=_config)  # ek baar banao, reuse karo


class EmailService:
    def __init__(self):
        self.client = _client  # module level client reuse

    async def send_otp_mail(self, email: str, code: str, expires_in_minutes: int = OTP_EXPIRE_MINUTES):
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0;padding:0;background:#f4f4f5;font-family:Arial,sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
            <tr><td align="center">
              <table width="520" cellpadding="0" cellspacing="0"
                     style="background:#ffffff;border-radius:8px;border:1px solid #e4e4e7;overflow:hidden;">

                <tr>
                  <td style="background:#18181b;padding:24px 32px;">
                    <p style="margin:0;font-size:18px;font-weight:600;color:#ffffff;letter-spacing:0.3px;">
                      Your App
                    </p>
                  </td>
                </tr>

                <tr>
                  <td style="padding:32px;">
                    <p style="margin:0 0 8px;font-size:22px;font-weight:600;color:#18181b;">
                      Verification Code
                    </p>
                    <p style="margin:0 0 24px;font-size:14px;color:#71717a;line-height:1.6;">
                      Use the code below to complete your verification.
                      This code expires in <strong>{expires_in_minutes} minutes</strong>.
                    </p>

                    <div style="background:#f4f4f5;border-radius:6px;padding:20px;text-align:center;
                                letter-spacing:10px;font-size:32px;font-weight:700;color:#18181b;
                                border:1px dashed #d4d4d8;margin-bottom:24px;">
                      {code}
                    </div>

                    <p style="margin:0;font-size:13px;color:#a1a1aa;line-height:1.6;">
                      If you did not request this code, please ignore this email.
                      Do not share this code with anyone.
                    </p>
                  </td>
                </tr>

                <tr>
                  <td style="padding:16px 32px;border-top:1px solid #f4f4f5;">
                    <p style="margin:0;font-size:12px;color:#a1a1aa;">
                      &copy; 2025 Your App. All rights reserved.
                    </p>
                  </td>
                </tr>

              </table>
            </td></tr>
          </table>
        </body>
        </html>
        """
        message = MessageSchema(
            recipients=[email],
            subject="Your verification code",
            body=html,
            subtype=MessageType.html
        )
        try:
            await self.client.send_message(message)
        except Exception:
            raise

    async def send_welcome_mail(self, email: str):
        html = """
        <!DOCTYPE html>
        <html>
        <body style="margin:0;padding:0;background:#f4f4f5;font-family:Arial,sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
            <tr><td align="center">
              <table width="520" cellpadding="0" cellspacing="0"
                     style="background:#ffffff;border-radius:8px;border:1px solid #e4e4e7;overflow:hidden;">

                <tr>
                  <td style="background:#18181b;padding:24px 32px;">
                    <p style="margin:0;font-size:18px;font-weight:600;color:#ffffff;letter-spacing:0.3px;">
                      Your App
                    </p>
                  </td>
                </tr>

                <tr>
                  <td style="padding:32px;">
                    <p style="margin:0 0 8px;font-size:22px;font-weight:600;color:#18181b;">
                      Welcome aboard
                    </p>
                    <p style="margin:0 0 20px;font-size:14px;color:#71717a;line-height:1.6;">
                      Your account has been created successfully. We're glad to have you with us.
                    </p>

                    <table cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                      <tr>
                        <td style="background:#18181b;border-radius:6px;padding:12px 24px;">
                          <a href="#" style="color:#ffffff;font-size:14px;font-weight:500;
                                            text-decoration:none;">
                            Get started &rarr;
                          </a>
                        </td>
                      </tr>
                    </table>

                    <p style="margin:0;font-size:13px;color:#a1a1aa;line-height:1.6;">
                      If you did not create this account, please contact our support team immediately.
                    </p>
                  </td>
                </tr>

                <tr>
                  <td style="padding:16px 32px;border-top:1px solid #f4f4f5;">
                    <p style="margin:0;font-size:12px;color:#a1a1aa;">
                      &copy; 2025 Your App. All rights reserved.
                    </p>
                  </td>
                </tr>

              </table>
            </td></tr>
          </table>
        </body>
        </html>
        """
        message = MessageSchema(
            recipients=[email],
            subject="Welcome to Your App",
            body=html,
            subtype=MessageType.html
        )
        try:
            await self.client.send_message(message)
        except Exception:
            raise


mail_service = EmailService()