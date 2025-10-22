# Available Backend API Endpoints

## ✅ Authentication APIs (Supabase)
**Base URL:** `http://localhost:8000/api/v1/auth`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/register` | POST | Register new user | `{email, password, full_name}` | `{access_token, user}` |
| `/login` | POST | Login user | `{email, password}` | `{access_token, user}` |
| `/me` | GET | Get current user info | - | `{id, email, full_name, ...}` |
| `/profile` | PUT | Update user profile | `{full_name, phone, ...}` | `{updated user}` |
| `/settings` | PUT | Update user settings | `{settings object}` | `{settings}` |
| `/reset-password` | POST | Request password reset | `{email}` | `{message}` |
| `/reset-password/confirm` | POST | Confirm password reset | `{token, new_password}` | `{message}` |
| `/otp/request` | POST | Request OTP code | `{email, action}` | `{message}` |
| `/otp/verify` | POST | Verify OTP code | `{email, otp_code, action}` | `{verified: true/false}` |
| `/refresh` | POST | Refresh access token | - | `{access_token}` |
| `/logout` | POST | Logout user | - | `{message}` |

**Authentication Header:** `Authorization: Bearer <token>`

---

## ✅ M-Pesa Payment APIs
**Base URL:** `http://localhost:8000/api/v1/payments/mpesa`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/stk-push` | POST | Initiate STK push payment | `{phone_number, amount, reference, description}` | `{CheckoutRequestID, ResponseCode, ...}` |
| `/check-payment-status` | POST | Check payment status | `{checkout_request_id}` | `{status, ResultCode, ...}` |
| `/callback` | POST | M-Pesa callback (Safaricom only) | Webhook data | `{message}` |

**Example STK Push Request:**
```json
{
  "phone_number": "254712345678",
  "amount": 100.0,
  "reference": "SUBSCRIPTION_001",
  "description": "Premium Plan Subscription"
}
```

---

## ✅ Health Profile APIs
**Base URL:** `http://localhost:8000/api/v1/health`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/profile` | POST | Create health profile | `{age, gender, weight, height, ...}` | `{profile object}` |
| `/profile` | GET | Get health profile | - | `{profile object}` |
| `/profile` | PUT | Update health profile | `{age, weight, ...}` | `{updated profile}` |
| `/metrics` | POST | Create health metric | `{metric_type, value, unit, ...}` | `{metric object}` |
| `/metrics/summary` | GET | Get metrics summary | Query: `?days=7` | `{period_days, metrics}` |
| `/metrics/history` | GET | Get metrics history | Query: `?metric_type=blood_pressure&days=30` | `[{metric objects}]` |

**Example Health Profile:**
```json
{
  "age": 35,
  "gender": "male",
  "weight": 75.5,
  "height": 175,
  "medical_conditions": ["hypertension"],
  "allergies": ["peanuts"]
}
```

**Example Health Metric:**
```json
{
  "metric_type": "blood_pressure",
  "value": 120,
  "unit": "mmHg",
  "notes": "Systolic pressure"
}
```

---

## ✅ Optimization Plan API
**Base URL:** `http://localhost:8000/api/v1/plan`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/run` | POST | Generate optimization plan | `{features, days, user_id}` | `{energy, plan[], meta}` |

**Example Plan Request:**
```json
{
  "features": {
    "age": 35,
    "bmi": 24.5,
    "activity_level": "moderate",
    "health_goals": ["weight_loss", "muscle_gain"]
  },
  "days": 7,
  "user_id": "user123"
}
```

**Example Plan Response:**
```json
{
  "energy": -125.5,
  "plan": [
    {
      "day": 1,
      "activity": "morning_jog",
      "duration": 30,
      "calories": 250
    }
  ],
  "meta": {
    "requested_by": "user@example.com"
  }
}
```

---

## 🔐 Authentication Flow

