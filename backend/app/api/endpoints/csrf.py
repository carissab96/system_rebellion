from fastapi import APIRouter, Request
from app.core.security import CSRFProtection

router = APIRouter()

@router.get("/csrf-token")
async def get_csrf_token(request: Request):
    """Endpoint to get CSRF token"""
    csrf = CSRFProtection()
    token = csrf.generate_csrf_token(request)
    
    # Set the token in a cookie as well for browsers that don't support JavaScript
    from fastapi.responses import JSONResponse
    response = JSONResponse({"csrf_token": token})
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=False,  # Allow JavaScript to read this cookie
        samesite="lax",  # Protect against CSRF while allowing navigation
        secure=False,    # Set to True in production with HTTPS
        max_age=3600     # 1 hour expiration
    )
    
    return response