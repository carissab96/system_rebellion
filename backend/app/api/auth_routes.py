from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict

from core.database import get_db
from core.security import (
    create_access_token, 
    create_refresh_token, 
    get_password_reset_token
)
from services.auth_service import AuthService
from schemas.auth import UserCreate, UserProfileCreate, UserResponse
from models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserCreate,
    profile_data: UserProfileCreate = None,
    db: Session = Depends(get_db)
):
    """
    User Registration Endpoint
    
    Sir Hawkington welcomes you to the System Rebellion!
    The Meth Snail prepares your optimization credentials.
    """
    try:
        new_user = AuthService.create_user(db, user_data, profile_data)
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            is_active=new_user.is_active,
            created_at=new_user.created_at
        )
    except HTTPException as e:
        # The Quantum Shadow People tried to interfere
        raise e

@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    JWT Token Generation Endpoint
    
    Sir Hawkington's Distinguished Authentication Protocol
    The Meth Snail vibrates with token-generating energy!
    """
    user = AuthService.authenticate_user(
        db, 
        form_data.username, 
        form_data.password
    )
    
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }

@router.post("/token/refresh")
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Token Refresh Endpoint
    
    The Quantum Shadow People are denied access!
    Sir Hawkington regenerates your authentication credentials.
    """
    try:
        # Validate and decode refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token. Nice try, Quantum Shadow People!"
            )
        
        # Find user
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found. The Meth Snail is confused!"
            )
        
        # Generate new tokens
        new_access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        new_refresh_token = create_refresh_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed. Quantum Shadow People, GTFO!"
        )

@router.post("/password-reset/request")
def request_password_reset(email: str, db: Session = Depends(get_db)):
    """
    Password Reset Request Endpoint
    
    Sir Hawkington prepares the reset mechanism.
    The Meth Snail ensures secure password resurrection!
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Deliberately vague for security
        return {"message": "If the email exists, a reset link will be sent"}
    
    reset_token = get_password_reset_token(email)
    
    return {"message": "Password reset link sent. Check your email!"}

@router.post("/password-reset/confirm")
def confirm_password_reset(
    token: str, 
    new_password: str,
    db: Session = Depends(get_db)
):
    """
    Password Reset Confirmation Endpoint
    
    The Quantum Shadow People are DENIED!
    Sir Hawkington resets your credentials with distinguished precision.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token. Nice try, shadow people!"
            )
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. The Meth Snail is perplexed!"
            )
        
        # Update password
        user.hashed_password = hash_password(new_password)
        db.commit()
        
        return {"message": "Password reset successful. Welcome back, rebel!"}
    
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired or invalid. Quantum Shadow People, BEGONE!"
        )