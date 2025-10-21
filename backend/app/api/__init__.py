# Import and re-export the router from metrics_routes.py
from fastapi import APIRouter
from app.api.metrics_routes import router as metrics_router
from app.api.simplified_websocket_routes import router as simplified_websocket_router
from app.api.minimal_websocket_routes import router as minimal_websocket_router
from app.api.system import router as system_router

# Create a main router
router = APIRouter()

# Include other routers
router.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
router.include_router(system_router, prefix="/system", tags=["system"])
router.include_router(simplified_websocket_router, prefix="/ws", tags=["websockets"])
router.include_router(minimal_websocket_router, prefix="/ws", tags=["websockets"])
