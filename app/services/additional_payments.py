from typing import Optional, Dict, Any
import requests
from datetime import datetime

from app.core.config import settings
from app.services.payment import PaymentService, PaymentProvider
from app.models.payment import Payment, PaymentStatus

class ApplePayService(PaymentService):
    """Apple Pay payment service implementation"""
    
    def __init__(self):
        self.api_key = settings.APPLE_PAY_SECRET_KEY
        self.merchant_id = settings.APPLE_PAY_MERCHANT_ID
        self.provider = PaymentProvider.APPLE_PAY
    
    async def create_payment(
        self,
        amount: float,
        currency: str,
        payment_method_id: str,
        metadata: Optional[Dict] = None
    ) -> Payment:
        try:
            # Create Apple Pay payment session
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "merchantIdentifier": self.merchant_id,
                "amount": amount,
                "currency": currency,
                "paymentData": payment_method_id,
                "metadata": metadata or {}
            }
            
            response = requests.post(
                settings.APPLE_PAY_API_URL + "/payments",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            payment = Payment(
                id=f"apple_{result['id']}",
                user_id=metadata.get('user_id'),
                subscription_id=metadata.get('subscription_id'),
                amount=amount,
                currency=currency,
                provider=self.provider,
                provider_payment_id=result['id'],
                status=PaymentStatus.COMPLETED if result['status'] == 'success'
                else PaymentStatus.PENDING,
                metadata=metadata or {}
            )
            
            return payment
            
        except Exception as e:
            payment = Payment(
                id=f"apple_error_{datetime.now().timestamp()}",
                user_id=metadata.get('user_id'),
                subscription_id=metadata.get('subscription_id'),
                amount=amount,
                currency=currency,
                provider=self.provider,
                provider_payment_id='',
                status=PaymentStatus.FAILED,
                metadata={
                    'error': str(e),
                    'error_type': e.__class__.__name__
                }
            )
            return payment
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Payment:
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "paymentId": payment_id.replace('apple_', ''),
                "amount": amount
            }
            
            response = requests.post(
                settings.APPLE_PAY_API_URL + "/refunds",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            payment = Payment(
                id=payment_id,
                status=PaymentStatus.REFUNDED,
                metadata={'refund_id': response.json().get('id')}
            )
            
            return payment
            
        except Exception as e:
            raise ValueError(f"Refund failed: {str(e)}")

class GooglePayService(PaymentService):
    """Google Pay payment service implementation"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_PAY_SECRET_KEY
        self.merchant_id = settings.GOOGLE_PAY_MERCHANT_ID
        self.provider = PaymentProvider.GOOGLE_PAY
    
    async def create_payment(
        self,
        amount: float,
        currency: str,
        payment_method_id: str,
        metadata: Optional[Dict] = None
    ) -> Payment:
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "merchantId": self.merchant_id,
                "amount": amount,
                "currency": currency,
                "paymentMethodData": payment_method_id,
                "metadata": metadata or {}
            }
            
            response = requests.post(
                settings.GOOGLE_PAY_API_URL + "/charges",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            payment = Payment(
                id=f"google_{result['id']}",
                user_id=metadata.get('user_id'),
                subscription_id=metadata.get('subscription_id'),
                amount=amount,
                currency=currency,
                provider=self.provider,
                provider_payment_id=result['id'],
                status=PaymentStatus.COMPLETED if result['status'] == 'success'
                else PaymentStatus.PENDING,
                metadata=metadata or {}
            )
            
            return payment
            
        except Exception as e:
            payment = Payment(
                id=f"google_error_{datetime.now().timestamp()}",
                user_id=metadata.get('user_id'),
                subscription_id=metadata.get('subscription_id'),
                amount=amount,
                currency=currency,
                provider=self.provider,
                provider_payment_id='',
                status=PaymentStatus.FAILED,
                metadata={
                    'error': str(e),
                    'error_type': e.__class__.__name__
                }
            )
            return payment
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Payment:
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "chargeId": payment_id.replace('google_', ''),
                "amount": amount
            }
            
            response = requests.post(
                settings.GOOGLE_PAY_API_URL + "/refunds",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            payment = Payment(
                id=payment_id,
                status=PaymentStatus.REFUNDED,
                metadata={'refund_id': response.json().get('id')}
            )
            
            return payment
            
        except Exception as e:
            raise ValueError(f"Refund failed: {str(e)}")

class CryptoPaymentService(PaymentService):
    """Cryptocurrency payment service implementation"""
    
    def __init__(self):
        self.api_key = settings.CRYPTO_API_KEY
        self.provider = PaymentProvider.CRYPTO
    
    async def create_payment(
        self,
        amount: float,
        currency: str,
        payment_method_id: str,
        metadata: Optional[Dict] = None
    ) -> Payment:
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Create crypto payment request
            data = {
                "price_amount": amount,
                "price_currency": currency,
                "pay_currency": payment_method_id,  # e.g., "BTC", "ETH"
                "metadata": metadata or {}
            }
            
            response = requests.post(
                settings.CRYPTO_API_URL + "/payments",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            payment = Payment(
                id=f"crypto_{result['id']}",
                user_id=metadata.get('user_id'),
                subscription_id=metadata.get('subscription_id'),
                amount=amount,
                currency=currency,
                provider=self.provider,
                provider_payment_id=result['id'],
                status=PaymentStatus.PENDING,
                metadata={
                    **metadata or {},
                    'payment_address': result['pay_address'],
                    'pay_amount': result['pay_amount'],
                    'pay_currency': result['pay_currency'],
                    'expires_at': result['expires_at']
                }
            )
            
            return payment
            
        except Exception as e:
            payment = Payment(
                id=f"crypto_error_{datetime.now().timestamp()}",
                user_id=metadata.get('user_id'),
                subscription_id=metadata.get('subscription_id'),
                amount=amount,
                currency=currency,
                provider=self.provider,
                provider_payment_id='',
                status=PaymentStatus.FAILED,
                metadata={
                    'error': str(e),
                    'error_type': e.__class__.__name__
                }
            )
            return payment
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Payment:
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "payment_id": payment_id.replace('crypto_', ''),
                "refund_address": payment.metadata.get('refund_address'),
                "amount": amount
            }
            
            response = requests.post(
                settings.CRYPTO_API_URL + "/refunds",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            payment = Payment(
                id=payment_id,
                status=PaymentStatus.REFUNDED,
                metadata={
                    'refund_id': response.json().get('id'),
                    'refund_transaction': response.json().get('transaction_id')
                }
            )
            
            return payment
            
        except Exception as e:
            raise ValueError(f"Refund failed: {str(e)}")
    
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{settings.CRYPTO_API_URL}/payments/"
                f"{payment_id.replace('crypto_', '')}",
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            status_map = {
                'new': PaymentStatus.PENDING,
                'pending': PaymentStatus.PENDING,
                'confirming': PaymentStatus.PENDING,
                'confirmed': PaymentStatus.COMPLETED,
                'sending': PaymentStatus.PENDING,
                'partially_paid': PaymentStatus.FAILED,
                'finished': PaymentStatus.COMPLETED,
                'failed': PaymentStatus.FAILED,
                'refunded': PaymentStatus.REFUNDED,
                'expired': PaymentStatus.FAILED
            }
            
            return status_map.get(result['payment_status'], PaymentStatus.FAILED)
            
        except Exception as e:
            raise ValueError(f"Failed to get payment status: {str(e)}")

# Update PaymentFactory to include new providers
class PaymentFactory:
    @staticmethod
    def get_service(provider: PaymentProvider) -> PaymentService:
        if provider == PaymentProvider.STRIPE:
            return StripeService()
        elif provider == PaymentProvider.PAYPAL:
            return PayPalService()
        elif provider == PaymentProvider.VISA_DIRECT:
            return VisaDirectService()
        elif provider == PaymentProvider.APPLE_PAY:
            return ApplePayService()
        elif provider == PaymentProvider.GOOGLE_PAY:
            return GooglePayService()
        elif provider == PaymentProvider.CRYPTO:
            return CryptoPaymentService()
        else:
            raise ValueError(f"Unsupported payment provider: {provider}")