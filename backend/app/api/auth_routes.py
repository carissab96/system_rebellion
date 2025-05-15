# app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError  # Add this import
import secrets
from datetime import datetime, timedelta
import uuid
from app.core.database import get_async_db
from app.models.user import User
from app.schemas.user import UserCreate, UserProfileUpdate
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.auth import get_current_user, get_optional_user
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from pydantic import BaseModel
from app.core.config import settings  # Add this import

# Change this to include the prefix
router = APIRouter(prefix="/api/auth")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict

class StatusResponse(BaseModel):
    status: str
    auth_service: str
    is_authenticated: bool
    username: str = None
    timestamp: str

# Add model for refresh token request
class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Your existing register_user function
@router.post("/register", response_model=TokenResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    # Your existing code...
    """Register a new user and return access tokens."""
    # Check if user already exists
    result = await db.execute(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    )
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    # Create user with UUID
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
        created_at=datetime.now(),
        needs_onboarding=True  # New users need onboarding
    )
    
    # Save to database
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Generate tokens
    access_token = create_access_token(
        data={"sub": new_user.username, "user_id": new_user.id}
    )
    
    refresh_token = create_refresh_token(
        data={"sub": new_user.username, "user_id": new_user.id}
    )
    
    # Return user data with tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at.isoformat(),
            "needs_onboarding": new_user.needs_onboarding
        }
    }

# Your existing login_for_access_token function
@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_async_db)
):
    """Login with username/password and return access tokens."""
    # Find user
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    
    # Validate credentials
    if not user or not verify_password(form_data.password, user.hashed_password):
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
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    # Update last login
    user.last_login = datetime.now()
    db.add(user)
    await db.commit()
    
    # Return tokens and user data
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "needs_onboarding": user.needs_onboarding,
            "operating_system": user.operating_system,
            "os_version": user.os_version,
            "cpu_cores": user.cpu_cores,
            "total_memory": user.total_memory,
            "avatar": user.avatar,
            "profile": user.profile,
            "preferences": user.preferences
        }
    }

# Your existing auth_status function
@router.get("/status", response_model=StatusResponse)
async def auth_status(
    request: Request,
    user: User = Depends(get_optional_user)
):
    """Check authentication status without requiring valid auth."""
    return {
        "status": "operational",
        "auth_service": "active",
        "is_authenticated": user is not None,
        "username": user.username if user else None,
        "timestamp": datetime.now().isoformat()
    }

# Your existing update_user_profile function
@router.post("/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update user profile with validation."""
    try:
        # Update user profile fields
        if hasattr(profile_data, "profile") and profile_data.profile:
            # Create profile dict if it doesn't exist
            if not current_user.profile:
                current_user.profile = {}
                
            # Update system information
            system_fields = [
                "operating_system", "os_version", "cpu_cores", "total_memory", 
                "linux_distro", "linux_distro_version", "avatar"
            ]
            
            for field in system_fields:
                if hasattr(profile_data.profile, field) and getattr(profile_data.profile, field) is not None:
                    # Update DB column
                    if hasattr(current_user.profile, field):
                        setattr(current_user.profile, field, getattr(profile_data.profile, field))
                    
                    # Update profile dict
                    current_user.profile[field] = getattr(profile_data.profile, field)
        
        # Update preferences if provided
        if hasattr(profile_data, "preferences") and profile_data.preferences:
            if not current_user.preferences:
                current_user.preferences = {}
            
            # Update preferences dict with new values
            current_user.preferences.update(profile_data.preferences.model_dump(exclude_unset=True))
        
        # Mark onboarding as completed
        current_user.needs_onboarding = False
        
        # Save changes
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        
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
                "avatar": current_user.avatar,
                "needs_onboarding": current_user.needs_onboarding,
                "profile": current_user.profile,
                "preferences": current_user.preferences
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

# CSRF token - updated to match frontend expectations
@router.get("/csrf_token")
async def get_csrf_token(response: Response):
    """Generate a new CSRF token and set it as a cookie."""
    csrf_token = secrets.token_urlsafe(32)
    
    # Update cookie name and settings
    response.set_cookie(
        key="XSRF-TOKEN",  # Changed from "csrftoken" to match frontend
        value=csrf_token, 
        httponly=False,    # Changed to allow JavaScript access
        secure=True,
        samesite='lax'
    )
    
    return {"csrf_token": csrf_token}

# Your existing refresh_access_token function
@router.post("/refresh-token")
async def refresh_access_token(
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a new access token using a refresh token."""
    refresh_token = request.headers.get("X-Refresh-Token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )
    
    try:
        # Validate refresh token
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        
        # Get user
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate new access token
        access_token = create_access_token(data={"sub": username, "user_id": user.id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

# New login alias for frontend compatibility
@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    """Alias for /token endpoint for frontend compatibility."""
    return await login_for_access_token(form_data, db)

# New me endpoint
@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's information."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "needs_onboarding": current_user.needs_onboarding,
        "operating_system": current_user.operating_system,
        "os_version": current_user.os_version,
        "cpu_cores": current_user.cpu_cores,
        "total_memory": current_user.total_memory,
        "avatar": current_user.avatar,
        "profile": current_user.profile,
        "preferences": current_user.preferences
    }

# New token validation endpoint
@router.get("/validate-token")
async def validate_token(current_user: User = Depends(get_current_user)):
    """Validate the current token and return success if valid."""
    return {
        "is_valid": True,
        "user_id": current_user.id,
        "username": current_user.username
    }

# Alternative refresh endpoint that takes token from request body
@router.post("/refresh")
async def refresh_token_alt(
    refresh_data: RefreshTokenRequest,  # Use Pydantic model for validation
    db: AsyncSession = Depends(get_async_db)
):
    """Alternative endpoint for token refresh that takes data from request body."""
    refresh_token = refresh_data.refresh_token
    
    try:
        # Validate refresh token
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        
        # Get user
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate new access token
        access_token = create_access_token(data={"sub": username, "user_id": user.id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

# Server-side logout endpoint
@router.post("/logout")
async def logout(current_user: User = Depends(get_optional_user)):
    """Server-side logout (optional).
    
    In a token-based auth system, the server doesn't need to do much for logout
    since the frontend will remove the tokens.
    """
    # You could implement token blacklisting here if needed
    return {"status": "success", "message": "Logged out successfully"}