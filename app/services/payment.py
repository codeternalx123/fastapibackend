from typing import Optional, Dict, Any
import stripe
from paypalcheckoutsdk.core import LiveEnvironment, PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest
import requests
from datetime import datetime

from app.core.config import settings
from app.models.payment import (
    PaymentProvider,
    PaymentStatus,
    Payment,
    PaymentMethod,
    Subscription,
    SubscriptionStatus
)

class PaymentService:
    """Base class for payment service implementations"""
    
    async def create_payment(
        self,
        amount: float,
        currency: str,
        payment_method_id: str,
        metadata: Optional[Dict] = None
    ) -> Payment:
        """Create a payment"""
        raise NotImplementedError
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Payment:
        """Refund a payment"""
        raise NotImplementedError
    
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Get payment status"""
        raise NotImplementedError

class StripeService(PaymentService):
    """Stripe payment service implementation"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.provider = PaymentProvider.STRIPE
    
    async def create_payment(
        self,
        amount: float,
        currency: str,
        payment_method_id: str,
        metadata: Optional[Dict] = None
    ) -> Payment:
        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                payment_method=payment_method_id,
                confirm=True,
                metadata=metadata or {}
            )
            
            # Create payment record
            payment = Payment(
                id=f"stripe_{intent.id}",
                user_id=metadata.get('user_id'),
                subscription_id=metadata.get('subscription_id'),
                amount=amount,
                currency=currency,
                provider=self.provider,
                provider_payment_id=intent.id,
                status=PaymentStatus.COMPLETED if intent.status == 'succeeded'
                else PaymentStatus.PENDING,
                metadata=metadata or {}
            )
            
            return payment
            
        except stripe.error.StripeError as e:
            # Handle specific Stripe errors
            payment = Payment(
                id=f"stripe_error_{datetime.now().timestamp()}",
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
            # Extract Stripe payment ID
            stripe_payment_id = payment_id.replace('stripe_', '')
            
            # Create refund
            refund = stripe.Refund.create(
                payment_intent=stripe_payment_id,
                amount=int(amount * 100) if amount else None
            )
            
            # Update payment record
            payment = Payment(
                id=payment_id,
                status=PaymentStatus.REFUNDED,
                metadata={'refund_id': refund.id}
            )
            
            return payment
            
        except stripe.error.StripeError as e:
            raise ValueError(f"Refund failed: {str(e)}")
    
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        try:
            # Extract Stripe payment ID
            stripe_payment_id = payment_id.replace('stripe_', '')
            
            # Get payment intent
            intent = stripe.PaymentIntent.retrieve(stripe_payment_id)
            
            # Map Stripe status to our status
            status_map = {
                'succeeded': PaymentStatus.COMPLETED,
                'processing': PaymentStatus.PENDING,
                'requires_payment_method': PaymentStatus.FAILED,
                'canceled': PaymentStatus.CANCELLED
            }
            
            return status_map.get(intent.status, PaymentStatus.FAILED)
            
        except stripe.error.StripeError as e:
            raise ValueError(f"Failed to get payment status: {str(e)}")

class PayPalService(PaymentService):
    """PayPal payment service implementation"""
    
    def __init__(self):
        # Set up PayPal environment
        if settings.PAYPAL_ENV == 'sandbox':
            environment = SandboxEnvironment(
                client_id=settings.PAYPAL_CLIENT_ID,
                client_secret=settings.PAYPAL_CLIENT_SECRET
            )
        else:
            environment = LiveEnvironment(
                client_id=settings.PAYPAL_CLIENT_ID,
                client_secret=settings.PAYPAL_CLIENT_SECRET
            )
        
        self.client = PayPalHttpClient(environment)
        self.provider = PaymentProvider.PAYPAL
    
    async def create_payment(
        self,
        amount: float,
        currency: str,
        payment_method_id: str,
        metadata: Optional[Dict] = None
    ) -> Payment:
        try:
            # Create order request
            request = OrdersCreateRequest()
            request.prefer('return=representation')
            request.request_body({
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency.upper(),
                        "value": str(amount)
                    }
                }]
            })
            
            # Create order
            response = self.client.execute(request)
            
            # Create payment record
            payment = Payment(
                id=f"paypal_{response.result.id}",
                user_id=metadata.get('user_id'),
                subscription_id=metadata.get('subscription_id'),
                amount=amount,
                currency=currency,
                provider=self.provider,
                provider_payment_id=response.result.id,
                status=PaymentStatus.PENDING,
                metadata=metadata or {}
            )
            
            return payment
            
        except Exception as e:
            # Handle PayPal errors
            payment = Payment(
                id=f"paypal_error_{datetime.now().timestamp()}",
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
            # Extract PayPal payment ID
            paypal_payment_id = payment_id.replace('paypal_', '')
            
            # Implement PayPal refund logic here
            # This would involve creating a refund through PayPal's API
            
            # Update payment record
            payment = Payment(
                id=payment_id,
                status=PaymentStatus.REFUNDED,
                metadata={'refund_requested': datetime.now().isoformat()}
            )
            
            return payment
            
        except Exception as e:
            raise ValueError(f"Refund failed: {str(e)}")
    
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        try:
            # Extract PayPal payment ID
            paypal_payment_id = payment_id.replace('paypal_', '')
            
            # Implement PayPal status check logic here
            # This would involve checking the order status through PayPal's API
            
            # For now, return pending
            return PaymentStatus.PENDING
            
        except Exception as e:
            raise ValueError(f"Failed to get payment status: {str(e)}")

class VisaDirectService(PaymentService):
    """Visa Direct payment service implementation"""
    
    def __init__(self):
        self.api_key = settings.VISA_API_KEY
        self.api_url = settings.VISA_API_URL
        self.provider = PaymentProvider.VISA_DIRECT
    
    async def create_payment(
        self,
        amount: float,
        currency: str,
        payment_method_id: str,
        metadata: Optional[Dict] = None
    ) -> Payment:
        try:
            # Create Visa Direct payment request
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "amount": amount,
                "currency": currency,
                "sourceAccount": payment_method_id,
                # Add other required Visa Direct parameters
            }
            
            response = requests.post(
                f"{self.api_url}/payments",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # Create payment record
            payment = Payment(
                id=f"visa_{result['id']}",
                user_id=metadata.get('user_id'),
                subscription_id=metadata.get('subscription_id'),
                amount=amount,
                currency=currency,
                provider=self.provider,
                provider_payment_id=result['id'],
                status=PaymentStatus.COMPLETED if result['status'] == 'completed'
                else PaymentStatus.PENDING,
                metadata=metadata or {}
            )
            
            return payment
            
        except Exception as e:
            # Handle Visa Direct errors
            payment = Payment(
                id=f"visa_error_{datetime.now().timestamp()}",
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
            # Extract Visa payment ID
            visa_payment_id = payment_id.replace('visa_', '')
            
            # Implement Visa Direct refund logic here
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "originalPaymentId": visa_payment_id,
                "amount": amount
            }
            
            response = requests.post(
                f"{self.api_url}/refunds",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            # Update payment record
            payment = Payment(
                id=payment_id,
                status=PaymentStatus.REFUNDED,
                metadata={'refund_id': response.json().get('id')}
            )
            
            return payment
            
        except Exception as e:
            raise ValueError(f"Refund failed: {str(e)}")
    
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        try:
            # Extract Visa payment ID
            visa_payment_id = payment_id.replace('visa_', '')
            
            # Implement Visa Direct status check
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_url}/payments/{visa_payment_id}",
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            # Map Visa Direct status to our status
            status_map = {
                'completed': PaymentStatus.COMPLETED,
                'processing': PaymentStatus.PENDING,
                'failed': PaymentStatus.FAILED,
                'cancelled': PaymentStatus.CANCELLED,
                'refunded': PaymentStatus.REFUNDED
            }
            
            return status_map.get(result['status'], PaymentStatus.FAILED)
            
        except Exception as e:
            raise ValueError(f"Failed to get payment status: {str(e)}")

class PaymentFactory:
    """Factory for creating payment service instances"""
    
    @staticmethod
    def get_service(provider: PaymentProvider) -> PaymentService:
        """Get payment service instance based on provider"""
        if provider == PaymentProvider.STRIPE:
            return StripeService()
        elif provider == PaymentProvider.PAYPAL:
            return PayPalService()
        elif provider == PaymentProvider.VISA_DIRECT:
            return VisaDirectService()
        else:
            raise ValueError(f"Unsupported payment provider: {provider}")