from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import stripe
import hmac
import hashlib
import json
from datetime import datetime

from app.deps import get_db
from app.core.config import settings
from app.models.payment import Payment, Subscription, PaymentStatus, SubscriptionStatus
from app.services.payment import PaymentFactory, PaymentProvider

router = APIRouter()

async def verify_stripe_signature(request: Request) -> bool:
    """Verify Stripe webhook signature"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
        return True
    except Exception:
        return False

async def verify_paypal_signature(request: Request) -> bool:
    """Verify PayPal webhook signature"""
    payload = await request.body()
    auth_algo = request.headers.get("paypal-auth-algo")
    cert_url = request.headers.get("paypal-cert-url")
    transmission_id = request.headers.get("paypal-transmission-id")
    transmission_sig = request.headers.get("paypal-transmission-sig")
    transmission_time = request.headers.get("paypal-transmission-time")
    
    # Verify signature using PayPal's SDK
    # This is a simplified example
    try:
        expected_sig = hmac.new(
            settings.PAYPAL_WEBHOOK_SECRET.encode('utf-8'),
            msg=f"{transmission_id}|{transmission_time}|{payload}".encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(transmission_sig, expected_sig)
    except Exception:
        return False

async def verify_visa_signature(request: Request) -> bool:
    """Verify Visa Direct webhook signature"""
    payload = await request.body()
    signature = request.headers.get("visa-signature")
    
    try:
        expected_sig = hmac.new(
            settings.VISA_WEBHOOK_SECRET.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_sig)
    except Exception:
        return False

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    if not await verify_stripe_signature(request):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    payload = await request.body()
    event = stripe.Event.construct_from(
        json.loads(payload),
        stripe.api_key
    )
    
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        # Update payment status
        payment = None  # Fetch from DB
        if payment:
            payment.status = PaymentStatus.COMPLETED
            # Update in DB
            
    elif event.type == "payment_intent.payment_failed":
        payment_intent = event.data.object
        # Update payment status
        payment = None  # Fetch from DB
        if payment:
            payment.status = PaymentStatus.FAILED
            # Update in DB
            
    elif event.type == "customer.subscription.updated":
        subscription = event.data.object
        # Update subscription details
        sub = None  # Fetch from DB
        if sub:
            sub.status = SubscriptionStatus.ACTIVE
            # Update in DB
            
    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object
        # Update subscription status
        sub = None  # Fetch from DB
        if sub:
            sub.status = SubscriptionStatus.CANCELLED
            # Update in DB
    
    return {"status": "success"}

@router.post("/paypal")
async def paypal_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle PayPal webhook events"""
    if not await verify_paypal_signature(request):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    payload = await request.json()
    event_type = payload.get("event_type")
    
    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        # Payment completed successfully
        payment_id = payload["resource"]["id"]
        payment = None  # Fetch from DB
        if payment:
            payment.status = PaymentStatus.COMPLETED
            # Update in DB
            
    elif event_type == "PAYMENT.CAPTURE.DENIED":
        # Payment failed
        payment_id = payload["resource"]["id"]
        payment = None  # Fetch from DB
        if payment:
            payment.status = PaymentStatus.FAILED
            # Update in DB
            
    elif event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
        # Subscription activated
        subscription_id = payload["resource"]["id"]
        sub = None  # Fetch from DB
        if sub:
            sub.status = SubscriptionStatus.ACTIVE
            # Update in DB
            
    elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        # Subscription cancelled
        subscription_id = payload["resource"]["id"]
        sub = None  # Fetch from DB
        if sub:
            sub.status = SubscriptionStatus.CANCELLED
            # Update in DB
    
    return {"status": "success"}

@router.post("/visa")
async def visa_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Visa Direct webhook events"""
    if not await verify_visa_signature(request):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    payload = await request.json()
    event_type = payload.get("eventType")
    
    if event_type == "payment.completed":
        # Payment completed successfully
        payment_id = payload["data"]["id"]
        payment = None  # Fetch from DB
        if payment:
            payment.status = PaymentStatus.COMPLETED
            # Update in DB
            
    elif event_type == "payment.failed":
        # Payment failed
        payment_id = payload["data"]["id"]
        payment = None  # Fetch from DB
        if payment:
            payment.status = PaymentStatus.FAILED
            # Update in DB
            
    elif event_type == "refund.completed":
        # Refund completed
        payment_id = payload["data"]["originalPaymentId"]
        payment = None  # Fetch from DB
        if payment:
            payment.status = PaymentStatus.REFUNDED
            # Update in DB
    
    return {"status": "success"}