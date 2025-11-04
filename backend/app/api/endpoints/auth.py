from posix import EX_TEMPFAIL
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Header, Body
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Union, Optional
from datetime import datetime, timezone, timedelta
import uuid
import logging
import secrets
import platform
import asyncio

from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_current_user   
from app.core.database import get_db, get_async_db, get_auth_db
from app.core.cache import auth_cache
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.token import Token
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, SECRET_KEY, ALGORITHM
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.config import get_settings

from app.services.system_log_service import LogService
from sqlalchemy.ext.asyncio import AsyncSession
import time
import json

# Define a simple UserProfileCreate if it doesn't exist in your schemas
from pydantic import BaseModel

class UserProfileCreate(BaseModel):
    """
    The Meth Snail's Profile Creation Schema
    """
    # Add any fields you need, or leave it empty
    pass

class OnboardingConfigurationData(BaseModel):
    """
    Schema for onboarding configuration data
    """
    system_name: str
    operating_system: str
    cpu_cores: int
    ram_gb: int
    storage_gb: int
    primary_use_case: str
    monitoring_preferences: dict
    agent_preferences: dict

router = APIRouter()

@router.get("/csrf_token")
async def get_csrf_token(response: Response):
    """
    Sir Hawkington's CSRF Token Generation Protocol
    The Quantum Shadow People shall not interfere!
    """
    # Generate a new CSRF token
    csrf_token = secrets.token_urlsafe(32)
    
    # Set CSRF token as a cookie
    response.set_cookie(
        key="XSRF-TOKEN", 
        value=csrf_token, 
        httponly=False,  # Allow JavaScript access for form submissions
        secure=False,    # Set to True in production
        samesite='lax'   # CSRF protection
    )
    
    return {
        "XSRF-TOKEN": csrf_token
    }
@router.post("/refresh-token", response_model=Dict[str, str])
async def refresh_access_token(
    request: Request,
    x_refresh_token: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Sir Hawkington's Token Refresh Protocol
    Refreshes an expired access token using the refresh token.
    """
    logging.info(f"🔄 Refresh token request received. Headers: {request.headers}")
    
    # Try to get token from header or request body
    refresh_token = x_refresh_token
    
    if not refresh_token:
        # Try to get from request body
        try:
            body = await request.json()
            refresh_token = body.get('refresh_token')
        except:
            pass
    
    if not refresh_token:
        logging.error("❌ No refresh token provided in headers or body")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        logging.info(f"🔍 Decoding refresh token")
        # Decode the refresh token
        payload = jwt.decode(
            refresh_token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM]
        )
        email = payload.get("sub")
        
        if not email:
            logging.error("❌ No email in token payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token - no email",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        logging.info(f"👤 Looking up user: {email}")
        # Find the user
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user:
            logging.error(f"❌ User not found: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        if not user.is_active:
            logging.error(f"❌ User inactive: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        logging.info(f"🔑 Generating new access token for {email}")
        # Generate a new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        logging.info(f"✅ Token refresh successful for {email}")
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except JWTError as e:
        logging.error(f"❌ JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logging.error(f"❌ Unexpected error in refresh_token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing refresh token: {str(e)}"
        )

async def is_async_session(session) -> bool:
    """Check if the session is async or not"""
    return isinstance(session, AsyncSession)

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
    db: Union[Session, AsyncSession] = Depends(get_auth_db)  # Use dedicated auth pool
):
    """
    User Registration Endpoint
    
    Sir Hawkington welcomes you to the System Rebellion!
    The Meth Snail prepares your optimization credentials.
    """
    try:
        logging.info(f"🚀 Registration attempt for user: {user_data.email}")
        logging.info(f"🔍 Database session type: {type(db)}")
        
        # Check if user already exists
        if await is_async_session(db):
            result = await db.execute(select(User).where(User.email == user_data.email))
            existing_user = result.scalar_one_or_none()
        else:
            existing_user = db.query(User).filter(User.email == user_data.email).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create new user
        user_id = str(uuid.uuid4())
        logging.info(f"🆔 Generated user ID: {user_id}")
        
        hashed_password = hash_password(user_data.password)
        logging.info(f"🔒 Password hashed successfully")
        
        logging.info(f"👤 Creating user object for: {user_data.email}")
        new_user = User(
            id=user_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            company_name=user_data.company_name,
            job_title=user_data.job_title,
            hashed_password=hashed_password,
            is_active=True,
            is_onboarded=False,  
            created_at=datetime.now(timezone.utc)
        )
        
        # Save user to database
        logging.info(f"💾 Adding user to database session")
        db.add(new_user)
        
        logging.info(f"💾 Committing transaction")
        if await is_async_session(db):
            logging.info("🔄 Using async commit")
            await db.commit()
            await db.refresh(new_user)
        else:
            logging.info("🔄 Using sync commit")
            db.commit()
            db.refresh(new_user)
        
        logging.info(f"✅ User created successfully: {new_user.id}")
        
        # Generate tokens for immediate login
        access_token = create_access_token(
            data={"sub": new_user.email, "user_id": new_user.id}
        )
        
        refresh_token = create_refresh_token(
            data={"sub": new_user.email}
        )
        
        logging.info(f"🎟️ Tokens generated successfully")
        
        # Return user data with tokens
        return {
            "user": {
                "id": new_user.id,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "company_name": new_user.company_name,
                "job_title": new_user.job_title,
                "is_active": new_user.is_active,
                "is_onboarded": new_user.is_onboarded, 
                "created_at": new_user.created_at
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        logging.error(f"❌ HTTPException in register_user: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"❌ Unexpected error in register_user: {str(e)}")
        logging.error(f"❌ Error type: {type(e)}")
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
            email="test@example.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        await save_user(db, test_user)
        
        return {"message": "Test user created successfully", "user_id": user_id}
    except Exception as e:
        if await is_async_session(db):
            await db.rollback()
        else:
            db.rollback()
        return {"error": str(e)}

class LoginRequest(BaseModel):
    username: str
    password: str
    grant_type: str = "password"

@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Union[Session, AsyncSession] = Depends(get_auth_db)  # Use dedicated auth pool
) -> Token:
    """
    The Meth Snail's Authentication Protocol
    Validates user credentials and returns access token
    """
    login_start = time.time()
    
    print(f"🔐 Login attempt for user: {form_data.username}")
    
    # Find the user directly from database (single query)
    db_query_start = time.time()
    if await is_async_session(db):
        result = await db.execute(select(User).where(User.email == form_data.username))
        user = result.scalar_one_or_none()
    else:
        user = db.query(User).filter(User.email == form_data.username).first()
    logging.info(f"⏱️ DB user lookup: {(time.time() - db_query_start)*1000:.2f}ms")
    
    if not user:
        logging.error(f"❌ User not found: {form_data.username}")
        # Log failed attempt in background (non-blocking)
        async def log_auth_failure():
            try:
                log_service = await LogService.get_instance()
                log_service.add_auth_log(email=form_data.username, success=False)
            except Exception as e:
                logging.warning(f"Failed to log auth failure: {e}")
        
        asyncio.create_task(log_auth_failure())
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logging.info(f"👤 User found: {user.email} (ID: {user.id})")
    
    # Validate password
    password_start = time.time()
    if not verify_password(form_data.password, user.hashed_password):
        logging.info(f"⏱️ Password verification: {(time.time() - password_start)*1000:.2f}ms")
        logging.error(f"❌ Invalid password for user: {user.email}")
        # Log failed attempt in background (non-blocking)
        async def log_auth_failure():
            try:
                log_service = await LogService.get_instance()
                log_service.add_auth_log(email=user.email, success=False)
            except Exception as e:
                logging.warning(f"Failed to log auth failure: {e}")
        
        asyncio.create_task(log_auth_failure())
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logging.info(f"⏱️ Password verification: {(time.time() - password_start)*1000:.2f}ms")
    
    # Create access token
    token_start = time.time()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": user.email})
    logging.info(f"⏱️ Token creation: {(time.time() - token_start)*1000:.2f}ms")
    
    # Log successful authentication in background (non-blocking)
    async def log_auth_success():
        try:
            log_service = await LogService.get_instance()
            log_service.add_auth_log(email=user.email, success=True)
        except Exception as e:
            logging.warning(f"Failed to log auth success: {e}")
    
    asyncio.create_task(log_auth_success())  # Run in background, don't wait
    
    # Update last login (prepare changes but don't wait for commit)
    user.failed_login_attempts = 0
    user.lockout_until = None
    user.last_login = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    # Don't auto-set is_onboarded - let the onboarding flow handle this
    
    # Flush changes to DB but don't wait for full commit (non-blocking)
    db_update_start = time.time()
    if await is_async_session(db):
        db.add(user)
        await db.flush()  # Write to DB without waiting for transaction commit
        # Commit happens in background when session closes
    else:
        db.add(user)
        db.flush()
    logging.info(f"⏱️ DB update flush: {(time.time() - db_update_start)*1000:.2f}ms")
    
    logging.info(f"✅ Total login time: {(time.time() - login_start)*1000:.2f}ms")
    
    def iso(dt):
        if not dt: return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    
    # Return token with user information
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_onboarded": user.is_onboarded,
            "is_active": user.is_active,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "last_login": datetime.now(timezone.utc),
            "failed_login_attempts": user.failed_login_attempts,
            "lockout_until": datetime.now(timezone.utc)
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
        test_email = f"test_{test_id[:8]}@example.com"
        test_password = hash_password("password123")
        
        logging.info(f"🧪 Creating test user: {test_email}")
        
        # Create test user
        test_user = User(
            id=test_id,
            email=test_email,
            hashed_password=test_password,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        # Add to session
        logging.info(f"🧪 Adding to database session")
        db.add(test_user)
        
        # Commit
        logging.info(f"🧪 Committing transaction")
        if await is_async_session(db):
            await db.commit()
            await db.refresh(test_user)
        else:
            db.commit()
            db.refresh(test_user)
        
        logging.info(f"🧪 Test user created: {test_id}")
        
        # Verify user exists
        logging.info(f"🧪 Verifying user exists")
        if await is_async_session(db):
            result = await db.execute(select(User).where(User.email == test_email))
            found_user = result.scalar_one_or_none()
        else:
            found_user = db.query(User).filter(User.email == test_email).first()
        
        if found_user:
            logging.info(f"✅ Test successful! User found: {found_user.id}")
            return {
                "success": True,
                "user_id": found_user.id,
                "email": found_user.email
            }
        else:
            logging.info(f"❌ Test failed! User not found after creation")
            return {
                "success": False,
                "error": "User not found after creation"
            }
    
    except Exception as e:
        logging.info(f"❌ Database test error: {str(e)}")
        import traceback
        logging.info(f"❌ Traceback: {traceback.format_exc()}")
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
        key="XSRF-TOKEN", 
        value=csrf_token, 
        httponly=False,  # Prevents JavaScript access
        secure=False,    # Only sent over HTTPS
        samesite='lax'  # Provides some protection against CSRF
    )
    
    from starlette.responses import JSONResponse
    return JSONResponse(
        content={
            "status": "operational",
            "XSRF-TOKEN": csrf_token
        }
    ) 

@router.get("/status/")
async def auth_status(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Sir Hawkington's Authentication Status Protocol
    The Quantum Shadow People shall not interfere!
    """
    try:
        # Log request headers for debugging
        logging.info(f"🧐 Auth status request headers: {request.headers}")
        
        # Extract token from Authorization header if present
        auth_header = request.headers.get('Authorization')
        is_authenticated = False
        email = None
        user_data = None
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            try:
                # Try to decode the token but don't fail if invalid
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                )
                email = payload.get("sub")
                is_authenticated = True
                logging.info(f"🧐 Token validated successfully for user: {email}")
                
                # If authenticated, fetch the user data
                if email:
                    try:
                        # Use sync_engine for user lookup to avoid async issues
                        from app.core.database import sync_engine
                        from sqlalchemy.orm import Session
                        
                        sync_session = Session(sync_engine)
                        try:
                            user = sync_session.query(User).filter(User.email == email).first()
                            if user:
                                user_data = {
                                    "id": str(user.id),
                                    "email": user.email,
                                    "first_name": user.first_name,
                                    "last_name": user.last_name,
                                    "company_name": user.company_name,
                                    "job_title": user.job_title,
                                    "operating_system": user.operating_system,
                                    "os_version": user.os_version,
                                    "cpu_cores": user.cpu_cores,
                                    "total_memory": user.total_memory,
                                    "is_onboarded": user.is_onboarded
                                }
                        finally:
                            sync_session.close()
                    except Exception as user_error:
                        logging.info(f"⚠️ Error fetching user data: {str(user_error)}")
            except Exception as e:
                logging.info(f"⚠️ Token validation failed: {str(e)}")
                # Don't fail the request, just note that auth failed
        
        response_data = {
            "status": "operational",
            "auth_service": "active",
            "is_authenticated": is_authenticated,
            "email": email,
            "timestamp": datetime.now(timezone.utc)
        }
        
        # Include user data if available
        if user_data:
            response_data["user"] = user_data
            
        return response_data
    except Exception as e:
        logging.info(f"❌ Auth status error: {str(e)}")
        # Return a 200 response even on error to prevent frontend issues
        return {
            "status": "operational",
            "auth_service": "active",
            "is_authenticated": False,
            "timestamp": datetime.now(timezone.utc)
        }

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    # Extract system info from system_profile JSON field
    system_profile = current_user.system_profile or {}
    
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "operating_system": system_profile.get("os_type"),
        "os_version": system_profile.get("os_version"),
        "cpu_cores": system_profile.get("cpu_cores"),
        "total_memory": system_profile.get("total_ram_gb"),
        "is_onboarded": current_user.is_onboarded
    }

