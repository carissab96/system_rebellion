"""
WebSocket authentication utilities for System Rebellion
"""
import logging
from typing import Optional, cast

from fastapi import WebSocket, status
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)

class WebSocketAuthError(Exception):
    """Raised when WebSocket authentication fails."""
    pass

async def get_current_user_from_token(token: str) -> User:
    """
    Validate JWT token and return a *detached* User.
    FAILS LOUDLY: raises WebSocketAuthError on any failure.
    """
    if not token:
        raise WebSocketAuthError("No authentication token provided")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError as e:
        logger.warning("JWT decode error: %s", str(e))
        raise WebSocketAuthError("Invalid or expired authentication token") from e
    except Exception as e:
        logger.error("Unexpected error decoding JWT: %s", str(e), exc_info=True)
        raise WebSocketAuthError("Authentication processing error") from e

    email = cast(Optional[str], payload.get("sub"))
    if not email:
        raise WebSocketAuthError("Token missing required 'sub' claim")

    # Lookup user
    try:
        async with AsyncSessionLocal() as db:
            db_session: AsyncSession = db
            stmt = select(User).where(User.email == email)
            result = (await db_session.execute(stmt)).scalars()
            user = result.first()
    except Exception as e:
        logger.error("Database error during user lookup: %s", str(e), exc_info=True)
        raise WebSocketAuthError("Authentication store unavailable") from e

    if not user:
        raise WebSocketAuthError(f"User not found: {email}")

    # Optional: enforce active flag if present
    if hasattr(user, "is_active") and not bool(getattr(user, "is_active")):
        raise WebSocketAuthError(f"User is inactive: {email}")

    # Return a detached copy to avoid lazy-load usage in WS handlers
    return User(
        id=str(user.id),
        email=cast(str, user.email),
        is_active=bool(user.is_active),
    )

async def authenticate_websocket(websocket: WebSocket) -> User:
    """
    Authenticate a WebSocket connection using JWT token.
    On failure: send error, close socket with 1008, and RAISE WebSocketAuthError.
    """
    # Prefer token from query (?token=...), else Authorization: Bearer ...
    token: Optional[str] = websocket.query_params.get("token")
    if not token:
        auth_header = websocket.headers.get("authorization") or websocket.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]

    try:
        user = await get_current_user_from_token(token or "")
        logger.info("WebSocket authenticated for user: %s", getattr(user, "email", None))
        return user
    except WebSocketAuthError as e:
        # Tell the client *why* and then close loudly
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e),
                "code": "auth_failed",
            })
        except Exception:
            pass
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning("WebSocket auth failed: %s", str(e))
        raise
    except Exception as e:
        # Unexpected failure path
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Authentication error",
                "code": "auth_error",
            })
        except Exception:
            pass
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.error("WebSocket auth unexpected error: %s", str(e), exc_info=True)
        raise WebSocketAuthError("Authentication error") from e

async def authenticate_websocket_user_id(websocket: WebSocket) -> str:
    """
    Convenience wrapper: returns a stable identifier (email preferred, else id).
    RAISES WebSocketAuthError on failure (no None).
    """
    user = await authenticate_websocket(websocket)
    return cast(Optional[str], getattr(user, "email", None)) or str(getattr(user, "id", ""))
