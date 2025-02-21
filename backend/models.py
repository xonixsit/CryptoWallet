from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    REFERRAL = "referral"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    wallet_address = Column(String, unique=True)
    balance = Column(Float, default=0.0)
    referral_code = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    
    transactions = relationship("Transaction", back_populates="user")
    referrals = relationship(
        "Referral",
        foreign_keys="[Referral.referrer_id]",
        back_populates="referrer"
    )

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(TransactionType))
    amount = Column(Float)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="transactions")

class Referral(Base):
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referred_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    referrer = relationship(
        "User",
        foreign_keys=[referrer_id],
        back_populates="referrals"
    )
    referred = relationship(
        "User",
        foreign_keys=[referred_id],
        backref="referred_by"
    )

class PromotionalBanner(Base):
    __tablename__ = "promotional_banners"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    image_url = Column(String)
    link = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)