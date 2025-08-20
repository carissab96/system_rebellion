"""
AI Agent Manager — unified, async-safe, with Redis-cached memory injection
"""

from __future__ import annotations

import asyncio
import importlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, TypeVar

import yaml
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

# ⬇️ Adjust these imports to your project layout
from app.ai_agents.base_agent import BaseAIAgent  # must expose process_metrics, health_check
from app.services.memory_redis_patch.agent_memory_service_with_cache import (
    AgentMemoryServiceWithCache,
)

logger = logging.getLogger(__name__)

_initialization_lock = asyncio.Lock()
_agent_manager_instance = None

async def get_agent_manager(
    *,
    db_getter=None,
    memory_service=None,
    agent_config_path: str | None = None,
    redis_url: str | None = None,
    cache_ttl: int = 300,
):
    """
    Async-safe singleton accessor. Creates and initializes once.
    """
    global _agent_manager_instance
    if _agent_manager_instance is not None:
        return _agent_manager_instance

    async with _initialization_lock:
        if _agent_manager_instance is not None:
            return _agent_manager_instance

        # Build default memory service if none was provided
        if memory_service is None:
            from app.services.memory_redis_patch.agent_memory_service_with_cache import AgentMemoryServiceWithCache
            memory_service = AgentMemoryServiceWithCache(
                db_getter=db_getter, redis_url=redis_url, cache_ttl=cache_ttl
            )
            ensure_ready = getattr(memory_service, "ensure_ready", None)
            if ensure_ready and asyncio.iscoroutinefunction(ensure_ready):
                try:
                    await ensure_ready()
                except Exception as e:
                    logger.error("Failed to initialize memory service: %s", e, exc_info=True)

        try:
            # Do NOT pass agent_config_path if __init__ doesn't accept it
            mgr = AIAgentManager(
                db_getter=db_getter,
                memory_service=memory_service,
                redis_url=redis_url,
                cache_ttl=cache_ttl,
            )
            # Attach optional config path post-construction
            if agent_config_path:
                setattr(mgr, "agent_config_path", agent_config_path)

            await mgr.initialize_agents()
            _agent_manager_instance = mgr
        except Exception as e:
            logger.error("Failed to initialize agent manager: %s", e, exc_info=True)
            # Optional: surface a hard error so callers don't get None
            raise

        return _agent_manager_instance

# --- Manager Implementation ---------------------------------------------------

