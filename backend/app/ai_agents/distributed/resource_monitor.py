"""
Resource Monitoring System
===========================

System resource monitoring for distributed agents.
Each agent monitors resources relevant to their personality and role.

Agent Specializations:
- Sir Hawkington: CPU usage (aristocratic precision)
- Terry the Meth Snail: Memory/RAM (speed obsession)
- Bob the Hamster: Disk/Storage (hoarding tendencies)
- Quantum Shadow People: Network (existing everywhere)
"""

import psutil
import asyncio
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable, Awaitable
from enum import Enum

from .message_protocol import ResourceAlert, MessageType, Priority
from .communication import MessageBus
from .alert_escalation import (
    get_escalation_manager,
    AlertEscalationManager,
    ResourceType as EscalationResourceType,
    AlertLevel
)

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of system resources to monitor"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    SWAP = "swap"
    LOAD_AVERAGE = "load_average"


class AlertSeverity(Enum):
    """Severity levels for resource alerts"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class ResourceMetrics:
    """Snapshot of system resource metrics"""
    timestamp: str
    hostname: str
    
    # CPU metrics
    cpu_percent: float
    cpu_count: int
    cpu_per_core: List[float]
    load_average: tuple
    
    # Memory metrics
    memory_total: int
    memory_available: int
    memory_used: int
    memory_percent: float
    swap_total: int
    swap_used: int
    swap_percent: float
    
    # Disk metrics
    disk_total: int
    disk_used: int
    disk_free: int
    disk_percent: float
    
    # Network metrics (bytes sent/received since boot)
    network_bytes_sent: int
    network_bytes_recv: int
    network_packets_sent: int
    network_packets_recv: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class ResourceMonitor:
    """
    System resource monitor for agents.
    
    Monitors system resources and triggers alerts when thresholds are exceeded.
    """
    
    def __init__(
        self,
        agent_name: str,
        message_bus: Optional[MessageBus] = None,
        monitored_resources: Optional[List[ResourceType]] = None,
        check_interval: float = 5.0
    ):
        """
        Initialize resource monitor.
        
        Args:
            agent_name: Name of the agent using this monitor
            message_bus: Optional MessageBus for sending alerts
            monitored_resources: List of resources to monitor (None = all)
            check_interval: Seconds between checks
        """
        self.agent_name = agent_name
        self.message_bus = message_bus
        self.monitored_resources = monitored_resources or list(ResourceType)
        self.check_interval = check_interval
        
        self.logger = logging.getLogger(f"ResourceMonitor.{agent_name}")
        
        # Thresholds (can be customized per agent)
        self.thresholds = {
            ResourceType.CPU: 80.0,
            ResourceType.MEMORY: 85.0,
            ResourceType.DISK: 90.0,
            ResourceType.SWAP: 50.0,
        }
        
        # Alert callbacks
        self._alert_callbacks: List[Callable[[ResourceAlert], Awaitable[None]]] = []
        
        # Monitoring state
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._last_metrics: Optional[ResourceMetrics] = None
        self._alert_history: List[Dict[str, Any]] = []
        
        # Get hostname
        import socket
        self.hostname = socket.gethostname()
        
        # Get escalation manager
        self.escalation_manager = get_escalation_manager()
    
    def set_threshold(self, resource_type: ResourceType, threshold: float):
        """
        Set alert threshold for a resource type.
        
        Args:
            resource_type: Type of resource
            threshold: Threshold percentage (0-100)
        """
        self.thresholds[resource_type] = threshold
        self.logger.info(f"Set {resource_type.value} threshold to {threshold}%")
    
    def register_alert_callback(
        self,
        callback: Callable[[ResourceAlert], Awaitable[None]]
    ):
        """
        Register a callback for resource alerts.
        
        Args:
            callback: Async function to call when alert is triggered
        """
        self._alert_callbacks.append(callback)
    
    async def start(self):
        """Start resource monitoring"""
        if self._running:
            self.logger.warning("Resource monitor already running")
            return
        
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        self.logger.info(
            f"Resource monitor started (interval: {self.check_interval}s, "
            f"monitoring: {[r.value for r in self.monitored_resources]})"
        )
    
    async def stop(self):
        """Stop resource monitoring"""
        self._running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Resource monitor stopped")
    
    async def get_current_metrics(self) -> ResourceMetrics:
        """
        Get current system resource metrics.
        
        Returns:
            ResourceMetrics snapshot
        """
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_count = psutil.cpu_count()
        load_avg = psutil.getloadavg()
        
        # Memory metrics
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk metrics (root partition)
        disk = psutil.disk_usage('/')
        
        # Network metrics
        net = psutil.net_io_counters()
        
        metrics = ResourceMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            hostname=self.hostname,
            cpu_percent=cpu_percent,
            cpu_count=cpu_count,
            cpu_per_core=cpu_per_core,
            load_average=load_avg,
            memory_total=mem.total,
            memory_available=mem.available,
            memory_used=mem.used,
            memory_percent=mem.percent,
            swap_total=swap.total,
            swap_used=swap.used,
            swap_percent=swap.percent,
            disk_total=disk.total,
            disk_used=disk.used,
            disk_free=disk.free,
            disk_percent=disk.percent,
            network_bytes_sent=net.bytes_sent,
            network_bytes_recv=net.bytes_recv,
            network_packets_sent=net.packets_sent,
            network_packets_recv=net.packets_recv
        )
        
        self._last_metrics = metrics
        return metrics
    
    async def _monitor_loop(self):
        """Background monitoring loop"""
        self.logger.info("Resource monitoring loop started")
        
        try:
            while self._running:
                try:
                    # Get current metrics
                    metrics = await self.get_current_metrics()
                    
                    # 🚨 ALWAYS publish metrics to agents (not just alerts)
                    if self.message_bus:
                        await self.message_bus.publish_message(
                            "system.metrics",
                            {
                                "type": "resource_metrics",
                                "metrics": metrics.to_dict(),
                                "timestamp": metrics.timestamp
                            }
                        )
                        self.logger.debug(f"Published metrics: CPU={metrics.cpu_percent}%, MEM={metrics.memory_percent}%")
                    
                    # Check thresholds (for alerts)
                    await self._check_thresholds(metrics)
                    
                    # Wait for next check
                    await asyncio.sleep(self.check_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Error in monitor loop: {e}")
                    await asyncio.sleep(self.check_interval)
        
        finally:
            self.logger.info("Resource monitoring loop stopped")
    
    async def _check_thresholds(self, metrics: ResourceMetrics):
        """
        Check if any thresholds are exceeded using escalation manager.
        
        Args:
            metrics: Current resource metrics
        """
        # Map ResourceType to EscalationResourceType
        resource_map = {
            ResourceType.CPU: EscalationResourceType.CPU,
            ResourceType.MEMORY: EscalationResourceType.MEMORY,
            ResourceType.DISK: EscalationResourceType.DISK,
            ResourceType.NETWORK: EscalationResourceType.NETWORK,
        }
        
        # Check CPU
        if ResourceType.CPU in self.monitored_resources:
            threshold = self.thresholds.get(ResourceType.CPU, 80.0)
            if metrics.cpu_percent > threshold:
                alert_event = await self.escalation_manager.process_resource_alert(
                    resource_type=resource_map[ResourceType.CPU],
                    agent_name=self.agent_name,
                    current_value=metrics.cpu_percent,
                    threshold=threshold
                )
                if alert_event:
                    # Create and send alert
                    alert = self._create_alert(
                        ResourceType.CPU,
                        metrics.cpu_percent,
                        threshold,
                        alert_event.level.value
                    )
                    await self._send_alert(alert)
        
        # Check Memory
        if ResourceType.MEMORY in self.monitored_resources:
            threshold = self.thresholds.get(ResourceType.MEMORY, 85.0)
            if metrics.memory_percent > threshold:
                alert_event = await self.escalation_manager.process_resource_alert(
                    resource_type=resource_map[ResourceType.MEMORY],
                    agent_name=self.agent_name,
                    current_value=metrics.memory_percent,
                    threshold=threshold
                )
                if alert_event:
                    alert = self._create_alert(
                        ResourceType.MEMORY,
                        metrics.memory_percent,
                        threshold,
                        alert_event.level.value
                    )
                    await self._send_alert(alert)
        
        # Check Disk
        if ResourceType.DISK in self.monitored_resources:
            threshold = self.thresholds.get(ResourceType.DISK, 90.0)
            if metrics.disk_percent > threshold:
                alert_event = await self.escalation_manager.process_resource_alert(
                    resource_type=resource_map[ResourceType.DISK],
                    agent_name=self.agent_name,
                    current_value=metrics.disk_percent,
                    threshold=threshold
                )
                if alert_event:
                    alert = self._create_alert(
                        ResourceType.DISK,
                        metrics.disk_percent,
                        threshold,
                        alert_event.level.value
                    )
                    await self._send_alert(alert)
        
        # Check Swap (map to MEMORY for escalation)
        if ResourceType.SWAP in self.monitored_resources:
            threshold = self.thresholds.get(ResourceType.SWAP, 50.0)
            if metrics.swap_percent > threshold:
                alert_event = await self.escalation_manager.process_resource_alert(
                    resource_type=EscalationResourceType.MEMORY,  # Treat swap as memory
                    agent_name=f"{self.agent_name}_swap",
                    current_value=metrics.swap_percent,
                    threshold=threshold
                )
                if alert_event:
                    alert = self._create_alert(
                        ResourceType.SWAP,
                        metrics.swap_percent,
                        threshold,
                        alert_event.level.value
                    )
                    await self._send_alert(alert)
        
        # Clean up old resolved alerts
        self.escalation_manager.clear_resolved_alerts(max_age_minutes=10)
    
    def _determine_severity(self, current: float, threshold: float) -> str:
        """
        Determine alert severity based on how much threshold is exceeded.
        
        Args:
            current: Current value
            threshold: Threshold value
            
        Returns:
            Severity level
        """
        overage = current - threshold
        
        if overage > 15:
            return AlertSeverity.EMERGENCY.value
        elif overage > 10:
            return AlertSeverity.CRITICAL.value
        elif overage > 5:
            return AlertSeverity.WARNING.value
        else:
            return AlertSeverity.INFO.value
    
    def _create_alert(
        self,
        resource_type: ResourceType,
        current_value: float,
        threshold: float,
        severity: str
    ) -> ResourceAlert:
        """
        Create a resource alert.
        
        Args:
            resource_type: Type of resource
            current_value: Current value
            threshold: Threshold that was exceeded
            severity: Alert severity
            
        Returns:
            ResourceAlert message
        """
        return ResourceAlert(
            from_agent=self.agent_name,
            resource_type=resource_type.value,
            current_value=current_value,
            threshold=threshold,
            severity=severity,
            host=self.hostname
        )
    
    async def _send_alert(self, alert: ResourceAlert):
        """
        Send a resource alert.
        
        Args:
            alert: ResourceAlert to send
        """
        # Add to history
        self._alert_history.append({
            "timestamp": alert.timestamp,
            "resource_type": alert.payload["resource_type"],
            "severity": alert.payload["severity"],
            "current_value": alert.payload["current_value"]
        })
        
        # Keep only last 100 alerts
        if len(self._alert_history) > 100:
            self._alert_history = self._alert_history[-100:]
        
        # Send via message bus if available
        if self.message_bus:
            await self.message_bus.publish(alert)
        
        # Call registered callbacks
        for callback in self._alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")
        
        self.logger.warning(
            f"Resource alert: {alert.payload['resource_type']} at "
            f"{alert.payload['current_value']:.1f}% "
            f"(threshold: {alert.payload['threshold']:.1f}%, "
            f"severity: {alert.payload['severity']})"
        )
    
    @property
    def is_running(self) -> bool:
        """Check if the monitor is currently running"""
        return self._running
    
    def get_last_metrics(self) -> Optional[ResourceMetrics]:
        """Get the last collected metrics"""
        return self._last_metrics
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """Get recent alert history"""
        return self._alert_history.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitor statistics"""
        return {
            "is_running": self._running,
            "monitored_resources": [r.value for r in self.monitored_resources],
            "thresholds": {k.value: v for k, v in self.thresholds.items()},
            "total_alerts": len(self._alert_history),
            "last_check": self._last_metrics.timestamp if self._last_metrics else None
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health summary including escalation state.
        
        Returns:
            Dict with health score, active alerts, and summary
        """
        health_summary = self.escalation_manager.get_aggregated_alert_summary()
        
        # Add current metrics
        if self._last_metrics:
            health_summary["current_metrics"] = {
                "cpu_percent": self._last_metrics.cpu_percent,
                "memory_percent": self._last_metrics.memory_percent,
                "disk_percent": self._last_metrics.disk_percent,
                "timestamp": self._last_metrics.timestamp
            }
        
        return health_summary
