import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database_schema import SessionLocal, StudentProfile

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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
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

    db = SessionLocal()
    try:
        student = db.query(StudentProfile).filter(StudentProfile.prn == prn).first()
    finally:
        db.close()

    if student is None:
        raise credentials_exception

    return {
        "prn": student.prn,
        "name": student.name,
        "email": student.email,
        "is_disadvantaged": student.is_disadvantaged,
        "has_disability": student.has_disability,
        "roles": _build_roles(student),
    }


def _build_roles(student):
    """Derive role list from DB role field + EOC eligibility flags."""
    roles = [student.role or "student"]
    if student.is_disadvantaged or student.has_disability:
        roles.append("eoc_eligible")
    return roles

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Academic SSO endpoint. Students use PCCOE email or PRN.
    Returns zero-knowledge JWT locking EOC capabilities.
    """
    db = SessionLocal()
    try:
        # Look up student by email or PRN
        student = db.query(StudentProfile).filter(
            (StudentProfile.email == form_data.username) | (StudentProfile.prn == form_data.username)
        ).first()
    finally:
        db.close()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect PCCOE ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password if the student has a password_hash set
    if student.password_hash and not verify_password(form_data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect PCCOE ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    roles = _build_roles(student)

    access_token = create_access_token(
        data={"sub": student.prn, "roles": roles}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_student)):
    """
    Returns the authenticated student's profile including roles.
    """
    return current_user
