from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class MpesaSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore", env_file=".env")
    
    MPESA_ENVIRONMENT: str = "sandbox"  # Change to "production" in production
    MPESA_CONSUMER_KEY: str = ""  # Your Safaricom app Consumer Key
    MPESA_CONSUMER_SECRET: str = ""  # Your Safaricom app Consumer Secret
    MPESA_SHORTCODE: str = ""  # Your M-Pesa shortcode
    MPESA_PASSKEY: str = ""  # Your M-Pesa passkey
    MPESA_CALLBACK_URL: str = "https://api.tumorheal.com/api/v1/payments/mpesa/callback"  # Your callback URL

mpesa_settings = MpesaSettings()