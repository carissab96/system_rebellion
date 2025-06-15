# Import and re-export the router from metrics_routes.py
from fastapi import APIRouter
from app.api.metrics_routes import router as metrics_router
from app.api.simplified_websocket_routes import router as websocket_router

# Create a main router
router = APIRouter()

# Include other routers
router.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
router.include_router(websocket_router, prefix="/ws", tags=["websockets"])
