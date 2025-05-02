from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import secrets

def setup_middleware(app: FastAPI):
    # Session middleware
    app.add_middleware(
        SessionMiddleware, 
        secret_key=secrets.token_hex(32)
        # session_cookie_name parameter might not be supported in this version
        # session_cookie_name="system_rebellion_session"
    )
    
    # Trusted Host middleware - disabled for testing
    # app.add_middleware(
    #     TrustedHostMiddleware, 
    #     allowed_hosts=["localhost", "127.0.0.1", "*.system-rebellion.com", "testserver"]
    # )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Frontend dev server
            "http://127.0.0.1:5173",  # Frontend dev server alternative URL
            "http://127.0.0.1:41585",  # Current browser preview URL
            "http://localhost:*",      # Any localhost port
            "http://127.0.0.1:*",     # Any 127.0.0.1 port
            "https://system-rebellion.com",  # Production domain
            "https://system-rebellion.onrender.com",  # Render domain
            "https://system-rebellion-api.onrender.com"  # Render API domain
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "X-CSRFToken", "Authorization"]
    )