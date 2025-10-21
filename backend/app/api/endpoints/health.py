from fastapi import APIRouter

router = APIRouter()

@router.get("/health-check")
async def health_check():
    """
    Health check endpoint for monitoring services like Render.
    Returns a simple 200 OK response to indicate the service is running.
    """
    return {"status": "ok", "message": "System Rebellion API is operational"}
