# Payment and Subscription API Documentation

## Overview

TumorHeal offers a flexible subscription system with three tiers (Free, Premium, and Ultra) and supports multiple payment providers (Stripe, PayPal, and Visa Direct).

## Subscription Tiers

### Free Tier
- Basic access to TumorHeal's core features
- 3 strategies per day
- Basic community access
- 1,000 API calls per month
- No cost

### Premium Tier
- $29.99/month or $299.99/year
- 10 strategies per day
- Full community access
- Personalized insights
- Real-time analytics
- Priority support
- 10,000 API calls per month

### Ultra Tier
- $99.99/month or $999.99/year
- Unlimited strategies
- All Premium features
- Advanced analytics
- Custom integrations
- Dedicated support
- Unlimited API calls

## Payment Providers

TumorHeal supports three payment providers:
- Stripe
- PayPal
- Visa Direct

## API Endpoints

### Subscription Management

#### List Subscription Plans
```http
GET /api/v2/subscription/plans
```

Lists all available subscription plans.

**Response:**
```json
[
    {
        "id": "plan_free",
        "tier": "free",
        "name": "Free",
        "description": "Basic access to TumorHeal's core features",
        "price_monthly": 0,
        "price_yearly": 0,
        "features": {
            "max_strategies_per_day": 3,
            "community_access": true,
            "personalized_insights": false,
            "real_time_analytics": false,
            "priority_support": false,
            "advanced_analytics": false,
            "max_api_calls": 1000,
            "custom_integrations": false,
            "dedicated_support": false
        }
    },
    {
        "id": "plan_premium",
        "tier": "premium",
        "name": "Premium",
        "description": "Enhanced access with personalized insights",
        "price_monthly": 29.99,
        "price_yearly": 299.99,
        "features": {
            "max_strategies_per_day": 10,
            "community_access": true,
            "personalized_insights": true,
            "real_time_analytics": true,
            "priority_support": true,
            "advanced_analytics": false,
            "max_api_calls": 10000,
            "custom_integrations": false,
            "dedicated_support": false
        }
    }
]
```

#### Get Current Subscription
```http
GET /api/v2/subscription/current
```

Retrieves the user's current subscription details.

**Response:**
```json
{
    "id": "sub_123",
    "user_id": "user_456",
    "plan_id": "plan_premium",
    "status": "active",
    "current_period_start": "2025-09-01T00:00:00Z",
    "current_period_end": "2025-10-01T00:00:00Z",
    "cancel_at_period_end": false,
    "payment_method_id": "pm_789",
    "quantity": 1
}
```

#### Upgrade Subscription
```http
POST /api/v2/subscription/upgrade
```

Upgrades to a new subscription plan.

**Request Body:**
```json
{
    "plan_id": "plan_premium",
    "payment_method_id": "pm_789"
}
```

#### Cancel Subscription
```http
POST /api/v2/subscription/cancel
```

Cancels the current subscription at the end of the billing period.

### Payment Methods

#### List Payment Methods
```http
GET /api/v2/payment-methods
```

Lists user's saved payment methods.

**Response:**
```json
[
    {
        "id": "pm_123",
        "user_id": "user_456",
        "provider": "stripe",
        "last_four": "4242",
        "expiry_month": 12,
        "expiry_year": 2025,
        "is_default": true
    }
]
```

#### Add Payment Method
```http
POST /api/v2/payment-methods
```

Adds a new payment method.

**Request Body:**
```json
{
    "provider": "stripe",
    "token": "tok_visa",
    "set_default": true
}
```

#### Remove Payment Method
```http
DELETE /api/v2/payment-methods/{method_id}
```

Removes a saved payment method.

### Payment History

#### List Payments
```http
GET /api/v2/payments
```

Lists payment history.

**Query Parameters:**
- `limit`: Maximum number of payments to return (default: 10)
- `offset`: Number of payments to skip (default: 0)

