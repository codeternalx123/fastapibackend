from sqlalchemy.orm import Session
from app.models.mpesa import MpesaTransaction
from app.models.payment_schemas.mpesa import MpesaTransactionCreate, MpesaTransactionUpdate

class MpesaTransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, transaction: MpesaTransactionCreate, checkout_request_id: str) -> MpesaTransaction:
        db_transaction = MpesaTransaction(
            checkout_request_id=checkout_request_id,
            **transaction.dict(),
            status="pending"
        )
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def update_transaction(self, checkout_request_id: str, transaction_update: MpesaTransactionUpdate) -> MpesaTransaction:
        db_transaction = (
            self.db.query(MpesaTransaction)
            .filter(MpesaTransaction.checkout_request_id == checkout_request_id)
            .first()
        )
        if db_transaction:
            for key, value in transaction_update.dict(exclude_unset=True).items():
                setattr(db_transaction, key, value)
            self.db.commit()
            self.db.refresh(db_transaction)
        return db_transaction

    def get_transaction(self, checkout_request_id: str) -> MpesaTransaction:
        return (
            self.db.query(MpesaTransaction)
            .filter(MpesaTransaction.checkout_request_id == checkout_request_id)
            .first()
        )