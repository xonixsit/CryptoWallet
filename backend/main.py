from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, schemas, crud
from database import SessionLocal, engine
from auth import create_access_token, verify_password, get_current_user
from datetime import timedelta

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Welcome to CryptoWallet API"}

class LoginData(BaseModel):
    username: str
    password: str

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    login_data: LoginData,
    db: Session = Depends(get_db)
):
    try:
        user = crud.get_user_by_email(db, email=login_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "balance": user.balance,
                "wallet_address": user.wallet_address,
                "referral_code": user.referral_code,
                "is_admin": user.is_admin
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/users/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        return crud.create_user(db=db, user=user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deposit/", response_model=schemas.TransactionResponse)
async def create_deposit(
    transaction: schemas.TransactionCreate,
    local_kw: bool = True,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        print("Received deposit request:", {
            "user_id": current_user.id,
            "amount": transaction.amount,
            "type": transaction.type,
            "local_kw": local_kw
        })
        
        # Convert type to proper enum value
        transaction_dict = transaction.dict()
        transaction_dict["type"] = models.TransactionType.DEPOSIT
        transaction_dict["status"] = models.TransactionStatus.PENDING
        
        result = crud.create_transaction(
            db=db,
            user_id=current_user.id,
            transaction=schemas.TransactionCreate(**transaction_dict)
        )
        
        return result
    except Exception as e:
        print("Deposit error:", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/withdraw/", response_model=schemas.TransactionResponse)
async def create_withdrawal(
    transaction: schemas.TransactionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    return crud.create_transaction(
        db=db,
        user_id=current_user.id,
        transaction=transaction
    )

@app.put("/admin/transactions/{transaction_id}/approve")
async def approve_transaction(
    transaction_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud.approve_transaction(db=db, transaction_id=transaction_id)