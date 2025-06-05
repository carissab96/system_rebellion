"""
WebSocket authentication utilities for System Rebellion
"""
from fastapi import WebSocket, WebSocketDisconnect, status
from jose import jwt, JWTError
from app.core.config import settings
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)

async def get_current_user_from_token(token: str) -> User:
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
        username: str = payload.get("sub")
        if username is None:
            logger.error("Token missing 'sub' field")
            return None
        logger.info(f"Token subject: {username}")

    except Exception as e:
        logger.error(f"Error decoding WebSocket token: {str(e)}")
        return None
    
    try:
        async with AsyncSessionLocal() as db:
            logger.info(f"Looking up user: {username}")
            result = await db.execute(
                select(User).where(User.username == username)
            )
            user = result.scalars().first()
                
        if not user:
            logger.error(f"User not found: {username}")
            return None
                
        # Create a detached copy of the user object
        detached_user = User(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active
            )
                
        logger.info(f"User authenticated successfully: {detached_user.username}")
        return detached_user
                
    except Exception as db_error:
        logger.error(f"Database error during authentication: {str(db_error)}")
        return None
            
    except JWTError as e:
        logger.error(f"JWT error in WebSocket: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error authenticating WebSocket: {str(e)}")
        return None

async def authenticate_websocket(websocket: WebSocket) -> User:
    """
    Authenticate a WebSocket connection using JWT token
    """
    try:
        # First try to get token from query parameters
        query_params = dict(websocket.query_params)
        token = query_params.get("token")
        
        # If no token in query params, try headers
        if not token:
            headers = dict(websocket.headers)
            auth_header = headers.get("authorization")
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
        
        logger.info(f"WebSocket authenticated for user: {user.username}")
        return user
        
    except Exception as e:
        logger.error(f"WebSocket authentication error: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
