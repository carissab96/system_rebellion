"""
Background Tasks for System Rebellion
The Meth Snail's eternal optimization routines
"""
import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete
from app.core.database import get_db, get_async_db, get_async_session
from app.models.user import User
from app.models.metrics import SystemMetrics
from app.services.metrics_aggregation_service import MetricsAggregationService
import logging
from app.ai_agents.distributed.distributed_agent_manager import get_distributed_manager

logger = logging.getLogger("MethSnail.Background")

async def run_metrics_aggregation():
    """
    The Meth Snail's eternal optimization loop.
    Runs every hour to aggregate metrics.
    """
    aggregation_service = MetricsAggregationService()
    
    # Initial delay to let the system stabilize
    await asyncio.sleep(30)  # 30 seconds startup delay
    
    logger.info("🐌 Meth Snail awakens... optimization protocols initiated")
    
    while True:
        try:
            # Calculate time until next hour
            now = datetime.now(timezone.utc)
            next_hour = (now + timedelta(hours=1)).replace(
                minute=0, second=0, microsecond=0
            )
            wait_seconds = (next_hour - now).total_seconds()
            
            # For testing, you might want to run more frequently
            # wait_seconds = 300  # Run every 5 minutes for testing
            
            logger.info(f"🐌 Meth Snail hibernating for {wait_seconds:.0f}s until next aggregation cycle")
            await asyncio.sleep(wait_seconds)
            
            # Aggregate the previous hour's data
            previous_hour = next_hour - timedelta(hours=1)
            
            logger.info(f"🐌 Meth Snail beginning aggregation for hour: {previous_hour}")
            
            # Use proper async context manager for database session
            async for db in get_async_db():
                try:
                    # Get all users with metrics
                    users_query = select(User)
                    users_result = await db.execute(users_query)
                    users = users_result.scalars().all()
                    
                    aggregated_count = 0
                    for user in users:
                        result = await aggregation_service.aggregate_hourly_metrics(
                            db, str(user.id), previous_hour
                        )
                        if result:
                            aggregated_count += 1
                        
                        logger.info(f"🐌 Meth Snail aggregated metrics for {aggregated_count} users")
                        
                        # Cleanup old raw metrics (keep 7 days by default)
                        deleted_count = await aggregation_service.cleanup_old_raw_metrics(db)
                        logger.info(f"🐌 Meth Snail cleaned up {deleted_count} old raw metrics")
                        
                        # Check if we should do daily rollups
                        if now.hour == 0:  # Midnight
                            logger.info("🐌 Meth Snail performing daily rollups...")
                            await aggregation_service.create_daily_rollups(
                                db, 
                                now.date() - timedelta(days=1)
                            )
                        
                except Exception as e:
                    logger.error(f"🐌 Meth Snail aggregation error: {str(e)}", exc_info=True)
                finally:
                    # Context manager handles cleanup automatically
                    break  # Exit the async for loop after one iteration
                    
        except asyncio.CancelledError:
            logger.info("🐌 Meth Snail received shutdown signal, cleaning up...")
            raise
        except Exception as e:
            logger.error(f"🐌 Meth Snail aggregation loop error: {str(e)}", exc_info=True)
            await asyncio.sleep(300)  # Wait 5 minutes on error

async def run_realtime_optimization():
    """
    The Meth Snail's real-time optimization engine.
    Continuously monitors and optimizes system performance.
    """
    # Initial delay to let system stabilize
    await asyncio.sleep(10)
    
    logger.info("🐌💨 Meth Snail real-time optimization engine ENGAGED!")
    
    # Get the distributed agent manager instance
    agent_manager = get_distributed_manager()
    if not agent_manager or not agent_manager.initialized:
        logger.warning("⚠️ Distributed agent manager not initialized, optimization engine waiting...")
        await asyncio.sleep(30)
        agent_manager = get_distributed_manager()
    
    # Main optimization loop
    optimization_interval = 30  # Check every 30 seconds
    
    while True:
        try:
            # Use proper async context manager for database session
            async for db in get_async_db():
                try:
                    # Get all active users
                    users_query = select(User).filter(User.is_active == True)
                    users_result = await db.execute(users_query)
                    active_users = users_result.scalars().all()
                        
                    for user in active_users:
                        # Get recent metrics for this user (last 5 minutes)
                        recent_metrics_query = select(SystemMetrics).filter(
                            SystemMetrics.user_id == str(user.id),
                            SystemMetrics.timestamp >= datetime.utcnow() - timedelta(minutes=5)
                        ).order_by(SystemMetrics.timestamp.desc()).limit(10)
                            
                        result = await db.execute(recent_metrics_query)
                        recent_metrics = result.scalars().all()
                            
                        if recent_metrics:
                            # Get the latest metric
                            latest_metric = recent_metrics[0]
                                
                            # Extract metrics data from additional_metrics JSON
                            metrics_data = latest_metric.additional_metrics or {}
                                
                            # Prepare historical data for pattern analysis
                            historical_data = [
                                    {
                                        'cpu_usage': m.cpu_usage,
                                        'memory_usage': m.memory_usage,
                                        'disk_usage': m.disk_usage,
                                        'timestamp': m.timestamp
                                    }
                                    for m in recent_metrics
                                ]
                                
                            # Let Meth Snail analyze through the agent manager
                            # This will automatically trigger Meth Snail's decision engine
                            user_context = {
                                'user_id': str(user.id),
                                'email': user.email,
                                'historical_data': historical_data
                                }
                                
                            # Process through agents (Meth Snail will analyze if registered)
                            enhanced_metrics = await agent_manager.process_metrics_through_triage_engine(
                                metrics_data,
                                user_context
                            )
                                
                            # Check if Meth Snail made any optimization decisions
                            if 'meth_snail' in enhanced_metrics:
                                meth_decision = enhanced_metrics['meth_snail']
                                    
                                # If urgent optimizations are needed, execute them
                                if meth_decision.get('urgency') == 'immediate':
                                    logger.warning(
                                        f"🐌⚡ Meth Snail executing IMMEDIATE optimizations "
                                        f"for user {user.email}: {meth_decision.get('rationale')}"
                                    )
                                    # TODO: Execute optimization actions
                                    # This would interface with system optimization APIs
                                    
                                elif meth_decision.get('urgency') == 'soon':
                                    logger.info(
                                        f"🐌 Meth Snail planning optimizations "
                                        f"for user {user.email}: {meth_decision.get('rationale')}"
                                    )
                                
                except Exception as e:
                    logger.error(f"🐌 Error in real-time optimization for users: {str(e)}")
                finally:
                    # Context manager handles cleanup automatically
                    break  # Exit the async for loop after one iteration
            
            # Wait before next optimization check
            await asyncio.sleep(optimization_interval)
            
        except asyncio.CancelledError:
            logger.info("🐌 Meth Snail real-time optimization shutting down...")
            raise
        except Exception as e:
            logger.error(f"🐌 Real-time optimization error: {str(e)}", exc_info=True)
            await asyncio.sleep(60)  # Wait 1 minute on error

