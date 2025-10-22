from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.services.mpesa import MpesaService
from app.services.mpesa_transaction import MpesaTransactionService
from app.deps import get_current_user, get_db
from app.models.payment_schemas.mpesa import (
    MpesaTransactionCreate,
    MpesaTransactionUpdate,
    MpesaTransactionResponse
)

router = APIRouter(prefix="/api/v1/payments/mpesa", tags=["mpesa"])

# Dependency to get MpesaService instance
def get_mpesa_service():
    return MpesaService()

class STKPushRequest(BaseModel):
    phone_number: str
    amount: float
    account_reference: str
    transaction_desc: str

class PaymentStatusRequest(BaseModel):
    checkout_request_id: str

@router.post("/stk-push", response_model=MpesaTransactionResponse)
async def initiate_stk_push(
    request: MpesaTransactionCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    mpesa_service: MpesaService = Depends(get_mpesa_service)
) -> Dict[str, Any]:
    """
    Initiate M-Pesa STK push payment
    """
    try:
        # Initialize transaction service
        transaction_service = MpesaTransactionService(db)
        
        # Format phone number (if not already in the correct format)
        phone_number = request.phone_number
        if not phone_number.startswith("254"):
            if phone_number.startswith("+"):
                phone_number = phone_number[1:]
            if phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
            elif not phone_number.startswith("254"):
                phone_number = "254" + phone_number

        # Initiate STK push
        result = mpesa_service.initiate_stk_push(
            phone_number=phone_number,
            amount=request.amount,
            account_reference=request.reference,
            transaction_desc=request.description
        )

        # Create transaction record
        transaction = transaction_service.create_transaction(
            transaction=request,
            checkout_request_id=result.get("CheckoutRequestID")
        )
        
        return transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/check-payment-status")
async def check_payment_status(
    request: PaymentStatusRequest,
    current_user = Depends(get_current_user),
    mpesa_service: MpesaService = Depends(get_mpesa_service)
) -> Dict[str, Any]:
    """
    Check M-Pesa payment status
    """
    try:
        result = mpesa_service.check_payment_status(
            checkout_request_id=request.checkout_request_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/callback")
async def mpesa_callback(
    payment_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    M-Pesa callback endpoint
    This endpoint will receive payment confirmation from Safaricom
    """
    try:
        transaction_service = MpesaTransactionService(db)
        
        # Extract relevant data from callback
        body = payment_data.get("Body", {}).get("stkCallback", {})
        checkout_request_id = body.get("CheckoutRequestID")
        merchant_request_id = body.get("MerchantRequestID")
        result_code = str(body.get("ResultCode"))
        result_desc = body.get("ResultDesc")
        
        # Determine transaction status
        status = "completed" if result_code == "0" else "failed"
        
        # Update transaction record
        transaction_update = MpesaTransactionUpdate(
            checkout_request_id=checkout_request_id,
            merchant_request_id=merchant_request_id,
            result_code=result_code,
            result_description=result_desc,
            status=status
        )
        
        transaction_service.update_transaction(
            checkout_request_id=checkout_request_id,
            transaction_update=transaction_update
        )
        
        return {"result_code": "0", "result_desc": "Success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))