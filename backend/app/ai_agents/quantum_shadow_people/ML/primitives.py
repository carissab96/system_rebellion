#!/usr/bin/env python3
"""
QSP's Primitive Executor

Atomic network operations with pre/post metric collection.
Each primitive is a single, measurable network action.

Primitives:
  Monitoring:  monitor_passive, investigate_connections, scan_ports,
               analyze_traffic, quantum_scan
  Defensive:   throttle_network, apply_rate_limit, close_connections
  Aggressive:  block_ips, update_firewall
  Escalation:  escalate_to_vic20

The base class execute() handles pre/post metric collection.
"""

import logging
import time
from typing import Any, Dict

from app.ai_agents.distributed.base_primitive_executor import (
    PrimitiveDefinition,
    PrimitiveExecutor,
    PrimitiveResult,
)

logger = logging.getLogger('QSPPrimitiveExecutor')


class QSPPrimitiveExecutor(PrimitiveExecutor):
    """
    QSP's primitive executor for network operations.

    👻 "Executing quantum network primitive... *coherence holding...*"
    """

    def __init__(self):
        super().__init__(agent_name='quantum_shadow_people')

    def _register_primitives(self):
        """Register all QSP primitives."""
        primitives = [
            PrimitiveDefinition(
                name='monitor_passive',
                command=None,
                requires_sudo=False,
                domain='network',
                description='Passive network monitoring — observe without intervention',
                risk_level=1,
                estimated_duration=1.0,
            ),
            PrimitiveDefinition(
                name='investigate_connections',
                command=None,
                requires_sudo=False,
                domain='network',
                description='Deep investigation of current connection states and patterns',
                risk_level=1,
                estimated_duration=5.0,
            ),
            PrimitiveDefinition(
                name='scan_ports',
                command=None,
                requires_sudo=False,
                domain='network',
                description='Scan for open ports and unexpected listeners',
                risk_level=2,
                estimated_duration=10.0,
            ),
            PrimitiveDefinition(
                name='analyze_traffic',
                command=None,
                requires_sudo=False,
                domain='network',
                description='Analyze traffic patterns and bandwidth distribution',
                risk_level=1,
                estimated_duration=5.0,
            ),
            PrimitiveDefinition(
                name='quantum_scan',
                command=None,
                requires_sudo=False,
                domain='network',
                description='Quantum-level network analysis — QSP specialty',
                risk_level=1,
                estimated_duration=3.0,
            ),
            PrimitiveDefinition(
                name='throttle_network',
                command=None,
                requires_sudo=True,
                domain='network',
                description='Apply network throttling to reduce bandwidth consumption',
                risk_level=3,
                estimated_duration=5.0,
            ),
            PrimitiveDefinition(
                name='apply_rate_limit',
                command=None,
                requires_sudo=True,
                domain='network',
                description='Apply rate limiting to specific targets or globally',
                risk_level=2,
                estimated_duration=3.0,
            ),
            PrimitiveDefinition(
                name='close_connections',
                command=None,
                requires_sudo=True,
                domain='network',
                description='Close suspicious or anomalous network connections',
                risk_level=3,
                estimated_duration=5.0,
            ),
            PrimitiveDefinition(
                name='block_ips',
                command=None,
                requires_sudo=True,
                domain='network',
                description='Block IP addresses via firewall rules',
                risk_level=4,
                estimated_duration=3.0,
            ),
            PrimitiveDefinition(
                name='update_firewall',
                command=None,
                requires_sudo=True,
                domain='network',
                description='Update firewall rules for network protection',
                risk_level=4,
                estimated_duration=5.0,
            ),
            PrimitiveDefinition(
                name='escalate_to_vic20',
                command=None,
                requires_sudo=False,
                domain='network',
                description='Escalate to VIC-20 for cross-agent coordination',
                risk_level=1,
                estimated_duration=2.0,
            ),
        ]
        for p in primitives:
            self.register(p)

    _PYTHON_DISPATCH = {
        'monitor_passive':         '_run_monitor_passive',
        'investigate_connections': '_run_investigate_connections',
        'scan_ports':              '_run_scan_ports',
        'analyze_traffic':         '_run_analyze_traffic',
        'quantum_scan':            '_run_quantum_scan',
        'throttle_network':        '_run_throttle_network',
        'apply_rate_limit':        '_run_apply_rate_limit',
        'close_connections':       '_run_close_connections',
        'block_ips':               '_run_block_ips',
        'update_firewall':         '_run_update_firewall',
        'escalate_to_vic20':       '_run_escalate',
    }

    async def _execute_python_primitive(
        self, name: str, context: Dict[str, Any]
    ) -> PrimitiveResult:
        handler_name = self._PYTHON_DISPATCH.get(name)
        if handler_name is None:
            self.logger.error(f"👻💥 No handler for primitive '{name}'")
            return PrimitiveResult(
                primitive_name=name,
                success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=0.0,
                error=f"No handler for '{name}'",
            )
        handler = getattr(self, handler_name)
        return await handler(name, context)

    async def _collect_metrics(self) -> Dict[str, Any]:
        """
        Collect current network metrics from psutil.

        Raises on failure — base class marks collection_failed=True.
        """
        import psutil

        connections = psutil.net_connections(kind='inet')
        total = len(connections)
        established = sum(1 for c in connections if c.status == 'ESTABLISHED')
        listen = sum(1 for c in connections if c.status == 'LISTEN')
        time_wait = sum(1 for c in connections if c.status == 'TIME_WAIT')
        close_wait = sum(1 for c in connections if c.status == 'CLOSE_WAIT')
        suspicious = time_wait + close_wait

        net_io = psutil.net_io_counters()

        return {
            'total_connections':      total,
            'established_connections': established,
            'listening_ports':        listen,
            'suspicious_connections': suspicious,
            'anomalous_states':       time_wait + close_wait,
            'network_anomalies':      net_io.errin + net_io.errout + net_io.dropin + net_io.dropout,
            'sent_rate_bps':          net_io.bytes_sent,
            'recv_rate_bps':          net_io.bytes_recv,
        }

    def _calculate_improvement(
        self, pre: Dict[str, Any], post: Dict[str, Any]
    ) -> float:
        """
        Weighted improvement across network metrics.

        Positive = improvement (metrics went down for lower-is-better).
        """
        conn_delta = pre.get('total_connections', 0) - post.get('total_connections', 0)
        susp_delta = pre.get('suspicious_connections', 0) - post.get('suspicious_connections', 0)
        anom_delta = pre.get('network_anomalies', 0) - post.get('network_anomalies', 0)

        max_conn = max(pre.get('total_connections', 1), 1)
        max_susp = max(pre.get('suspicious_connections', 1), 1)
        max_anom = max(pre.get('network_anomalies', 1), 1)

        weighted = (
            (conn_delta / max_conn) * 0.4 +
            (susp_delta / max_susp) * 0.4 +
            (anom_delta / max_anom) * 0.2
        )
        return round(weighted, 4)

    # =========================================================================
    # Primitive handlers — each routes to SystemActions
    # =========================================================================

    async def _run_monitor_passive(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        start = time.monotonic()
        self.logger.info("👻👁️ Passive monitoring — no intervention")
        return PrimitiveResult(
            primitive_name=name, success=True,
            pre_metrics={}, post_metrics={}, improvement=0.0,
            duration_seconds=time.monotonic() - start,
            stdout="Passive monitoring complete",
        )

    async def _run_investigate_connections(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        start = time.monotonic()
        try:
            from app.ai_agents.distributed.system_actions import SystemActions
            result = await SystemActions.investigate_network_activity(
                agent_name='quantum_shadow_people', verify=True
            )
            return PrimitiveResult(
                primitive_name=name, success=result.get('success', False),
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=str(result),
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e),
            )

    async def _run_scan_ports(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        start = time.monotonic()
        try:
            from app.ai_agents.distributed.system_actions import SystemActions
            result = await SystemActions.scan_network_ports(
                agent_name='quantum_shadow_people', verify=True
            )
            return PrimitiveResult(
                primitive_name=name, success=result.get('success', False),
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=str(result),
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e),
            )

    async def _run_analyze_traffic(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        start = time.monotonic()
        try:
            from app.ai_agents.distributed.system_actions import SystemActions
            result = await SystemActions.analyze_network_traffic(
                agent_name='quantum_shadow_people', verify=True
            )
            return PrimitiveResult(
                primitive_name=name, success=result.get('success', False),
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=str(result),
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e),
            )

    async def _run_quantum_scan(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        start = time.monotonic()
        try:
            from app.ai_agents.distributed.system_actions import SystemActions
            result = await SystemActions.quantum_security_scan(
                agent_name='quantum_shadow_people', verify=True
            )
            return PrimitiveResult(
                primitive_name=name, success=result.get('success', False),
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=str(result),
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e),
            )

    async def _run_throttle_network(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        start = time.monotonic()
        try:
            from app.ai_agents.distributed.system_actions import SystemActions
            result = await SystemActions.throttle_network_operations()
            return PrimitiveResult(
                primitive_name=name, success=result.get('success', False),
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=str(result),
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e),
            )

    async def _run_apply_rate_limit(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        start = time.monotonic()
        try:
            from app.ai_agents.distributed.system_actions import SystemActions
            result = await SystemActions.apply_rate_limiting(
                target=context.get('target'),
                limit=context.get('limit', 100),
                agent_name='quantum_shadow_people',
                verify=True,
            )
            return PrimitiveResult(
                primitive_name=name, success=result.get('success', False),
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=str(result),
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e),
            )

    async def _run_close_connections(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        start = time.monotonic()
        try:
            from app.ai_agents.distributed.system_actions import SystemActions
            result = await SystemActions.close_network_connections(
                connection_ids=context.get('connection_ids', []),
                agent_name='quantum_shadow_people',
                verify=True,
            )
            return PrimitiveResult(
                primitive_name=name, success=result.get('success', False),
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=str(result),
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e),
            )

    async def _run_block_ips(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        start = time.monotonic()
        try:
            from app.ai_agents.distributed.system_actions import SystemActions
            result = await SystemActions.block_suspicious_connections(
                ip_addresses=context.get('ip_addresses', []),
                agent_name='quantum_shadow_people',
                verify=True,
            )
            return PrimitiveResult(
                primitive_name=name, success=result.get('success', False),
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=str(result),
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e),
            )

    async def _run_update_firewall(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        start = time.monotonic()
        try:
            from app.ai_agents.distributed.system_actions import SystemActions
            result = await SystemActions.update_firewall_rules(
                rules=context.get('rules', []),
                agent_name='quantum_shadow_people',
                verify=True,
            )
            return PrimitiveResult(
                primitive_name=name, success=result.get('success', False),
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                stdout=str(result),
            )
        except Exception as e:
            return PrimitiveResult(
                primitive_name=name, success=False,
                pre_metrics={}, post_metrics={}, improvement=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(e),
            )

    async def _run_escalate(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        start = time.monotonic()
        self.logger.warning(
            "👻📢 ESCALATING to VIC-20 — quantum network situation beyond local handling"
        )
        return PrimitiveResult(
            primitive_name=name, success=True,
            pre_metrics={}, post_metrics={}, improvement=0.0,
            duration_seconds=time.monotonic() - start,
            stdout="Escalated to VIC-20 for coordination",
        )
