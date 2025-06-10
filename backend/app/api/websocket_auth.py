"""
WebSocket authentication utilities for System Rebellion
"""
from fastapi import WebSocket, status
from jose import jwt, JWTError
from app.core.config import settings
from app.models.user import User
from sqlalchemy import select # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from sqlalchemy.engine.result import ScalarResult # type: ignore
from app.core.database import AsyncSessionLocal # type: ignore
import logging
from typing import Optional, cast, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar('T')

async def get_current_user_from_token(token: str) -> Optional[User]:
    """
    Validate JWT token and return the user
    """
    try:
        # Decode the JWT token
        logger.info(f"Decoding WebSocket token: {token[:10]}...")
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Extract the subject (username)
        username = cast(str, payload.get("sub"))
        if not username:
            logger.error("Token missing 'sub' field")
            return None
        logger.info(f"Token subject: {username}")

        # Get user from database
        async with AsyncSessionLocal() as db:  # type: ignore
            db_session: AsyncSession = db
            logger.info(f"Looking up user: {username}")
            stmt = select(User).where(User.username == username)  # type: ignore
            result = (await db_session.execute(stmt)).scalars()  # type: ignore
            user = result.first()  # type: ignore
                
            if not user:
                logger.error(f"User not found: {username}")
                return None
                
        # Create a detached copy of the user object
        detached_user = User(
            id=int(user.id),  # Ensure integer type
            username=cast(str, user.username),  # Use type.cast to ensure proper typing
            email=str(user.email),
            is_active=bool(user.is_active)
        )
        
        logger.info(f"User authenticated successfully: {detached_user.username}")
        return detached_user
                
    except JWTError as e:
        logger.error(f"JWT error in WebSocket: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error authenticating WebSocket: {str(e)}")
        return None

async def authenticate_websocket(websocket: WebSocket) -> Optional[User]:
    """
    Authenticate a WebSocket connection using JWT token
    """
    try:
        # First try to get token from query parameters
        token: Optional[str] = websocket.query_params.get("token")
        
        # If no token in query params, try headers
        if not token:
            auth_header = websocket.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        if not token:
            logger.warning("No token provided for WebSocket connection")
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": "No authentication token provided"
                })
            except Exception as e:
                logger.error(f"Failed to send error message: {str(e)}")
            finally:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        
        logger.debug(f"Authenticating WebSocket with token: {token[:10]}...")
        
        # Validate token and get user
        user = await get_current_user_from_token(token)
        
        if not user:
            logger.error("Invalid token for WebSocket connection")
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid or expired authentication token"
                })
            except Exception as e:
                logger.error(f"Failed to send error message: {str(e)}")
            finally:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        
        logger.info(f"WebSocket authenticated for user: {getattr(user, 'username')}")  # type: ignore
        return user
        
    except Exception as e:
        logger.error(f"WebSocket authentication error: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
