# TumorHeal API Documentation

## Base URL
```
https://api.tumorheal.com/api/v1
```

## Authentication

### JWT Authentication
All API requests must include a JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "string",
  "password": "string"
}
```

**Response**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "string",
    "email": "string",
    "name": "string",
    "subscription_status": "string"
  }
}
```

### Refresh Token
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

**Response**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Payment Endpoints

### Process Quantum-Secure Payment
```http
POST /payments/process
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "amount": number,
  "currency": "string",
  "payment_method_id": "string",
  "provider": "string",
  "metadata": {
    "device_info": {
      "os": "string",
      "model": "string",
      "browser": "string",
      "screen_resolution": "string",
      "timezone": "string"
    },
    "location": {
      "latitude": number,
      "longitude": number
    },
    "network_info": {
      "ip_address": "string",
      "is_vpn": boolean,
      "is_proxy": boolean
    },
    "subscription_id": "string"
  }
}
```

**Response**
```json
{
  "id": "string",
  "status": "string",
  "amount": number,
  "currency": "string",
  "provider": "string",
  "created_at": "string",
  "provider_payment_id": "string",
  "secured_payment": {
    "encrypted_data": "string",
    "encrypted_key": "string",
    "mac": "string",
    "timestamp": "string"
  },
  "fraud_analysis": {
    "is_fraudulent": boolean,
    "fraud_probability": number,
    "risk_level": "string",
    "feature_importance": {
      "amount": number,
      "frequency": number,
      "time_pattern": number,
      "location_risk": number,
      "device_risk": number
    }
  }
}
```

### Verify Payment
```http
POST /payments/verify/{payment_id}
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "secured_data": {
    "encrypted_data": "string",
    "encrypted_key": "string",
    "mac": "string"
  }
}
```

**Response**
```json
{
  "status": "string",
  "payment_data": {
    "id": "string",
    "amount": number,
    "currency": "string",
    "status": "string",
    "verification_status": "string"
  }
}
```

### Analyze Payment Risk
```http
POST /payments/analyze-risk
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "payment_data": {
    "amount": number,
    "currency": "string",
    "device_info": object,
    "location": object,
    "network_info": object
  }
}
```

**Response**
```json
{
  "risk_analysis": {
    "is_fraudulent": boolean,
    "fraud_probability": number,
    "risk_level": "string",
    "feature_importance": object
  },
  "recommendation": "string",
  "quantum_enhanced": boolean
}
```

## Error Responses

### Standard Error Response
```json
{
  "detail": {
    "message": "string",
    "code": "string",
    "params": object
  }
}
```

### Error Codes
```json
{
  "PAYMENT_ERROR": {
    "P001": "General payment processing error",
    "P002": "Fraud detected",
    "P003": "Invalid payment amount",
    "P004": "Unsupported payment provider",
    "P005": "Payment verification failed",
    "P006": "Payment encryption failed"
  },
  "AUTH_ERROR": {
    "A001": "Authentication failed",
    "A002": "Token expired",
    "A003": "Invalid credentials",
    "A004": "User not found"
  },
  "SECURITY_ERROR": {
    "S001": "Invalid signature",
    "S002": "Encryption failed",
    "S003": "Decryption failed",
    "S004": "Invalid MAC"
  }
}
```

## Data Models

### Payment Model
```dart
class Payment {
  final String id;
  final double amount;
  final String currency;
  final String status;
  final String provider;
  final DateTime createdAt;
  final String providerPaymentId;
  final SecuredPayment? securedPayment;
  final FraudAnalysis? fraudAnalysis;

  // Add constructor and fromJson/toJson methods
}

class SecuredPayment {
  final String encryptedData;
  final String encryptedKey;
  final String mac;
  final DateTime timestamp;

  // Add constructor and fromJson/toJson methods
}

class FraudAnalysis {
  final bool isFraudulent;
  final double fraudProbability;
  final String riskLevel;
  final Map<String, double> featureImportance;

  // Add constructor and fromJson/toJson methods
}
```

