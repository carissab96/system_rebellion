"""
WebSocket authentication utilities for System Rebellion
"""
import logging
import time
from typing import Optional, cast, Dict, Tuple

from fastapi import WebSocket, status
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings

from app.core.database import AsyncSessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)

class WebSocketAuthError(Exception):
    """Raised when WebSocket authentication fails."""
    pass

# User cache: {token: (User, expiry_timestamp)}
_user_cache: Dict[str, Tuple[User, float]] = {}
_CACHE_TTL = 300  # 5 minutes

async def get_current_user_from_token(token: str) -> User:
    """
    Validate JWT token and return a *detached* User.
    FAILS LOUDLY: raises WebSocketAuthError on any failure.
    Uses in-memory cache to avoid repeated DB lookups.
    """
    start_time = time.time()
    
    if not token:
        raise WebSocketAuthError("No authentication token provided")

    # Check cache first
    now = time.time()
    if token in _user_cache:
        cached_user, expiry = _user_cache[token]
        if now < expiry:
            logger.debug("✅ User cache hit (%.3fms)", (time.time() - start_time) * 1000)
            return cached_user
        else:
            # Expired, remove from cache
            del _user_cache[token]
            logger.debug("🗑️ Expired cache entry removed")

    try:
        # Add 5 minute leeway to tolerate clock skew between machines
        payload = jwt.decode(
            token,
            get_settings().SECRET_KEY,
            algorithms=[get_settings().ALGORITHM],
            options={"verify_exp": True, "leeway": 300}  # 5 minutes tolerance for clock skew
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

    # Lookup user from database
    db_start = time.time()
    try:
        async with AsyncSessionLocal() as db:
            db_session: AsyncSession = db
            stmt = select(User).where(User.email == email)
            result = (await db_session.execute(stmt)).scalars()
            user = result.first()
        logger.debug("📊 DB lookup took %.3fms", (time.time() - db_start) * 1000)
    except Exception as e:
        logger.error("Database error during user lookup: %s", str(e), exc_info=True)
        raise WebSocketAuthError("Authentication store unavailable") from e

    if not user:
        raise WebSocketAuthError(f"User not found: {email}")

    # Optional: enforce active flag if present
    if hasattr(user, "is_active") and not bool(getattr(user, "is_active")):
        raise WebSocketAuthError(f"User is inactive: {email}")

    # Return a detached copy to avoid lazy-load usage in WS handlers
    detached_user = User(
        id=str(user.id),
        email=cast(str, user.email),
        is_active=bool(user.is_active),
    )
    
    # Cache the user
    _user_cache[token] = (detached_user, now + _CACHE_TTL)
    logger.debug("💾 Cached user for token (total: %.3fms)", (time.time() - start_time) * 1000)
    
    return detached_user

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
