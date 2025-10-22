from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re

class MpesaTransactionBase(BaseModel):
    phone_number: str = Field(..., pattern=r"^254\d{9}$")
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    reference: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=255)

class MpesaTransactionCreate(MpesaTransactionBase):
    pass

class MpesaTransactionUpdate(BaseModel):
    checkout_request_id: str
    merchant_request_id: str
    result_code: str
    result_description: str
    status: str

class MpesaTransactionResponse(MpesaTransactionBase):
    id: int
    checkout_request_id: str
    merchant_request_id: Optional[str] = None
    status: str
    result_code: Optional[str] = None
    result_description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True