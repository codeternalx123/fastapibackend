# TumorHeal API Testing Guide

## 🚀 Running the Server

### Command to Start Server
```bash
C:/Users/Codeternal/Music/flaskbackend/.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access URLs
- **API Base URL**: `http://localhost:8000`
- **Interactive API Docs (Swagger)**: `http://localhost:8000/api/docs`
- **Alternative Docs (ReDoc)**: `http://localhost:8000/api/redoc`
- **Health Check**: `http://localhost:8000/health`

> **Note**: The server binds to `0.0.0.0:8000` but you must use `localhost:8000` or `127.0.0.1:8000` in your browser/API client.

---

## 📋 API Endpoints Overview

### 1. Health & Status
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Server health check | ❌ No |

### 2. Authentication (Supabase)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | ❌ No |
| POST | `/api/v1/auth/login` | Login user | ❌ No |
| GET | `/api/v1/auth/me` | Get current user info | ✅ Yes |
| PUT | `/api/v1/auth/profile` | Update user profile | ✅ Yes |
| PUT | `/api/v1/auth/settings` | Update user settings | ✅ Yes |
| POST | `/api/v1/auth/reset-password` | Request password reset | ❌ No |
| POST | `/api/v1/auth/reset-password/confirm` | Confirm password reset | ❌ No |
| POST | `/api/v1/auth/otp/request` | Request OTP code | ❌ No |
| POST | `/api/v1/auth/otp/verify` | Verify OTP code | ❌ No |
| POST | `/api/v1/auth/refresh` | Refresh access token | ✅ Yes |
| POST | `/api/v1/auth/logout` | Logout user | ✅ Yes |

### 3. Legacy Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register (legacy) | ❌ No |
| POST | `/api/v1/auth/login` | Login (legacy) | ❌ No |
| GET | `/api/v1/auth/me` | Get user info (legacy) | ✅ Yes |
| PUT | `/api/v1/auth/me` | Update user (legacy) | ✅ Yes |

### 4. M-Pesa Payments
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/payments/mpesa/stk-push` | Initiate STK push | ✅ Yes |
| POST | `/api/v1/payments/mpesa/check-payment-status` | Check payment status | ✅ Yes |
| POST | `/api/v1/payments/mpesa/callback` | M-Pesa callback (webhook) | ❌ No |

### 5. Health Profile
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/health/profile` | Create health profile | ✅ Yes |
| GET | `/api/v1/health/profile` | Get health profile | ✅ Yes |
| PUT | `/api/v1/health/profile` | Update health profile | ✅ Yes |
| POST | `/api/v1/health/metrics` | Create health metric | ✅ Yes |
| GET | `/api/v1/health/metrics/summary` | Get metrics summary | ✅ Yes |
| GET | `/api/v1/health/metrics/history` | Get metrics history | ✅ Yes |

### 6. Optimization Plan
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/plan/run` | Generate optimization plan | ✅ Yes |

---

## 🧪 Testing Methods

### Method 1: Interactive API Documentation (Recommended for Beginners)
1. Start the server
2. Open browser: `http://localhost:8000/api/docs`
3. Click on any endpoint to expand it
4. Click **"Try it out"** button
5. Fill in the request body/parameters
6. Click **"Execute"**
7. View the response below

### Method 2: Using cURL (Command Line)
Terminal/PowerShell commands for testing

### Method 3: Using Postman
1. Import the API by entering base URL: `http://localhost:8000`
2. Use the collection builder
3. Set headers and body as shown in examples below

### Method 4: Using Python Requests
```python
import requests

# Example
response = requests.get("http://localhost:8000/health")
print(response.json())
```

---

## 📝 Detailed Test Examples

### Test 1: Health Check (No Auth)
**cURL:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok"
}
```

---

### Test 2: Register New User
**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"SecurePass123!\",\"full_name\":\"Test User\"}"
```

**PowerShell:**
```powershell
$body = @{
    email = "test@example.com"
    password = "SecurePass123!"
    full_name = "Test User"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method Post -Body $body -ContentType "application/json"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "test@example.com",
    "full_name": "Test User",
    "created_at": "2025-10-22T06:30:00Z"
  }
}
```

**Save the `access_token` from the response! You'll need it for authenticated requests.**

---

### Test 3: Login User
**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"SecurePass123!\"}"
```

**PowerShell:**
```powershell
$body = @{
    email = "test@example.com"
    password = "SecurePass123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $body -ContentType "application/json"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "test@example.com",
    "full_name": "Test User"
  }
}
```

---

### Test 4: Get Current User Info (Authenticated)
**cURL:**
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**PowerShell:**
```powershell
$token = "YOUR_ACCESS_TOKEN_HERE"
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" -Method Get -Headers $headers
```

**Expected Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "test@example.com",
  "full_name": "Test User",
  "created_at": "2025-10-22T06:30:00Z"
}
```

---

