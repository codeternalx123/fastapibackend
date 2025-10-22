from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Optional

from app.models.payment import Payment
from app.services.additional_payments import (
    ApplePayService,
    GooglePayService,
    CryptoPaymentService
)
from app.core.security import get_current_user
from app.models.schemas import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/payments")

@router.post("/apple-pay", response_model=PaymentResponse)
async def create_apple_pay_payment(
    payment: PaymentCreate,
    current_user = Depends(get_current_user)
):
    """Create a new Apple Pay payment"""
    try:
        service = ApplePayService()
        result = await service.create_payment(
            amount=payment.amount,
            currency=payment.currency,
            payment_method_id=payment.payment_method_id,
            metadata={
                'user_id': current_user.id,
                'subscription_id': payment.subscription_id,
                **payment.metadata or {}
            }
        )
        return PaymentResponse.from_orm(result)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create Apple Pay payment: {str(e)}"
        )

@router.post("/google-pay", response_model=PaymentResponse)
async def create_google_pay_payment(
    payment: PaymentCreate,
    current_user = Depends(get_current_user)
):
    """Create a new Google Pay payment"""
    try:
        service = GooglePayService()
        result = await service.create_payment(
            amount=payment.amount,
            currency=payment.currency,
            payment_method_id=payment.payment_method_id,
            metadata={
                'user_id': current_user.id,
                'subscription_id': payment.subscription_id,
                **payment.metadata or {}
            }
        )
        return PaymentResponse.from_orm(result)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create Google Pay payment: {str(e)}"
        )

@router.post("/crypto", response_model=PaymentResponse)
async def create_crypto_payment(
    payment: PaymentCreate,
    current_user = Depends(get_current_user)
):
    """Create a new cryptocurrency payment"""
    try:
        service = CryptoPaymentService()
        result = await service.create_payment(
            amount=payment.amount,
            currency=payment.currency,
            payment_method_id=payment.payment_method_id,  # e.g., "BTC", "ETH"
            metadata={
                'user_id': current_user.id,
                'subscription_id': payment.subscription_id,
                'refund_address': payment.metadata.get('refund_address'),
                **payment.metadata or {}
            }
        )
        return PaymentResponse.from_orm(result)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create crypto payment: {str(e)}"
        )

@router.get("/crypto/{payment_id}/status")
async def get_crypto_payment_status(
    payment_id: str,
    current_user = Depends(get_current_user)
):
    """Get the status of a cryptocurrency payment"""
    try:
        service = CryptoPaymentService()
        status = await service.get_payment_status(payment_id)
        return {"status": status.value}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get payment status: {str(e)}"
        )

@router.post("/{payment_id}/refund")
async def refund_payment(
    payment_id: str,
    amount: Optional[float] = None,
    current_user = Depends(get_current_user)
):
    """Refund a payment"""
    try:
        # Determine provider from payment_id prefix
        if payment_id.startswith('apple_'):
            service = ApplePayService()
        elif payment_id.startswith('google_'):
            service = GooglePayService()
        elif payment_id.startswith('crypto_'):
            service = CryptoPaymentService()
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported payment provider"
            )
        
        result = await service.refund_payment(payment_id, amount)
        return {"status": "success", "refund": result.metadata}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Refund failed: {str(e)}"
        )