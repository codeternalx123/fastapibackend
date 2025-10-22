# Supabase Authentication Integration for TumorHeal

## Overview
This integration uses Supabase as the backend database for TumorHeal authentication system, providing secure user management, settings, and token handling.

## Features
- ✅ User registration and login
- ✅ JWT token-based authentication
- ✅ Password reset functionality
- ✅ OTP (One-Time Password) support
- ✅ User roles and permissions
- ✅ User settings management
- ✅ Profile management
- ✅ Secure password hashing with bcrypt

## Setup Instructions

### 1. Create Supabase Project
1. Go to [https://supabase.com](https://supabase.com)
2. Create a new project
3. Note your project URL and API keys

### 2. Run Database Schema
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and run the SQL from `docs/supabase_schema.sql`
4. This will create all necessary tables and security policies

### 3. Configure Environment Variables
Add the following to your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
```

### 4. Install Dependencies
```bash
pip install supabase pyjwt bcrypt python-dotenv
```

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1/auth
```

### 1. Register User
**POST** `/register`

Request:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe",
  "metadata": {
    "age": 30,
    "location": "Nairobi"
  }
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "user_xxxxx",
    "email": "user@example.com",
    "name": "John Doe",
    "is_email_verified": false,
    "roles": ["user"],
    "created_at": "2025-10-22T10:00:00Z",
    "settings": {
      "language": "en",
      "timezone": "UTC",
      "notifications": {...},
      "privacy": {...}
    }
  }
}
```

### 2. Login
**POST** `/login`

Request:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Response: Same as register

### 3. Get Current User
**GET** `/me`

Headers:
```
Authorization: Bearer <access_token>
```

Response:
```json
{
  "id": "user_xxxxx",
  "email": "user@example.com",
  "name": "John Doe",
  ...
}
```

### 4. Update Profile
**PUT** `/profile`

Headers:
```
Authorization: Bearer <access_token>
```

Request:
```json
{
  "name": "Jane Doe",
  "profile_picture": "https://example.com/avatar.jpg",
  "metadata": {
    "bio": "Health enthusiast"
  }
}
```

### 5. Update Settings
**PUT** `/settings`

Request:
```json
{
  "language": "sw",
  "timezone": "Africa/Nairobi",
  "notification_email": true,
  "notification_push": false,
  "privacy_profile_public": true
}
```

### 6. Request Password Reset
**POST** `/reset-password`

Request:
```json
{
  "email": "user@example.com"
}
```

### 7. Confirm Password Reset
**POST** `/reset-password/confirm`

Request:
```json
{
  "token": "reset_token_from_email",
  "new_password": "newsecurepassword123"
}
```

### 8. Request OTP
**POST** `/otp/request`

Request:
```json
{
  "email": "user@example.com",
  "action": "login"
}
```

### 9. Verify OTP
**POST** `/otp/verify`

Request:
```json
{
  "email": "user@example.com",
  "otp_code": "123456",
  "action": "login"
}
```

### 10. Refresh Token
**POST** `/refresh`

Headers:
```
Authorization: Bearer <access_token>
```

### 11. Logout
**POST** `/logout`

Headers:
```
Authorization: Bearer <access_token>
```

## Database Schema

### Tables Created:
1. **users** - Main user data
2. **user_roles** - User roles and permissions
3. **user_settings** - User preferences and settings
4. **password_reset_tokens** - Password reset tokens
5. **otp_tokens** - One-time passwords for verification

## Security Features

1. **Password Hashing**: Bcrypt with salt
2. **JWT Tokens**: Secure token-based authentication
3. **Row Level Security**: Supabase RLS policies
4. **Token Expiration**: Tokens expire after 24 hours
5. **OTP Expiration**: OTP codes expire after 10 minutes
6. **Reset Token Expiration**: Reset tokens expire after 1 hour

## Flutter Integration

### Installation
```yaml
dependencies:
  dio: ^5.0.0
  flutter_secure_storage: ^9.0.0
```

### Example Code
```dart
class AuthService {
  final Dio _dio = Dio(BaseOptions(
    baseUrl: 'http://your-api-url.com/api/v1/auth',
  ));

  Future<AuthResponse> register(String email, String password, String name) async {
    try {
      final response = await _dio.post('/register', data: {
        'email': email,
        'password': password,
        'name': name,
      });
      return AuthResponse.fromJson(response.data);
    } catch (e) {
      throw Exception('Registration failed: $e');
    }
  }

  Future<AuthResponse> login(String email, String password) async {
    try {
      final response = await _dio.post('/login', data: {
        'email': email,
        'password': password,
      });
      
      // Store token securely
      final storage = FlutterSecureStorage();
      await storage.write(
        key: 'access_token',
        value: response.data['access_token'],
      );
      
      return AuthResponse.fromJson(response.data);
    } catch (e) {
      throw Exception('Login failed: $e');
    }
  }

  Future<UserResponse> getCurrentUser() async {
    final storage = FlutterSecureStorage();
    final token = await storage.read(key: 'access_token');
    
    final response = await _dio.get('/me',
      options: Options(headers: {
        'Authorization': 'Bearer $token',
      }),
    );
    
    return UserResponse.fromJson(response.data);
  }
}
```

## Testing

### Using cURL
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get current user
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure Supabase package is installed
```bash
pip install supabase
```

2. **Connection errors**: Verify SUPABASE_URL and SUPABASE_KEY in `.env`

3. **Authentication errors**: Check JWT_SECRET_KEY is set and consistent

4. **Database errors**: Ensure SQL schema is properly executed in Supabase

## Production Checklist

- [ ] Change JWT_SECRET_KEY to a strong random value
- [ ] Enable RLS policies in Supabase
- [ ] Set up email service for password reset and OTP
- [ ] Configure CORS origins properly
- [ ] Enable HTTPS
- [ ] Set up rate limiting
- [ ] Implement logging and monitoring
- [ ] Add input validation
- [ ] Set up backup strategy
- [ ] Configure Supabase security rules

## Support

For issues or questions, contact the development team or check the Supabase documentation at [https://supabase.com/docs](https://supabase.com/docs)
