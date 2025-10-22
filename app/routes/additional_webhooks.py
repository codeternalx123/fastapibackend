# Webhook handlers for additional payment providers

from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict
import hmac
import hashlib

from app.core.config import settings
from app.services.additional_payments import (
    ApplePayService,
    GooglePayService,
    CryptoPaymentService
)
from app.models.payment import PaymentStatus

router = APIRouter(prefix="/webhooks")

async def verify_apple_pay_signature(request: Request) -> bool:
    """Verify Apple Pay webhook signature"""
    payload = await request.body()
    signature = request.headers.get('Apple-Pay-Signature')
    
    if not signature:
        return False
    
    expected_signature = hmac.new(
        settings.APPLE_PAY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

async def verify_google_pay_signature(request: Request) -> bool:
    """Verify Google Pay webhook signature"""
    payload = await request.body()
    signature = request.headers.get('Google-Pay-Signature')
    
    if not signature:
        return False
    
    expected_signature = hmac.new(
        settings.GOOGLE_PAY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

async def verify_crypto_signature(request: Request) -> bool:
    """Verify cryptocurrency payment webhook signature"""
    payload = await request.body()
    signature = request.headers.get('Crypto-Signature')
    
    if not signature:
        return False
    
    expected_signature = hmac.new(
        settings.CRYPTO_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@router.post("/apple-pay")
async def apple_pay_webhook(request: Request):
    """Handle Apple Pay webhook events"""
    if not await verify_apple_pay_signature(request):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    payload = await request.json()
    event_type = payload.get('type')
    
    try:
        service = ApplePayService()
        
        if event_type == 'payment.completed':
            # Handle successful payment
            payment = await service.create_payment(
                amount=payload['data']['amount'],
                currency=payload['data']['currency'],
                payment_method_id=payload['data']['payment_id'],
                metadata=payload['data'].get('metadata', {})
            )
            # Update payment status in database
            # Add notification or trigger other business logic
            
        elif event_type == 'payment.failed':
            # Handle failed payment
            # Update payment status and notify user
            pass
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Apple Pay webhook: {str(e)}"
        )

@router.post("/google-pay")
async def google_pay_webhook(request: Request):
    """Handle Google Pay webhook events"""
    if not await verify_google_pay_signature(request):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    payload = await request.json()
    event_type = payload.get('type')
    
    try:
        service = GooglePayService()
        
        if event_type == 'charge.succeeded':
            # Handle successful payment
            payment = await service.create_payment(
                amount=payload['data']['amount'],
                currency=payload['data']['currency'],
                payment_method_id=payload['data']['payment_method_id'],
                metadata=payload['data'].get('metadata', {})
            )
            # Update payment status in database
            # Add notification or trigger other business logic
            
        elif event_type == 'charge.failed':
            # Handle failed payment
            # Update payment status and notify user
            pass
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Google Pay webhook: {str(e)}"
        )

@router.post("/crypto")
async def crypto_webhook(request: Request):
    """Handle cryptocurrency payment webhook events"""
    if not await verify_crypto_signature(request):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    payload = await request.json()
    event_type = payload.get('type')
    
    try:
        service = CryptoPaymentService()
        
        if event_type == 'transaction.confirmed':
            # Handle confirmed crypto transaction
            payment_id = payload['data']['payment_id']
            status = await service.get_payment_status(payment_id)
            
            if status == PaymentStatus.COMPLETED:
                # Payment confirmed, trigger success flow
                # Update subscription status, send confirmation email, etc.
                pass
                
        elif event_type == 'transaction.failed':
            # Handle failed transaction
            # Update payment status and notify user
            pass
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process crypto webhook: {str(e)}"
        )