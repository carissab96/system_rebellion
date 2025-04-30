#  app/core/auth.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.database import get_async_db
from app.models.user import User
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

async def get_token_from_request(request: Request) -> Optional[str]:
    """Extract token from Authorization header or cookie."""
    # Try header first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "")
    
    # Fall back to cookie
    token = request.cookies.get("access_token")
    return token

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """
    Validate authentication and return the current user.
    This is the main dependency for protected routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Get user from database
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        
        if user is None:
            raise credentials_exception
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account"
            )
            
        return user
        
    except JWTError:
        raise credentials_exception

async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db)
) -> Optional[User]:
    """
    Try to get the current user but don't fail if no valid auth is present.
    Useful for endpoints that work with or without authentication.
    """
    try:
        token = await get_token_from_request(request)
        if not token:
            return None
            
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if not username:
            return None
            
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        return user
    except:
        return None

async def validate_token(token: str) -> dict:
    """
    Validate a token and return the payload.
    Raises an exception if token is invalid.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )