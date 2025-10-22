"""
Secure payment processing routes with quantum security
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime

from app.core.quantum_security import PaymentSecurityManager
from app.services.quantum_fraud_detection import QuantumFraudDetector
from app.deps import get_current_user
from app.models.schemas import PaymentCreate, PaymentResponse
from app.services.payment import PaymentProvider, PaymentFactory
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quantum-secure-payments")

# Initialize security and fraud detection
security_manager = PaymentSecurityManager()
fraud_detector = QuantumFraudDetector()

@router.post("/process", response_model=PaymentResponse)
async def process_secure_payment(
    payment: PaymentCreate,
    current_user = Depends(get_current_user)
):
    """
    Process a payment with quantum-enhanced security
    """
    try:
        # Enrich payment data
        payment_data = payment.dict()
        payment_data.update({
            'user_id': current_user.id,
            'timestamp': datetime.utcnow(),
            'device_info': payment.metadata.get('device_info', {}),
            'network_info': payment.metadata.get('network_info', {}),
            'location': payment.metadata.get('location', {})
        })
        
        # Run quantum-enhanced fraud detection
        fraud_analysis = fraud_detector.predict(payment_data)
        
        if fraud_analysis['is_fraudulent']:
            logger.warning(f"Fraud detected for payment: {payment_data}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "High fraud risk detected",
                    "risk_analysis": fraud_analysis
                }
            )
        
        # Apply quantum security measures
        secured_payment = security_manager.secure_transaction(
            payment_data,
            current_user.id
        )
        
        # Process payment with appropriate service
        service = PaymentFactory.get_service(payment.provider)
        
        result = await service.create_payment(
            amount=payment.amount,
            currency=payment.currency,
            payment_method_id=payment.payment_method_id,
            metadata={
                **(payment.metadata or {}),
                'secured_payment': secured_payment,
                'fraud_analysis': fraud_analysis
            }
        )
        
        # Update fraud detection model
        fraud_detector.update(payment_data, is_fraud=False)
        
        return PaymentResponse.from_orm(result)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            fraud_detector.update(payment_data, is_fraud=True)
            raise e
        
        logger.error(f"Payment processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Payment processing failed: {str(e)}"
        )

@router.post("/verify/{payment_id}")
async def verify_secure_payment(
    payment_id: str,
    secured_data: Dict[str, bytes],
    current_user = Depends(get_current_user)
):
    """
    Verify a secured payment
    """
    try:
        # Verify and decrypt payment data
        payment_data = security_manager.verify_transaction(
            secured_data,
            current_user.id
        )
        
        # Run additional fraud checks
        risk_analysis = fraud_detector.predict(payment_data)
        
        return {
            "status": "verified",
            "payment_data": payment_data,
            "risk_analysis": risk_analysis
        }
        
    except Exception as e:
        logger.error(f"Payment verification failed: {str(e)}")
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
    Analyze payment risk with quantum-enhanced detection
    """
    try:
        # Enrich data
        payment_data.update({
            'user_id': current_user.id,
            'timestamp': datetime.utcnow()
        })
        
        # Run quantum fraud detection
        risk_analysis = fraud_detector.predict(payment_data)
        
        return {
            "risk_analysis": risk_analysis,
            "recommendation": "proceed" if not risk_analysis['is_fraudulent']
            else "block",
            "quantum_enhanced": True
        }
        
    except Exception as e:
        logger.error(f"Risk analysis failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Risk analysis failed: {str(e)}"
        )