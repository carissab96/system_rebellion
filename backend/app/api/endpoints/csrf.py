from fastapi import APIRouter, Request
from app.core.security import CSRFProtection

router = APIRouter()

@router.get("/csrf-token")
async def get_csrf_token(request: Request):
    """Endpoint to get CSRF token"""
    csrf = CSRFProtection()
    token = csrf.generate_csrf_token(request)
    return {"csrf_token": token}