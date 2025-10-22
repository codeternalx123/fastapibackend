# TumorHeal Backend API Documentation

## Overview

TumorHeal's backend API provides a comprehensive set of endpoints for managing the four pillars of the healing system: Quantum Nutritionist, Emotive Health Correlator, Chrono-Therapeutic Optimizer, and the Kintsugi Community.

## Table of Contents

1. [Base URL and Authentication](#base-url)
2. [Common Response Codes](#common-response-codes)
3. [Rate Limiting](#rate-limiting)
4. [Kintsugi Community Endpoints](#kintsugi-community-endpoints)
5. [Analytics & Reporting](#analytics--reporting)
6. [Advanced Features](#advanced-features)
7. [Error Codes](#extended-error-code-documentation)
8. [Integration Examples](#integration-examples)
9. [Rate Limiting and Quotas](#rate-limiting-and-quotas)

## Base URL
```
https://api.tumorheal.com/v2
```

## Authentication

All API requests require authentication using JWT (JSON Web Tokens). Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

## Common Response Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per user

---

## Kintsugi Community Endpoints

### User Experiences

#### Create Experience
```http
POST /experiences/
```

Creates a new user experience entry.

**Request Body:**
```json
{
    "title": "My Journey with Natural Remedies",
    "content": "I discovered that combining ginger tea with meditation...",
    "tags": ["natural-remedies", "meditation"],
    "treatment_phase": "early_treatment"
}
```

**Response:**
```json
{
    "id": "exp_123",
    "user_id": "user_456",
    "title": "My Journey with Natural Remedies",
    "content": "I discovered that combining ginger tea with meditation...",
    "tags": ["natural-remedies", "meditation"],
    "treatment_phase": "early_treatment",
    "created_at": "2025-09-30T10:00:00Z",
    "updated_at": "2025-09-30T10:00:00Z",
    "helpful_count": 0
}
```

#### Get Experience
```http
GET /experiences/{experience_id}
```

Retrieves a specific user experience.

**Parameters:**
- `experience_id`: Unique identifier of the experience

**Response:**
```json
{
    "id": "exp_123",
    "user_id": "user_456",
    "title": "My Journey with Natural Remedies",
    "content": "I discovered that combining ginger tea with meditation...",
    "tags": ["natural-remedies", "meditation"],
    "treatment_phase": "early_treatment",
    "created_at": "2025-09-30T10:00:00Z",
    "updated_at": "2025-09-30T10:00:00Z",
    "helpful_count": 42
}
```

### Inspiring Quotes

#### Share Quote
```http
POST /quotes/
```

Shares an inspiring quote with the community.

**Request Body:**
```json
{
    "quote": "Your body knows how to heal itself, trust in that wisdom",
    "author": "Dr. Jane Smith",
    "context": "This helped me during difficult treatment days",
    "tags": ["inspiration", "healing"]
}
```

#### List Quotes
```http
GET /quotes/
```

Lists inspiring quotes with optional filtering.

**Query Parameters:**
- `tag`: Filter by tag (optional)
- `limit`: Maximum number of quotes to return (default: 10)

**Response:**
```json
[
    {
        "id": "quote_123",
        "user_id": "user_789",
        "quote": "Your body knows how to heal itself, trust in that wisdom",
        "author": "Dr. Jane Smith",
        "context": "This helped me during difficult treatment days",
        "tags": ["inspiration", "healing"],
        "created_at": "2025-09-30T09:00:00Z",
        "resonance_count": 156
    }
]
```

### Healing Strategies

#### Create Strategy
```http
POST /strategies/
```

Shares a healing strategy with the community.

**Request Body:**
```json
{
    "category": "recipe",
    "title": "Anti-inflammatory Golden Milk",
    "description": "A powerful combination of turmeric and other healing spices",
    "instructions": [
        "Heat almond milk in a small saucepan",
        "Add turmeric, ginger, and black pepper",
        "Simmer for 5 minutes",
        "Strain and enjoy"
    ],
    "effectiveness_rating": 4.5,
    "conditions_helped": ["inflammation", "nausea"],
    "duration_minutes": 15,
    "frequency": "daily",
    "scientific_backing": "Studies show turmeric's anti-inflammatory properties..."
}
```

#### Get Strategy
```http
GET /strategies/{strategy_id}
```

Retrieves a specific healing strategy.

**Parameters:**
- `strategy_id`: Unique identifier of the strategy

### Community Interactions

#### Record Interaction
```http
POST /interactions/
```

Records user interaction with community content.

**Request Body:**
```json
{
    "content_id": "strategy_123",
    "content_type": "strategy",
    "interaction_type": "save",
    "metadata": {
        "rating": 5,
        "comment": "This strategy helped me tremendously"
    }
}
```

### Recommendations

#### Get Recommendations
```http
GET /recommendations/
```

Retrieves personalized strategy recommendations.

**Query Parameters:**
- `limit`: Maximum number of recommendations (default: 5)

**Response:**
```json
[
    {
        "id": "rec_123",
        "user_id": "user_456",
        "strategy_id": "strategy_789",
        "similarity_score": 0.85,
        "success_probability": 0.78,
        "relevance_factors": [
            {
                "factor": "similar_users",
                "count": 25,
                "description": "25 similar users found this strategy helpful"
            }
        ],
        "timestamp": "2025-09-30T10:00:00Z",
        "status": "pending"
    }
]
```

### Community Insights

#### Get Insights
```http
GET /insights/
```

Retrieves community-derived insights.

**Query Parameters:**
- `insight_type`: Filter by insight type (optional)

**Response:**
```json
[
    {
        "id": "insight_123",
        "insight_type": "correlation",
        "description": "Users combining meditation with ginger tea report 30% better outcomes",
        "confidence_score": 0.85,
        "supporting_data": {
            "sample_size": 500,
            "correlation_strength": 0.75
        },
        "affected_users": ["user_123", "user_456"],
        "discovered_at": "2025-09-30T08:00:00Z",
        "validated": true,
        "validation_method": "statistical_analysis"
    }
]
```

### User Profiles

#### Update Profile
```http
POST /profile/
```

Updates user's community profile.

**Request Body:**
```json
{
    "diagnosis": "stage_2_breast_cancer",
    "treatment_phase": "active_treatment",
    "age_group": "40-50",
    "preferences": {
        "notification_frequency": "daily",
        "preferred_categories": ["mindfulness", "nutrition"]
    }
}
```

#### Get Profile
```http
GET /profile/
```

Retrieves user's community profile.

**Response:**
```json
{
    "id": "user_123",
    "diagnosis": "stage_2_breast_cancer",
    "treatment_phase": "active_treatment",
    "age_group": "40-50",
    "preferences": {
        "notification_frequency": "daily",
        "preferred_categories": ["mindfulness", "nutrition"]
    },
    "activity_metrics": {
        "posts": 15,
        "comments": 45,
        "helpful_votes": 120
    },
    "successful_strategies": ["strategy_123", "strategy_456"],
    "created_at": "2025-01-15T00:00:00Z",
    "updated_at": "2025-09-30T10:00:00Z"
}
```

## Extended Error Code Documentation

### HTTP Status Codes

#### 4xx Client Errors
- `400 Bad Request`
  - VALIDATION_ERROR: Request parameters failed validation
  - INVALID_FORMAT: Data format is incorrect
  - MISSING_FIELD: Required field is missing
  
- `401 Unauthorized`
  - TOKEN_MISSING: No authentication token provided
  - TOKEN_INVALID: Invalid authentication token
  - TOKEN_EXPIRED: Authentication token has expired
  
- `403 Forbidden`
  - INSUFFICIENT_PERMISSIONS: User lacks required permissions
  - ACCOUNT_SUSPENDED: User account is suspended
  - RATE_LIMIT_EXCEEDED: API rate limit exceeded
  
- `404 Not Found`
  - RESOURCE_NOT_FOUND: Requested resource does not exist
  - ENDPOINT_NOT_FOUND: Invalid API endpoint
  - USER_NOT_FOUND: Referenced user does not exist

- `409 Conflict`
  - DUPLICATE_ENTRY: Resource already exists
  - STALE_DATA: Resource has been modified by another request
  - CONCURRENT_MODIFICATION: Conflicting concurrent modification

#### 5xx Server Errors
- `500 Internal Server Error`
  - SERVER_ERROR: Generic server error
  - DATABASE_ERROR: Database operation failed
  - INTEGRATION_ERROR: Third-party service integration failed

- `503 Service Unavailable`
  - SERVICE_UNAVAILABLE: Service temporarily unavailable
  - MAINTENANCE_MODE: System under maintenance
  - OVERLOADED: System is overloaded

Example Error Response:
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Request validation failed",
        "details": [
            {
                "field": "effectiveness_rating",
                "error": "Must be between 0 and 5",
                "value": 6
            },
            {
                "field": "treatment_phase",
                "error": "Must be one of [early_treatment, active_treatment, recovery]",
                "value": "invalid_phase"
            }
        ],
        "request_id": "req_123abc",
        "documentation_url": "https://docs.tumorheal.com/errors/VALIDATION_ERROR"
    }
}
```

## Analytics & Reporting

### Get User Progress Report
```http
GET /analytics/progress
```

Retrieves comprehensive progress report for the user.

**Query Parameters:**
- `start_date`: Start date for analysis (ISO 8601)
- `end_date`: End date for analysis (ISO 8601)
- `metrics`: Comma-separated list of metrics to include

**Response:**
```json
{
    "report_id": "report_123",
    "period": {
        "start": "2025-08-01T00:00:00Z",
        "end": "2025-09-30T23:59:59Z"
    },
    "metrics": {
        "strategy_adherence": 0.85,
        "symptom_improvement": 0.32,
        "community_engagement": 0.76,
        "emotional_wellbeing": 0.68
    },
    "trends": [
        {
            "date": "2025-08-01",
            "metrics": {
                "strategy_adherence": 0.75,
                "symptom_improvement": 0.20
            }
        }
    ],
    "insights": [
        {
            "type": "improvement",
            "description": "32% reduction in reported symptoms",
            "confidence": 0.89
        }
    ]
}
```

### Get Community Impact Metrics
```http
GET /analytics/community-impact
```

Retrieves metrics about user's community contributions.

**Response:**
```json
{
    "contributions": {
        "experiences_shared": 15,
        "strategies_contributed": 8,
        "quotes_posted": 12
    },
    "impact": {
        "users_helped": 156,
        "total_resonance": 432,
        "success_stories": 23
    },
    "recognition": {
        "badges": ["Wisdom Sharer", "Community Builder"],
        "achievement_level": "Gold",
        "impact_score": 89
    }
}
```

## Pagination

For endpoints returning lists, pagination is supported using cursor-based pagination:

```http
GET /quotes/?limit=10&cursor=quote_123
```

Response includes pagination metadata:

```json
{
    "data": [...],
    "pagination": {
        "next_cursor": "quote_456",
        "has_more": true
    }
}
```

## Integration Examples

### Python Client Integration
```python
from tumorheal import TumorHealClient

# Initialize client
client = TumorHealClient(
    api_key="your_api_key",
    environment="production"
)

# Share an experience
experience = client.experiences.create(
    title="My Healing Journey",
    content="Today marked a significant milestone...",
    tags=["milestone", "progress"],
    treatment_phase="active_treatment"
)

# Get personalized recommendations
recommendations = client.recommendations.get(
    limit=5,
    context={
        "current_symptoms": ["fatigue"],
        "preferences": ["natural-remedies"]
    }
)

# Real-time updates using WebSocket
async def handle_updates():
    async with client.realtime.connect() as socket:
        socket.subscribe(["new_strategies", "new_insights"])
        async for update in socket:
            print(f"New update: {update}")
```

### JavaScript/TypeScript Integration
```typescript
import { TumorHealSDK } from '@tumorheal/sdk';

// Initialize SDK
const tumorHeal = new TumorHealSDK({
    apiKey: 'your_api_key',
    environment: 'production'
});

// Share a healing strategy
async function shareStrategy() {
    try {
        const strategy = await tumorHeal.strategies.create({
            category: 'mindfulness',
            title: 'Peaceful Morning Routine',
            description: 'Start your day with intention...',
            instructions: [
                'Begin with 5 deep breaths',
                'Gentle stretching for 5 minutes',
                'Short meditation focusing on healing'
            ],
            effectiveness_rating: 4.8,
            duration_minutes: 15
        });
        console.log('Strategy shared:', strategy.id);
    } catch (error) {
        console.error('Error sharing strategy:', error);
    }
}

// Listen for real-time updates
tumorHeal.realtime.connect()
    .then(socket => {
        socket.on('new_insight', insight => {
            console.log('New community insight:', insight);
        });
        
        socket.on('recommendation_update', rec => {
            console.log('Updated recommendation:', rec);
        });
    });
```

## Rate Limiting and Quotas

### Rate Limit Tiers

1. Basic Tier
   - 100 requests/minute
   - 1,000 requests/hour
   - 10,000 requests/day

2. Professional Tier
   - 500 requests/minute
   - 5,000 requests/hour
   - 50,000 requests/day

3. Enterprise Tier
   - Custom limits
   - Dedicated infrastructure
   - SLA guarantees

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1583850767
X-RateLimit-Tier: "basic"
```

### Quota Usage Endpoint
```http
GET /account/quota
```

**Response:**
```json
{
    "tier": "professional",
    "limits": {
        "requests_per_minute": 500,
        "requests_per_hour": 5000,
        "requests_per_day": 50000
    },
    "current_usage": {
        "requests_this_minute": 42,
        "requests_this_hour": 385,
        "requests_today": 2456
    },
    "reset_times": {
        "minute_reset": "2025-09-30T10:01:00Z",
        "hour_reset": "2025-09-30T11:00:00Z",
        "day_reset": "2025-10-01T00:00:00Z"
    }
}
```

## Websocket Connections

Real-time updates are available through WebSocket connections:

```
ws://api.tumorheal.com/v2/ws
```

Supported events:
- `new_experience`
- `new_quote`
- `new_strategy`
- `new_insight`
- `recommendation_update`
- `progress_update`
- `community_alert`
- `achievement_earned`

Example WebSocket message:
```json
{
    "event": "new_insight",
    "data": {
        "id": "insight_789",
        "type": "correlation",
        "description": "New correlation found between morning meditation and reduced anxiety",
        "confidence": 0.92,
        "affected_users": 156
    },
    "timestamp": "2025-09-30T10:15:00Z"
}
```