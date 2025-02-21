from sqlalchemy.orm import Session
import models, schemas
from auth import get_password_hash
from fastapi import HTTPException
import uuid

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        wallet_address=str(uuid.uuid4()),
        referral_code=str(uuid.uuid4())[:8]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_transaction(db: Session, user_id: int, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(
        user_id=user_id,
        type=transaction.type,
        amount=transaction.amount
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def approve_transaction(db: Session, transaction_id: int):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction.status = models.TransactionStatus.APPROVED
    if transaction.type == models.TransactionType.DEPOSIT:
        transaction.user.balance += transaction.amount
    elif transaction.type == models.TransactionType.WITHDRAWAL:
        transaction.user.balance -= transaction.amount
    
    db.commit()
    db.refresh(transaction)
    return transaction