### API Service Implementation
```dart
class ApiService {
  final Dio _dio;
  final SecureStorage _storage;

  ApiService({required String baseUrl}) 
      : _dio = Dio(BaseOptions(baseUrl: baseUrl)) {
    _setupInterceptors();
  }

  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) {
          if (error.response?.statusCode == 401) {
            // Handle token refresh
          }
          return handler.next(error);
        },
      ),
    );
  }

  Future<Payment> processPayment(PaymentRequest request) async {
    try {
      final response = await _dio.post(
        '/payments/process',
        data: request.toJson(),
      );
      return Payment.fromJson(response.data);
    } on DioError catch (e) {
      throw _handleError(e);
    }
  }

  PaymentException _handleError(DioError error) {
    if (error.response?.data != null) {
      final errorData = error.response!.data;
      return PaymentException(
        message: errorData['detail']['message'],
        code: errorData['detail']['code'],
        params: errorData['detail']['params'],
      );
    }
    return PaymentException(
      message: 'Network error occurred',
      code: 'NETWORK_ERROR',
    );
  }
}
```

### Example Provider Implementation
```dart
class PaymentProvider extends ChangeNotifier {
  final ApiService _api;
  Payment? _currentPayment;
  bool _loading = false;
  String? _error;

  PaymentProvider(this._api);

  Future<void> processPayment(PaymentRequest request) async {
    try {
      _loading = true;
      _error = null;
      notifyListeners();

      _currentPayment = await _api.processPayment(request);
      
    } on PaymentException catch (e) {
      _error = e.message;
    } finally {
      _loading = false;
      notifyListeners();
    }
  }
}
```

### Example UI Implementation
```dart
class PaymentScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<PaymentProvider>(
      builder: (context, provider, _) {
        if (provider.loading) {
          return LoadingSpinner();
        }

        if (provider.error != null) {
          return ErrorView(
            message: provider.error!,
            onRetry: () => provider.retryPayment(),
          );
        }

        return PaymentForm(
          onSubmit: (request) => provider.processPayment(request),
        );
      },
    );
  }
}
```

## Security Requirements

1. **SSL Pinning**
```dart
class SecurityConfig {
  static String get certificateAuthority => '''
    -----BEGIN CERTIFICATE-----
    ... Your CA certificate ...
    -----END CERTIFICATE-----
  ''';
}
```

2. **Secure Storage**
```dart
class SecureStorage {
  final FlutterSecureStorage _storage = FlutterSecureStorage();

  Future<void> setToken(String token) async {
    await _storage.write(key: 'auth_token', value: token);
  }

  Future<String?> getToken() async {
    return await _storage.read(key: 'auth_token');
  }
}
```

3. **Biometric Authentication**
```dart
class BiometricAuth {
  static Future<bool> authenticate() async {
    final LocalAuthentication auth = LocalAuthentication();
    
    try {
      return await auth.authenticate(
        localizedReason: 'Please authenticate to complete payment',
        options: const AuthenticationOptions(
          biometricOnly: true,
        ),
      );
    } catch (e) {
      return false;
    }
  }
}
```

## Meal Tracking and Planning

### Log Meal
```http
POST /meals/log
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "string",
  "description": "string",
  "meal_type": "breakfast" | "lunch" | "dinner" | "snack",
  "calories": number,
  "protein": number,
  "carbs": number,
  "fats": number,
  "nutrients": {
    "vitamins": object,
    "minerals": object,
    "antioxidants": object
  },
  "cancer_fighting_ingredients": string[],
  "consumed_at": "string" // ISO date string
}
```

**Response**
```json
{
  "id": "string",
  "name": "string",
  "meal_type": "string",
  "nutritional_info": {
    "calories": number,
    "protein": number,
    "carbs": number,
    "fats": number,
    "nutrients": object
  },
  "cancer_fighting_properties": {
    "ingredients": string[],
    "benefits": object
  },
  "consumed_at": "string",
  "created_at": "string"
}
```

### Get Meal History
```http
GET /meals/history?start_date=string&end_date=string&meal_type=string
Authorization: Bearer <jwt_token>
```

**Response**
```json
{
  "meals": [
    {
      "id": "string",
      "name": "string",
      "meal_type": "string",
      "nutritional_info": object,
      "consumed_at": "string"
    }
  ],
  "summary": {
    "total_meals": number,
    "average_calories": number,
    "nutritional_goals_met": boolean,
    "cancer_fighting_foods_consumed": number
  }
}
```

### Create Meal Plan
```http
POST /meal-plans
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "string",
  "description": "string",
  "start_date": "string",
  "end_date": "string",
  "plan_type": "weekly" | "monthly",
  "nutritional_goals": {
    "daily_calories": number,
    "protein_target": number,
    "carbs_target": number,
    "fats_target": number,
    "cancer_fighting_foods_target": number
  },
  "meals": [
    {
      "meal_id": "string",
      "day_of_week": number, // 0-6
      "week_number": number, // 1-4 for monthly plans
      "meal_type": "string",
      "scheduled_time": "string" // HH:mm
    }
  ]
}
```

