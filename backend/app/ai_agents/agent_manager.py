"""
AI Agent Manager — unified, async-safe, with Redis-cached memory injection
"""

from __future__ import annotations

import asyncio
import importlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# ⬇️ Adjust these imports to your project layout
from app.ai_agents.base_agent import BaseAIAgent  # must expose process_metrics, health_check
from app.services.memory_redis_patch.agent_memory_service_with_cache import (
    AgentMemoryServiceWithCache,
)

logger = logging.getLogger("AIAgentManager")

# --- Singleton helpers --------------------------------------------------------

_agent_manager_instance: Optional["AIAgentManager"] = None
_initialization_lock = asyncio.Lock()


async def get_agent_manager(
    db_getter=None,
    agent_config_path: str = "app/ai_agents/agents_config.yaml",
    triage_engine=None,
    redis_url: str = "redis://localhost:6379",
    cache_ttl: int = 300,
) -> "AIAgentManager":
    """
    Async-safe singleton accessor. Creates and initializes once.
    """
    global _agent_manager_instance
    if _agent_manager_instance is None:
        async with _initialization_lock:
            if _agent_manager_instance is None:
                mgr = AIAgentManager(
                    db_getter=db_getter,
                    agent_config_path=agent_config_path,
                    triage_engine=triage_engine,
                    redis_url=redis_url,
                    cache_ttl=cache_ttl,
                )
                await mgr.initialize_agents()
                _agent_manager_instance = mgr
    return _agent_manager_instance


# --- Manager ------------------------------------------------------------------

class AIAgentManager:
    def __init__(
        self,
        db_getter=None,
        agent_config_path: str = "app/ai_agents/agents_config.yaml",
        triage_engine=None,
        redis_url: str = "redis://localhost:6379",
        cache_ttl: int = 300,
    ):
        """
        db_getter: callable used by agents/services to obtain AsyncSession or a sessionmaker.
        agent_config_path: YAML file with a top-level 'agents' list.
        triage_engine: optional reference injected into agents that need it.
        redis_url/cache_ttl: passed to AgentMemoryServiceWithCache.
        """
        self.db_getter = db_getter
        self.agent_config_path = str(Path(agent_config_path))
        self.triage_engine = triage_engine

        self.redis_url = redis_url
        self.cache_ttl = cache_ttl

        self.agent_configs: Dict[str, Dict[str, Any]] = {}
        self.processing_order: List[str] = []
        self.agents: Dict[str, BaseAIAgent] = {}

        self.initialized: bool = False
        self.initialization_time: Optional[datetime] = None
        self.total_processing_count: int = 0

        # Shared service injected once and passed to all agents
        self.memory_service: Optional[AgentMemoryServiceWithCache] = None

        self.logger = logger

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

    async def initialize_agents(self) -> None:
        """
        Build shared services, then construct and initialize each agent exactly once.
        """
        if self.initialized:
            self.logger.debug("🤖 Agents already initialized; skipping.")
            return

        await self.load_agent_configs()

        # Create shared memory service (uses db_getter internally)
        # NOTE: we pass the db_getter so the service can acquire sessions per call.
        self.memory_service = AgentMemoryServiceWithCache(
            db_getter=self.db_getter,
            redis_url=self.redis_url,
            cache_ttl=self.cache_ttl,
        )

        # Spin up agents in the configured order
        created = 0
        for agent_name in self.processing_order:
            agent_config = self.agent_configs[agent_name]
            agent = await self.initialize_agent(agent_name, agent_config)
            if agent:
                self.agents[agent_name] = agent
                created += 1
            else:
                self.logger.warning("⚠️ Continuing without agent '%s'", agent_name)

        if created == 0:
            raise RuntimeError("No agents successfully initialized")

        self.initialized = True
        self.initialization_time = datetime.now()
        self.logger.info("🤖 Initialized %d agents: %s", created, list(self.agents.keys()))

    async def initialize_agent(
        self, agent_name: str, agent_config: Dict[str, Any]
    ) -> Optional[BaseAIAgent]:
        """
        Create, sanity-check, and initialize a single agent.
        """
        try:
            agent_class = agent_config["class"]

            # Pass common deps to every agent (db_getter, memory service, triage engine, and any custom config)
            agent = agent_class(
                db_getter=self.db_getter,
                memory_service=self.memory_service,
                triage_engine=self.triage_engine,
                **agent_config.get("config", {}),
            )

            self.ensure_agent_interface(agent, agent_name)

            # If the agent exposes an async initialize, call it
            init_fn = getattr(agent, "initialize", None)
            if init_fn and asyncio.iscoroutinefunction(init_fn):
                await init_fn()

            self.logger.info("✅ Initialized agent '%s' (%s)", agent_name, agent_config.get("role", ""))
            return agent

        except Exception as e:
            self.logger.error("❌ Failed to initialize agent '%s': %s", agent_name, e, exc_info=True)
            return None

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

    async def process_metrics_through_agents(
        self,
        metrics: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
        concurrent: bool = True,
    ) -> Dict[str, Any]:
        """
        Fan out a metrics payload to all active agents.
        Returns a dict of {agent_name: result_or_error}.
        """
        if not self.initialized:
            await self.initialize_agents()

        tasks = []
        for agent_name, agent in self.agents.items():
            if not getattr(agent, "is_active", True):
                continue
            if concurrent:
                tasks.append(
                    asyncio.create_task(
                        self._process_single_agent(agent_name, agent, metrics, user_context)
                    )
                )
            else:
                tasks.append(
                    await self._process_single_agent(agent_name, agent, metrics, user_context)
                )

        results: Dict[str, Any] = {}
        if concurrent:
            finished: List[Tuple[bool, Optional[Any], Optional[str], str]] = await asyncio.gather(
                *tasks, return_exceptions=False
            )
            for ok, payload, err, agent_name in finished:
                if ok:
                    results[agent_name] = payload
                    self.total_processing_count += 1
                else:
                    results[agent_name] = {"error": err}
        else:
            # sequential path already awaited; tasks hold tuples
            for ok, payload, err, agent_name in tasks:  # type: ignore
                if ok:
                    results[agent_name] = payload
                    self.total_processing_count += 1
                else:
                    results[agent_name] = {"error": err}

        return results

    async def _process_single_agent(
        self,
        agent_name: str,
        agent: BaseAIAgent,
        metrics: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[Any], Optional[str], str]:
        """
        Attempt the agent with retry policy (from YAML).
        """
        retry_attempts = int(self.agent_configs.get(agent_name, {}).get("retry_attempts", 1))
        last_error: Optional[str] = None

        for attempt in range(1, retry_attempts + 1):
            try:
                # Ensure we await agent.process_metrics if it's async
                result = agent.process_metrics(metrics, user_context)
                if asyncio.iscoroutine(result):
                    result = await result
                return True, result, None, agent_name
            except Exception as e:
                last_error = str(e)
                if attempt < retry_attempts:
                    self.logger.warning(
                        "⚠️ Agent '%s' attempt %d/%d failed: %s — retrying...",
                        agent_name, attempt, retry_attempts, last_error
                    )
                    await asyncio.sleep(0.5 * attempt)

        self.logger.error("❌ Agent '%s' failed after %d attempts: %s",
                          agent_name, retry_attempts, last_error)
        return False, None, last_error, agent_name

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
