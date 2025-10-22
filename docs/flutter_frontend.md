# TumorHeal Frontend Documentation

## Overview
TumorHeal's Flutter frontend application provides a user-friendly interface to interact with the quantum-secure payment system and other health optimization features. This documentation covers implementation details, API integration, and code examples.

## Table of Contents
1. [Installation & Setup](#installation--setup)
2. [Payment Features](#payment-features)
3. [Authentication](#authentication)
4. [Health Plans](#health-plans)
5. [Reports](#reports)
6. [Analytics](#analytics)
7. [Food Scanning](#food-scanning)

## Installation & Setup

### Requirements
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.0.5
  flutter_secure_storage: ^8.0.0
  json_annotation: ^4.8.1
  dio: ^5.3.2
  flutter_stripe: ^9.4.0
  pay: ^1.1.2
  crypto: ^3.0.3
  local_auth: ^2.1.6
```

### Project Structure
```
lib/
├── main.dart
├── config/
│   ├── api_config.dart
│   └── app_config.dart
├── models/
│   ├── payment.dart
│   ├── user.dart
│   ├── plan.dart
│   └── report.dart
├── providers/
│   ├── auth_provider.dart
│   ├── payment_provider.dart
│   └── health_provider.dart
├── screens/
│   ├── auth/
│   ├── payments/
│   ├── plans/
│   └── reports/
├── services/
│   ├── api_service.dart
│   ├── payment_service.dart
│   └── secure_storage.dart
└── widgets/
    ├── payment/
    ├── plan/
    └── common/
```

## Payment Features

### Quantum-Secure Payment Integration

#### 1. Setup Payment Service
```dart
class QuantumSecurePaymentService {
  final Dio _dio;
  final String baseUrl;

  QuantumSecurePaymentService({required this.baseUrl}) 
      : _dio = Dio(BaseOptions(baseUrl: baseUrl));

  Future<PaymentResponse> processPayment({
    required double amount,
    required String currency,
    required String paymentMethodId,
    required Map<String, dynamic> metadata,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/payments/process',
        data: {
          'amount': amount,
          'currency': currency,
          'payment_method_id': paymentMethodId,
          'metadata': {
            ...metadata,
            'device_info': await _getDeviceInfo(),
            'location': await _getLocation(),
            'network_info': await _getNetworkInfo(),
          }
        }
      );

      return PaymentResponse.fromJson(response.data);
    } catch (e) {
      throw PaymentException(e.toString());
    }
  }

  Future<Map<String, dynamic>> _getDeviceInfo() async {
    DeviceInfoPlugin deviceInfo = DeviceInfoPlugin();
    if (Platform.isAndroid) {
      AndroidDeviceInfo androidInfo = await deviceInfo.androidInfo;
      return {
        'os': 'android',
        'model': androidInfo.model,
        'device_id': androidInfo.androidId,
      };
    } else if (Platform.isIOS) {
      IosDeviceInfo iosInfo = await deviceInfo.iosInfo;
      return {
        'os': 'ios',
        'model': iosInfo.model,
        'device_id': iosInfo.identifierForVendor,
      };
    }
    return {};
  }
}
```

#### 2. Payment Screen Implementation
```dart
class PaymentScreen extends StatefulWidget {
  @override
  _PaymentScreenState createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  final _paymentService = QuantumSecurePaymentService(
    baseUrl: AppConfig.apiUrl,
  );

  Future<void> _handlePayment(PaymentMethod method) async {
    try {
      final result = await _paymentService.processPayment(
        amount: 100.00,
        currency: 'USD',
        paymentMethodId: method.id,
        metadata: {
          'subscription_type': 'premium',
          'duration': 'monthly'
        }
      );

      if (result.status == 'success') {
        // Handle successful payment
        Navigator.pushNamed(context, '/payment-success');
      }
    } catch (e) {
      // Handle payment error
      showErrorDialog(context, e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Secure Payment')),
      body: PaymentMethodSelector(
        onMethodSelected: _handlePayment,
        supportedMethods: [
          PaymentMethodType.stripe,
          PaymentMethodType.applePay,
          PaymentMethodType.googlePay,
          PaymentMethodType.crypto
        ],
      ),
    );
  }
}
```

### Payment Method Types

#### Apple Pay Integration
```dart
class ApplePayButton extends StatelessWidget {
  final Function(PaymentMethod) onPaymentComplete;

  Future<void> _handleApplePay() async {
    final paymentMethod = await Pay.createPaymentMethod(
      paymentRequest: PaymentRequest(
        merchantIdentifier: 'merchant.com.tumorheal',
        countryCode: 'US',
        currencyCode: 'USD',
        supportedNetworks: [
          PaymentNetwork.visa,
          PaymentNetwork.mastercard,
        ],
      ),
    );

    await onPaymentComplete(paymentMethod);
  }

  @override
  Widget build(BuildContext context) {
    return ApplePayButton(
      onPressed: _handleApplePay,
      paymentConfigurationAsset: 'apple_pay_config.json',
    );
  }
}
```

#### Google Pay Integration
```dart
class GooglePayButton extends StatelessWidget {
  final Function(PaymentMethod) onPaymentComplete;

  Future<void> _handleGooglePay() async {
    final paymentMethod = await Pay.createPaymentMethod(
      paymentRequest: PaymentRequest(
        merchantIdentifier: 'YOUR_MERCHANT_ID',
        countryCode: 'US',
        currencyCode: 'USD',
        supportedNetworks: [
          PaymentNetwork.visa,
          PaymentNetwork.mastercard,
        ],
      ),
    );

    await onPaymentComplete(paymentMethod);
  }

  @override
  Widget build(BuildContext context) {
    return GooglePayButton(
      onPressed: _handleGooglePay,
      paymentConfigurationAsset: 'google_pay_config.json',
    );
  }
}
```

#### Crypto Payment Integration
```dart
class CryptoPaymentWidget extends StatefulWidget {
  final Function(String) onPaymentComplete;

  @override
  _CryptoPaymentWidgetState createState() => _CryptoPaymentWidgetState();
}

class _CryptoPaymentWidgetState extends State<CryptoPaymentWidget> {
  String selectedCurrency = 'BTC';
  String paymentAddress = '';
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _initializeCryptoPayment();
  }

  Future<void> _initializeCryptoPayment() async {
    final response = await _paymentService.createCryptoPayment(
      amount: 15.00,
      currency: 'USD',
      cryptoCurrency: selectedCurrency,
    );

    setState(() {
      paymentAddress = response.paymentAddress;
    });

    // Start polling for payment status
    _pollTimer = Timer.periodic(Duration(seconds: 10), (_) {
      _checkPaymentStatus(response.paymentId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        CryptoCurrencySelector(
          value: selectedCurrency,
          onChanged: (value) {
            setState(() {
              selectedCurrency = value;
            });
            _initializeCryptoPayment();
          },
        ),
        QRCodeWidget(
          data: paymentAddress,
          size: 200,
        ),
        Text('Send $selectedCurrency to:'),
        SelectableText(paymentAddress),
      ],
    );
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }
}
```

## Authentication

### Secure User Authentication
```dart
class AuthService {
  final SecureStorage _storage;
  final ApiService _api;

  Future<User> login(String email, String password) async {
    final response = await _api.post('/auth/login', {
      'email': email,
      'password': password,
    });

    final user = User.fromJson(response.data['user']);
    await _storage.setToken(response.data['token']);

    return user;
  }

  Future<void> logout() async {
    await _storage.deleteToken();
  }
}
```

## Health Plans

### Plan Management
```dart
class PlanScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<PlanProvider>(
      builder: (context, provider, child) {
        return ListView.builder(
          itemCount: provider.plans.length,
          itemBuilder: (context, index) {
            final plan = provider.plans[index];
            return PlanCard(
              plan: plan,
              onSubscribe: () => _handleSubscription(context, plan),
            );
          },
        );
      },
    );
  }
}
```

## Reports

### Health Reports Viewer
```dart
class ReportViewer extends StatelessWidget {
  final Report report;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: [
          ReportHeader(report: report),
          ReportMetrics(metrics: report.metrics),
          ReportRecommendations(
            recommendations: report.recommendations,
          ),
        ],
      ),
    );
  }
}
```

## Analytics

### Health Analytics Dashboard
```dart
class AnalyticsDashboard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: 2,
      children: [
        AnalyticsCard(
          title: 'Health Score',
          value: '85',
          trend: '+5',
        ),
        AnalyticsCard(
          title: 'Activity Level',
          value: 'High',
          trend: 'Improving',
        ),
        // More analytics cards...
      ],
    );
  }
}
```

## Food Scanning

### Food Scanner Integration
```dart
class FoodScanner extends StatefulWidget {
  @override
  _FoodScannerState createState() => _FoodScannerState();
}

class _FoodScannerState extends State<FoodScanner> {
  Future<void> _scanFood() async {
    final image = await ImagePicker().pickImage(
      source: ImageSource.camera,
    );

    if (image != null) {
      final result = await _foodScanningService.analyzeFood(
        image.path,
      );

      setState(() {
        _scanResults = result;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ElevatedButton(
          onPressed: _scanFood,
          child: Text('Scan Food'),
        ),
        if (_scanResults != null)
          FoodAnalysisResult(results: _scanResults!),
      ],
    );
  }
}
```

## Error Handling

### Global Error Handler
```dart
class ErrorHandler {
  static void handleError(BuildContext context, dynamic error) {
    String message = 'An error occurred';

    if (error is PaymentException) {
      message = error.message;
    } else if (error is AuthException) {
      message = 'Authentication failed';
    } else if (error is NetworkException) {
      message = 'Network error occurred';
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }
}
```

## State Management

### Using Provider
```dart
void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => PaymentProvider()),
        ChangeNotifierProvider(create: (_) => HealthProvider()),
      ],
      child: MyApp(),
    ),
  );
}
```

## Testing

### Unit Tests
```dart
void main() {
  group('Payment Service Tests', () {
    test('processPayment should complete successfully', () async {
      final service = QuantumSecurePaymentService(
        baseUrl: 'http://localhost:8000',
      );

      final result = await service.processPayment(
        amount: 100.00,
        currency: 'USD',
        paymentMethodId: 'test_payment_method',
        metadata: {},
      );

      expect(result.status, equals('success'));
    });
  });
}
```

### Widget Tests
```dart
void main() {
  testWidgets('Payment screen shows payment methods', (tester) async {
    await tester.pumpWidget(MaterialApp(home: PaymentScreen()));

    expect(find.text('Select Payment Method'), findsOneWidget);
    expect(find.byType(PaymentMethodSelector), findsOneWidget);
  });
}
```

## Security Considerations

1. All sensitive data is encrypted using quantum-resistant encryption
2. Biometric authentication for payments above certain threshold
3. Secure storage for tokens and payment methods
4. Certificate pinning for API communications
5. Device integrity checks before processing payments

## Error Codes and Messages

| Code | Message | Description |
|------|---------|-------------|
| P001 | Payment Failed | General payment processing error |
| P002 | Fraud Detection | Transaction blocked by fraud detection |
| P003 | Invalid Amount | Payment amount is invalid |
| A001 | Auth Failed | Authentication failed |
| A002 | Session Expired | User session has expired |