**Response**
```json
{
  "id": "string",
  "name": "string",
  "plan_type": "string",
  "date_range": {
    "start": "string",
    "end": "string"
  },
  "meals": array,
  "nutritional_goals": object,
  "created_at": "string"
}
```

### Set Reminders
```http
POST /reminders
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "string",
  "description": "string",
  "reminder_type": "meal" | "medication" | "hydration",
  "frequency": "daily" | "weekly" | "monthly",
  "scheduled_time": "string", // HH:mm
  "days_of_week": number[] // 0-6
}
```

**Response**
```json
{
  "id": "string",
  "title": "string",
  "reminder_type": "string",
  "next_reminder": "string",
  "created_at": "string"
}
```

### Get Health Analytics
```http
GET /analytics/health-report?period=weekly|monthly&date=string
Authorization: Bearer <jwt_token>
```

**Response**
```json
{
  "period": "string",
  "date_range": {
    "start": "string",
    "end": "string"
  },
  "nutritional_metrics": {
    "average_daily_calories": number,
    "protein_intake": number,
    "carbs_intake": number,
    "fats_intake": number,
    "cancer_fighting_foods_consumption": number
  },
  "meal_plan_adherence": number,
  "health_indicators": {
    "nutritional_balance": number,
    "cancer_fighting_food_score": number,
    "meal_timing_consistency": number
  },
  "recommendations": {
    "dietary_adjustments": array,
    "suggested_cancer_fighting_foods": array,
    "lifestyle_tips": array
  }
}
```

## Data Models

### Meal Model
```dart
class Meal {
  final String id;
  final String name;
  final String description;
  final String mealType;
  final NutritionalInfo nutritionalInfo;
  final List<String> cancerFightingIngredients;
  final DateTime consumedAt;
  final DateTime createdAt;

  // Add constructor and fromJson/toJson methods
}

class NutritionalInfo {
  final int calories;
  final double protein;
  final double carbs;
  final double fats;
  final Map<String, dynamic> nutrients;

  // Add constructor and fromJson/toJson methods
}
```

### MealPlan Model
```dart
class MealPlan {
  final String id;
  final String name;
  final String description;
  final DateTime startDate;
  final DateTime endDate;
  final String planType;
  final NutritionalGoals goals;
  final List<MealPlanItem> meals;

  // Add constructor and fromJson/toJson methods
}

class MealPlanItem {
  final String id;
  final String mealId;
  final int dayOfWeek;
  final int? weekNumber;
  final String mealType;
  final String scheduledTime;

  // Add constructor and fromJson/toJson methods
}
```

### Reminder Model
```dart
class Reminder {
  final String id;
  final String title;
  final String description;
  final String reminderType;
  final String frequency;
  final String scheduledTime;
  final List<int> daysOfWeek;
  final bool isActive;

  // Add constructor and fromJson/toJson methods
}
```

### Analytics Model
```dart
class HealthAnalytics {
  final String period;
  final DateTimeRange dateRange;
  final NutritionalMetrics metrics;
  final double mealPlanAdherence;
  final HealthIndicators indicators;
  final List<String> recommendations;

  // Add constructor and fromJson/toJson methods
}
```

## Testing Examples

### Unit Tests
```dart
void main() {
  group('ApiService', () {
    late ApiService apiService;
    late MockDio mockDio;

    setUp(() {
      mockDio = MockDio();
      apiService = ApiService(dio: mockDio);
    });

    test('processPayment success', () async {
      when(mockDio.post(any, data: any))
        .thenAnswer((_) async => Response(
          data: paymentResponseJson,
          statusCode: 200,
        ));

      final payment = await apiService.processPayment(
        PaymentRequest(amount: 100),
      );

      expect(payment.status, equals('success'));
    });
  });
}
```

### Widget Tests
```dart
void main() {
  testWidgets('PaymentScreen shows error on failure',
    (WidgetTester tester) async {
      final mockProvider = MockPaymentProvider();
      when(mockProvider.error).thenReturn('Payment failed');

      await tester.pumpWidget(
        ChangeNotifierProvider<PaymentProvider>.value(
          value: mockProvider,
          child: MaterialApp(home: PaymentScreen()),
        ),
      );

      expect(find.text('Payment failed'), findsOneWidget);
      expect(find.byType(ErrorView), findsOneWidget);
    });
}
```