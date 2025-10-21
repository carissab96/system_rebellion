#  app/core/auth.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import get_settings
from app.core.database import get_async_db
from app.models.user import User
from typing import Optional
from app.core.cache import auth_cache

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
    token: str,
    db: AsyncSession = Depends(get_async_db)
) -> Optional[User]:
    """
    Validate authentication and return the current user.
    This is the main dependency for protected routes.
    """
    cached_user = await auth_cache.get(f"user:session:{token}")
    if cached_user:
        return json.loads(cached_user)

    # If not found in Redis, try to retrieve from database
    query = select(User).where(User.session_token == token)
    result = await db.execute(query)
    user = result.scalars().first()
    if user:
        # Cache the user in local cache to avoid further database queries
        await auth_cache.set(
            f"user:session:{token}", json.dumps(user.__dict__), ex=60 * 60
        )
    return user


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
            token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM]
        )
        email: str = payload.get("sub")
        if not email:
            return None
            
        result = await db.execute(select(User).where(User.email == email))
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
            token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )