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
# Deprecated: agent_events_websocket and agent_insights_websocket
# Now unified into simplified_websocket_routes
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

# Import Background Tasks (Week 5 Task 5.4: Removed legacy AIAgentManager)
from app.core.background_tasks import start_all_background_tasks
from app.ai_agents.meth_snail import router as meth_snail_router
from app.api.endpoints import distributed_agents
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
from app.ai_agents.distributed.distributed_agent_manager import (
    initialize_distributed_agents,
    shutdown_distributed_agents
)
app = FastAPI()
app.state.redis_client = None
app.state.memory_service = None
app.state.task_queue = None
app.state.background_tasks = []  # Store background tasks in app state for lazy init access

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

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = await RedisClient.get_instance(
            redis_url=redis_url,
            max_connections=20,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        logger.info(f"🔴 Connecting to Redis at {redis_url}")
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
            redis_url=redis_url,
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
        
        logger.info("✅ Core services ready - authentication available")
        logger.info("")
        
        # Schedule agent initialization to happen AFTER startup completes
        # This allows auth to work immediately without waiting for agents
        async def initialize_agents_after_startup():
            """Initialize agents after the server is fully started and accepting requests"""
            import asyncio
            import time
            from app.core.database import get_async_db
            
            await asyncio.sleep(2)  # Give server time to fully start
            
            logger.info("=" * 80)
            logger.info("🎭 INITIALIZING AI AGENTS AND WEBSOCKETS")
            logger.info("=" * 80)
            
            try:
                # Initialize WebSocket manager with Redis bridge
                _ws_manager = get_websocket_manager()
                
                # Connect WebSocket manager to Redis for distributed agent messages
                if redis_client:
                    _ws_manager.set_redis_client(redis_client.client)
                    logger.info("🌉 WebSocket manager connected to Redis for agent message forwarding")
                else:
                    logger.warning("⚠️ Redis client not available - distributed agent messages won't be forwarded to WebSocket")
                
                await _ws_manager.start()
                logger.info("✅ Sir Hawkington websocket manager startup complete")
                
                # Initialize AI Agents ONCE through AgentManager
                
                # Initialize distributed agent consciousness system (Week 5 Task 5.4: Single unified system)
                try:
                    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
                    logger.info(f"🌐 Initializing distributed agent consciousness (Redis: {redis_url})...")
                    
                    # Get system user ID for agent database writes
                    from sqlalchemy import select
                    from app.models.user import User
                    from app.core.database import get_async_db
                    
                    system_user_id = None
                    async for session in get_async_db():
                        result = await session.execute(select(User.id).limit(1))
                        system_user_id = result.scalar_one_or_none()
                        break
                    
                    if not system_user_id:
                        logger.warning("⚠️ No users found in database - agents will not be able to write to database")
                    else:
                        logger.info(f"✅ System user ID: {system_user_id}")
                    
                    # Use get_async_db directly - it's an async generator that yields sessions
                    await initialize_distributed_agents(redis_url, db_getter=get_async_db, user_id=system_user_id)
                    logger.info("✅ Distributed agents initialized:")
                    logger.info("  🧐 Sir Hawkington - CPU Monitor")
                    logger.info("  🐌💨 Terry the Meth Snail - Memory Monitor")
                    logger.info("  🐹 The Hamsters - Disk Monitor (Steve, Bob and Carl)")
                    logger.info("  👻 Quantum Shadow People - Network Monitor")
                    logger.info("  📏 The Stick - Learning Coordinator")
                    logger.info("  🖥️ VIC-20 Sage - Orchestrator")
                    
                    # Set up WebSocket logging to broadcast agent logs to frontend
                    from app.core.websocket_log_handler import setup_websocket_logging
                    from app.api.websockets import get_websocket_manager
                    
                    ws_manager = get_websocket_manager()
                    event_loop = asyncio.get_running_loop()
                    
                    # Use ws_manager.broadcast as the broadcast function
                    setup_websocket_logging(ws_manager.broadcast, event_loop, level=logging.INFO)
                    logger.info("✅ WebSocket logging enabled - agent logs will broadcast via /ws/system-metrics")
                    
                    # Test the logging handler
                    test_logger = logging.getLogger('TheStick.Distributed')
                    test_logger.info("🧪 TEST LOG - WebSocket handler attached and working!")
                    
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
                    logger.info("  📊 Memory bank metadata scheduler running")
                    
                except Exception as e:
                    logger.error(f"⚠️  Failed to initialize distributed agents: {e}", exc_info=True)
                    logger.warning("Continuing without distributed agent system")
                
                logger.info("=" * 80)
                logger.info("🎉 ALL SYSTEMS OPERATIONAL")
                logger.info("=" * 80)
            except Exception as e:
                logger.error(f"❌ Failed to initialize agents: {e}", exc_info=True)
        
        # Start agent initialization in background - don't block startup
        asyncio.create_task(initialize_agents_after_startup())
        logger.info("⏳ Agent initialization scheduled (will complete in background)")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Redis services: {str(e)}")
        if 'redis_client' in locals():
            await close_redis()
        raise
    
    yield  # This is where the application runs
    
    # Shutdown logic
    logger.info("🛑 Shutting down System Rebellion application...")
    
    # Cancel all background tasks gracefully (from both global and app.state)
    all_tasks = background_tasks + (app.state.background_tasks if hasattr(app.state, 'background_tasks') else [])
    for task in all_tasks:
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
    
    # Shutdown distributed agents (Week 5 Task 5.4: Single unified system)
    try:
        await shutdown_distributed_agents()
        logger.info("🌐 Distributed agents shut down")
    except Exception as e:
        logger.error(f"Error shutting down distributed agents: {e}")
    
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
        # Check distributed agent status (Week 5 Task 5.4: Use distributed registry)
        from app.ai_agents.distributed.distributed_agent_manager import get_distributed_manager
        try:
            manager = get_distributed_manager()
            active_agents = list(manager.agents.keys()) if manager._initialized else []
        except:
            active_agents = []
    
        return JSONResponse(
        content={
            "status": "operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "ai_agents": {
                "active": active_agents,
                "count": len(active_agents),
                "sir_hawkington": "🧐 Monitoring with distinction" if 'sir_hawkington' in active_agents else "🧐 Adjusting monocle...",
                "terry_meth_snail": "🐌💨 Optimizing furiously" if 'terry_meth_snail' in active_agents else "🐌 Preparing optimization protocols...",
                "the_stick": "📏 Enforcing compliance" if 'the_stick' in active_agents else "📏 Calibrating compliance metrics...",
                "quantum_shadow_people": "👻 Monitoring network" if 'quantum_shadow_people' in active_agents else "👻 Phasing into existence...",
                "bob_hamster": "🐹 Ready to fix" if 'bob_hamster' in active_agents else "🐹 Preparing tools...",
                "vic_20_sage": "🖥️ Dispensing wisdom" if 'vic_20_sage' in active_agents else "🖥️ Loading ancient protocols..."
            }
        }
    )        

    # AI Agents status endpoint (Week 5 Task 5.4: Use distributed agents endpoint)
    @app.get("/api/ai-agents/status")
    async def ai_agents_status():
        """Get detailed status of all AI agents - redirects to distributed agents endpoint"""
        from app.ai_agents.distributed.distributed_agent_manager import get_distributed_manager
        try:
            manager = get_distributed_manager()
            return await manager.get_system_status()
        except Exception as e:
            return {"error": str(e), "agents": {}}
    
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
    
    # Include agent logs WebSocket route
    from app.api import agent_logs_websocket
    app.include_router(
        agent_logs_websocket.router,
        prefix="/api",
        tags=["Agent Logs"]
    )
    
    # Deprecated: Agent events and insights WebSocket routes
    # These are now unified into the system-metrics endpoint (/api/ws/system-metrics)
    # which sends a unified payload with metrics, agents, recent_insights, and recent_events
    logger.info("ℹ️ Agent events and insights now served via unified /api/ws/system-metrics endpoint")
  

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
    
    # Hamsters API Router removed - Week 5 Task 5.4
    # Hamsters now operate through distributed system coordinated by VIC-20
    # Direct API bypassed coordination and is deprecated
    # See: app/ai_agents/legacy/hamsters_api_routes_refactored.py
    
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
    
    # Add distributed agents router
    app.include_router(
        distributed_agents.router,
        prefix="/api",
        tags=["Distributed Agents"]
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
        error_type="ConnectionClosedError",
        recovery_action=RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            max_retries=3,
            retry_delay=2.0,
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