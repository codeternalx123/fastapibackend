"""
Integration of quantum security and fraud detection with payment processing
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.core.quantum_security import PaymentSecurityManager
from app.services.fraud_detection import QuantumFraudDetection
from app.core.security import get_current_user
from app.models.schemas import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/secure-payments")

# Initialize security manager and fraud detection
security_manager = PaymentSecurityManager()
fraud_detector = QuantumFraudDetection()

@router.post("/process", response_model=PaymentResponse)
async def process_secure_payment(
    payment: PaymentCreate,
    current_user = Depends(get_current_user)
):
    """
    Process a payment with quantum-resistant security and fraud detection
    """
    try:
        # Enrich payment data with user and device info
        payment_data = payment.dict()
        payment_data.update({
            'user_id': current_user.id,
            'timestamp': datetime.now(),
            'device_info': payment.metadata.get('device_info', {})
        })
        
        # Run fraud detection
        fraud_analysis = fraud_detector.detect_fraud(payment_data)
        
        if fraud_analysis['is_fraudulent']:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "High fraud risk detected",
                    "fraud_analysis": fraud_analysis
                }
            )
        
        # Apply quantum-resistant security
        secured_payment = security_manager.secure_payment_data(payment_data)
        
        # Process the payment with the appropriate service
        if payment.provider == PaymentProvider.STRIPE:
            service = StripeService()
        elif payment.provider == PaymentProvider.PAYPAL:
            service = PayPalService()
        elif payment.provider == PaymentProvider.APPLE_PAY:
            service = ApplePayService()
        elif payment.provider == PaymentProvider.GOOGLE_PAY:
            service = GooglePayService()
        elif payment.provider == PaymentProvider.CRYPTO:
            service = CryptoPaymentService()
        else:
            raise ValueError(f"Unsupported payment provider: {payment.provider}")
        
        # Process payment with encrypted data
        result = await service.create_payment(
            amount=payment.amount,
            currency=payment.currency,
            payment_method_id=payment.payment_method_id,
            metadata={
                **payment.metadata or {},
                'secured_payment': secured_payment,
                'fraud_analysis': fraud_analysis
            }
        )
        
        # Update fraud detection model
        fraud_detector.update_model(payment_data, is_fraud=False)
        
        return PaymentResponse.from_orm(result)
        
    except Exception as e:
        # Log the error and update fraud detection if payment failed
        if isinstance(e, HTTPException):
            fraud_detector.update_model(payment_data, is_fraud=True)
        raise HTTPException(
            status_code=400,
            detail=f"Payment processing failed: {str(e)}"
        )

@router.post("/verify")
async def verify_payment(
    payment_id: str,
    secured_data: Dict[str, bytes],
    current_user = Depends(get_current_user)
):
    """
    Verify a secured payment using quantum-resistant verification
    """
    try:
        # Verify and decrypt payment data
        payment_data = security_manager.verify_and_decrypt_payment(secured_data)
        
        # Verify user authorization
        if payment_data.get('user_id') != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized payment verification attempt"
            )
        
        return {
            "status": "verified",
            "payment_data": payment_data
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Payment verification failed: {str(e)}"
        )

@router.post("/analyze-risk")
async def analyze_payment_risk(
    payment_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """
    Analyze payment risk using quantum-inspired fraud detection
    """
    try:
        # Enrich data with user info
        payment_data['user_id'] = current_user.id
        payment_data['timestamp'] = datetime.now()
        
        # Run fraud analysis
        fraud_analysis = fraud_detector.detect_fraud(payment_data)
        
        return {
            "risk_analysis": fraud_analysis,
            "recommendation": "proceed" if not fraud_analysis['is_fraudulent']
            else "block"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Risk analysis failed: {str(e)}"
        )