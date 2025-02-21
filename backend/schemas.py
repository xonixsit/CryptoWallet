from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from models import TransactionType, TransactionStatus

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    referral_code: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    wallet_address: str
    balance: float
    referral_code: str
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    amount: float
    type: str
    status: Optional[TransactionStatus] = TransactionStatus.PENDING

class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str