**Response:**
```json
[
    {
        "id": "pay_123",
        "user_id": "user_456",
        "subscription_id": "sub_789",
        "amount": 29.99,
        "currency": "USD",
        "provider": "stripe",
        "provider_payment_id": "pi_123",
        "status": "completed",
        "created_at": "2025-09-01T10:00:00Z"
    }
]
```

#### Refund Payment
```http
POST /api/v2/payments/refund/{payment_id}
```

Initiates a refund for a payment.

**Request Body:**
```json
{
    "amount": 29.99  // Optional, if not provided, full amount is refunded
}
```

## Webhooks

### Stripe Webhooks
```http
POST /api/v2/webhooks/stripe
```

Handles Stripe webhook events for:
- Payment success/failure
- Subscription updates
- Refund status
- Dispute handling

### PayPal Webhooks
```http
POST /api/v2/webhooks/paypal
```

Handles PayPal webhook events for:
- Payment completion
- Subscription changes
- Refund processing

### Visa Direct Webhooks
```http
POST /api/v2/webhooks/visa
```

Handles Visa Direct webhook events for:
- Payment status updates
- Transaction completion
- Refund status

## Error Responses

### Payment Errors
```json
{
    "error": {
        "code": "PAYMENT_FAILED",
        "message": "Payment processing failed",
        "details": {
            "reason": "insufficient_funds",
            "provider": "stripe"
        }
    }
}
```

### Subscription Errors
```json
{
    "error": {
        "code": "SUBSCRIPTION_ERROR",
        "message": "Failed to update subscription",
        "details": {
            "reason": "invalid_plan",
            "plan_id": "invalid_plan_id"
        }
    }
}
```

## Rate Limiting

- Free Tier: 60 requests/minute
- Premium Tier: 120 requests/minute
- Ultra Tier: 300 requests/minute

Rate limit headers included in responses:
```http
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 115
X-RateLimit-Reset: 1583850767
```

## Integration Examples

### JavaScript
```javascript
const tumorheal = new TumorHealClient({
    apiKey: 'your_api_key'
});

// Subscribe to Premium plan
async function subscribeToPremium() {
    try {
        const paymentMethod = await tumorheal.paymentMethods.create({
            provider: 'stripe',
            token: 'tok_visa'
        });
        
        const subscription = await tumorheal.subscriptions.upgrade({
            planId: 'plan_premium',
            paymentMethodId: paymentMethod.id
        });
        
        console.log('Upgraded to Premium:', subscription);
    } catch (error) {
        console.error('Subscription failed:', error);
    }
}
```

### Python
```python
from tumorheal import TumorHealClient

client = TumorHealClient(api_key='your_api_key')

# Add payment method
payment_method = client.payment_methods.create(
    provider='stripe',
    token='tok_visa',
    set_default=True
)

# Subscribe to Premium
subscription = client.subscriptions.upgrade(
    plan_id='plan_premium',
    payment_method_id=payment_method.id
)

print(f"Subscribed to Premium: {subscription.id}")
```

## Webhook Integration Example

### Node.js with Express
```javascript
const express = require('express');
const app = express();

app.post('/webhooks/stripe', express.raw({type: 'application/json'}), (req, res) => {
    const sig = req.headers['stripe-signature'];
    
    try {
        const event = stripe.webhooks.constructEvent(
            req.body,
            sig,
            'whsec_your_signing_secret'
        );
        
        switch (event.type) {
            case 'payment_intent.succeeded':
                handlePaymentSuccess(event.data.object);
                break;
            case 'customer.subscription.updated':
                handleSubscriptionUpdate(event.data.object);
                break;
        }
        
        res.json({received: true});
    } catch (err) {
        res.status(400).send(`Webhook Error: ${err.message}`);
    }
});
```

### Python with FastAPI
```python
from fastapi import FastAPI, Request, HTTPException
import stripe

app = FastAPI()

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            "whsec_your_signing_secret"
        )
        
        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            handle_payment_success(payment_intent)
        elif event.type == "customer.subscription.updated":
            subscription = event.data.object
            handle_subscription_update(subscription)
            
        return {"received": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```