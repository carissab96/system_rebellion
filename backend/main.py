from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# Load environment variables from .env.development
env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.development')
if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"✅ Loaded environment from: {env_file}")
else:
    print(f"⚠️ No .env.development found at: {env_file}")

from app.core.database import async_engine as engine, Base, init_models, log_registered_models
from app.core.middleware import setup_middleware
from app.core.redis import get_redis_client, close_redis
from app.api.endpoints import auth
from app.api.endpoints import users
from app.api.endpoints import system_logs
from app.api.endpoints import health
from app.api.endpoints import onboarding
from app.api import router as api_router
from app.api import router as metrics_router
from app.api import router as debug_router
from app.api import system
from app.api import simplified_websocket_routes
from app.api import agent_events_websocket
from app.api import agent_insights_websocket
from datetime import datetime, timezone 
import uvicorn
import logging
import secrets
from fastapi import Response
import asyncio
from app.services.memory_redis_patch.workers.db_processor import process_memory_batch
from app.services.memory_redis_patch.agent_memory_service_with_cache import AgentMemoryServiceWithCache
from app.services.memory_redis_patch.task_queue import RedisTaskQueue
from app.services.memory_redis_patch.memory_cache_mixin import MemoryCacheMixin
from contextlib import asynccontextmanager
from app.services.memory_redis_patch.redis_client import RedisClient
from app.services.memory_redis_patch.health import RedisHealthMonitor


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *  # noqa

