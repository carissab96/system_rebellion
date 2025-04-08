from fastapi import APIRouter, Depends, HTTPException, status, Form, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Union, Optional
import inspect
import secrets
from datetime import datetime, timedelta
import uuid
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_current_user   
from app.core.database import get_db, get_async_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES

# Define a simple UserProfileCreate if it doesn't exist in your schemas
from pydantic import BaseModel

class UserProfileCreate(BaseModel):
    """
    The Meth Snail's Profile Creation Schema
    """
    # Add any fields you need, or leave it empty
    pass

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

@router.post("/register", response_model=Dict)
async def register_user(
    user_data: UserCreate,
    db: Union[Session, AsyncSession] = Depends(get_db)
):
    """
    User Registration Endpoint
    
    Sir Hawkington welcomes you to the System Rebellion!
    The Meth Snail prepares your optimization credentials.
    """
    try:
        print(f"🚀 Registration attempt for user: {user_data.username}")
        print(f"🔍 Database session type: {type(db)}")
        # Check if user already exists
        existing_user = await find_user_by_username_or_email(
            db, 
            username=user_data.username, 
            email=user_data.email
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Create new user
     # Create new user
        user_id = str(uuid.uuid4())
        print(f"🆔 Generated user ID: {user_id}")
        
        hashed_password = hash_password(user_data.password)
        print(f"🔒 Password hashed successfully")
        
        print(f"👤 Creating user object for: {user_data.username}")
        new_user = User(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.now()
        )
        
         # Save user to database
        print(f"💾 Adding user to database session")
        db.add(new_user)
        
        print(f"💾 Committing transaction")
        if await is_async_session(db):
            print("🔄 Using async commit")
            await db.commit()
            await db.refresh(new_user)
        else:
            print("🔄 Using sync commit")
            db.commit()
            db.refresh(new_user)
        
        print(f"✅ User created successfully: {new_user.id}")
        
        # Generate tokens for immediate login
        access_token = create_access_token(
            data={"sub": new_user.username, "user_id": new_user.id}
        )
        
        refresh_token = create_refresh_token(
            data={"sub": new_user.username, "user_id": new_user.id}
        )
        
        print(f"🎟️ Tokens generated successfully")
        
        # Return user data with tokens
        return {
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "is_active": new_user.is_active,
                "created_at": new_user.created_at
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        print(f"❌ HTTPException in register_user: {e.detail}")
        raise e
    except Exception as e:
        print(f"❌ Unexpected error in register_user: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"The Meth Snail crashed during registration: {str(e)}"
        )
@router.post("/create-test-user")
async def create_test_user(db: Union[Session, AsyncSession] = Depends(get_db)):
    """
    Test User Creation Endpoint
    
    Sir Hawkington's debugging protocol!
    """
    try:
        user_id = str(uuid.uuid4())
        test_user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            created_at=datetime.now()
        )
        
        await save_user(db, test_user)
        
        return {"message": "Test user created successfully", "user_id": user_id}
    except Exception as e:
        if await is_async_session(db):
            await db.rollback()
        else:
            db.rollback()
        return {"error": str(e)}

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Union[Session, AsyncSession] = Depends(get_db)
) -> Dict[str, Any]:
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
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }
# Add this to a route to check your User model structure
@router.get("/debug/user-model")
def debug_user_model():
    """
    Sir Hawkington's Model Inspection Protocol
    """
    model_info = {
        "tablename": User.__tablename__,
        "columns": [
            {
                "name": column.name,
                "type": str(column.type),
                "nullable": column.nullable,
                "primary_key": column.primary_key,
                "default": str(column.default) if column.default else None
            }
            for column in User.__table__.columns
        ]
    }
    return model_info

@router.post("/debug/db-test")
async def test_database_operations(db: Union[Session, AsyncSession] = Depends(get_db)):
    """
    The Meth Snail's Database Testing Protocol
    """
    try:
        # Generate test data
        test_id = str(uuid.uuid4())
        test_username = f"test_user_{test_id[:8]}"
        test_email = f"test_{test_id[:8]}@example.com"
        test_password = hash_password("password123")
        
        print(f"🧪 Creating test user: {test_username}")
        
        # Create test user
        test_user = User(
            id=test_id,
            username=test_username,
            email=test_email,
            hashed_password=test_password,
            is_active=True,
            created_at=datetime.now()
        )
        
        # Add to session
        print(f"🧪 Adding to database session")
        db.add(test_user)
        
        # Commit
        print(f"🧪 Committing transaction")
        if await is_async_session(db):
            await db.commit()
            await db.refresh(test_user)
        else:
            db.commit()
            db.refresh(test_user)
        
        print(f"🧪 Test user created: {test_id}")
        
        # Verify user exists
        print(f"🧪 Verifying user exists")
        found_user = await find_user_by_username_or_email(db, username=test_username)
        
        if found_user:
            print(f"✅ Test successful! User found: {found_user.id}")
            return {
                "success": True,
                "user_id": found_user.id,
                "username": found_user.username
            }
        else:
            print(f"❌ Test failed! User not found after creation")
            return {
                "success": False,
                "error": "User not found after creation"
            }
    
    except Exception as e:
        print(f"❌ Database test error: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
@router.get("/debug/db-config")
async def debug_db_config():
    """
    Sir Hawkington's Database Configuration Inspection
    """
    from app.core.config import settings
    
    # Don't expose actual credentials
    db_config = {
        "database_type": settings.DATABASE_URL.split("://")[0] if hasattr(settings, "DATABASE_URL") else "unknown",
        "database_name": settings.DATABASE_URL.split("/")[-1] if hasattr(settings, "DATABASE_URL") else "unknown",
        "connection_pool_size": getattr(settings, "DATABASE_POOL_SIZE", "unknown"),
        "echo": getattr(settings, "DATABASE_ECHO", "unknown"),
    }
    
    return db_config

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
        "timestamp": datetime.now().isoformat()
    }
    
@router.post("/users/complete-onboarding")
async def complete_onboarding(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Update the user's onboarding status
    current_user.needs_onboarding = False
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return {"message": "Onboarding completed successfully"}