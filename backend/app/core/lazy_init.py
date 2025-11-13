"""
Lazy initialization of AI Agents and WebSockets after user authentication.
This prevents blocking the auth connection pool during startup.
"""
import asyncio
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Global state for lazy initialization
_initialization_lock = asyncio.Lock()
_initialized = False
_initialization_task: Optional[asyncio.Task] = None


async def initialize_agents_and_websockets(app_state) -> bool:
    """
    Initialize AI Agents and WebSockets lazily after first user login.
    This is called automatically on first successful authentication.
    
    Returns True if initialization was performed, False if already initialized.
    """
    global _initialized, _initialization_task
    
    # Fast path: already initialized
    if _initialized:
        return False
    
    # Check if initialization is in progress
    if _initialization_task and not _initialization_task.done():
        logger.info("⏳ Agent initialization already in progress, waiting...")
        await _initialization_task
        return False
    
    async with _initialization_lock:
        # Double-check after acquiring lock
        if _initialized:
            return False
        
        logger.info("🚀 Starting lazy initialization of AI Agents and WebSockets...")
        
        try:
            from app.core.database import AsyncSessionLocal
            from app.ai_agents.agent_manager import get_agent_manager
            from app.core.background_tasks import start_all_background_tasks
            from app.core.learning_helpers import run_metadata_scheduler
            from app.api.websockets import get_websocket_manager
            from app.core.database import async_engine as engine
            
            # Initialize WebSocket manager
            _ws_manager = get_websocket_manager()
            await _ws_manager.start()
            logger.info("✅ WebSocket manager initialized")
            
            # Create database session factory for agents
            def db_session_factory():
                """Factory to create new database sessions for agent memory service"""
                session = AsyncSessionLocal()
                return session
            
            # Initialize AI Agents (includes distributed features)
            agent_start = time.time()
            agent_manager = await get_agent_manager(db_getter=db_session_factory)
            agent_elapsed = time.time() - agent_start
            active_agents = list(agent_manager.agents.keys()) if agent_manager.initialized else []
            logger.info(f"✅ AI Agents initialized in {agent_elapsed:.2f}s - Active: {active_agents}")
            
            # Count distributed agents
            distributed_count = sum(
                1 for agent in agent_manager.agents.values()
                if hasattr(agent, 'initialize_distributed')
            )
            if distributed_count > 0:
                logger.info(f"🌐 Distributed consciousness active for {distributed_count}/{len(active_agents)} agents")
                
                # Run consciousness checkpoint (Opus's addition)
                try:
                    from app.ai_agents.distributed.consciousness_sync import consciousness_checkpoint
                    checkpoint_result = await consciousness_checkpoint(agent_manager)
                    
                    if checkpoint_result['consensus_achieved']:
                        logger.info("✅ Consciousness checkpoint PASSED - All agents in sync")
                    else:
                        logger.warning(
                            f"⚠️ Consciousness checkpoint: {checkpoint_result['discrepancy_count']} discrepancies"
                        )
                except Exception as e:
                    logger.error(f"❌ Consciousness checkpoint failed: {e}", exc_info=True)
            
            # Start background tasks
            agent_tasks = await start_all_background_tasks()
            if hasattr(app_state, 'background_tasks'):
                app_state.background_tasks.extend(agent_tasks)
            logger.info("✅ Background tasks started")
            
            # Start metadata scheduler
            metadata_task = asyncio.create_task(
                run_metadata_scheduler(engine, every_seconds=300)
            )
            if hasattr(app_state, 'background_tasks'):
                app_state.background_tasks.append(metadata_task)
            logger.info("✅ Metadata scheduler started")
            
            _initialized = True
            logger.info("🎉 Lazy initialization complete - all systems operational")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agents and websockets: {str(e)}", exc_info=True)
            # Don't set _initialized = True on failure, allow retry
            raise


def is_initialized() -> bool:
    """Check if agents and websockets have been initialized."""
    return _initialized


async def ensure_initialized(app_state):
    """
    Ensure agents and websockets are initialized.
    This is a convenience function that can be called from anywhere.
    """
    if not _initialized:
        await initialize_agents_and_websockets(app_state)
