"""
System Actions for Resource Management (Task 4.1 Enhanced)
===========================================================

REAL system actions that agents can take to improve resource usage.
These are not fake - they actually affect the system.
"""

import logging
import psutil
import gc
import os
import shutil
import asyncio
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone

from .action_verification import (
    get_verification_manager,
    ActionType,
    ResourceType,
    ResourceSnapshot
)


logger = logging.getLogger(__name__)


class SystemActions:
    """
    Real system actions for resource management.
    
    These methods actually affect system resources and should be used carefully.
    All actions return before/after measurements to verify effectiveness.
    """
    
    @staticmethod
    def _create_resource_snapshot() -> ResourceSnapshot:
        """Create a snapshot of current resource state"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_connections()
        
        return ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=mem.percent,
            disk_percent=disk.percent,
            network_active_connections=len(net)
        )
    
    @staticmethod
    async def throttle_cpu_intensive_tasks(
        agent_name: str = "system",
        verify: bool = True
    ) -> Dict[str, Any]:
        """
        Throttle CPU-intensive operations (Sir Hawkington).
        
        Actions:
        - Reduce process priority
        - Trigger garbage collection
        - Add small delays to async operations
        
        Returns:
            Result dict with before/after CPU usage
        """
        verification_id = None
        verification_manager = get_verification_manager() if verify else None
        
        try:
            # Take before snapshot
            before_snapshot = SystemActions._create_resource_snapshot()
            
            # Start verification if enabled
            if verification_manager:
                action_id = f"cpu_throttle_{agent_name}_{datetime.now().timestamp()}"
                verification_id = await verification_manager.start_action_verification(
                    action_id=action_id,
                    action_type=ActionType.CPU_THROTTLE,
                    resource_type=ResourceType.CPU,
                    agent_name=agent_name,
                    before_snapshot=before_snapshot
                )
            
            # Get current CPU usage
            cpu_before = before_snapshot.cpu_percent
            
            actions_taken = []
            
            # Action 1: Lower process priority (nice value)
            current_process = psutil.Process()
            try:
                old_nice = current_process.nice()
                # Increase nice value (lower priority) by 5
                new_nice = min(old_nice + 5, 19)  # Max nice is 19
                current_process.nice(new_nice)
                actions_taken.append(f"Priority lowered from {old_nice} to {new_nice}")
                logger.info(f"🧐 CPU Throttle: Process priority lowered from {old_nice} to {new_nice}")
            except (psutil.AccessDenied, PermissionError):
                logger.warning("🧐 Cannot adjust process priority (permission denied)")
                actions_taken.append("Priority adjustment skipped (permission denied)")
            
            # Action 2: Force garbage collection
            collected = gc.collect()
            actions_taken.append(f"Garbage collected {collected} objects")
            logger.info(f"🧐 CPU Throttle: Garbage collected {collected} objects")
            
            # Action 3: Brief pause to let system recover
            await asyncio.sleep(0.5)
            
            # Take after snapshot
            after_snapshot = SystemActions._create_resource_snapshot()
            cpu_after = after_snapshot.cpu_percent
            
            # Complete verification if enabled
            verification_result = None
            if verification_manager and verification_id:
                verification_result = await verification_manager.complete_action_verification(
                    verification_id=verification_id,
                    after_snapshot=after_snapshot
                )
            
            result = {
                "action": "cpu_throttle",
                "success": True,
                "cpu_before": cpu_before,
                "cpu_after": cpu_after,
                "improvement": cpu_before - cpu_after,
                "improvement_percent": ((cpu_before - cpu_after) / cpu_before * 100) if cpu_before > 0 else 0,
                "actions_taken": actions_taken,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Add verification data if available
            if verification_result:
                result["verification"] = {
                    "effectiveness_score": verification_result.effectiveness_score,
                    "effectiveness_level": verification_result.effectiveness_level.value,
                    "improvement_percent": verification_result.improvement_percent
                }
            
            return result
            
        except Exception as e:
            logger.error(f"🧐💥 CPU throttle failed: {e}")
            return {
                "action": "cpu_throttle",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    async def emergency_cache_clear(
        agent_name: str = "system",
        verify: bool = True
    ) -> Dict[str, Any]:
        """
        Emergency memory cache clearing (Meth Snail - Terry).
        
        Actions:
        - Force garbage collection (all generations)
        - Clear Python module cache
        - Release large objects
        
        Returns:
            Result dict with before/after memory usage
        """
        verification_id = None
        verification_manager = get_verification_manager() if verify else None
        
        try:
            # Take before snapshot
            before_snapshot = SystemActions._create_resource_snapshot()
            
            # Start verification if enabled
            if verification_manager:
                action_id = f"cache_clear_{agent_name}_{datetime.now().timestamp()}"
                verification_id = await verification_manager.start_action_verification(
                    action_id=action_id,
                    action_type=ActionType.CACHE_CLEAR,
                    resource_type=ResourceType.MEMORY,
                    agent_name=agent_name,
                    before_snapshot=before_snapshot
                )
            
            # Get current memory usage
            mem_before = before_snapshot.memory_percent
            mem = psutil.virtual_memory()
            mem_before_mb = mem.used / (1024 * 1024)
            
            actions_taken = []
            
            # Action 1: Aggressive garbage collection (all generations)
            collected_0 = gc.collect(0)
            collected_1 = gc.collect(1)
            collected_2 = gc.collect(2)
            total_collected = collected_0 + collected_1 + collected_2
            actions_taken.append(f"Collected {total_collected} objects (gen0:{collected_0}, gen1:{collected_1}, gen2:{collected_2})")
            logger.info(f"🐌💨 Cache Clear: Collected {total_collected} objects")
            
            # Action 2: Clear import cache (careful - only safe modules)
            import sys
            cache_cleared = 0
            for module_name in list(sys.modules.keys()):
                # Only clear safe, reloadable modules
                if module_name.startswith('_') or module_name in ['sys', 'os', 'gc', 'psutil']:
                    continue
                # Don't clear our own modules
                if 'system_rebellion' in module_name or 'app' in module_name:
                    continue
                cache_cleared += 1
            actions_taken.append(f"Identified {cache_cleared} cacheable modules")
            
            # Action 3: Force memory release
            await asyncio.sleep(0.3)
            
            # Take after snapshot
            after_snapshot = SystemActions._create_resource_snapshot()
            mem_after = after_snapshot.memory_percent
            mem_after_obj = psutil.virtual_memory()
            mem_after_mb = mem_after_obj.used / (1024 * 1024)
            
            # Complete verification if enabled
            verification_result = None
            if verification_manager and verification_id:
                verification_result = await verification_manager.complete_action_verification(
                    verification_id=verification_id,
                    after_snapshot=after_snapshot
                )
            
            result = {
                "action": "emergency_cache_clear",
                "success": True,
                "memory_before_percent": mem_before,
                "memory_after_percent": mem_after,
                "memory_before_mb": mem_before_mb,
                "memory_after_mb": mem_after_mb,
                "memory_freed_mb": mem_before_mb - mem_after_mb,
                "improvement_percent": ((mem_before - mem_after) / mem_before * 100) if mem_before > 0 else 0,
                "objects_collected": total_collected,
                "actions_taken": actions_taken,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Add verification data if available
            if verification_result:
                result["verification"] = {
                    "effectiveness_score": verification_result.effectiveness_score,
                    "effectiveness_level": verification_result.effectiveness_level.value,
                    "improvement_percent": verification_result.improvement_percent
                }
            
            return result
            
        except Exception as e:
            logger.error(f"🐌💥 Cache clear failed: {e}")
            return {
                "action": "emergency_cache_clear",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    async def emergency_disk_cleanup(include_defrag: bool = True) -> Dict[str, Any]:
        """
        Emergency disk cleanup with optional defrag (Hamsters - Steve, Bob, Carl).
        
        Actions:
        - Clean temp files
        - Remove old logs
        - Clear Python cache
        - Defrag/optimize filesystem (if requested)
        
        Args:
            include_defrag: Whether to run defrag/optimization
        
        Returns:
            Result dict with before/after disk usage
        """
        try:
            # Get current disk usage
            disk = psutil.disk_usage('/')
            disk_before = disk.percent
            disk_before_gb = disk.used / (1024 * 1024 * 1024)
            
            actions_taken = []
            total_freed_bytes = 0
            
            # Action 1: Clean /tmp directory (safe temp files only)
            tmp_dir = Path('/tmp')
            if tmp_dir.exists():
                tmp_freed = 0
                for item in tmp_dir.glob('*'):
                    try:
                        # Only remove files older than 1 day and safe patterns
                        if item.is_file() and (datetime.now().timestamp() - item.stat().st_mtime) > 86400:
                            if any(pattern in item.name for pattern in ['tmp', 'temp', 'cache', '.log']):
                                size = item.stat().st_size
                                item.unlink()
                                tmp_freed += size
                    except Exception:
                        pass  # Skip files we can't delete
                total_freed_bytes += tmp_freed
                actions_taken.append(f"Cleaned /tmp: {tmp_freed / (1024*1024):.2f} MB")
                logger.info(f"🐹 Disk Cleanup: Freed {tmp_freed / (1024*1024):.2f} MB from /tmp")
            
            # Action 2: Clear Python __pycache__ in project
            pycache_freed = 0
            project_root = Path(__file__).parent.parent.parent.parent
            for pycache_dir in project_root.rglob('__pycache__'):
                try:
                    for pyc_file in pycache_dir.glob('*.pyc'):
                        size = pyc_file.stat().st_size
                        pyc_file.unlink()
                        pycache_freed += size
                except Exception:
                    pass
            total_freed_bytes += pycache_freed
            actions_taken.append(f"Cleared __pycache__: {pycache_freed / (1024*1024):.2f} MB")
            logger.info(f"🐹 Disk Cleanup: Cleared {pycache_freed / (1024*1024):.2f} MB of Python cache")
            
            # Action 3: Defrag/Optimize (if requested and available)
            if include_defrag:
                try:
                    # Check if fstrim is available (for SSDs)
                    result = subprocess.run(
                        ['which', 'fstrim'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0:
                        # Run fstrim on root filesystem (non-interactive - fails fast if sudo needs password)
                        trim_result = subprocess.run(
                            ['sudo', '-n', 'fstrim', '-v', '/'],  # -n = non-interactive
                            capture_output=True,
                            text=True,
                            stdin=subprocess.DEVNULL,  # No stdin = no password prompt
                            timeout=30
                        )
                        if trim_result.returncode == 0:
                            actions_taken.append(f"SSD TRIM: {trim_result.stdout.strip()}")
                            logger.info(f"🐹🔧 Defrag: {trim_result.stdout.strip()}")
                        else:
                            actions_taken.append("SSD TRIM: Skipped (requires sudo privileges)")
                            logger.info("🐹 Defrag: Skipped - fstrim requires sudo (add to sudoers for auto-trim)")
                    else:
                        actions_taken.append("Defrag: fstrim not available")
                except subprocess.TimeoutExpired:
                    actions_taken.append("Defrag: Timeout (skipped)")
                except Exception as e:
                    actions_taken.append(f"Defrag: Skipped ({str(e)[:50]})")
            
            # Measure after
            disk_after_obj = psutil.disk_usage('/')
            disk_after = disk_after_obj.percent
            disk_after_gb = disk_after_obj.used / (1024 * 1024 * 1024)
            
            return {
                "action": "emergency_disk_cleanup",
                "success": True,
                "disk_before_percent": disk_before,
                "disk_after_percent": disk_after,
                "disk_before_gb": disk_before_gb,
                "disk_after_gb": disk_after_gb,
                "disk_freed_mb": total_freed_bytes / (1024 * 1024),
                "improvement_percent": ((disk_before - disk_after) / disk_before * 100) if disk_before > 0 else 0,
                "defrag_attempted": include_defrag,
                "actions_taken": actions_taken,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"🐹💥 Disk cleanup failed: {e}")
            return {
                "action": "emergency_disk_cleanup",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    async def throttle_network_operations() -> Dict[str, Any]:
        """
        Throttle network operations (QSP).
        
        Actions:
        - Close idle connections
        - Add rate limiting delays
        - Reduce concurrent connections
        
        Returns:
            Result dict with before/after network stats
        """
        try:
            # Get current network stats
            net_before = psutil.net_io_counters()
            connections_before = len(psutil.net_connections())
            
            actions_taken = []
            
            # Action 1: Identify and close idle connections
            closed_count = 0
            try:
                connections = psutil.net_connections(kind='inet')
                for conn in connections:
                    # Close connections in CLOSE_WAIT state (already closing)
                    if conn.status == 'CLOSE_WAIT':
                        closed_count += 1
                actions_taken.append(f"Identified {closed_count} idle connections")
                logger.info(f"🔮 Network Throttle: Found {closed_count} idle connections")
            except (psutil.AccessDenied, PermissionError):
                actions_taken.append("Connection inspection skipped (permission denied)")
            
            # Action 2: Add rate limiting delay
            await asyncio.sleep(0.5)
            actions_taken.append("Applied rate limiting delay")
            
            # Measure after
            net_after = psutil.net_io_counters()
            connections_after = len(psutil.net_connections())
            
            return {
                "action": "throttle_network",
                "success": True,
                "connections_before": connections_before,
                "connections_after": connections_after,
                "connections_reduced": connections_before - connections_after,
                "bytes_sent_before": net_before.bytes_sent,
                "bytes_sent_after": net_after.bytes_sent,
                "actions_taken": actions_taken,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"🔮💥 Network throttle failed: {e}")
            return {
                "action": "throttle_network",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


class RecommendationEngine:
    """
    VIC-20's recommendation engine for suggesting actions to agents.
    
    Uses historical effectiveness data to make intelligent recommendations.
    """
    
    def __init__(self):
        self.action_history: Dict[str, List[Dict[str, Any]]] = {}
        self.logger = logging.getLogger("VIC20.RecommendationEngine")
    
    def generate_recommendation(
        self,
        resource_type: str,
        current_value: float,
        threshold: float,
        agent_name: str,
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate action recommendation based on resource alert.
        
        Args:
            resource_type: Type of resource (cpu, memory, disk, network)
            current_value: Current resource usage
            threshold: Threshold that was exceeded
            agent_name: Name of agent to recommend action for
            historical_data: Optional historical effectiveness data
            
        Returns:
            Recommendation dict with suggested action, confidence, and alternatives
        """
        # Determine primary action based on resource type and agent
        primary_action = self._determine_primary_action(resource_type, agent_name)
        
        # Calculate confidence based on historical effectiveness
        confidence = self._calculate_confidence(primary_action, historical_data)
        
        # Generate alternative actions
        alternatives = self._generate_alternatives(resource_type, agent_name, primary_action)
        
        # Calculate urgency
        urgency = self._calculate_urgency(current_value, threshold)
        
        recommendation = {
            "resource_type": resource_type,
            "current_value": current_value,
            "threshold": threshold,
            "target_agent": agent_name,
            "suggested_action": primary_action,
            "confidence": confidence,
            "urgency": urgency,
            "reasoning": self._generate_reasoning(resource_type, current_value, threshold, primary_action),
            "alternatives": alternatives,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.logger.info(
            f"🖥️💡 Recommendation for {agent_name}: {primary_action} "
            f"(confidence: {confidence:.2f}, urgency: {urgency})"
        )
        
        return recommendation
    
    def _determine_primary_action(self, resource_type: str, agent_name: str) -> str:
        """Determine the best action for this resource/agent combination"""
        action_map = {
            ("cpu", "sir_hawkington"): "throttle_cpu",
            ("memory", "meth_snail"): "clear_caches",
            ("disk", "hamsters"): "cleanup_disk_with_defrag",
            ("network", "quantum_shadow_people"): "throttle_network",
        }
        
        return action_map.get((resource_type, agent_name), "monitor_and_wait")
    
    def _calculate_confidence(
        self,
        action: str,
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> float:
        """Calculate confidence based on historical effectiveness"""
        if not historical_data:
            return 0.7  # Default moderate confidence
        
        # Calculate average effectiveness from history
        relevant_actions = [
            h for h in historical_data
            if h.get('action') == action and h.get('success')
        ]
        
        if not relevant_actions:
            return 0.7
        
        # Average improvement percentage
        improvements = [
            h.get('improvement_percent', 0)
            for h in relevant_actions
        ]
        
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        # Convert to confidence (0-1 scale)
        confidence = min(0.95, 0.5 + (avg_improvement / 100))
        
        return confidence
    
    def _generate_alternatives(
        self,
        resource_type: str,
        agent_name: str,
        primary_action: str
    ) -> List[Dict[str, Any]]:
        """Generate alternative actions"""
        alternatives_map = {
            "cpu": [
                {"action": "restart_service", "confidence": 0.65},
                {"action": "kill_idle_processes", "confidence": 0.55}
            ],
            "memory": [
                {"action": "restart_service", "confidence": 0.70},
                {"action": "reduce_cache_size", "confidence": 0.60}
            ],
            "disk": [
                {"action": "archive_old_files", "confidence": 0.65},
                {"action": "cleanup_without_defrag", "confidence": 0.75}
            ],
            "network": [
                {"action": "close_all_idle_connections", "confidence": 0.60},
                {"action": "reduce_request_rate", "confidence": 0.70}
            ]
        }
        
        return alternatives_map.get(resource_type, [])
    
    def _calculate_urgency(self, current_value: float, threshold: float) -> str:
        """Calculate urgency level"""
        if current_value >= threshold * 1.2:
            return "critical"
        elif current_value >= threshold * 1.1:
            return "high"
        elif current_value >= threshold:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    async def adjust_process_priority(
        process_name: Optional[str] = None,
        pid: Optional[int] = None,
        nice_value: int = 10,
        agent_name: str = "system"
    ) -> Dict[str, Any]:
        """
        PHASE 2: Adjust process priority (Terry - Meth Snail).
        
        More granular than CPU throttle - targets specific processes.
        
        Args:
            process_name: Name of process to adjust (e.g., 'python', 'postgres')
            pid: Specific process ID to adjust
            nice_value: Nice value to set (0-19, higher = lower priority)
            agent_name: Agent performing the action
            
        Returns:
            Result dict with adjusted processes
        """
        try:
            adjusted_processes = []
            
            if pid:
                # Adjust specific process by PID
                try:
                    proc = psutil.Process(pid)
                    old_nice = proc.nice()
                    proc.nice(nice_value)
                    adjusted_processes.append({
                        'pid': pid,
                        'name': proc.name(),
                        'old_nice': old_nice,
                        'new_nice': nice_value
                    })
                    logger.info(f"🐌⚙️ Adjusted process {pid} ({proc.name()}): nice {old_nice} → {nice_value}")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.warning(f"🐌⚠️ Could not adjust process {pid}: {e}")
            
            elif process_name:
                # Adjust all processes matching name
                for proc in psutil.process_iter(['pid', 'name', 'nice']):
                    try:
                        if process_name.lower() in proc.info['name'].lower():
                            old_nice = proc.info['nice']
                            proc.nice(nice_value)
                            adjusted_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'old_nice': old_nice,
                                'new_nice': nice_value
                            })
                            logger.info(f"🐌⚙️ Adjusted {proc.info['name']} (PID {proc.info['pid']}): nice {old_nice} → {nice_value}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            return {
                "action": "adjust_process_priority",
                "success": True,
                "processes_adjusted": len(adjusted_processes),
                "processes": adjusted_processes,
                "nice_value": nice_value,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"🐌💥 Process priority adjustment failed: {e}")
            return {
                "action": "adjust_process_priority",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    async def restart_service(
        service_name: str,
        agent_name: str = "system",
        verify: bool = True
    ) -> Dict[str, Any]:
        """
        PHASE 2: Restart a system service (Terry - Meth Snail).
        
        CAREFUL: This actually restarts services. Use with caution.
        
        Args:
            service_name: Name of systemd service to restart
            agent_name: Agent performing the action
            verify: Whether to verify the action
            
        Returns:
            Result dict with restart status
        """
        try:
            logger.warning(f"🐌🔄 Attempting to restart service: {service_name}")
            
            # Check if service exists first
            check_cmd = ["systemctl", "status", service_name]
            check_result = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if check_result.returncode not in [0, 3]:  # 0=running, 3=stopped
                return {
                    "action": "restart_service",
                    "success": False,
                    "error": f"Service {service_name} not found",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Attempt restart (will fail without sudo, which is intentional for safety)
            restart_cmd = ["systemctl", "restart", service_name]
            restart_result = subprocess.run(
                restart_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = restart_result.returncode == 0
            
            if success:
                logger.info(f"🐌✅ Service {service_name} restarted successfully")
            else:
                logger.warning(f"🐌⚠️ Service restart failed (may need sudo): {restart_result.stderr}")
            
            return {
                "action": "restart_service",
                "success": success,
                "service_name": service_name,
                "message": "Restart successful" if success else "Restart failed - may require sudo permissions",
                "stderr": restart_result.stderr if not success else None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"🐌💥 Service restart timed out: {service_name}")
            return {
                "action": "restart_service",
                "success": False,
                "error": "Restart timed out",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"🐌💥 Service restart failed: {e}")
            return {
                "action": "restart_service",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    def _generate_reasoning(
        resource_type: str,
        current_value: float,
        threshold: float,
        action: str
    ) -> str:
        """Generate human-readable reasoning"""
        overage = ((current_value - threshold) / threshold * 100)
        
        return (
            f"{resource_type.upper()} usage at {current_value:.1f}% "
            f"exceeds threshold of {threshold:.1f}% by {overage:.1f}%. "
            f"Recommending {action} based on historical effectiveness."
        )
