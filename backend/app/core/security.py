# app/core/security.py  (or wherever this lives)

from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Request, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import logging
import hashlib

logger = logging.getLogger(__name__)
from redis.asyncio import Redis
from app.core.redis import get_redis_client
from app.core.config import get_settings
from app.core.database import get_async_db
from app.models.user import User  # adjust import if your model path differs

# ----- Config / crypto -----
SECRET_KEY = get_settings().SECRET_KEY
ALGORITHM = get_settings().ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = get_settings().REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _prepare_password(password: str) -> str:
    """
    Prepare password for bcrypt hashing.
    Bcrypt has a 72-byte limit. For passwords >72 bytes, pre-hash with SHA256.
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Pre-hash with SHA256 to stay under bcrypt's 72-byte limit
        return hashlib.sha256(password_bytes).hexdigest()
    return password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    import time
    start_time = time.time()
    try:
        prepared_password = _prepare_password(plain_password)
        result = pwd_context.verify(prepared_password, hashed_password)
        verify_time = time.time() - start_time
        logger.info(f"⏱️ Password verification: {verify_time:.2f}ms")
        return result
    except Exception as e:
        verify_time = time.time() - start_time
        logger.error(f"⏱️ Password verification failed after {verify_time:.2f}ms: {str(e)}")
        return False

def hash_password(password: str) -> str:
    prepared_password = _prepare_password(password)
    return pwd_context.hash(prepared_password)

# TIP: long-term, prefer sub = user_id. For backward compatibility we still
# encode both for now. Keep this until you rotate tokens.
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),
    })
    return jwt.encode(to_encode, get_settings().SECRET_KEY, algorithm=get_settings().ALGORITHM)

def create_refresh_token(data: dict) -> str:
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})

# ----- Bearer helpers -----
def _extract_bearer(request: Request) -> str:
    auth = request.headers.get("Authorization") or ""
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token", headers={"WWW-Authenticate": "Bearer"})
    return auth.split(" ", 1)[1].strip()

async def _lookup_user_by_claims(payload: dict, db: AsyncSession) -> User:
    """
    Supports both:
      - legacy: sub = email, optional user_id
      - preferred: sub = user_id (UUID/str)
    """
    import time
    start_time = time.time()

    user: Optional[User] = None

    # Preferred path: explicit user_id claim
    uid: Optional[str] = payload.get("user_id")
    if uid:
        lookup_start = time.time()
        user = await db.scalar(select(User).where(User.id == uid))
        lookup_time = time.time() - lookup_start
        logger.info(f"⏱️ User ID lookup: {lookup_time:.2f}ms (id: {uid[:8]}...)")

    # Fallback: infer from sub
    if user is None:
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Token missing subject")

        # heuristic: if it looks like a UUID, treat as id; if it has '@', treat as email
        found: Optional[User] = None

        lookup_start = time.time()
        try:
            uuid.UUID(str(sub))
            found = await db.scalar(select(User).where(User.id == str(sub)))
            lookup_type = "UUID"
        except Exception:
            # not a UUID, try email
            if "@" in str(sub):
                found = await db.scalar(select(User).where(User.email == str(sub)))
                lookup_type = "email"
            else:
                lookup_type = "unknown"

        lookup_time = time.time() - lookup_start
        logger.info(f"⏱️ Fallback {lookup_type} lookup: {lookup_time:.2f}ms (sub: {str(sub)[:8]}...)")

        user = found

    total_time = time.time() - start_time
    logger.info(f"⏱️ Total user lookup: {total_time:.2f}ms")

    if not user:
        raise HTTPException(status_code=401, detail="User not found for token subject")

    if getattr(user, "is_active", True) is False:
        raise HTTPException(status_code=403, detail="User is inactive")

    return user

# Public: use this in normal HTTP deps
def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
) -> User:
    token = _extract_bearer(request)
    payload = decode_token(token)
    return _lookup_user_by_claims(payload, db)

# Public: use this when you already have the raw token (e.g., WebSocket handshake)
def get_current_user_from_token(
    token: str,
    db: AsyncSession = Depends(get_async_db),
) -> User:
    payload = decode_token(token)
    return _lookup_user_by_claims(payload, db)
