from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ULTRA = "ultra"

class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    VISA_DIRECT = "visa_direct"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class SubscriptionFeatures(BaseModel):
    """Features available in each subscription tier"""
    max_strategies_per_day: int
    community_access: bool
    personalized_insights: bool
    real_time_analytics: bool
    priority_support: bool
    advanced_analytics: bool
    max_api_calls: int
    custom_integrations: bool
    dedicated_support: bool

class SubscriptionPlan(BaseModel):
    """Subscription plan details"""
    id: str = Field(..., description="Unique identifier for the plan")
    tier: SubscriptionTier
    name: str
    description: str
    price_monthly: float
    price_yearly: float
    features: SubscriptionFeatures
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class PaymentMethod(BaseModel):
    """Stored payment method details"""
    id: str = Field(..., description="Unique identifier for the payment method")
    user_id: str
    provider: PaymentProvider
    last_four: str
    expiry_month: Optional[int]
    expiry_year: Optional[int]
    is_default: bool = False
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Subscription(BaseModel):
    """User subscription details"""
    id: str = Field(..., description="Unique identifier for the subscription")
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    payment_method_id: str
    quantity: int = 1
    trial_end: Optional[datetime]
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Payment(BaseModel):
    """Payment transaction details"""
    id: str = Field(..., description="Unique identifier for the payment")
    user_id: str
    subscription_id: Optional[str]
    amount: float
    currency: str = "USD"
    provider: PaymentProvider
    provider_payment_id: str
    status: PaymentStatus
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Invoice(BaseModel):
    """Invoice details for subscription payments"""
    id: str = Field(..., description="Unique identifier for the invoice")
    user_id: str
    subscription_id: str
    amount: float
    currency: str = "USD"
    status: PaymentStatus
    due_date: datetime
    paid_at: Optional[datetime]
    payment_id: Optional[str]
    line_items: List[dict]
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Predefined subscription tiers
SUBSCRIPTION_TIERS = {
    SubscriptionTier.FREE: SubscriptionPlan(
        id="plan_free",
        tier=SubscriptionTier.FREE,
        name="Free",
        description="Basic access to TumorHeal's core features",
        price_monthly=0,
        price_yearly=0,
        features=SubscriptionFeatures(
            max_strategies_per_day=3,
            community_access=True,
            personalized_insights=False,
            real_time_analytics=False,
            priority_support=False,
            advanced_analytics=False,
            max_api_calls=1000,
            custom_integrations=False,
            dedicated_support=False
        )
    ),
    SubscriptionTier.PREMIUM: SubscriptionPlan(
        id="plan_premium",
        tier=SubscriptionTier.PREMIUM,
        name="Premium",
        description="Enhanced access with personalized insights",
        price_monthly=29.99,
        price_yearly=299.99,
        features=SubscriptionFeatures(
            max_strategies_per_day=10,
            community_access=True,
            personalized_insights=True,
            real_time_analytics=True,
            priority_support=True,
            advanced_analytics=False,
            max_api_calls=10000,
            custom_integrations=False,
            dedicated_support=False
        )
    ),
    SubscriptionTier.ULTRA: SubscriptionPlan(
        id="plan_ultra",
        tier=SubscriptionTier.ULTRA,
        name="Ultra",
        description="Ultimate access with advanced features and dedicated support",
        price_monthly=99.99,
        price_yearly=999.99,
        features=SubscriptionFeatures(
            max_strategies_per_day=999999,  # Unlimited (represented as very large number)
            community_access=True,
            personalized_insights=True,
            real_time_analytics=True,
            priority_support=True,
            advanced_analytics=True,
            max_api_calls=999999,  # Unlimited (represented as very large number)
            custom_integrations=True,
            dedicated_support=True
        )
    )
}