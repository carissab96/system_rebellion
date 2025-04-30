from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.database import async_engine as engine, Base
from app.core.middleware import setup_middleware
from app.api.endpoints import csrf
from app.api.endpoints import auth
from app.api.endpoints import optimization
from app.api.endpoints import configuration
from app.api.endpoints import alerts
from app.api.endpoints import auto_tuner
from app.api.endpoints import users
from app.api import router as metrics_router
# Import websocket routes
from app.api import websocket_routes
from datetime import datetime
import uvicorn

# Database initialization
async def init_db(db_engine=None):
    # Use provided engine or default to the global engine
    engine_to_use = db_engine or engine
    async with engine_to_use.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def init_db_sync(db_engine=None):
    """Synchronous version of init_db for testing"""
    engine_to_use = db_engine or engine
    with engine_to_use.begin() as conn:
        conn.run_sync(Base.metadata.create_all)

def create_application() -> FastAPI:
    # Create FastAPI app
    print("Available models in registry:", Base.registry._class_registry)
    app = FastAPI(
        title="System Rebellion",
        description="Quantum Optimization Platform",
        version="0.1.0"
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Add health-check endpoint
    @app.get("/health-check/")
    @app.get("/api/health-check/")
    async def health_check():
        """
        Sir Hawkington's Health Check Protocol
        The Quantum Shadow People shall not interfere!
        """
        return JSONResponse(
            content={
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "version": "0.1.0"
            }
        )
    
    # Register startup event to initialize database
    async def startup_event():
        await init_db()

    app.add_event_handler("startup", startup_event)

    # Include routers
    app.include_router(
        csrf.router, 
        prefix="/api/csrf", 
        tags=["CSRF"]
    )
    app.include_router(
        auth.router, 
        prefix="/api/auth", 
        tags=["Authentication"]
    )   
    # Include websocket routes if they exist
    if hasattr(websocket_routes, 'router'):
        app.include_router(
            websocket_routes.router,
            prefix="/ws",
            tags=["WebSockets"]
        )
    # Add other routers...
    app.include_router(
        metrics_router,
        prefix="/api/metrics",
        tags=["Metrics"]
    )
    # Add optimization profiles router
    app.include_router(
        optimization.router,
        prefix="/api/optimization-profiles",
        tags=["Optimization"]
    )
    # Add system configuration router
    app.include_router(
        configuration.router,
        prefix="/api/system-configurations",
        tags=["Configuration"]
    )
    # Add system alerts router
    app.include_router(
        alerts.router,
        prefix="/api/system-alerts",
        tags=["Alerts"]
    )
    
    # Add auto-tuner router
    app.include_router(
        auto_tuner.router,
        prefix="/api/auto-tuner",
        tags=["Auto-Tuner"]
    )
    
    # Add users router
    app.include_router(
        users.router,
        prefix="/api/users",
        tags=["Users"]
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "X-CSRFToken"],
    )
    
    return app

# Create the app
app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