class AIAgentManager:
    def __init__(
        self,
        *,
        memory_service: AgentMemoryServiceWithCache,
        db_getter: DBGetter,
        agent_config_path: str = "app/ai_agents/agents_config.yaml",
        redis_url: str = "redis://localhost:6379",
        cache_ttl: int = 300,
        max_parallel_agents: int = 3
    ) -> None:
        """Initialize the AI Agent Manager.
        
        Args:
            memory_service: Configured memory service instance
            db_getter: Async callable to get database session
            agent_config_path: Path to YAML config file
            redis_url: Redis connection URL
            cache_ttl: Cache TTL in seconds
            max_parallel_agents: Maximum number of agents to run in parallel
        """
        # Required services
        self.memory_service = memory_service
        self.db_getter = db_getter
        
        # Configuration
        self.agent_config_path = Path(agent_config_path)
        self.redis_url = redis_url
        self.cache_ttl = cache_ttl
        self.max_parallel_agents = max_parallel_agents
        
        # Runtime state
        self._sem = asyncio.Semaphore(max_parallel_agents)
        self.agent_configs: Dict[str, Dict[str, Any]] = {}
        self.agents: Dict[str, BaseAIAgent] = {}
        self.processing_order: List[str] = []
        self.initialized = False
        self.initialization_time: Optional[datetime] = None
        self.total_processing_count = 0
        
        self.logger = logger
    async def initialize(self) -> None:
        """Initialize the manager and all agents."""
        if self.initialized:
            return
            
        await self.load_agent_configs()
        await self.initialize_agents()
        self.initialized = True
        self.initialization_time = datetime.utcnow()
        self.logger.info("✅ AIAgentManager initialized with %d agents", len(self.agents))

    async def load_agent_configs(self) -> None:
        """Load and validate agent configurations from YAML.
        
        Expected YAML format:
            agents:
              - name: sir_hawkington
                module: app.ai_agents.sir_hawkington.agent
                class: SirHawkington
                role: "Triage & insights"
                retry_attempts: 2
                config:
                  some_flag: true
        """
        try:
            with open(self.agent_config_path, "r") as f:
                data = yaml.safe_load(f) or {}

            agents_list = data.get("agents", [])
            if not isinstance(agents_list, list):
                raise ValueError("YAML key 'agents' must be a list")

            self.agent_configs.clear()
            self.processing_order.clear()

            for item in agents_list:
                try:
                    agent_name = item["name"]
                    mod_path = item["module"]
                    cls_name = item["class"]
                    
                    # Lazy load the module and class when needed
                    self.agent_configs[agent_name] = {
                        "module_path": mod_path,
                        "class_name": cls_name,
                        "role": str(item.get("role", "Unknown")),
                        "retry_attempts": int(item.get("retry_attempts", 1)),
                        "config": dict(item.get("config", {})),
                    }
                    self.processing_order.append(agent_name)
                    
                except KeyError as e:
                    self.logger.error("Missing required field in agent config: %s", e)
                    raise
                except Exception as e:
                    self.logger.error("Error processing agent config for %s: %s", 
                                    item.get("name", "unknown"), e)
                    raise

            self.logger.info("✅ Loaded %d agent configs", len(self.agent_configs))

        except yaml.YAMLError as e:
            self.logger.error("❌ Invalid YAML in agent config: %s", e)
            raise
        except Exception as e:
            self.logger.error("❌ Failed to load agent configs: %s", e, exc_info=True)
            raise

    async def initialize_agents(self) -> None:
        """Initialize all configured agents."""
        for agent_name, config in self.agent_configs.items():
            try:
                module = importlib.import_module(config["module_path"])
                agent_class: Type[BaseAIAgent] = getattr(module, config["class_name"])
                
                agent = agent_class(
                    name=agent_name,
                    memory_service=self.memory_service,
                    **(config.get("config", {}))
                )
                
                if hasattr(agent, "initialize") and asyncio.iscoroutinefunction(agent.initialize):
                    await agent.initialize()
                    
                self.agents[agent_name] = agent
                self.logger.info("✅ Initialized agent: %s", agent_name)
                
            except Exception as e:
                self.logger.error("❌ Failed to initialize agent %s: %s", agent_name, e, exc_info=True)
                raise
    async def process_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Process metrics through all agents in parallel.
        
        Args:
            metrics: Dictionary of metrics to process
            
        Returns:
            Dict containing results from all agents
        """
        results = {}
        
        async def process_agent(agent_name: str, agent: BaseAIAgent) -> None:
            try:
                async with self._sem:
                    result = await agent.process_metrics(metrics.copy())
                    results[agent_name] = result
            except Exception as e:
                self.logger.error("Error in agent %s: %s", agent_name, e, exc_info=True)
                results[agent_name] = {"error": str(e)}
        
        # Run all agents in parallel
        tasks = [process_agent(name, agent) for name, agent in self.agents.items()]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.total_processing_count += 1
        return results

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all agents.
        
        Returns:
            Dict with health status of each agent
        """
        health = {
            "initialized": self.initialized,
            "initialization_time": self.initialization_time.isoformat() if self.initialization_time else None,
            "total_processing_count": self.total_processing_count,
            "agents": {}
        }
        
        for name, agent in self.agents.items():
            try:
                if hasattr(agent, 'health_check') and asyncio.iscoroutinefunction(agent.health_check):
                    health["agents"][name] = await agent.health_check()
                else:
                    health["agents"][name] = {"status": "healthy", "details": "No health check implemented"}
            except Exception as e:
                health["agents"][name] = {"status": "error", "error": str(e)}
                
        return health
    async def shutdown(self) -> None:
        """Cleanup resources and shutdown all agents."""
        self.logger.info("Shutting down AIAgentManager...")
        
        # Shutdown all agents that implement an async shutdown method
        shutdown_tasks = []
        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'shutdown') and asyncio.iscoroutinefunction(agent.shutdown):
                self.logger.debug("Shutting down agent: %s", agent_name)
                shutdown_tasks.append(agent.shutdown())
        
        # Wait for all agents to shutdown
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        # Clear state
        self.agents.clear()
        self.agent_configs.clear()
        self.processing_order.clear()
        self.initialized = False
        self.initialization_time = None
        
        self.logger.info("AIAgentManager shutdown complete")
    async def __aenter__(self) -> 'AIAgentManager':
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.shutdown()

    def __del__(self) -> None:
        """Cleanup on garbage collection."""
        if hasattr(self, 'initialized') and self.initialized:
            self.logger.warning("AIAgentManager destroyed without proper shutdown!")
    async def get_agent(self, agent_name: str) -> Optional[BaseAIAgent]:
        """Get an agent by name.
        
        Args:
            agent_name: Name of the agent to retrieve
            
        Returns:
            The agent instance if found, None otherwise
        """
        return self.agents.get(agent_name)
        
    async def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get status of a specific agent.
        
        Args:
            agent_name: Name of the agent to check
            
        Returns:
            Dict with agent status information
        """
        if agent_name not in self.agents:
            return {"status": "not_found", "error": f"Agent {agent_name} not found"}
            
        agent = self.agents[agent_name]
        status = {
            "name": agent_name,
            "initialized": self.initialized,
            "config": self.agent_configs.get(agent_name, {})
        }
        
        if hasattr(agent, 'get_status') and asyncio.iscoroutinefunction(agent.get_status):
            try:
                agent_status = await agent.get_status()
                status.update({"agent_status": agent_status})
            except Exception as e:
                status["status"] = "error"
                status["error"] = str(e)
        
        return status

    # ------------- Initialization ---------------------------------------------

    async def load_agent_configs(self) -> None:
        """
        Load agent metadata from YAML.

        Expected YAML shape:
        agents:
          - name: sir_hawkington
            module: app.ai_agents.sir_hawkington.agent
            class: SirHawkington
            role: "Triage & insights"
            retry_attempts: 2
            config:
              some_flag: true
        """
        try:
            with open(self.agent_config_path, "r") as f:
                data = yaml.safe_load(f) or {}

            agents_list = data.get("agents", [])
            if not isinstance(agents_list, list):
                raise ValueError("YAML key 'agents' must be a list")

            self.agent_configs.clear()
            self.processing_order.clear()

            for item in agents_list:
                mod_path = item["module"]
                cls_name = item["class"]
                agent_name = item["name"]

                mod = importlib.import_module(mod_path)
                cls = getattr(mod, cls_name)

                self.agent_configs[agent_name] = {
                    "class": cls,
                    "role": item.get("role", "Unknown"),
                    "retry_attempts": int(item.get("retry_attempts", 1)),
                    "config": item.get("config", {}) or {},
                }
                self.processing_order.append(agent_name)

            self.logger.info("✅ Loaded %d agent configs: %s",
                             len(self.agent_configs), self.processing_order)

        except Exception as e:
            self.logger.error("❌ Failed to load agent configs: %s", e, exc_info=True)
            raise

# imports you likely already have:
import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

# ...

async def initialize_agents(self):
    """
    Build shared services, then construct and initialize each agent exactly once.
    """
    if getattr(self, "initialized", False):
        self.logger.debug("🤖 Agents already initialized; skipping.")
        return

    await self.load_agent_configs()

    # Create shared memory service (uses db_getter internally)
    self.memory_service = AgentMemoryServiceWithCache(
        db_getter=self.db_getter,
        redis_url=self.redis_url,
        cache_ttl=self.cache_ttl,
    )
    # If the cache wrapper lazy-inits, finalize it once the loop is alive
    ensure_ready = getattr(self.memory_service, "ensure_ready", None)
    if ensure_ready and asyncio.iscoroutinefunction(ensure_ready):
        await ensure_ready()

    # ---- Phase 1: instantiate agents with NO kwargs ----
    temp_agents: Dict[str, Any] = {}
    created = 0
    for agent_name in self.processing_order:
        try:
            agent_class = self.agent_configs[agent_name]["class"]
            agent = agent_class()   # <-- no kwargs into __init__
            temp_agents[agent_name] = agent
            created += 1
        except Exception as e:
            self.logger.error("❌ Failed to instantiate agent '%s': %s", agent_name, e, exc_info=True)

    if created == 0:
        raise RuntimeError("No agents successfully initialized")

    # ---- Phase 2: resolve triage engine (Sir Hawkington) ----
    self.triage_engine = temp_agents.get("sir_hawkington")
    if not self.triage_engine:
        self.logger.warning("⚠️ Triage engine (sir_hawkington) not found; routing will be limited.")

    # ---- Phase 3: attach shared deps, apply config, and run optional initialize() ----
    self.agents = {}
    for agent_name in self.processing_order:
        agent = temp_agents.get(agent_name)
        if not agent:
            self.logger.warning("⚠️ Skipping missing agent '%s'", agent_name)
            continue

        # Attach shared deps after construction
        setattr(agent, "memory_service", self.memory_service)
        setattr(agent, "db_getter", self.db_getter)
        if self.triage_engine is not None:
            setattr(agent, "triage_engine", self.triage_engine)

        # Optional per-agent config
        agent_cfg = self.agent_configs[agent_name].get("config", {})
        configure_fn = getattr(agent, "configure", None)
        if configure_fn and callable(configure_fn):
            try:
                configure_fn(agent_cfg)
            except Exception as e:
                self.logger.error("⚠️ configure() failed for '%s': %s", agent_name, e, exc_info=True)

        # Validate interface
        self.ensure_agent_interface(agent, agent_name)

        # Optional async initialize
        init_fn = getattr(agent, "initialize", None)
        if init_fn and asyncio.iscoroutinefunction(init_fn):
            try:
                await init_fn()
            except Exception as e:
                self.logger.error("⚠️ initialize() failed for '%s': %s", agent_name, e, exc_info=True)

        self.agents[agent_name] = agent

    self.initialized = True
    self.initialization_time = datetime.now()
    self.logger.info("🤖 Initialized %d agents: %s", len(self.agents), list(self.agents.keys()))


    def ensure_agent_interface(self, agent: Any, name: str) -> None:
        """
        Make sure minimum interface exists; provide safe fallbacks for optional bits.
        Required: process_metrics (async), health_check (async).
        Optional: is_active, activate, deactivate, get_agent_status.
        """
        # Required
        if not hasattr(agent, "process_metrics"):
            raise ValueError(f"Agent '{name}' missing required method 'process_metrics'")
        if not hasattr(agent, "health_check"):
            raise ValueError(f"Agent '{name}' missing required method 'health_check'")

        # Optional niceties
        if not hasattr(agent, "is_active"):
            agent.is_active = True
        if not hasattr(agent, "activate"):
            agent.activate = lambda: setattr(agent, "is_active", True)
        if not hasattr(agent, "deactivate"):
            agent.deactivate = lambda: setattr(agent, "is_active", False)
        if not hasattr(agent, "get_agent_status"):
            agent.get_agent_status = lambda: {
                "status": "operational" if getattr(agent, "is_active", True) else "inactive",
                "name": name,
            }

    # ------------- Runtime -----------------------------------------------------
    async def process_metrics_through_triage_engine(self, metrics: dict, user_context: dict | None = None) -> dict:
        """Single entry: Hawk triages, then route to VIC-20 or Stick."""
        user_id = (user_context or {}).get("user_id") or "system"
        ts = metrics.get("timestamp")

        # 1) TRIAGE (Hawk)
        triage = await self.agents["sir_hawkington"].process_metrics(metrics, user_context)
        triage_severity = triage.get("severity")  # e.g., "LOW"|"MEDIUM"|"HIGH"|"CRITICAL"
        triage_reason   = triage.get("reason")
        await self.memory_service.store_memory(
            user_id=user_id, agent_name="sir_hawkington",
            memory_type="triage_decision",
            content={"metrics": metrics, "severity": triage_severity, "reason": triage_reason, "timestamp": ts},
            importance=5 if SEVERITY.get(triage_severity, 0) <= SEVERITY["MEDIUM"] else 7,
        )

        # LOW/MEDIUM: log only (Stick), no broadcast to agents
        if SEVERITY.get(triage_severity, 0) <= SEVERITY["MEDIUM"]:
            await self._stick_log("triage_low_medium", {
                "metrics": metrics, "triage": triage, "timestamp": ts
            }, user_id=user_id)
            return {
                "routed_by": "sir_hawkington",
                "triage_decision": triage,
                "disposition": "logged_only",
                "agent_dispatch": [],
                "results": [],
            }

        # 2) HIGH/CRITICAL → VIC-20 for plan
        vic20_plan = await self.agents["vic_20_sage"].process_metrics(metrics, user_context)
        # Expected shape (adjust if your Sage returns differently):
        # {
        #   "area_of_concern": "...",
        #   "target_agents": ["hamsters", "meth_snail"],
        #   "recommendations": [{"agent":"hamsters","action":"tune_cache",...}, ...],
        #   "cpu_issue": bool
        # }
        await self._stick_log("vic20_plan", {"plan": vic20_plan, "triage": triage, "timestamp": ts}, user_id=user_id)

        # Special: CPU loopback to Hawk
        if vic20_plan.get("cpu_issue"):
            # Reduce concurrency for next dispatch window
            await self._set_parallel_budget(max(1, self._base_parallel // 2))
            hawk_cpu = await self.agents["sir_hawkington"].handle_cpu_issue(metrics, user_context)
            await self._stick_log("hawk_cpu_followup", {"result": hawk_cpu, "timestamp": ts}, user_id=user_id)
            # Restore budget (optional, or use a timer)
            await self._set_parallel_budget(self._base_parallel)
            return {
                "routed_by": "sir_hawkington",
                "triage_decision": triage,
                "vic20_plan": vic20_plan,
                "cpu_followup": hawk_cpu,
                "disposition": "cpu_loopback",
                "agent_dispatch": [],
                "results": [],
            }

        # 3) Dispatch to target agents (bounded parallelism)
        targets = vic20_plan.get("target_agents", [])
        recs = vic20_plan.get("recommendations", [])
        rec_map = {r.get("agent"): r for r in recs if r.get("agent")}
        results = []

        async def _run(agent_key: str):
            async with self._sem:
                agent = self.agents.get(agent_key)
                if not agent:
                    return {"agent": agent_key, "error": "agent_not_found"}
                # Provide recommendation (agent may accept or choose its own fix)
                agent_rec = rec_map.get(agent_key)
                out = await agent.process_metrics({**metrics, "vic20_recommendation": agent_rec}, user_context)
                await self._stick_log("agent_result", {
                    "agent": agent_key,
                    "recommendation": agent_rec,
                    "result": out,
                    "timestamp": ts
                }, user_id=user_id)
                return {"agent": agent_key, "result": out}

        results = await asyncio.gather(*[_run(a) for a in targets], return_exceptions=True)

        return {
            "routed_by": "sir_hawkington",
            "triage_decision": triage,
            "vic20_plan": vic20_plan,
            "disposition": "routed_to_target_agents",
            "agent_dispatch": targets,
            "results": results,
        }

    async def _stick_log(self, event: str, payload: dict, *, user_id: str):
        await self.memory_service.store_memory(
            user_id=user_id, agent_name="the_stick",
            memory_type=f"log:{event}", content=payload, importance=4
        )

    async def _set_parallel_budget(self, n: int):
        # Replace semaphore with a new size (simple approach for now)
        self._sem = asyncio.Semaphore(max(1, int(n)))

    # async def process_metrics_through_triage_engine(
    #     metrics: dict, user_context: dict | None = None) -> dict:

    #     """
    #     Fan out a metrics payload to all active agents.
    #     Returns a dict of {agent_name: result_or_error}.
    #     """
    #     if not self.initialized:
    #         await self.initialize_agents()

    #     tasks = []
    #     for agent_name, agent in self.agents.items():
    #         if not getattr(agent, "is_active", True):
    #             continue
    #         if concurrent:
    #             tasks.append(
    #                 asyncio.create_task(
    #                     self._process_single_agent(agent_name, agent, metrics, user_context)
    #                 )
    #             )
    #         else:
    #             tasks.append(
    #                 await self._process_single_agent(agent_name, agent, metrics, user_context)
    #             )

    #     results: Dict[str, Any] = {}
    #     if concurrent:
    #         finished: List[Tuple[bool, Optional[Any], Optional[str], str]] = await asyncio.gather(
    #             *tasks, return_exceptions=False
    #         )
    #         for ok, payload, err, agent_name in finished:
    #             if ok:
    #                 results[agent_name] = payload
    #                 self.total_processing_count += 1
    #             else:
    #                 results[agent_name] = {"error": err}
    #     else:
    #         # sequential path already awaited; tasks hold tuples
    #         for ok, payload, err, agent_name in tasks:  # type: ignore
    #             if ok:
    #                 results[agent_name] = payload
    #                 self.total_processing_count += 1
    #             else:
    #                 results[agent_name] = {"error": err}

    #     return results

    # async def _process_single_agent(
    #     self,
    #     agent_name: str,
    #     agent: BaseAIAgent,
    #     metrics: Dict[str, Any],
    #     user_context: Optional[Dict[str, Any]] = None,
    # ) -> Tuple[bool, Optional[Any], Optional[str], str]:
    #     """
    #     Attempt the agent with retry policy (from YAML).
    #     """
    #     retry_attempts = int(self.agent_configs.get(agent_name, {}).get("retry_attempts", 1))
    #     last_error: Optional[str] = None

    #     for attempt in range(1, retry_attempts + 1):
    #         try:
    #             # Ensure we await agent.process_metrics if it's async
    #             result = agent.process_metrics(metrics, user_context)
    #             if asyncio.iscoroutine(result):
    #                 result = await result
    #             return True, result, None, agent_name
    #         except Exception as e:
    #             last_error = str(e)
    #             if attempt < retry_attempts:
    #                 self.logger.warning(
    #                     "⚠️ Agent '%s' attempt %d/%d failed: %s — retrying...",
    #                     agent_name, attempt, retry_attempts, last_error
    #                 )
    #                 await asyncio.sleep(0.5 * attempt)

    #     self.logger.error("❌ Agent '%s' failed after %d attempts: %s",
    #                       agent_name, retry_attempts, last_error)
    #     return False, None, last_error, agent_name

    async def health_check(self) -> Dict[str, Any]:
        """
        Poll each agent’s health_check; never raises, returns error payloads instead.
        """
        if not self.initialized:
            await self.initialize_agents()

        statuses: Dict[str, Any] = {}
        for name, agent in self.agents.items():
            try:
                status = agent.health_check()
                if asyncio.iscoroutine(status):
                    status = await status
                statuses[name] = status
            except Exception as e:
                statuses[name] = {"status": "error", "error": str(e)}
        return statuses

    async def shutdown_agent(self, name: str) -> Dict[str, Any]:
        """
        Optional graceful shutdown per agent (if the agent implements 'shutdown').
        """
        agent = self.agents.get(name)
        if not agent:
            return {"status": "not_found", "name": name}

        try:
            if hasattr(agent, "shutdown"):
                res = agent.shutdown()
                if asyncio.iscoroutine(res):
                    await res
            del self.agents[name]
            return {"status": "stopped", "name": name}
        except Exception as e:
            self.logger.error("Error shutting down agent '%s': %s", name, e, exc_info=True)
            return {"status": "error", "name": name, "error": str(e)}
