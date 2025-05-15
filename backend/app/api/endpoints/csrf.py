from fastapi import APIRouter, Request, Response
import secrets

# Create router without prefix - we'll add it in main.py
router = APIRouter()

@router.get("/csrf_token")
async def get_csrf_token(response: Response):
    """Generate a new CSRF token and set it as a cookie and in headers"""
    csrf_token = secrets.token_urlsafe(32)
    
    # Set cookie that matches frontend expectations
    response.set_cookie(
        key="XSRF-TOKEN",
        value=csrf_token,
        httponly=False,  # Allow JavaScript to read
        secure=False,    # Set to True in production with HTTPS
        samesite="lax",  # Protect against CSRF while allowing navigation
        max_age=3600,    # 1 hour expiration
        path="/"
    )
    # Also include the token in the response header
    response.headers["X-CSRFToken"] = csrf_token    
        
    return {"csrf_token": csrf_token}