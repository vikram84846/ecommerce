import httpx
from core.config import get_settings

settings = get_settings()

BASE_URL = "https://verify.twilio.com"


class TwilioVerifyClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._instantiated = False
        return cls._instance

    def __init__(
        self,
        twilio_sid: str = settings.TWILIO_ACCOUNT_SID,
        twilio_auth_secret: str = settings.TWILIO_AUTH_TOKEN,
        verify_service_id: str = settings.TWILIO_VERIFY_SERVICE_ID,
    ):
        if self._instantiated:
            return

        self.sid = twilio_sid
        self.auth_secret = twilio_auth_secret
        self.verify_service_id = verify_service_id
        self._client = httpx.AsyncClient(
            auth=(self.sid, self.auth_secret),
            base_url=BASE_URL,
             timeout=10.0
        )
        self._instantiated = True

    async def send_otp(self, number: str, channel: str = "sms") -> bool:
        try:
            response = await self._client.post(
                f"/v2/Services/{self.verify_service_id}/Verifications",
                data={"To": number, "Channel": channel}
            )
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            return False

    async def verify_otp(self, number: str, code: str) -> bool:
        try:
            response = await self._client.post(
                f"/v2/Services/{self.verify_service_id}/VerificationCheck",
                data={"To": number, "Code": code}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("valid", False)
        except httpx.HTTPStatusError as e:
            return False

    async def close(self):
        await self._client.aclose()


twilio_verify_client = TwilioVerifyClient()