#!/usr/bin/env python3
"""
Terry's Primitive Executor

Atomic system operations for CPU and memory management.
Each primitive is a single, reversible (where possible) system action.

10 primitives:
  Memory:  sync_filesystem, drop_page_cache, drop_slab_cache, drop_all_caches, compact_memory
  CPU:     kill_memory_hog, renice_cpu_hog, throttle_cpu_process
  Swap:    adjust_swappiness
  Service: restart_service

The base class execute() handles pre/post metric collection — Python primitives
do NOT need to call _collect_metrics() themselves.
"""

import asyncio
import logging
import os
import signal
import time
from typing import Any, Dict

from app.ai_agents.distributed.base_primitive_executor import (
    PrimitiveDefinition,
    PrimitiveExecutor,
    PrimitiveResult,
)

logger = logging.getLogger('TerryPrimitiveExecutor')


# Processes that must never be killed, regardless of memory consumption.
# Terry will skip these and find the next highest consumer.
PROTECTED_PROCESSES = frozenset([
    'systemd', 'init', 'kthreadd', 'kworker',
    'sshd', 'sudo', 'su',
    'postgres', 'postgresql',
    'redis-server', 'redis',
    'nginx',
    'python3', 'python',   # gunicorn workers — Terry should not kill himself
    'gunicorn',
    'bash', 'sh', 'zsh',
])