### 1. Register New User
```bash
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

### 2. Login
```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {...}
}
```

### 3. Use Token in Headers
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

## 💳 M-Pesa Payment Flow

### 1. Initiate Payment
```bash
POST /api/v1/payments/mpesa/stk-push
Authorization: Bearer <token>
{
  "phone_number": "254712345678",
  "amount": 100.0,
  "reference": "SUB_001",
  "description": "Premium Plan"
}

Response:
{
  "checkout_request_id": "ws_CO_123456789",
  "response_code": "0",
  "response_description": "Success. Request accepted for processing",
  "merchant_request_id": "12345-67890-1"
}
```

### 2. Check Payment Status
```bash
POST /api/v1/payments/mpesa/check-payment-status
Authorization: Bearer <token>
{
  "checkout_request_id": "ws_CO_123456789"
}

Response:
{
  "status": "completed",
  "result_code": "0",
  "result_description": "The service request is processed successfully"
}
```

---

## 🏥 Health Profile Flow

### 1. Create Profile
```bash
POST /api/v1/health/profile
Authorization: Bearer <token>
{
  "age": 35,
  "gender": "male",
  "weight": 75.5,
  "height": 175
}
```

### 2. Add Metrics
```bash
POST /api/v1/health/metrics
Authorization: Bearer <token>
{
  "metric_type": "blood_pressure",
  "value": 120,
  "unit": "mmHg"
}
```

### 3. View Summary
```bash
GET /api/v1/health/metrics/summary?days=7
Authorization: Bearer <token>

Response:
{
  "period_days": 7,
  "metrics": {
    "blood_pressure": 122.5,
    "heart_rate": 72.3,
    "weight": 75.2
  }
}
```

---

## 📊 Complete Integration Example

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register
register_response = requests.post(
    f"{BASE_URL}/api/v1/auth/register",
    json={
        "email": "john@example.com",
        "password": "SecurePass123!",
        "full_name": "John Doe"
    }
)
token = register_response.json()["access_token"]

# 2. Create Health Profile
headers = {"Authorization": f"Bearer {token}"}
profile_response = requests.post(
    f"{BASE_URL}/api/v1/health/profile",
    headers=headers,
    json={
        "age": 35,
        "gender": "male",
        "weight": 75.5,
        "height": 175
    }
)

# 3. Generate Plan
plan_response = requests.post(
    f"{BASE_URL}/api/v1/plan/run",
    headers=headers,
    json={
        "features": {
            "age": 35,
            "bmi": 24.5,
            "activity_level": "moderate"
        },
        "days": 7,
        "user_id": "john_doe"
    }
)

# 4. Make Payment
payment_response = requests.post(
    f"{BASE_URL}/api/v1/payments/mpesa/stk-push",
    headers=headers,
    json={
        "phone_number": "254712345678",
        "amount": 100.0,
        "reference": "PLAN_PAYMENT",
        "description": "7-Day Optimization Plan"
    }
)

print("Plan:", plan_response.json())
print("Payment:", payment_response.json())
```

---

## 🚀 Server Status

**Health Check:** `GET http://localhost:8000/health`
```json
{
  "status": "ok"
}
```

**API Documentation:** `http://localhost:8000/api/docs` (Swagger UI)

**Alternative Docs:** `http://localhost:8000/api/redoc` (ReDoc)

---

## ⚠️ Important Notes

1. **All endpoints except `/register` and `/login` require authentication**
2. **Use `Authorization: Bearer <token>` header for authenticated requests**
3. **M-Pesa phone numbers must be in format `254XXXXXXXXX`** (Kenya country code)
4. **Tokens expire after 24 hours** - use `/refresh` endpoint to get new token
5. **M-Pesa callback endpoint is for Safaricom use only** - configure in M-Pesa portal

---

## 🔗 CORS Configuration

The backend accepts requests from all origins (`*`) in development. Update `CORS_ORIGINS` in production.

**Allowed Methods:** GET, POST, PUT, DELETE  
**Allowed Headers:** All  
**Credentials:** Enabled

---

## 📝 Environment Variables Required

```env
# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key

# M-Pesa
MPESA_ENVIRONMENT=sandbox  # or production
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/v1/payments/mpesa/callback

# JWT
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```
