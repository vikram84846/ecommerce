from core.config import app_settings
from threading import Lock
import httpx
import asyncio

BASE_URL = "https://verify.twilio.com"
class TwillioVerifyClient:
    _instance = None
    _lock = Lock()

    
    def __new__(cls,*args,**kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._instantiated = False
        return cls._instance
        
    def __init__(self,twillio_sid:str = app_settings.TWILIO_ACCOUNT_SID,
                 twillio_auth_secret:str= app_settings.TWILIO_AUTH_TOKEN,
                 verify_sevice_id:str = app_settings.TWILIO_VERIFY_SERVICE_ID):
        if self._instantiated:
            return
        self.sid = twillio_sid
        self.auth_secret = twillio_auth_secret
        self.base_url = BASE_URL
        self.verify_service_id = verify_sevice_id


    async def send_verification_otp(self,number:str,channel:str = "sms"):
        async with httpx.AsyncClient(auth=(self.sid,self.auth_secret)) as client:
            data = {
                "To": number,
                "Channel":channel
            }
            response = await client.post(
                url= f"{self.base_url}/v2/Services/{self.verify_service_id}/Verifications",
                data=data
            )
            print(response)
            return response.status_code
    async def verify_otp(self,number:str,code:str):
        async with httpx.AsyncClient(auth=(self.sid,self.auth_secret)) as client:
            data = {
                "To":number,
                "Code": code
            }
            response = await client.post(
                url = f"{BASE_URL}/v2/Services/{self.verify_service_id}/VerificationCheck",
                data=data
            )
            print(response.status_code)
            if response.status_code == 200:
                
                result = response.json()
                print(result)
                return result["valid"]
        
twilio_verify_clinet = TwillioVerifyClient()

