from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.database import async_engine as engine, Base, init_models, log_registered_models
from app.core.middleware import setup_middleware
from app.api.endpoints import auth
from app.api.endpoints import optimization
from app.api.endpoints import configuration
from app.api.endpoints import alerts
from app.api.endpoints import users
from app.api.endpoints import system_logs
from app.api.endpoints import health
from app.api import router as api_router
from app.api import router as metrics_router
from app.api import router as debug_router
from app.api import simplified_websocket_routes, minimal_websocket_routes
from datetime import datetime
import uvicorn
import logging
import secrets
from fastapi import Response
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *  # noqa

# Import AI Agents and Background Tasks
from app.ai_agents.agent_manager import get_agent_manager
from app.core.background_tasks import start_all_background_tasks
from app.ai_agents.hamsters.hamsters_api_routes import router as hamsters_router

# Global reference to background tasks for cleanup
background_tasks = []

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

# REMOVED - No longer needed, AgentManager handles this
# async def init_ai_agents():
#     """This function is now handled by AgentManager.initialize_agents()"""
#     pass

# Define lifespan for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    global background_tasks
    
    # Startup logic
    logger.info("🚀 Starting up System Rebellion application...")
    logger.info("🎭 The Virtual Misfits are awakening...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database initialization successful")
        
        # Initialize AI Agents ONCE through AgentManager
        agent_manager = await get_agent_manager()
        logger.info("🤖 AI Agents initialized and ready")
        
        # Start background tasks (Meth Snail's optimization, aggregation, etc.)
        background_tasks = await start_all_background_tasks()
        logger.info("🔄 Background tasks started:")
        logger.info("  🐌 Metrics aggregation engine running")
        logger.info("  🐌💨 Real-time optimization engine engaged")
        logger.info("  🏥 System health monitor active")
        
    except Exception as e:
        logger.error(f"❌ Failed during startup: {str(e)}")
        raise
    
    yield  # This is where the application runs
    
    # Shutdown logic
    logger.info("🛑 Shutting down System Rebellion application...")
    
    # Cancel all background tasks gracefully
    for task in background_tasks:
        try:
            task.cancel()
            await asyncio.wait_for(task, timeout=5.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
    
    # Shutdown agent manager
    agent_manager = await get_agent_manager()
    await agent_manager.shutdown()
    
    logger.info("🐌 Background tasks stopped")
    logger.info("🧐 Sir Hawkington bids you farewell")
    logger.info("👋 System Rebellion shutdown complete")

def create_application() -> FastAPI:
    # Log registered models for debugging
    log_registered_models()
    
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="System Rebellion - AI-Powered System Monitoring",
        description="Quantum Optimization Platform with AI Consciousness | Featuring Sir Hawkington & The Virtual Misfits",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Setup middleware
    setup_middleware(app)

    # Debug endpoint
    @app.get("/api/debug/ping")
    def ping():
        return {"message": "pong", "ai_status": "🧐 Sir Hawkington is watching"}
    
    # Health check endpoint
    @app.get("/health-check/")
    @app.get("/api/health-check/")
    async def health_check():
        """
        Sir Hawkington's Health Check Protocol
        The Quantum Shadow People shall not interfere!
        """
        # Check AI agent status
        agent_manager = await get_agent_manager()
        active_agents = agent_manager.get_active_agents()
        
        return JSONResponse(
            content={
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "ai_agents": {
                    "active": active_agents,
                    "count": len(active_agents),
                    "sir_hawkington": "🧐 Monitoring with distinction" if 'sir_hawkington' in active_agents else "🧐 Adjusting monocle...",
                    "meth_snail": "🐌💨 Optimizing furiously" if 'meth_snail' in active_agents else "🐌 Preparing optimization protocols...",
                    "the_stick": "📏 Enforcing compliance" if 'the_stick' in active_agents else "📏 Calibrating compliance metrics...",
                    "quantum_shadows": "👻 Monitoring network" if 'quantum_shadow_people' in active_agents else "👻 Phasing into existence..."
                }
            }
        )
    
    # AI Agents status endpoint
    @app.get("/api/ai-agents/status")
    async def ai_agents_status():
        """Get detailed status of all AI agents"""
        agent_manager = await get_agent_manager()
        return agent_manager.get_agent_status()
    
    # CSRF token endpoint directly in main.py for guaranteed availability
    @app.get("/api/auth/csrf_token")
    async def get_csrf_token(response: Response):
        """Generate a new CSRF token and set it as a cookie and in headers"""
        csrf_token = secrets.token_urlsafe(32)
        
        # Set cookie that matches frontend expectations
        response.set_cookie(
            key="csrftoken", 
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

    # Include websocket routes if they exist
    if hasattr(simplified_websocket_routes, 'router'):
        app.include_router(
            simplified_websocket_routes.router,
            prefix="/api",
            tags=["WebSockets"]
        )
    if hasattr(minimal_websocket_routes, 'router'):
        app.include_router(
            minimal_websocket_routes.router,
            prefix="/api",
            tags=["WebSockets"]
        )

    # if hasattr(master_websocket_router_v2, 'router'):
    #     app.include_router(
    #         master_websocket_router_v2.router,
    #         prefix="/api",
    #         tags=["WebSockets"]
    #     )

    # Include routers
    app.include_router(
        auth.router, 
        prefix="/api/auth", 
        tags=["Authentication"]
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
    
    # Add Hamsters API Router   
    app.include_router(
        hamsters_router,
        prefix="/api/hamsters",
        tags=["Hamsters"]
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
    
    return app

# Create the app
app = create_application()

if __name__ == "__main__":
    logger.info("🎮 System Rebellion starting in development mode...")
    logger.info("🧐 Sir Hawkington is adjusting his monocle...")
    logger.info("🐌 Meth Snail is preparing optimization protocols...")
    logger.info("🐹 The Hamsters are ready to serve...")
    logger.info("📏 The Stick is enforcing compliance...")
    logger.info("👻 Quantum Shadows are monitoring...")
    logger.info("VIC20 Are you ready to optimize your system?...")
    
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000,
        reload=True,
        log_level="debug"
    )