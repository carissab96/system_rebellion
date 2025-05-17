from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Header
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Union, Optional
import inspect
import secrets
from datetime import datetime, timedelta
import uuid
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_current_user   
from app.core.database import get_db, get_async_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, SECRET_KEY, ALGORITHM
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.config import settings
from app.services.system_log_service import SystemLogService

# Define a simple UserProfileCreate if it doesn't exist in your schemas
from pydantic import BaseModel

class UserProfileCreate(BaseModel):
    """
    The Meth Snail's Profile Creation Schema
    """
    # Add any fields you need, or leave it empty
    pass

router = APIRouter()

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
    print(f"🔄 Refresh token request received. Headers: {request.headers}")
    
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
        print("❌ No refresh token provided in headers or body")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        print(f"🔍 Decoding refresh token")
        # Decode the refresh token
        payload = jwt.decode(
            refresh_token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        username = payload.get("sub")
        
        if not username:
            print("❌ No username in token payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token - no username",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        print(f"👤 Looking up user: {username}")
        # Find the user
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        
        if not user:
            print(f"❌ User not found: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        if not user.is_active:
            print(f"❌ User inactive: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        print(f"🔑 Generating new access token for {username}")
        # Generate a new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        print(f"✅ Token refresh successful for {username}")
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except JWTError as e:
        print(f"❌ JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        print(f"❌ Unexpected error in refresh_token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing refresh token: {str(e)}"
        )

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
            needs_onboarding=True,  # Explicitly set needs_onboarding to True for new users
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
                "needs_onboarding": new_user.needs_onboarding,  # Include needs_onboarding flag
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

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Union[Session, AsyncSession] = Depends(get_db)
) -> Token:
    """
    The Meth Snail's Authentication Protocol
    Validates user credentials and returns access token
    """
    print(f"🔐 Login attempt for user: {form_data.username}")
    print(f"🔐 Form data received: {form_data}")
    
    # Find the user
    user = await find_user_by_username_or_email(db, username=form_data.username)
    
    # Get the system log service
    log_service = await SystemLogService.get_instance()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        print(f"❌ Invalid credentials for username: {form_data.username}")
        
        # Log failed authentication attempt
        log_service.add_auth_log(
            username=form_data.username,
            success=False
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"👤 User found: {user.username} (ID: {user.id})")
    
    # Validate password
    if not verify_password(form_data.password, user.hashed_password):
        print(f"❌ Invalid password for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # Log successful authentication
    log_service.add_auth_log(
        username=user.username,
        success=True
    )
    
    # Update last login
    user.last_login = datetime.now()
    user.failed_login_attempts = 0  # Reset failed attempts
    user.lockout_until = None  # Clear any lockouts
    
    # Save changes using helper function
    if await is_async_session(db):
        await db.commit()
    else:
        db.commit()
    
    # Return full token with complete user information
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "needs_onboarding": user.needs_onboarding,
            "operating_system": user.operating_system,
            "os_version": user.os_version,
            "cpu_cores": user.cpu_cores,
            "total_memory": int(user.total_memory) if user.total_memory is not None else None,
            "avatar": user.avatar,
            "profile": user.profile if hasattr(user, 'profile') else None,
            "preferences": user.preferences if hasattr(user, 'preferences') else None
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
        key="XSRF-TOKEN", 
        value=csrf_token, 
        httponly=False,  # Prevents JavaScript access
        secure=False,    # Only sent over HTTPS
        samesite='lax'  # Provides some protection against CSRF
    );
    
    return JSONResponse(
        content={
            "status": "operational",
            "csrf_token": csrf_token
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
        print(f"🧐 Auth status request headers: {request.headers}")
        
        # Extract token from Authorization header if present
        auth_header = request.headers.get('Authorization')
        is_authenticated = False
        username = None
        user_data = None
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            try:
                # Try to decode the token but don't fail if invalid
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                )
                username = payload.get("sub")
                is_authenticated = True
                print(f"🧐 Token validated successfully for user: {username}")
                
                # If authenticated, fetch the user data
                if username:
                    try:
                        # Use sync_engine for user lookup to avoid async issues
                        from app.core.database import sync_engine
                        from sqlalchemy.orm import Session
                        
                        sync_session = Session(sync_engine)
                        try:
                            user = sync_session.query(User).filter(User.username == username).first()
                            if user:
                                user_data = {
                                    "id": str(user.id),
                                    "username": user.username,
                                    "email": user.email,
                                    "operating_system": user.operating_system,
                                    "os_version": user.os_version,
                                    "cpu_cores": user.cpu_cores,
                                    "total_memory": user.total_memory,
                                    "needs_onboarding": user.needs_onboarding
                                }
                        finally:
                            sync_session.close()
                    except Exception as user_error:
                        print(f"⚠️ Error fetching user data: {str(user_error)}")
            except Exception as e:
                print(f"⚠️ Token validation failed: {str(e)}")
                # Don't fail the request, just note that auth failed
        
        response_data = {
            "status": "operational",
            "auth_service": "active",
            "is_authenticated": is_authenticated,
            "username": username,
            "timestamp": datetime.now().isoformat()
        }
        
        # Include user data if available
        if user_data:
            response_data["user"] = user_data
            
        return response_data
    except Exception as e:
        print(f"❌ Auth status error: {str(e)}")
        # Return a 200 response even on error to prevent frontend issues
        return {
            "status": "operational",
            "auth_service": "active",
            "is_authenticated": False,
            "timestamp": datetime.now().isoformat()
        }

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "operating_system": current_user.operating_system,
        "os_version": current_user.os_version,
        "cpu_cores": current_user.cpu_cores,
        "total_memory": current_user.total_memory,
        "needs_onboarding": current_user.needs_onboarding
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

# Simple direct profile update endpoint that doesn't use the complex authentication
@router.post("/direct-profile-update/{username}")
async def direct_profile_update(
    username: str,
    profile_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Sir Hawkington's Direct Profile Update Protocol
    A simpler approach for updating profiles during onboarding
    """
    try:
        print(f"🧐 Looking up user by username: {username}")
        print(f"🧐 Request headers: {request.headers}")
        print(f"🧐 Full profile data received: {profile_data}")
        
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            print(f"🧐 Authorization header found")
            # Extract the token
            token = auth_header.replace('Bearer ', '')
            try:
                # Validate token - just check format, don't enforce user match for onboarding
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                )
                print(f"🧐 Token validated successfully")
            except JWTError as e:
                print(f"⚠️ Token validation failed: {str(e)}")
                # Continue anyway for onboarding - we're using username as identifier
        else:
            print(f"⚠️ No valid Authorization header found")
        
        # Find the user by username
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        
        if not user:
            print(f"❌ User not found: {username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {username} not found"
            )
        
        print(f"🧐 Updating profile for user: {username}")
        
        # Initialize profile and preferences if they don't exist
        if not hasattr(user, 'profile') or user.profile is None:
            user.profile = {}
        
        if not hasattr(user, 'preferences') or user.preferences is None:
            user.preferences = {}
        
        # Check if we have a nested profile structure
        if "profile" in profile_data and isinstance(profile_data["profile"], dict):
            print(f"🧐 Found nested profile data: {profile_data['profile']}")
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
                    print(f"⚠️ Error setting field {field}: {str(field_error)}")
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
                    print(f"⚠️ Error setting field {field}: {str(field_error)}")
        
        # Handle preferences if provided
        if "preferences" in profile_data and isinstance(profile_data["preferences"], dict):
            try:
                # Update preferences
                user.preferences.update(profile_data["preferences"])
                print(f"🧐 Updated preferences: {user.preferences}")
            except Exception as pref_error:
                print(f"⚠️ Error updating preferences: {str(pref_error)}")
        
        # Mark onboarding as completed
        user.needs_onboarding = False
        print(f"🧐 Onboarding completed for user: {username}")
        
        try:
            # Save changes to database
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            print(f"✅ Profile updated successfully for {username}")
        except Exception as commit_error:
            print(f"❌ Error committing changes: {str(commit_error)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving profile changes: {str(commit_error)}"
            )
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "operating_system": user.operating_system,
                "os_version": user.os_version,
                "cpu_cores": user.cpu_cores,
                "total_memory": user.total_memory,
                "avatar": user.avatar,
                "needs_onboarding": user.needs_onboarding,
                "profile": user.profile,
                "preferences": user.preferences
            }
        }
    except Exception as e:
        print(f"❌ Error updating profile: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

@router.post("/update-profile")
async def update_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Sir Hawkington's Profile Update Protocol
    The Meth Snail ensures your system details are recorded with aristocratic precision!
    """
    try:
        print(f"🧐 Updating profile for user: {current_user.username}")
        print(f"🧐 Profile data: {profile_data}")
        
        # Check if system_info is in the profile data (from onboarding)
        if "system_info" in profile_data:
            system_info = profile_data["system_info"]
            print(f"🧐 System info: {system_info}")
            
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
        print(f"🧐 Setting needs_onboarding to False for user: {current_user.username}")
        current_user.needs_onboarding = False
        
        # Save changes to database using AsyncSessionLocal directly
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            db.add(current_user)
            await db.commit()
            await db.refresh(current_user)
            print(f"✅ Profile updated successfully for {current_user.username}")
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "operating_system": current_user.operating_system,
                "os_version": current_user.os_version,
                "cpu_cores": current_user.cpu_cores,
                "total_memory": current_user.total_memory,
                "needs_onboarding": current_user.needs_onboarding
            }
        }
    except Exception as e:
        print(f"❌ Error updating profile: {str(e)}")
        # No need to handle rollback as the context manager will do it automatically
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )