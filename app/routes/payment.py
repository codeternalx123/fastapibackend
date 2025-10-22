from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.payment import (
    PaymentProvider,
    SubscriptionTier,
    SubscriptionPlan,
    Subscription,
    Payment,
    PaymentMethod,
    SUBSCRIPTION_TIERS
)
from app.services.payment import PaymentFactory

router = APIRouter()

@router.get("/subscription/plans", response_model=List[SubscriptionPlan])
async def list_subscription_plans():
    """List all available subscription plans"""
    return list(SUBSCRIPTION_TIERS.values())

@router.get("/subscription/current", response_model=Subscription)
async def get_current_subscription(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current user's subscription"""
    # Fetch from database
    subscription = None  # Replace with DB query
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    return subscription

@router.post("/subscription/upgrade", response_model=Subscription)
async def upgrade_subscription(
    plan_id: str,
    payment_method_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upgrade to a new subscription plan"""
    # Validate plan exists
    plan = next(
        (p for p in SUBSCRIPTION_TIERS.values() if p.id == plan_id),
        None
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Process payment for subscription
    payment_method = None  # Fetch from DB
    if not payment_method:
        raise HTTPException(
            status_code=404,
            detail="Payment method not found"
        )
    
    # Create payment service
    payment_service = PaymentFactory.get_service(payment_method.provider)
    
    # Process payment
    payment = await payment_service.create_payment(
        amount=plan.price_monthly,
        currency="USD",
        payment_method_id=payment_method_id,
        metadata={
            'user_id': current_user.id,
            'plan_id': plan_id
        }
    )
    
    if payment.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Payment failed"
        )
    
    # Create subscription
    subscription = None  # Create in DB
    return subscription

@router.post("/subscription/cancel")
async def cancel_subscription(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancel current subscription"""
    # Update subscription in DB
    # Will be cancelled at period end
    return {"message": "Subscription cancelled successfully"}

@router.get("/payment-methods", response_model=List[PaymentMethod])
async def list_payment_methods(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List user's payment methods"""
    # Fetch from database
    methods = []  # Replace with DB query
    return methods

@router.post("/payment-methods", response_model=PaymentMethod)
async def add_payment_method(
    provider: PaymentProvider,
    token: str,
    set_default: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add a new payment method"""
    # Create payment service
    payment_service = PaymentFactory.get_service(provider)
    
    # Add payment method logic here
    # This would typically involve creating a payment method
    # with the provider and storing the reference
    
    payment_method = None  # Create in DB
    return payment_method

@router.delete("/payment-methods/{method_id}")
async def remove_payment_method(
    method_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove a payment method"""
    # Delete from database
    return {"message": "Payment method removed successfully"}

@router.get("/payments", response_model=List[Payment])
async def list_payments(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List user's payment history"""
    # Fetch from database
    payments = []  # Replace with DB query
    return payments

@router.post("/payments/refund/{payment_id}", response_model=Payment)
async def refund_payment(
    payment_id: str,
    amount: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Refund a payment"""
    # Fetch payment from database
    payment = None  # Replace with DB query
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Create payment service
    payment_service = PaymentFactory.get_service(payment.provider)
    
    # Process refund
    refunded_payment = await payment_service.refund_payment(
        payment_id=payment.provider_payment_id,
        amount=amount
    )
    
    # Update payment in database
    return refunded_payment