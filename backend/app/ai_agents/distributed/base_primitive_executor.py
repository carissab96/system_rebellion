#!/usr/bin/env python3
"""
Base Primitive Executor

The static layer of the intelligent execution architecture.
Knows HOW to run atomic system operations. Does NOT decide what to run.

Each agent domain subclasses this and registers its own primitives.
The ExecutionPlanner (base_execution_planner.py) sits above this and
composes sequences from registered primitives based on learned effectiveness.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional


@dataclass
class PrimitiveDefinition:
    """Definition of a single atomic system operation."""
    name: str
    command: Optional[str]          # Shell command, or None for Python impl
    requires_sudo: bool
    domain: str                     # Logical grouping: cleanup, optimization, log_management, archival
    description: str
    risk_level: int = 1             # 1-5, higher = more impactful/dangerous
    estimated_duration: float = 5.0  # Seconds — initial estimate, learned over time


@dataclass
class PrimitiveResult:
    """Result from executing a single primitive operation."""
    primitive_name: str
    success: bool
    pre_metrics: Dict[str, Any]
    post_metrics: Dict[str, Any]
    improvement: float              # Calculated delta (post vs pre), domain-specific
    duration_seconds: float
    error: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def failed(self) -> bool:
        return not self.success


class PrimitiveExecutor(ABC):
    """
    Executes atomic system operations for a specific agent domain.

    This is the ONLY static layer in the execution pipeline and it
    SHOULD be static — system commands are what they are. fstrim is
    fstrim. What's dynamic is which primitives get composed into
    sequences and in what order. That's the ExecutionPlanner's job.

    Subclasses implement domain-specific primitives and the
    _execute_python_primitive() method for operations that aren't
    simple shell commands.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"rebellion.{agent_name}.primitive_executor")
        self._primitives: Dict[str, PrimitiveDefinition] = {}
        self._register_primitives()
        self.logger.info(
            f"🔧 PrimitiveExecutor initialized for {agent_name} — "
            f"{len(self._primitives)} primitives registered: "
            f"{list(self._primitives.keys())}"
        )

    @abstractmethod
    def _register_primitives(self):
        """Register all primitive operations for this agent's domain."""
        pass

    @abstractmethod
    async def _execute_python_primitive(
        self, name: str, context: Dict[str, Any]
    ) -> PrimitiveResult:
        """Execute a primitive that requires Python implementation (no shell command)."""
        pass

    @abstractmethod
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics for this agent's domain."""
        pass

    @abstractmethod
    def _calculate_improvement(
        self, pre: Dict[str, Any], post: Dict[str, Any]
    ) -> float:
        """
        Calculate improvement from pre/post metrics.
        Domain-specific — disk improvement is different from CPU improvement.
        Returns float in [-1.0, 1.0]: positive = improvement, negative = degradation.
        """
        pass

    def register(self, primitive: PrimitiveDefinition):
        """Register a primitive operation."""
        self._primitives[primitive.name] = primitive

    def get_available_primitives(self) -> List[str]:
        """Return list of all registered primitive names."""
        return list(self._primitives.keys())

    def get_primitive(self, name: str) -> Optional[PrimitiveDefinition]:
        """Get primitive definition by name."""
        return self._primitives.get(name)

    async def execute(
        self, primitive_name: str, context: Dict[str, Any]
    ) -> PrimitiveResult:
        """
        Execute a single primitive operation with pre/post metrics.

        This is the atomic unit. It runs ONE thing. It collects metrics
        before and after. It returns a structured result. It does NOT
        decide what to run — that's the planner's job.
        """
        primitive = self._primitives.get(primitive_name)
        if primitive is None:
            self.logger.error(
                f"Unknown primitive '{primitive_name}' — "
                f"available: {self.get_available_primitives()}"
            )
            return PrimitiveResult(
                primitive_name=primitive_name,
                success=False,
                pre_metrics={},
                post_metrics={},
                improvement=0.0,
                duration_seconds=0.0,
                error=f"Unknown primitive: {primitive_name}"
            )

        # Collect pre-execution metrics
        try:
            pre_metrics = await self._collect_metrics()
        except Exception as e:
            self.logger.error(
                f"Failed to collect pre-metrics for '{primitive_name}': {e}"
            )
            pre_metrics = {"collection_failed": True, "error": str(e)}

        # Execute
        start_time = time.monotonic()
        try:
            if primitive.command is not None:
                raw_result = await self._execute_shell_primitive(primitive, context)
            else:
                raw_result = await self._execute_python_primitive(primitive_name, context)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            duration = time.monotonic() - start_time
            self.logger.error(
                f"Primitive '{primitive_name}' raised exception: {e}",
                exc_info=True
            )
            return PrimitiveResult(
                primitive_name=primitive_name,
                success=False,
                pre_metrics=pre_metrics,
                post_metrics={},
                improvement=0.0,
                duration_seconds=duration,
                error=str(e)
            )

        duration = time.monotonic() - start_time

        # Collect post-execution metrics
        try:
            post_metrics = await self._collect_metrics()
        except Exception as e:
            self.logger.error(
                f"Failed to collect post-metrics for '{primitive_name}': {e}"
            )
            post_metrics = {"collection_failed": True, "error": str(e)}

        # Calculate improvement from first pre to last post
        if pre_metrics.get("collection_failed") or post_metrics.get("collection_failed"):
            improvement = 0.0
        else:
            improvement = self._calculate_improvement(pre_metrics, post_metrics)

        return PrimitiveResult(
            primitive_name=primitive_name,
            success=raw_result.success,
            pre_metrics=pre_metrics,
            post_metrics=post_metrics,
            improvement=improvement,
            duration_seconds=duration,
            stdout=raw_result.stdout,
            stderr=raw_result.stderr,
            error=raw_result.error
        )

    async def _execute_shell_primitive(
        self, primitive: PrimitiveDefinition, context: Dict[str, Any]
    ) -> PrimitiveResult:
        """Execute a shell command primitive."""
        command = primitive.command
        if primitive.requires_sudo:
            command = f"sudo {command}"

        timeout = context.get('timeout', 300)

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            stdout = stdout_bytes.decode() if stdout_bytes else None
            stderr = stderr_bytes.decode() if stderr_bytes else None
            success = (process.returncode == 0)

            if not success:
                self.logger.warning(
                    f"Shell primitive '{primitive.name}' exited {process.returncode}: "
                    f"{stderr[:200] if stderr else 'no stderr'}"
                )

            return PrimitiveResult(
                primitive_name=primitive.name,
                success=success,
                pre_metrics={},
                post_metrics={},
                improvement=0.0,
                duration_seconds=0.0,
                stdout=stdout,
                stderr=stderr,
                error=stderr if not success else None
            )

        except asyncio.TimeoutError:
            self.logger.error(
                f"Primitive '{primitive.name}' timed out after {timeout}s"
            )
            return PrimitiveResult(
                primitive_name=primitive.name,
                success=False,
                pre_metrics={},
                post_metrics={},
                improvement=0.0,
                duration_seconds=float(timeout),
                error=f"Timeout after {timeout}s"
            )
