from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Request, HTTPException
import os
from dotenv import load_dotenv
import secrets
import uuid

# Configuration
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Sir Hawkington's Distinguished Password Protection
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    """
    The Meth Snail's Password Verification Protocol
    Checks passwords with maximum optimization energy!
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # The Stick's Anxiety Management Protocol
        print(f"🚨 Password verification failed: {e}")
        return False

def get_password_hash(password: str):
    """
    Sir Hawkington's Password Hashing Mechanism
    Quantum-grade password protection with aristocratic precision!
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Token Generation with Quantum Shadow People Resistance
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire, 
        "jti": str(uuid.uuid4())  # Unique token identifier
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """
    Refresh Token Generation with Extra Fuck-You Security
    """
    return create_access_token(
        data, 
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

def decode_token(token: str):
    """
    Token Decoding with Quantum Shadow People Detection
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=401, 
            detail="The Quantum Shadow People have intercepted your token!"
        )

class CSRFProtection:
    def __init__(self, secret_key: str = None):
        """
        Sir Hawkington's CSRF Protection Mechanism
        """
        self.secret_key = secret_key or secrets.token_hex(16)
        self.token = None

    def generate_csrf_token(self, request: Request):
        """
        Generate a CSRF token with distinguished chaos
        The Meth Snail ensures maximum token randomness!
        """
        token = secrets.token_hex(32)
        request.session['csrf_token'] = token
        return token

    def validate_csrf_token(self, request: Request):
        """
        CSRF Token Validation with Quantum-Level Precision
        The Quantum Shadow People are DENIED ACCESS!
        """
        # Get token from header or form
        header_token = request.headers.get('X-CSRFToken')
        session_token = request.session.get('csrf_token')
        
        if not header_token or not session_token:
            raise HTTPException(
                status_code=403, 
                detail="CSRF token missing. Nice try, shadow people!"
            )
        
        if not secrets.compare_digest(header_token, session_token):
            raise HTTPException(
                status_code=403, 
                detail="Invalid CSRF token. The Meth Snail says NO!"
            )
        
        return True

def get_password_reset_token(email: str):
    """
    Password Reset Token Generation
    Sir Hawkington ensures maximum security with distinguished chaos!
    """
    return create_access_token(
        {"sub": email}, 
        expires_delta=timedelta(hours=1)
    )