class TerryPrimitiveExecutor(PrimitiveExecutor):
    """
    Terry's primitive executor for CPU and memory operations.

    ⚡ "I don't just pick actions. I EXECUTE them. With PRECISION."
    """

    def __init__(self):
        super().__init__(agent_name='meth_snail')

    # =========================================================================
    # Registration
    # =========================================================================

    def _register_primitives(self):
        """Register all 10 Terry primitives."""
        primitives = [
            PrimitiveDefinition(
                name='sync_filesystem',
                command='sync',
                requires_sudo=False,
                domain='memory',
                description='Flush filesystem buffers to disk before cache drop',
                risk_level=1,
                estimated_duration=2.0,
            ),
            PrimitiveDefinition(
                name='drop_page_cache',
                command='echo 1 | sudo tee /proc/sys/vm/drop_caches',
                requires_sudo=False,  # command already contains sudo tee
                domain='memory',
                description='Drop page cache (file data cache) — safe, kernel re-reads on demand',
                risk_level=1,
                estimated_duration=3.0,
            ),
            PrimitiveDefinition(
                name='drop_slab_cache',
                command='echo 2 | sudo tee /proc/sys/vm/drop_caches',
                requires_sudo=False,
                domain='memory',
                description='Drop slab cache (dentries/inodes) — safe, kernel rebuilds on demand',
                risk_level=1,
                estimated_duration=3.0,
            ),
            PrimitiveDefinition(
                name='drop_all_caches',
                command='echo 3 | sudo tee /proc/sys/vm/drop_caches',
                requires_sudo=False,
                domain='memory',
                description='Drop page + slab caches — most aggressive cache reclaim',
                risk_level=2,
                estimated_duration=5.0,
            ),
            PrimitiveDefinition(
                name='compact_memory',
                command='echo 1 | sudo tee /proc/sys/vm/compact_memory',
                requires_sudo=False,
                domain='memory',
                description='Trigger kernel memory compaction to reduce fragmentation',
                risk_level=2,
                estimated_duration=10.0,
            ),
            PrimitiveDefinition(
                name='kill_memory_hog',
                command=None,  # Python impl — reads /proc directly
                requires_sudo=False,
                domain='memory',
                description='SIGTERM then SIGKILL the top memory-consuming process',
                risk_level=4,
                estimated_duration=5.0,
            ),
            PrimitiveDefinition(
                name='renice_cpu_hog',
                command=None,  # Python impl — os.setpriority with sudo renice fallback
                requires_sudo=False,
                domain='cpu',
                description='Lower priority of top CPU-consuming process (nice +10)',
                risk_level=2,
                estimated_duration=2.0,
            ),
            PrimitiveDefinition(
                name='adjust_swappiness',
                command=None,  # Python impl — sysctl
                requires_sudo=False,
                domain='swap',
                description='Lower vm.swappiness to keep more data in RAM',
                risk_level=2,
                estimated_duration=1.0,
            ),
            PrimitiveDefinition(
                name='restart_service',
                command=None,  # Python impl — systemctl, requires context['service_name']
                requires_sudo=False,
                domain='service',
                description='Restart a named systemd service',
                risk_level=4,
                estimated_duration=15.0,
            ),
            PrimitiveDefinition(
                name='throttle_cpu_process',
                command=None,  # Python impl — cpulimit with renice fallback
                requires_sudo=False,
                domain='cpu',
                description='Throttle CPU usage of top consumer via cpulimit or renice',
                risk_level=2,
                estimated_duration=3.0,
            ),
        ]
        for p in primitives:
            self.register(p)

    # =========================================================================
    # Python primitive dispatch — dict replaces if/elif chain
    # =========================================================================

    # Maps primitive name → handler method name (string for late binding)
    _PYTHON_DISPATCH: Dict[str, str] = {
        'kill_memory_hog':      '_run_kill_memory_hog',
        'renice_cpu_hog':       '_run_renice_cpu_hog',
        'adjust_swappiness':    '_run_adjust_swappiness',
        'restart_service':      '_run_restart_service',
        'throttle_cpu_process': '_run_throttle_cpu_process',
    }

    async def _execute_python_primitive(
        self, name: str, context: Dict[str, Any]
    ) -> PrimitiveResult:
        """Dispatch to the correct Python handler via _PYTHON_DISPATCH dict."""
        handler_name = self._PYTHON_DISPATCH.get(name)
        if handler_name is None:
            self.logger.error(
                f" No Python handler for primitive '{name}'. "
                f"Known handlers: {list(self._PYTHON_DISPATCH.keys())}"
            )
            return PrimitiveResult(
                primitive_name=name,
                success=False,
                pre_metrics={},
                post_metrics={},
                improvement=0.0,
                duration_seconds=0.0,
                error=f"No Python handler registered for '{name}'"
            )
        handler = getattr(self, handler_name)
        return await handler(name, context)

    # =========================================================================
    # Metric collection
    # =========================================================================

    async def _collect_metrics(self) -> Dict[str, Any]:
        """
        Collect current CPU and memory metrics from /proc.

        Raises on failure — base class execute() catches and marks
        collection_failed=True so improvement calculation is skipped.
        """
        memory_usage = self._read_memory_usage()
        cpu_usage = await self._read_cpu_usage()
        load_average = self._read_load_average()
        swap_usage = self._read_swap_usage()

        return {
            'memory_usage': memory_usage,
            'cpu_usage': cpu_usage,
            'load_average': load_average,
            'swap_usage': swap_usage,
        }

    def _read_memory_usage(self) -> float:
        """Read memory usage % from /proc/meminfo. Raises on failure."""
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        info = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                info[parts[0].rstrip(':')] = int(parts[1])
        total = info['MemTotal']
        available = info['MemAvailable']
        return round((total - available) / total * 100.0, 2)

    async def _read_cpu_usage(self) -> float:
        """
        Read CPU usage % from /proc/stat with a 200ms sample.

        Raises on failure — let _collect_metrics() propagate to base class.
        """
        def _read_stat():
            with open('/proc/stat', 'r') as f:
                line = f.readline()
            parts = line.split()
            # parts[0] == 'cpu', parts[1:] == user nice system idle iowait irq softirq ...
            values = [int(x) for x in parts[1:]]
            idle = values[3]
            total = sum(values)
            return idle, total

        idle1, total1 = _read_stat()
        await asyncio.sleep(0.2)
        idle2, total2 = _read_stat()

        delta_total = total2 - total1
        delta_idle = idle2 - idle1

        if delta_total == 0:
            raise RuntimeError("CPU stat delta is zero — /proc/stat may not have updated")

        return round((1.0 - delta_idle / delta_total) * 100.0, 2)

    def _read_load_average(self) -> float:
        """
        Read 1-minute load average from /proc/loadavg.

        Raises on failure — let _collect_metrics() propagate to base class.
        """
        with open('/proc/loadavg', 'r') as f:
            content = f.read()
        parts = content.split()
        if not parts:
            raise RuntimeError("/proc/loadavg is empty")
        return float(parts[0])

    def _read_swap_usage(self) -> float:
        """Read swap usage % from /proc/meminfo. Returns 0.0 if no swap configured."""
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        info = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                info[parts[0].rstrip(':')] = int(parts[1])
        swap_total = info.get('SwapTotal', 0)
        if swap_total == 0:
            return 0.0
        swap_free = info.get('SwapFree', 0)
        return round((swap_total - swap_free) / swap_total * 100.0, 2)

    # =========================================================================
    # Improvement calculation
    # =========================================================================

    def _calculate_improvement(
        self, pre: Dict[str, Any], post: Dict[str, Any]
    ) -> float:
        """
        Weighted improvement across memory (0.5), CPU (0.3), swap (0.2).

        Positive = improvement (metrics went down).
        Negative = degradation (metrics went up).
        """
        memory_delta = pre.get('memory_usage', 0) - post.get('memory_usage', 0)
        cpu_delta = pre.get('cpu_usage', 0) - post.get('cpu_usage', 0)
        swap_delta = pre.get('swap_usage', 0) - post.get('swap_usage', 0)

        # Normalise to 0-1 range (metrics are 0-100%)
        weighted = (
            (memory_delta / 100.0) * 0.5 +
            (cpu_delta / 100.0) * 0.3 +
            (swap_delta / 100.0) * 0.2
        )
        return round(weighted, 4)

    # =========================================================================
    # Python primitive handlers
    # =========================================================================

    async def _run_kill_memory_hog(
        self, name: str, context: Dict[str, Any]
    ) -> PrimitiveResult:
        """Kill the top memory-consuming process. SIGTERM first, SIGKILL after 5s."""
        start = time.monotonic()
        try:
            pid = context.get('pid')
            process_name = context.get('process_name', 'unknown')

            if pid is None:
                # Identify from /proc directly
                pid, process_name = self._find_top_memory_process()

            if pid is None:
                return PrimitiveResult(
                    primitive_name=name, success=False,
                    pre_metrics={}, post_metrics={}, improvement=0.0,
                    duration_seconds=time.monotonic() - start,
                    error="Could not identify target process from /proc"
                )

            self.logger.info(f" Sending SIGTERM to {process_name} (pid={pid})")
            os.kill(pid, signal.SIGTERM)
            await asyncio.sleep(5.0)

            # Check if still alive
            try:
                os.kill(pid, 0)  # Signal 0 = existence check
                self.logger.warning(
                    f" {process_name} (pid={pid}) still alive after SIGTERM — sending SIGKILL"
                )
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Already dead — good

            return PrimitiveResult(
                primitive_name=name, success=True,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=f"Killed {process_name} (pid={pid})"
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e)
            )

    async def _run_renice_cpu_hog(
        self, name: str, context: Dict[str, Any]
    ) -> PrimitiveResult:
        """Lower priority of top CPU consumer. os.setpriority first, sudo renice fallback."""
        start = time.monotonic()
        try:
            pid = context.get('pid')
            process_name = context.get('process_name', 'unknown')
            nice_value = context.get('nice_value', 10)

            if pid is None:
                pid, process_name = self._find_top_cpu_process()

            if pid is None:
                return PrimitiveResult(
                    primitive_name=name, success=False,
                    pre_metrics={}, post_metrics={}, improvement=0.0,
                    duration_seconds=time.monotonic() - start,
                    error="Could not identify target process from /proc"
                )

            try:
                os.setpriority(os.PRIO_PROCESS, pid, nice_value)
                self.logger.info(
                    f" Reniced {process_name} (pid={pid}) to nice={nice_value}"
                )
                return PrimitiveResult(
                    primitive_name=name, success=True,
                    pre_metrics={}, post_metrics={}, improvement=0.0,
                    duration_seconds=time.monotonic() - start,
                    stdout=f"Reniced {process_name} (pid={pid}) to {nice_value}"
                )
            except PermissionError:
                # Fall back to sudo renice
                proc = await asyncio.create_subprocess_exec(
                    'sudo', 'renice', str(nice_value), '-p', str(pid),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=10)
                success = (proc.returncode == 0)
                return PrimitiveResult(
                    primitive_name=name, success=success,
                    pre_metrics={}, post_metrics={}, improvement=0.0,
                    duration_seconds=time.monotonic() - start,
                    stdout=stdout_b.decode() if stdout_b else None,
                    stderr=stderr_b.decode() if stderr_b else None,
                    error=None if success else f"sudo renice exited {proc.returncode}"
                )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e)
            )

    async def _run_adjust_swappiness(
        self, name: str, context: Dict[str, Any]
    ) -> PrimitiveResult:
        """Lower vm.swappiness via sysctl to keep more data in RAM."""
        start = time.monotonic()
        try:
            target = context.get('swappiness', 10)
            proc = await asyncio.create_subprocess_exec(
                'sudo', 'sysctl', f'vm.swappiness={target}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=10)
            success = (proc.returncode == 0)
            return PrimitiveResult(
                primitive_name=name, success=success,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=stdout_b.decode() if stdout_b else None,
                stderr=stderr_b.decode() if stderr_b else None,
                error=None if success else f"sysctl exited {proc.returncode}"
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e)
            )

    async def _run_restart_service(
        self, name: str, context: Dict[str, Any]
    ) -> PrimitiveResult:
        """Restart a named systemd service. Requires context['service_name']."""
        start = time.monotonic()
        service_name = context.get('service_name')
        if not service_name:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error="restart_service requires context['service_name'] — primitive cannot proceed"
            )
        try:
            proc = await asyncio.create_subprocess_exec(
                'sudo', 'systemctl', 'restart', service_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=60)
            success = (proc.returncode == 0)
            return PrimitiveResult(
                primitive_name=name, success=success,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=stdout_b.decode() if stdout_b else None,
                stderr=stderr_b.decode() if stderr_b else None,
                error=None if success else f"systemctl restart {service_name} exited {proc.returncode}"
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e)
            )

    async def _run_throttle_cpu_process(
        self, name: str, context: Dict[str, Any]
    ) -> PrimitiveResult:
        """Throttle CPU usage via cpulimit. Falls back to renice if cpulimit unavailable."""
        start = time.monotonic()
        try:
            pid = context.get('pid')
            process_name = context.get('process_name', 'unknown')
            cpu_limit = context.get('cpu_limit', 50)  # % of one core

            if pid is None:
                pid, process_name = self._find_top_cpu_process()

            if pid is None:
                return PrimitiveResult(
                    primitive_name=name, success=False,
                    pre_metrics={}, post_metrics={}, improvement=0.0,
                    duration_seconds=time.monotonic() - start,
                    error="Could not identify target process from /proc"
                )

            # Try cpulimit first
            try:
                proc = await asyncio.create_subprocess_exec(
                    'cpulimit', '--pid', str(pid), '--limit', str(cpu_limit),
                    '--background',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=10)
                if proc.returncode == 0:
                    return PrimitiveResult(
                        primitive_name=name, success=True,
                        pre_metrics={}, post_metrics={}, improvement=0.0,
                        duration_seconds=time.monotonic() - start,
                        stdout=f"cpulimit applied {cpu_limit}% to {process_name} (pid={pid})"
                    )
            except (FileNotFoundError, asyncio.TimeoutError):
                pass  # cpulimit not available — fall through to renice

            # Renice fallback
            return await self._run_renice_cpu_hog(name, context)

        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e)
            )

    # =========================================================================
    # /proc helpers
    # =========================================================================

    def _find_top_memory_process(self):
        """Find the PID and name of the top memory-consuming process from /proc.
        
        Skips processes in PROTECTED_PROCESSES — never kills sshd, systemd,
        postgres, gunicorn workers, etc.
        """
        top_pid = None
        top_name = None
        top_rss = 0

        try:
            for entry in os.listdir('/proc'):
                if not entry.isdigit():
                    continue
                pid = int(entry)
                try:
                    with open(f'/proc/{pid}/status', 'r') as f:
                        status = {}
                        for line in f:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                status[parts[0].strip()] = parts[1].strip()
                    name = status.get('Name', 'unknown')
                    if name in PROTECTED_PROCESSES:
                        continue
                    rss = int(status.get('VmRSS', '0 kB').split()[0])
                    if rss > top_rss:
                        top_rss = rss
                        top_pid = pid
                        top_name = name
                except (FileNotFoundError, ValueError, PermissionError):
                    continue
        except Exception as e:
            self.logger.error(f"🐌💥 Failed to scan /proc for top memory process: {e}")

        return top_pid, top_name

    def _find_top_cpu_process(self):
        """Find the PID and name of the top CPU-consuming process from /proc/stat snapshots."""
        top_pid = None
        top_name = None
        top_utime = 0

        try:
            for entry in os.listdir('/proc'):
                if not entry.isdigit():
                    continue
                pid = int(entry)
                try:
                    with open(f'/proc/{pid}/stat', 'r') as f:
                        parts = f.read().split()
                    # Field 14 (0-indexed 13) = utime, field 15 = stime
                    utime = int(parts[13]) + int(parts[14])
                    name = parts[1].strip('()')
                    if utime > top_utime:
                        top_utime = utime
                        top_pid = pid
                        top_name = name
                except (FileNotFoundError, ValueError, IndexError, PermissionError):
                    continue
        except Exception as e:
            self.logger.error(f" Failed to scan /proc for top CPU process: {e}")

        return top_pid, top_name
