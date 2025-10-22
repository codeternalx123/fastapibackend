import requests
import base64
from datetime import datetime
import pytz
from typing import Dict, Any
import logging

from app.core.mpesa_config import mpesa_settings

logger = logging.getLogger(__name__)

class MpesaService:
    def __init__(self):
        self.env = mpesa_settings.MPESA_ENVIRONMENT
        self.consumer_key = mpesa_settings.MPESA_CONSUMER_KEY
        self.consumer_secret = mpesa_settings.MPESA_CONSUMER_SECRET
        self.shortcode = mpesa_settings.MPESA_SHORTCODE
        self.passkey = mpesa_settings.MPESA_PASSKEY
        self.callback_url = mpesa_settings.MPESA_CALLBACK_URL
        
        if self.env == "sandbox":
            self.base_url = "https://sandbox.safaricom.co.ke"
        else:
            self.base_url = "https://api.safaricom.co.ke"
        
        self._access_token = None
        self._token_timestamp = None

    def _get_access_token(self) -> str:
        """Get OAuth access token from Safaricom (cached for 1 hour)"""
        # Check if credentials are configured
        if not self.consumer_key or not self.consumer_secret:
            logger.warning("M-Pesa credentials not configured. Please set MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET in .env")
            raise Exception("M-Pesa credentials not configured")
        
        # Return cached token if still valid (tokens last 1 hour)
        if self._access_token and self._token_timestamp:
            from datetime import datetime, timedelta
            if datetime.now() - self._token_timestamp < timedelta(minutes=50):
                return self._access_token
        
        auth = base64.b64encode(
            f"{self.consumer_key}:{self.consumer_secret}".encode()
        ).decode()
        
        try:
            response = requests.get(
                f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
                headers={"Authorization": f"Basic {auth}"},
            )
            response.raise_for_status()
            self._access_token = response.json()["access_token"]
            self._token_timestamp = datetime.now()
            return self._access_token
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get access token: {str(e)}")

    def _generate_password(self, timestamp: str) -> str:
        """Generate password for STK push"""
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_str.encode()).decode()

    def initiate_stk_push(
        self, 
        phone_number: str, 
        amount: float, 
        account_reference: str, 
        transaction_desc: str
    ) -> Dict[str, Any]:
        """Initiate STK push payment"""
        timestamp = datetime.now(pytz.timezone('Africa/Nairobi')).strftime('%Y%m%d%H%M%S')
        password = self._generate_password(timestamp)
        
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"STK push failed: {str(e)}")

    def check_payment_status(self, checkout_request_id: str) -> Dict[str, Any]:
        """Check status of an STK push payment"""
        timestamp = datetime.now(pytz.timezone('Africa/Nairobi')).strftime('%Y%m%d%H%M%S')
        password = self._generate_password(timestamp)
        
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/mpesa/stkpushquery/v1/query",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Payment status check failed: {str(e)}")