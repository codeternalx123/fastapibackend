from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.models.database import Base

class MpesaTransaction(Base):
    __tablename__ = "mpesa_transactions"

    id = Column(Integer, primary_key=True, index=True)
    checkout_request_id = Column(String(100), unique=True, index=True)
    merchant_request_id = Column(String(100), index=True)
    phone_number = Column(String(15))
    amount = Column(Float)
    reference = Column(String(100))
    description = Column(String(255))
    status = Column(String(50))  # 'pending', 'completed', 'failed'
    result_code = Column(String(10))
    result_description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())