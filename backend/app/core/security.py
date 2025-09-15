# app/core/security.py  (or wherever this lives)

from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Request, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.config import get_settings
s=get_settings()
from app.core.database import get_async_db
from app.models.user import User  # adjust import if your model path differs

# ----- Config / crypto -----
SECRET_KEY = s.SECRET_KEY
ALGORITHM = s.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# TIP: long-term, prefer sub = user_id. For backward compatibility we still
# encode both for now. Keep this until you rotate tokens.
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
    user: Optional[User] = None

    # Preferred path: explicit user_id claim
    uid: Optional[str] = payload.get("user_id")
    if uid:
        user = await db.scalar(select(User).where(User.id == uid))

    # Fallback: infer from sub
    if user is None:
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Token missing subject")

        # heuristic: if it looks like a UUID, treat as id; if it has '@', treat as email
        found: Optional[User] = None
        try:
            uuid.UUID(str(sub))
            found = await db.scalar(select(User).where(User.id == str(sub)))
        except Exception:
            # not a UUID, try email
            if "@" in str(sub):
                found = await db.scalar(select(User).where(User.email == str(sub)))

        user = found

    if not user:
        raise HTTPException(status_code=401, detail="User not found for token subject")

    if getattr(user, "is_active", True) is False:
        raise HTTPException(status_code=403, detail="User is inactive")

    return user

# Public: use this in normal HTTP deps
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
) -> User:
    token = _extract_bearer(request)
    payload = decode_token(token)
    return await _lookup_user_by_claims(payload, db)

# Public: use this when you already have the raw token (e.g., WebSocket handshake)
async def get_current_user_from_token(
    token: str,
    db: AsyncSession = Depends(get_async_db),
) -> User:
    payload = decode_token(token)
    return await _lookup_user_by_claims(payload, db)