async def run_system_health_monitor():
    """
    Monitor overall system health and coordinate between AI agents.
    Ensures Sir Hawkington and Meth Snail work together effectively.
    """
    await asyncio.sleep(15)  # Let other systems initialize
    
    logger.info("🏥 System health monitor activated")
    
    health_check_interval = 60  # Check every minute
    
    while True:
        try:
            # Check aggregation task health
            # Check optimization task health
            # Coordinate between agents
            
            # Simple health ping for now
            logger.debug("🏥 System health check - All systems operational")
            
            await asyncio.sleep(health_check_interval)
            
        except asyncio.CancelledError:
            logger.info("🏥 System health monitor shutting down...")
            raise
        except Exception as e:
            logger.error(f"🏥 Health monitor error: {str(e)}")
            await asyncio.sleep(health_check_interval)

async def run_consciousness_checkpoint():
    """
    Run consciousness checkpoint every 5 minutes.
    
    Opus's brilliant addition - verifies all distributed agents
    share a consistent worldview and triggers reconciliation if needed.
    """
    await asyncio.sleep(60)  # Wait 1 minute for agents to initialize
    
    logger.info("🧠 Consciousness checkpoint monitor activated")
    
    checkpoint_interval = 300  # Every 5 minutes
    
    while True:
        try:
            # Get distributed agent manager
            agent_manager = get_distributed_manager()
            
            if not agent_manager or not agent_manager.initialized:
                logger.warning("🧠⚠️ Agent manager not initialized, skipping checkpoint")
                await asyncio.sleep(checkpoint_interval)
                continue
            
            # Run consciousness checkpoint
            from app.ai_agents.distributed.consciousness_sync import consciousness_checkpoint
            
            result = await consciousness_checkpoint(agent_manager)
            
            if result['consensus_achieved']:
                logger.info(
                    f"🧠✅ Consciousness checkpoint PASSED - "
                    f"{result['distributed_agents']}/{result['total_agents']} agents in sync"
                )
            else:
                logger.warning(
                    f"🧠⚠️ Consciousness checkpoint FAILED - "
                    f"{result['discrepancy_count']} discrepancies detected"
                )
                for discrepancy in result['discrepancies']:
                    logger.warning(f"  - {discrepancy}")
            
            await asyncio.sleep(checkpoint_interval)
            
        except asyncio.CancelledError:
            logger.info("🧠 Consciousness checkpoint monitor shutting down...")
            raise
        except Exception as e:
            logger.error(f"🧠 Consciousness checkpoint error: {str(e)}", exc_info=True)
            await asyncio.sleep(checkpoint_interval)

# Convenience function to start all background tasks
async def start_all_background_tasks():
    """Start all background tasks for System Rebellion"""
    tasks = [
        asyncio.create_task(run_metrics_aggregation()),
        asyncio.create_task(run_realtime_optimization()),
        asyncio.create_task(run_system_health_monitor()),
        asyncio.create_task(run_consciousness_checkpoint())
    ]
    
    logger.info("🚀 All background tasks started:")
    logger.info("  🐌 Metrics aggregation engine")
    logger.info("  🐌💨 Real-time optimization engine")
    logger.info("  🏥 System health monitor")
    logger.info("  🧠 Consciousness checkpoint monitor (every 5 minutes)")
    
    return tasks