### Test 5: Create Health Profile (Authenticated)
**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/health/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"age\":30,\"gender\":\"male\",\"height\":175,\"weight\":70,\"medical_conditions\":[\"None\"]}"
```

**PowerShell:**
```powershell
$token = "YOUR_ACCESS_TOKEN_HERE"
$headers = @{
    Authorization = "Bearer $token"
}
$body = @{
    age = 30
    gender = "male"
    height = 175
    weight = 70
    medical_conditions = @("None")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/profile" -Method Post -Headers $headers -Body $body -ContentType "application/json"
```

---

### Test 6: Initiate M-Pesa Payment (Authenticated)
**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/payments/mpesa/stk-push \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\":\"254712345678\",\"amount\":100,\"reference\":\"SUB001\",\"description\":\"Premium Subscription\"}"
```

**PowerShell:**
```powershell
$token = "YOUR_ACCESS_TOKEN_HERE"
$headers = @{
    Authorization = "Bearer $token"
}
$body = @{
    phone_number = "254712345678"
    amount = 100
    reference = "SUB001"
    description = "Premium Subscription"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/payments/mpesa/stk-push" -Method Post -Headers $headers -Body $body -ContentType "application/json"
```

**Note**: M-Pesa requires proper credentials in `.env` file. Without valid credentials, this will fail.

---

## 🔑 Authentication Flow

### Step-by-Step Authentication
1. **Register** or **Login** to get an `access_token`
2. **Copy the token** from the response
3. **Add the token** to all subsequent requests in the `Authorization` header:
   ```
   Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
   ```

### Token Format
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIn0.signature
```

### Token Expiration
- Tokens expire after **24 hours**
- Use `/api/v1/auth/refresh` to get a new token
- Or login again to get a fresh token

---

## 🛠️ Testing Checklist

### ✅ Basic Tests (No Auth Required)
- [ ] Server is running: `GET http://localhost:8000/health`
- [ ] API docs accessible: `http://localhost:8000/api/docs`
- [ ] Can register new user: `POST /api/v1/auth/register`
- [ ] Can login: `POST /api/v1/auth/login`

### ✅ Authenticated Tests (Requires Token)
- [ ] Get current user: `GET /api/v1/auth/me`
- [ ] Update profile: `PUT /api/v1/auth/profile`
- [ ] Create health profile: `POST /api/v1/health/profile`
- [ ] Get health profile: `GET /api/v1/health/profile`
- [ ] Create health metric: `POST /api/v1/health/metrics`
- [ ] Get metrics summary: `GET /api/v1/health/metrics/summary`

### ✅ M-Pesa Tests (Requires M-Pesa Credentials)
- [ ] Initiate STK push: `POST /api/v1/payments/mpesa/stk-push`
- [ ] Check payment status: `POST /api/v1/payments/mpesa/check-payment-status`

---

## 🐛 Troubleshooting

### Issue: "ERR_ADDRESS_INVALID" or Can't Connect
**Solution**: Use `http://localhost:8000` instead of `http://0.0.0.0:8000`

### Issue: "401 Unauthorized"
**Solution**: 
1. Make sure you're logged in and have a valid token
2. Check that the `Authorization` header is set correctly
3. Verify token hasn't expired (24-hour lifespan)

### Issue: "M-Pesa credentials not configured"
**Solution**: 
1. Add M-Pesa credentials to `.env` file:
   ```
   MPESA_ENVIRONMENT=sandbox
   MPESA_CONSUMER_KEY=your_consumer_key
   MPESA_CONSUMER_SECRET=your_consumer_secret
   MPESA_SHORTCODE=your_shortcode
   MPESA_PASSKEY=your_passkey
   ```
2. Restart the server

### Issue: Server won't start
**Solution**:
1. Check if port 8000 is already in use: `netstat -ano | findstr :8000`
2. Kill the process if needed
3. Check Python virtual environment is activated
4. Verify all dependencies installed: `pip install -r requirements.txt`

---

## 📊 Example Test Workflow

### Complete User Journey
```bash
# 1. Check server health
curl http://localhost:8000/health

# 2. Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"Pass123!","full_name":"John Doe"}'

# 3. Save the access_token from response, then get user info
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 4. Create health profile
curl -X POST http://localhost:8000/api/v1/health/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"age":35,"gender":"male","height":180,"weight":75}'

# 5. Add health metric
curl -X POST http://localhost:8000/api/v1/health/metrics \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"metric_type":"blood_pressure","value":120,"unit":"mmHg"}'

# 6. Get metrics summary
curl http://localhost:8000/api/v1/health/metrics/summary?days=7 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🎯 Quick Start for Testing

### Option 1: Use Swagger UI (Easiest)
1. Run: `C:/Users/Codeternal/Music/flaskbackend/.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. Open: `http://localhost:8000/api/docs`
3. Click "Authorize" button (top right)
4. After login, paste your token in the format: `Bearer YOUR_TOKEN`
5. Test endpoints by clicking "Try it out"

### Option 2: Use Postman Collection
1. Create new collection in Postman
2. Set base URL: `http://localhost:8000`
3. Create environment variable `token` for authentication
4. Use `{{token}}` in Authorization header
5. Import examples from this guide

### Option 3: Use Python Script
```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
})
print("Register:", response.json())

# Save token
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get user info
response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
print("User Info:", response.json())

# Create health profile
response = requests.post(f"{BASE_URL}/api/v1/health/profile", 
    headers=headers,
    json={"age": 30, "gender": "male", "height": 175, "weight": 70}
)
print("Health Profile:", response.json())
```

---

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Swagger UI Guide**: https://swagger.io/tools/swagger-ui/
- **M-Pesa API Docs**: https://developer.safaricom.co.ke/
- **Supabase Docs**: https://supabase.com/docs

---

## 💡 Tips

1. **Always test health endpoint first** to ensure server is running
2. **Use the interactive docs** (`/api/docs`) for quick testing
3. **Save your tokens** - they're valid for 24 hours
4. **Test without auth first**, then with auth
5. **Check console logs** on server for detailed error messages
6. **Use JSON formatters** in browser for readable responses
7. **Set up Postman environments** for dev/staging/production

---

**Last Updated**: October 22, 2025  
**API Version**: 2.0.0  
**Contact**: support@tumorheal.com
