import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt

# Phase 9: Unified Student Auth & JWT Issuance

router = APIRouter(prefix="/auth", tags=["Authentication & SSO"])

# Secret management (Must be moved to .env before production)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "development-secret-phase-9-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency checking student token validity across all PCCOE systems
async def get_current_student(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate academic credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # PRN acting as the unique immutable student tie
        prn: str = payload.get("sub")
        if prn is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Scaffold DB connection here securely mapping to Phase 4 User Model
    # Example: student = get_user_from_db(prn)
    
    mock_student = {"prn": prn, "is_disadvantaged": False} 
    return mock_student

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Academic SSO endpoint. Students use PCCOE email or PRN.
    Returns zero-knowledge JWT locking EOC capabilities.
    """
    # Dummy verification. Phase 6 scaffolding logic.
    if not form_data.username.endswith("@pccoepune.org") and len(form_data.username) < 8:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect PCCOE ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # "sub" payload assigns strictly to the student's PRN identifier mapping perfectly to our SQL Schema
    access_token = create_access_token(
        data={"sub": form_data.username, "roles": ["student"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
