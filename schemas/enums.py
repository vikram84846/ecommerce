from enum import Enum

class Provider(str, Enum):
    email = "email"
    phone = "phone"
    google = "google"

class Role(str, Enum):
    consumer = "consumer"
    retailer = "retailer"
    admin = "admin"

class OTPPurpose(str, Enum):
    #twillio hanles phone verification, so we only need to handle email related OTPs
    password_reset = "password_reset"
    email_verification = "email_verification"
    