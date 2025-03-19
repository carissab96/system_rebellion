from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import secrets

def setup_middleware(app: FastAPI):
    # Session middleware
    app.add_middleware(
        SessionMiddleware, 
        secret_key=secrets.token_hex(32),
        session_cookie_name="system_rebellion_session"
    )
    
    # Trusted Host middleware
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["localhost", "127.0.0.1", "*.system-rebellion.com"]
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Frontend dev server
            "https://system-rebellion.com"  # Production domain
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "X-CSRFToken"]
    )