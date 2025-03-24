from fastapi import APIRouter, Depends, HTTPException, status, Form, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Union, Optional
import inspect
import secrets
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_db, get_async_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from datetime import timedelta
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

async def is_async_session(session) -> bool:
    """Check if the session is async or not"""
    return hasattr(session, "execute") and inspect.iscoroutinefunction(session.execute)

async def find_user_by_username_or_email(db, username=None, email=None):
    """Find a user by username or email, handling both async and sync sessions"""
    if await is_async_session(db):
        # Async session
        query = select(User)
        if username and email:
            query = query.where((User.username == username) | (User.email == email))
        elif username:
            query = query.where(User.username == username)
        elif email:
            query = query.where(User.email == email)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    else:
        # Sync session
        query = db.query(User)
        if username and email:
            return query.filter((User.username == username) | (User.email == email)).first()
        elif username:
            return query.filter(User.username == username).first()
        elif email:
            return query.filter(User.email == email).first()
        return None

async def save_user(db, user):
    """Save a user to the database, handling both async and sync sessions"""
    db.add(user)
    
    if await is_async_session(db):
        await db.commit()
        await db.refresh(user)
    else:
        db.commit()
        db.refresh(user)
    
    return user

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db = Depends(get_db)):
    # Check if user exists
    existing_user = await find_user_by_username_or_email(
        db, username=user.username, email=user.email
    )
    
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password
    )
    
    # Save the user
    await save_user(db, db_user)
    
    return db_user

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)) -> Dict[str, Any]:
    """
    The Meth Snail's Authentication Protocol
    Validates user credentials and returns access token
    """
    # Find the user
    user = await find_user_by_username_or_email(db, username=form_data.username)
    # Validate user and password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # Update last login
    user.last_login = datetime.now()
    user.failed_login_attempts = 0  # Reset failed attempts
    user.lockout_until = None  # Clear any lockouts
    
    # Save changes using helper function
    if await is_async_session(db):
        await db.commit()
    else:
        db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
@router.get("/health-check/")
async def health_check(response: Response):
    """
    Sir Hawkington's CSRF Token Generation Protocol
    The Quantum Shadow People shall not interfere!
    """
    # Generate a new CSRF token
    csrf_token = secrets.token_urlsafe(32)
    
    # Set CSRF token as a secure, HTTP-only cookie
    response.set_cookie(
        key="csrftoken", 
        value=csrf_token, 
        httponly=True,  # Prevents JavaScript access
        secure=True,    # Only sent over HTTPS
        samesite='lax'  # Provides some protection against CSRF
    )
    
    return JSONResponse(
        content={
            "status": "operational",
            "csrf_token": csrf_token
        }
    ) 

@router.get("/status/")
async def auth_status():
    """
    Sir Hawkington's Authentication Status Protocol
    The Quantum Shadow People shall not interfere!
    """
    return {
        "status": "operational",
        "auth_service": "active",
        "timestamp": datetime.utcnow().isoformat()
    }