from app.utils.agent_preferences import adjust_agent_preferences_for_system, adjust_monitoring_preferences_for_system

# Complete onboarding
@router.post("/complete-onboarding")
async def complete_onboarding(
    onboarding_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)  # Ensure we're using async DB
):
    """
    Complete user onboarding with all collected data.
    
    This endpoint applies system-adjusted defaults to agent and monitoring preferences
    based on the user's system profile before saving them.
    """
    try:
        # Start a transaction
        async with db.begin():
            # Get fresh user object from database
            result = await db.execute(select(User).where(User.id == current_user.id))
            user = result.scalars().first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
                
            # Update basic user info
            user.first_name = onboarding_data.get('first_name')
            user.last_name = onboarding_data.get('last_name')
            user.company_name = onboarding_data.get('company_name')
            user.job_title = onboarding_data.get('job_title')
            user.system_name = onboarding_data.get('system_name')
            
            # Get system profile from onboarding data
            system_profile = onboarding_data.get('system_profile', {})
            user.system_profile = system_profile
            
            # Apply system-adjusted defaults to agent preferences
            agent_prefs = onboarding_data.get('agent_preferences', {})
            user.agent_preferences = adjust_agent_preferences_for_system(
                user_preferences=agent_prefs,
                system_profile=system_profile
            )
            
            # Apply system-adjusted defaults to monitoring preferences
            monitoring_prefs = onboarding_data.get('monitoring_preferences', {})
            user.monitoring_preferences = adjust_monitoring_preferences_for_system(
                user_preferences=monitoring_prefs,
                system_profile=system_profile
            )
            
            # Track permissions and installation
            user.permissions_granted_at = datetime.now(timezone.utc)
            user.installation_method = onboarding_data.get('installation_method')
            user.is_onboarded = True
            
            # Add user to session and commit transaction
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # Initialize agent memory banks for this user
        # await initialize_agent_memories(user.id, db)
        
        return {
            "success": True,
            "user": user_to_dict(user),
            "next_steps": determine_next_steps(user),
            "message": "Onboarding completed successfully with system-optimized preferences"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
                # Log the full error for debugging
        logging.error(f"Error completing onboarding: {str(e)}", exc_info=True)
        # Return a user-friendly error message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while completing your onboarding. Please try again."
        )

