"""
AI Agent Manager - Refactored with Dynamic Loading, Async Queue Processing, Metrics Versioning, and Triage Engine Integration
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from functools import wraps
import importlib
import yaml
from pathlib import Path
from app.ai_agents.base_agent import BaseAIAgent

logger = logging.getLogger(__name__)

_initialization_lock = asyncio.Lock()
_agent_manager_instance = None


def retry_on_failure(max_attempts: int = 3, delay: float = 0.5):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator


class AIAgentManager:
    def __init__(self, db_getter=None, agent_config_path: str = 'app/ai_agents/agents_config.yaml', triage_engine=None):
        self.db_getter = db_getter
        self.agent_config_path = agent_config_path
        self.agent_configs: Dict[str, Any] = {}
        self.agents: Dict[str, BaseAIAgent] = {}
        self.triage_engine = triage_engine
        self.initialized = False
        self.initialization_time = datetime.now()
        self.processing_order: List[str] = []
        self.total_processing_count = 0
        self.logger = logging.getLogger("AIAgentManager")

    async def initialize_agents(self):
        if self.initialized:
            self.logger.debug("🤖 Agents already initialized, skipping")
            return

        await self.load_agent_configs()

        for agent_name, agent_config in self.agent_configs.items():
            agent = await self.initialize_agent(agent_name, agent_config)
            if agent:
                self.agents[agent_name] = agent
            else:
                self.logger.warning(f"⚠️ Continuing without {agent_name}")

        if not self.agents:
            raise Exception("No agents successfully initialized")

        self.initialized = True
        self.logger.info(f"🤖 Initialized {len(self.agents)} agents: {list(self.agents.keys())}")

    async def load_agent_configs(self):
        """Load agent definitions from YAML file (supports top-level 'agents' key)."""
        try:
            with open(self.agent_config_path) as f:
                config_data = yaml.safe_load(f)

            agent_list = config_data.get('agents', [])
            if not isinstance(agent_list, list):
                raise ValueError("YAML 'agents' key must contain a list of agent definitions")

            for agent_info in agent_list:
                mod = importlib.import_module(agent_info['module'])
                cls = getattr(mod, agent_info['class'])
                self.agent_configs[agent_info['name']] = {
                    'class': cls,
                    'role': agent_info.get('role', 'Unknown'),
                    'retry_attempts': agent_info.get('retry_attempts', 1),
                    'config': agent_info.get('config', {})
                }
                self.processing_order.append(agent_info['name'])

            self.logger.info(f"✅ Loaded {len(agent_list)} agent configs from YAML")

        except Exception as e:
            self.logger.error(f"❌ Failed to load agent configs: {e}")
            raise

    async def initialize_agent(self, agent_name: str, agent_config: Dict[str, Any]) -> Optional[BaseAIAgent]:
        try:
            agent_class = agent_config['class']
            agent = agent_class(db_getter=self.db_getter, **agent_config.get('config', {}))
            self.ensure_agent_interface(agent, agent_name)

            if hasattr(agent, 'initialize'):
                await agent.initialize()

            self.logger.info(f"✅ Initialized {agent_name}: {agent_config['role']}")
            return agent
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {agent_name}: {e}")
            return None

    def ensure_agent_interface(self, agent: Any, name: str):
        if not hasattr(agent, 'is_active'):
            agent.is_active = True
        if not hasattr(agent, 'activate'):
            agent.activate = lambda: setattr(agent, 'is_active', True)
        if not hasattr(agent, 'deactivate'):
            agent.deactivate = lambda: setattr(agent, 'is_active', False)
        if not hasattr(agent, 'process_metrics'):
            self._logger.warning(f"Agent '{name}' missing process_metrics method")
        if not hasattr(agent, 'get_agent_status'):
            agent.get_agent_status = lambda: {
                'status': 'operational' if agent.is_active else 'inactive',
                'name': name
            }
    async def _process_single_agent(self, agent_name: str, agent: BaseAIAgent, metrics: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        retry_attempts = self.agent_configs.get(agent_name, {}).get('retry_attempts', 1)
        last_error = None
        for attempt in range(retry_attempts):
            try:
                result = await agent.process_metrics(metrics, user_context)
                return True, result, None
            except Exception as e:
                last_error = str(e)
                if attempt < retry_attempts - 1:
                    self.logger.warning(f"⚠️ Agent '{agent_name}' attempt {attempt+1} failed, retrying...")
                    await asyncio.sleep(0.5 * (attempt + 1))
        return False, None, last_error

    async def process_metrics_through_agents(self, metrics: Union[Dict[str, Any], str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.triage_engine:
            routing_decision = await self.triage_engine.route_metrics(metrics, user_context)
            if routing_decision == 'skip_specialists':
                return metrics

        if not self._initialized:
            await self.initialize_agents()

        self.total_processing_count += 1

        if isinstance(metrics, dict):
            enhanced_metrics = metrics.copy()
        elif isinstance(metrics, str):
            import json
            try:
                enhanced_metrics = json.loads(metrics)
            except (ValueError, json.JSONDecodeError):
                enhanced_metrics = {'raw_data': metrics}
        else:
            enhanced_metrics = {'data': metrics} if metrics is not None else {}

        metrics_version = enhanced_metrics.get('agent_processing', {}).get('version', 0) + 1
        enhanced_metrics['agent_processing'] = {
            'version': metrics_version,
            'timestamp': datetime.now().isoformat(),
            'agents': {}
        }

        async def run_agent(agent_name: str):
            agent = self.agents[agent_name]
            if not getattr(agent, 'is_active', True):
                return agent_name, None, 'inactive'
            success, result, error = await self._process_single_agent(agent_name, agent, enhanced_metrics, user_context)
            return agent_name, result if success else None, error

        tasks = [run_agent(name) for name in self.processing_order if name in self.agents]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        for agent_name, agent_result, error in results:
            enhanced_metrics['agent_processing']['agents'][agent_name] = {
                'processed_at': datetime.now().isoformat(),
                'result': agent_result,
                'error': error
            }
            if agent_result:
                enhanced_metrics = self._merge_agent_results(enhanced_metrics, agent_name, agent_result)

        return enhanced_metrics

    def _merge_agent_results(self, base_metrics: Dict[str, Any], agent_name: str, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(agent_result, dict):
            base_metrics[agent_name] = agent_result
            return base_metrics
        base_metrics.update({k: v for k, v in agent_result.items() if k not in base_metrics})
        return base_metrics

    async def get_agent_status(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        if agent_name:
            agent = self.agents.get(agent_name)
            if not agent:
                return {'error': f"Agent {agent_name} not found"}
            status = agent.get_agent_status() if hasattr(agent, 'get_agent_status') else {}
            status.update({
                'agent_name': agent_name,
                'is_active': getattr(agent, 'is_active', True),
                'role': self.agent_configs.get(agent_name, {}).get('role', 'Unknown'),
                'retry_attempts': self.agent_configs.get(agent_name, {}).get('retry_attempts', 1)
            })
            return status
        all_status = {}
        for name, agent in self.agents.items():
            all_status[name] = await self.get_agent_status(name)
        return all_status

    async def activate_agent(self, agent_name: str) -> bool:
        agent = self.agents.get(agent_name)
        if agent:
            agent.activate() if hasattr(agent, 'activate') else setattr(agent, 'is_active', True)
            return True
        return False

    async def deactivate_agent(self, agent_name: str) -> bool:
        agent = self.agents.get(agent_name)
        if agent:
            agent.deactivate() if hasattr(agent, 'deactivate') else setattr(agent, 'is_active', False)
            return True
        return False

    async def shutdown(self):
        tasks = [self._shutdown_agent(name, agent) for name, agent in self.agents.items() if hasattr(agent, 'shutdown')]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.agents.clear()
        self._initialized = False

    async def _shutdown_agent(self, agent_name: str, agent: BaseAIAgent):
        try:
            await agent.shutdown()
        except Exception as e:
            self.logger.error(f"❌ Error shutting down {agent_name}: {e}")

    async def health_check(self) -> Dict[str, Any]:
        try:
            if not self._initialized:
                await self.initialize_agents()
            agent_health = {}
            for name, agent in self.agents.items():
                if hasattr(agent, 'health_check'):
                    try:
                        agent_health[name] = await agent.health_check()
                    except Exception as e:
                        agent_health[name] = {'status': 'error', 'error': str(e)}
                else:
                    agent_health[name] = {'status': 'operational' if getattr(agent, 'is_active', True) else 'inactive'}
            return {
                'status': 'OPERATIONAL',
                'total_agents': len(self.agents),
                'active_agents': sum(1 for a in self.agents.values() if getattr(a, 'is_active', True)),
                'agent_health': agent_health,
                'total_processing_count': self.total_processing_count,
                'uptime_seconds': (datetime.now() - self.initialization_time).total_seconds(),
                'last_health_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'FAILED', 'error': str(e), 'last_health_check': datetime.now().isoformat()}


async def get_agent_manager(triage_engine=None):
    global _agent_manager_instance
    if _agent_manager_instance is None:
        async with _initialization_lock:
            if _agent_manager_instance is None:
                _agent_manager_instance = AIAgentManager(triage_engine=triage_engine)
                await _agent_manager_instance.initialize_agents()
    return _agent_manager_instance

