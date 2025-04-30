from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload

# Fix the tokenUrl to match the actual endpoint in auth.py
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token"
)

async def get_db() -> Generator:
    async with AsyncSessionLocal() as db:
        yield db

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Log token info for debugging (don't log the full token in production)
        logger.info(f"Decoding token: {token[:10]}...")
        
        # Decode the JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        logger.info(f"Token payload decoded successfully")
        
        # Validate the token data
        token_data = TokenPayload(**payload)
        logger.info(f"Token subject: {token_data.sub}")
        
    except JWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
        )
    except ValidationError as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token payload: {str(e)}",
        )
    
    try:
        # Query for the user by username
        logger.info(f"Looking up user: {token_data.sub}")
        
        # Use a completely different approach to avoid ChunkedIteratorResult issues
        # Create a synchronous session and execute the query
        from sqlalchemy.orm import Session
        from app.core.database import sync_engine
        
        # Get a synchronous session
        sync_session = Session(sync_engine)
        try:
            # Execute the query synchronously
            user = sync_session.query(User).filter(User.username == token_data.sub).first()
            
            if not user:
                logger.error(f"User not found: {token_data.sub}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"User {token_data.sub} not found"
                )
                
            # Create a copy of the user object to return
            from copy import deepcopy
            user_copy = deepcopy(user)
            
            logger.info(f"User authenticated successfully: {user.username}")
            return user_copy
        finally:
            # Always close the session
            sync_session.close()
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}",
        )

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
