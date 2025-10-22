# In models/payment.py, update PaymentProvider enum

from enum import Enum

class PaymentProvider(Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    VISA_DIRECT = "visa_direct"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    CRYPTO = "crypto"