def user_to_dict(user: User) -> dict:
    """Convert User object to dictionary for API response"""
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "company_name": user.company_name,
        "job_title": user.job_title,
        "system_name": user.system_name,
        "is_onboarded": user.is_onboarded,
        "system_profile": user.system_profile,
        "agent_preferences": user.agent_preferences,
        "monitoring_preferences": user.monitoring_preferences,
        "permissions_granted_at": user.permissions_granted_at if user.permissions_granted_at else None,
        "installation_method": user.installation_method,
        "created_at": user.created_at if user.created_at else None
    }

def determine_next_steps(user: User) -> dict:
    """Determine what the user should do next based on their profile"""
    steps = {
        "agent_installation": False,
        "limited_mode": False,
        "enterprise_setup": False,
        "immediate_monitoring": False
    }
    
    profile = user.system_profile or {}
    
    # Check if they need special setup
    if profile.get('admin_access') in ['none', 'limited']:
        steps['limited_mode'] = True
    elif profile.get('mdm_controlled') or profile.get('network_type') == 'enterprise':
        steps['enterprise_setup'] = True
    else:
        steps['immediate_monitoring'] = True
    
    # Check if agent is installed
    if not user.agent_installed:
        steps['agent_installation'] = True
    
    return steps

# Simple direct profile update endpoint that doesn't use the complex authentication
@router.post("/direct-profile-update/{email}")
async def direct_profile_update(
    email: str,
    profile_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Sir Hawkington's Direct Profile Update Protocol
    A simpler approach for updating profiles during onboarding
    """
    try:
        logging.info(f"🧐 Looking up user by email: {email}")
        logging.info(f"🧐 Request headers: {request.headers}")
        logging.info(f"🧐 Full profile data received: {profile_data}")
        
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            logging.info(f"🧐 Authorization header found")
            # Extract the token
            token = auth_header.replace('Bearer ', '')
            try:
                # Validate token - just check format, don't enforce user match for onboarding
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                )
                logging.info(f"🧐 Token validated successfully")
            except JWTError as e:
                logging.info(f"⚠️ Token validation failed: {str(e)}")
                # Continue anyway for onboarding - we're using email as identifier
        else:
            logging.info(f"⚠️ No valid Authorization header found")
        
        # Find the user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user:
            print(f"❌ User not found: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {email} not found"
            )
        
        print(f"🧐 Updating profile for user: {email}")
        
        # Initialize profile and preferences if they don't exist
        if not hasattr(user, 'profile') or user.profile is None:
            user.profile = {}
        
        if not hasattr(user, 'preferences') or user.preferences is None:
            user.preferences = {}
        
        # Check if we have a nested profile structure
        if "profile" in profile_data and isinstance(profile_data["profile"], dict):
            logging.info(f"🧐 Found nested profile data: {profile_data['profile']}")
            nested_profile = profile_data["profile"]
            
            # Update system information fields from nested profile
            system_fields = [
                "operating_system", "os_version", "cpu_cores", "total_memory", 
                "linux_distro", "linux_distro_version", "avatar"
            ]
            
            for field in system_fields:
                try:
                    if field in nested_profile and nested_profile[field] is not None:
                        print(f"🧐 Setting {field} = {nested_profile[field]}")
                        # Update the column in the database
                        setattr(user, field, nested_profile[field])
                        
                        # Also update the profile dictionary
                        user.profile[field] = nested_profile[field]
                except Exception as field_error:
                    logging.info(f"⚠️ Error setting field {field}: {str(field_error)}")
        else:
            # Handle direct fields in the root of profile_data
            system_fields = [
                "operating_system", "os_version", "cpu_cores", "total_memory", 
                "linux_distro", "linux_distro_version", "avatar"
            ]
            
            for field in system_fields:
                try:
                    if field in profile_data and profile_data[field] is not None:
                        print(f"🧐 Setting {field} = {profile_data[field]}")
                        setattr(user, field, profile_data[field])
                        # Also update the profile dictionary
                        user.profile[field] = profile_data[field]
                except Exception as field_error:
                    logging.info(f"⚠️ Error setting field {field}: {str(field_error)}")
        
        # Handle preferences if provided
        if "preferences" in profile_data and isinstance(profile_data["preferences"], dict):
            try:
                # Update preferences
                user.preferences.update(profile_data["preferences"])
                logging.info(f"🧐 Updated preferences: {user.preferences}")
            except Exception as pref_error:
                logging.info(f"⚠️ Error updating preferences: {str(pref_error)}")
        
        # Mark onboarding as completed
        user.is_onboarded = True
        logging.info(f"🧐 Onboarding completed for user: {email}")
        
        try:
            # Save changes to database
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logging.info(f"✅ Profile updated successfully for {email}")
        except Exception as commit_error:
            logging.info(f"❌ Error committing changes: {str(commit_error)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving profile changes: {str(commit_error)}"
            )
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "operating_system": user.operating_system,
                "os_version": user.os_version,
                "cpu_cores": user.cpu_cores,
                "total_memory": user.total_memory,
                "avatar": getattr(user, 'avatar', None),
                "is_onboarded": user.is_onboarded,
                "profile": user.profile,
                "preferences": user.preferences
            }
        }
    except Exception as e:
        logging.info(f"❌ Error updating profile: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

@router.post("/update-profile")
async def update_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Sir Hawkington's Profile Update Protocol
    The Meth Snail ensures your system details are recorded with aristocratic precision!
    """
    try:
        logging.info(f"🧐 Updating profile for user: {current_user.email}")
        logging.info(f"🧐 Profile data: {profile_data}")
        
        # Check if system_info is in the profile data (from onboarding)
        if "system_info" in profile_data:
            system_info = profile_data["system_info"]
            logging.info(f"🧐 System info: {system_info}")
            
            # Update the user's system information from nested structure
            if "operating_system" in system_info:
                current_user.operating_system = system_info["operating_system"]
            if "os_version" in system_info:
                current_user.os_version = system_info["os_version"]
            if "cpu_cores" in system_info:
                current_user.cpu_cores = system_info["cpu_cores"]
            if "total_memory" in system_info:
                current_user.total_memory = system_info["total_memory"]
        else:
            # Handle direct properties (from profile updates)
            if "operating_system" in profile_data:
                current_user.operating_system = profile_data["operating_system"]
            if "os_version" in profile_data:
                current_user.os_version = profile_data["os_version"]
            if "cpu_cores" in profile_data:
                current_user.cpu_cores = profile_data["cpu_cores"]
            if "total_memory" in profile_data:
                current_user.total_memory = profile_data["total_memory"]
        
        # Always mark onboarding as completed when profile data is updated
        # This ensures the user won't be redirected back to onboarding
        logging.info(f"🧐 Setting is_onboarded to True for user: {current_user.email}")
        current_user.is_onboarded = True
        
        # Save changes to database
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        
        logging.info(f"✅ Profile updated successfully for {current_user.email}")
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "operating_system": current_user.operating_system,
                "os_version": current_user.os_version,
                "cpu_cores": current_user.cpu_cores,
                "total_memory": current_user.total_memory,
                "is_onboarded": current_user.is_onboarded
            }
        }
    except Exception as e:
        logging.info(f"❌ Error updating profile: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )
        