# Import AI Agents and Background Tasks
from app.ai_agents.agent_manager import get_agent_manager
from app.core.background_tasks import start_all_background_tasks
from app.ai_agents.hamsters.hamsters_api_routes_refactored import router as hamsters_router
from app.ai_agents.meth_snail import router as meth_snail_router
from rich.console import Console
from rich.table import Table
from rich.live import Live
from app.services.metrics_repository import get_metrics_repository
from app.core.learning_helpers import run_metadata_scheduler
from app.api.websockets import get_websocket_manager
from app.core.resilience import (
    error_recovery,
    RecoveryAction,
    RecoveryStrategy,
    ErrorSeverity,
    get_circuit_breaker,
    get_backpressure_handler
)
app = FastAPI()
app.state.redis_client = None
app.state.memory_service = None
app.state.task_queue = None

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

        redis_client = await RedisClient.get_instance(
            redis_url="redis://localhost:6379",
            max_connections=20,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        app.state.redis = redis_client
        logger.info("🔴 Redis connection established with circuit breaker")
        
        # Initialize health monitor
        health_monitor = RedisHealthMonitor(redis_client.client)
        await health_monitor.start()
        app.state.redis_health_monitor = health_monitor
        logger.info("📊 Redis health monitoring started")
        
        # Create a database session factory for memory service
        from app.core.database import AsyncSessionLocal
        
        def memory_db_session_factory():
            """Factory to create new database sessions for memory service"""
            session = AsyncSessionLocal()
            return session

        app.state.memory_service = AgentMemoryServiceWithCache(
            redis_url="redis://localhost:6379",
            db_getter=memory_db_session_factory,
            max_connections=20,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        await app.state.memory_service.ensure_ready()

        # Initialize task queue
        app.state.task_queue = RedisTaskQueue(redis_client.client)
        logger.info("📋 Task queue initialized")

        # Start the memory batch processor
        memory_processor_task = asyncio.create_task(
            process_memory_batch(app.state.memory_service)
        )
        background_tasks.append(memory_processor_task)
        logger.info("💾 Memory batch processor started")
        
        await get_metrics_repository()  # warms the singleton
        logger.info("🟡 MetricsRepository initialized")
        
        # Initialize WebSocket manager
        _ws_manager = get_websocket_manager()
        await _ws_manager.start()
        logger.info("Sir Hawkington websocket manager startup complete")
        
        # Initialize resilience components
        await initialize_websocket_resilience()
        logger.info("🛡️  WebSocket resilience system activated")

        # Initialize AI Agents ONCE through AgentManager
        import time
        from app.core.database import AsyncSessionLocal
        
        # Create a database session factory for the agent manager
        # Note: AsyncSessionLocal is already a sessionmaker, we just need to call it
        def db_session_factory():
            """Factory to create new database sessions for agent memory service"""
            # AsyncSessionLocal() returns a context manager, we need the actual session
            session = AsyncSessionLocal()
            return session
        
        agent_start = time.time()
        agent_manager = await get_agent_manager(db_getter=db_session_factory)
        agent_elapsed = time.time() - agent_start
        active_agents = list(agent_manager.agents.keys()) if agent_manager.initialized else []
        logger.info(f"🤖 AI Agents initialized in {agent_elapsed:.2f}s - Active: {active_agents}")
        
        # Start background tasks (Meth Snail's optimization, aggregation, etc.)
        agent_tasks = await start_all_background_tasks()
        background_tasks.extend(agent_tasks)
        
        metadata_task = asyncio.create_task(
            run_metadata_scheduler(engine, every_seconds=300)
        )
        background_tasks.append(metadata_task)

        logger.info("🔄 Background tasks started:")
        logger.info("  🐌 Metrics aggregation engine running")
        logger.info("  🐌💨 Real-time optimization engine engaged")
        logger.info("  🏥 System health monitor active")
        logger.info(" Memory bank metadata scheduler running")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Redis services: {str(e)}")
        if 'redis_client' in locals():
            await close_redis()
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
    
    if hasattr(app.state, 'redis_health_monitor'):
            await app.state.redis_health_monitor.stop()
            logger.info("🛑 Stopped Redis health monitor")
    if hasattr(app.state, 'redis'):
            await RedisClient.close_instance()
            logger.info("🛑 Closed Redis connection")
    
    # Shutdown agent manager
    agent_manager = await get_agent_manager()
    await agent_manager.shutdown()
    
    logger.info("🐌 Background tasks stopped")
    logger.info("🧐 Sir Hawkington bids you farewell")
    logger.info("👋 System Rebellion shutdown complete")

async def get_memory_service():
    return app.memory_service

async def get_task_queue():
    return app.task_queue


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
    @app.get("/health/redis")
    async def get_redis_health():
        """Get Redis Health status"""
        return {
            "status": "ok",
            "redis": app.state.redis_health_monitor.get_status(),
            "circuit_breaker": app.state.redis.get_circuit_state()
        }

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
        active_agents = list(agent_manager.agents.keys()) if agent_manager.initialized else []
    
        return JSONResponse(
        content={
            "status": "operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "ai_agents": {
                "active": active_agents,
                "count": len(active_agents),
                "sir_hawkington": "🧐 Monitoring with distinction" if 'sir_hawkington' in active_agents else "🧐 Adjusting monocle...",
                "meth_snail": "🐌💨 Optimizing furiously" if 'meth_snail' in active_agents else "🐌 Preparing optimization protocols...",
                "the_stick": "📏 Enforcing compliance" if 'the_stick' in active_agents else "📏 Calibrating compliance metrics...",
                "quantum_shadow_people": "👻 Monitoring network" if 'quantum_shadow_people' in active_agents else "👻 Phasing into existence...",
                "hamsters": "🐹 Ready to fix" if 'hamsters' in active_agents else "🐹 Preparing tools...",
                "vic_20_sage": "🖥️ Dispensing wisdom" if 'vic_20_sage' in active_agents else "🖥️ Loading ancient protocols..."
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
            path="/api/auth"  # Restrict to authentication endpoints
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
    
    # Include agent events WebSocket route
    if hasattr(agent_events_websocket, 'router'):
        logger.info("✅ Registering Agent Events WebSocket route")
        app.include_router(
            agent_events_websocket.router,
            prefix="/api",
            tags=["Agent Events"]
        )
        logger.info("✅ Agent Events route registered")
    else:
        logger.error("❌ agent_events_websocket has no 'router' attribute")
    
    # Include agent insights WebSocket route
    if hasattr(agent_insights_websocket, 'router'):
        logger.info("✅ Registering Agent Insights WebSocket route")
        app.include_router(
            agent_insights_websocket.router,
            prefix="/api",
            tags=["Agent Insights"]
        )
        logger.info("✅ Agent Insights route registered")
    else:
        logger.error("❌ agent_insights_websocket has no 'router' attribute")
  

    # Include routers
    app.include_router(
        system.router,
        prefix="/api/system",
        tags=["System"]
    )
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
        prefix="/api/system-metrics",
        tags=["System-Metrics"]
    )
    
    # Add Hamsters API Router   
    app.include_router(
        hamsters_router,
        prefix="/api/hamsters",
        tags=["Hamsters"]
    )
    
    # Add Meth Snail API Router
    app.include_router(
        meth_snail_router,
        prefix="/api/meth-snail",
        tags=["Meth Snail"]
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
    
    # Add onboarding router
    app.include_router(
        onboarding.router,
        prefix="/api/onboarding",
        tags=["Onboarding"]
    )
    # Note: agent_insights and agent_events routers already registered above (lines 362-383)
    # Include API router (includes WebSocket routes)
    app.include_router(
        api_router,
        prefix="/api"
    )
    
    return app


        
async def initialize_websocket_resilience():
    """Initialize WebSocket resilience components"""
    # Register WebSocket error recovery strategies
    error_recovery.register_strategy(
        component="websocket",
        error_type="ConnectionError",
        recovery_action=RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            max_retries=3,
            retry_delay=1.0,
            exponential_backoff=True
        )
    )
    
    error_recovery.register_strategy(
        component="websocket",
        error_type="RuntimeError",
        recovery_action=RecoveryAction(
            strategy=RecoveryStrategy.CIRCUIT_BREAK,
            max_retries=2,
            retry_delay=5.0
        )
    )
    
    # Initialize circuit breaker for WebSocket connections
    ws_circuit_breaker = get_circuit_breaker(
        name="websocket_connection",
        max_failures=5,
        reset_timeout=30,
        exponential_backoff_factor=2.0
    )
    
    # Initialize backpressure handler for WebSocket messages
    ws_backpressure = get_backpressure_handler(
        name="websocket_messages",
        max_buffer_size=1000,
        sampling_strategy="latest"
    )
    
    # Note: Circuit breakers and backpressure handlers for agent_insights and agent_events
    # are created on-demand by get_circuit_breaker() and get_backpressure_handler()
    # when the endpoints call them (same pattern as metrics endpoint)
    
    logger.info("🔄 WebSocket resilience components initialized")
    return {
        "circuit_breaker": ws_circuit_breaker,
        "backpressure_handler": ws_backpressure
    }

async def get_memory_service() -> AgentMemoryServiceWithCache:
    """Get the memory service instance"""
    if not hasattr(app.state, 'memory_service') or not app.state.memory_service:
        raise RuntimeError("Memory service not initialized")
    return app.state.memory_service

async def get_task_queue() -> RedisTaskQueue:
    """Get the task queue instance"""
    if not hasattr(app.state, 'task_queue') or not app.state.task_queue:
        raise RuntimeError("Task queue not initialized")
    return app.state.task_queue

# Create the app
app = create_application()

if __name__ == "__main__":
    logger.info("🎮 System Rebellion starting in development mode...")
    logger.info("🧐 Sir Hawkington is adjusting his monocle...")
    logger.info("🐌 Meth Snail is preparing optimization protocols...")
    logger.info("🐹 The Hamsters are ready to serve...")
    logger.info("📏 The Stick is enforcing compliance...")
    logger.info("👻 Quantum Shadows are monitoring...")
    logger.info("VIC20 Sage is preparing ancient computer wisdom...")    
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000,
        reload=True,
        log_level="debug"
    )