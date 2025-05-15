from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.database import async_engine as engine, Base, init_models, log_registered_models
from app.core.middleware import setup_middleware
from app.api.endpoints import auth
from app.api.endpoints import optimization
from app.api.endpoints import configuration
from app.api.endpoints import alerts
from app.api.endpoints import auto_tuner
from app.api.endpoints import users
from app.api.endpoints import system_logs
from app.api.endpoints import health
from app.api import router as api_router
from app.api import router as metrics_router
from app.api import router as debug_router
# Import websocket routes
from app.api import websocket_routes
from datetime import datetime
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *  # noqa

# Database initialization
async def init_db(db_engine=None):
    try:
        # Log registered models for debugging
        log_registered_models()
        
        # Use provided engine or default to the global engine
        engine_to_use = db_engine or engine
        
        # Initialize models (create tables)
        await init_models()
        
        logger.info("Database initialization complete")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")

def init_db_sync(db_engine=None):
    """Synchronous version of init_db for testing"""
    try:
        # Log registered models for debugging
        log_registered_models()
        
        engine_to_use = db_engine or engine
        with engine_to_use.begin() as conn:
            Base.metadata.create_all(conn)
        
        logger.info("Synchronous database initialization complete")
        return True
    except Exception as e:
        logger.error(f"Error in synchronous database initialization: {str(e)}", exc_info=True)
        raise

def create_application() -> FastAPI:
    # Log registered models for debugging
    log_registered_models()
    
    # Create FastAPI app
    app = FastAPI(
        title="System Rebellion",
        description="Quantum Optimization Platform",
        version="0.1.0"
    )
    
    # Initialize database on startup
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up application...")
        try:
            await init_db()
            logger.info("Database initialization successful")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    # Setup middleware
    setup_middleware(app)
    
    # Debug endpoint
    @app.get("/api/debug/ping")
    def ping():
        return {"message": "pong"}
    # Health check endpoint
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
        debug_router,
        prefix="/api/debug",
        tags=["Debug"]
    )
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
    
    # Add system logs router
    app.include_router(
        system_logs.router,
        prefix="/api/system-logs",
        tags=["System Logs"]
    )
    
    # Add health check router
    app.include_router(
        health.router,
        prefix="/api/health-check",
        tags=["Health"]
    )
    
    # Include API router (includes WebSocket routes)
    app.include_router(
        api_router,
        prefix="/api"
    )

    # CORS is handled in core/middleware.py
    # WebSocket CORS is handled by the CORS middleware
    # @app.middleware("http")
    # async def add_cors_headers(request, call_next):
    #     response = await call_next(request)
    #     response.headers["Access-Control-Allow-Origin"] = "*"
    #     response.headers["Access-Control-Allow-Methods"] = "*"
    #     response.headers["Access-Control-Allow-Headers"] = "*"
    #     response.headers["Access-Control-Allow-Credentials"] = "true"
    #     return response
    
    return app

# Create the app
app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000,
        reload=True,
        log_level="debug"
    )
