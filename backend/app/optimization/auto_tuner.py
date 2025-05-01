import logging
import psutil
import json
import subprocess
import os
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from app.optimization.system_permissions import check_required_permissions, get_permission_summary
from app.services.system_metrics_service import SystemMetricsService

# FastAPI doesn't need viewsets or serializers like Django REST framework

class TuningParameter(Enum):
    CPU_GOVERNOR = "cpu_governor"
    PROCESS_PRIORITY = "process_priority"
    IO_SCHEDULER = "io_scheduler"
    MEMORY_PRESSURE = "memory_pressure"
    SWAP_TENDENCY = "swap_tendency"
    CACHE_PRESSURE = "cache_pressure"
    DISK_READ_AHEAD = "disk_read_ahead"
    NETWORK_BUFFER = "network_buffer"

@dataclass
class TuningAction:
    parameter: TuningParameter
    current_value: any
    new_value: any
    confidence: float
    impact_score: float
    timestamp: datetime
    reason: str

class AutoTuner:
    def __init__(self):
        self.logger = logging.getLogger('WebAutoTuner')
        self.tuning_history = []
        self.active_tunings = {}
        self.permissions = {}
        self._initialized = False
        # Initialize with default permissions
        self.permissions = {
            'cpu_governor': False,
            'network_buffer': False,
            'disk_read_ahead': False,
            'io_scheduler': False,
            'swap_tendency': False,
            'cache_pressure': False,
            'memory_pressure': False,
            'process_priority': True  # Non-negative nice values don't require sudo
        }
        # Note: We'll properly initialize in the first get_tuning_recommendations call
        # Can't await in __init__, so we'll do it lazily

    async def _initialize_system_state(self):
        # Only initialize once
        if self._initialized:
            return
            
        # Initialize system state here
        self.permissions = check_required_permissions()
        has_all_permissions, missing = get_permission_summary()
        
        if not has_all_permissions:
            self.logger.warning(f"Missing system permissions for full auto-tuning: {', '.join(missing)}")
            
        # Log permission status
        self.logger.info(f"System permissions initialized. Full access: {has_all_permissions}")
        
        # Mark as initialized
        self._initialized = True

    async def get_current_metrics(self) -> Dict:
        """Get current system metrics from the centralized metrics service"""
        try:
            # Use the centralized metrics service
            metrics_service = await SystemMetricsService.get_instance()
            return await metrics_service.get_metrics()
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {str(e)}")
            return None

    async def apply_tuning(self, data: Dict) -> Optional[Dict]:
        """Apply a tuning action
        
        Args:
            data: Dictionary containing tuning parameters
            
        Returns:
            Dictionary containing the result of the tuning action
        """
        try:
            # Handle both direct data and TuningAction objects
            if isinstance(data, TuningAction):
                tuning_data = {
                    'parameter': data.parameter.value,
                    'current_value': data.current_value,
                    'new_value': data.new_value,
                    'confidence': data.confidence,
                    'impact_score': data.impact_score,
                    'reason': data.reason
                }
            else:
                tuning_data = data

            # Get metrics before applying tuning
            metrics_before = await self.get_current_metrics()
            
            # Apply the actual system changes here
            parameter = tuning_data['parameter']
            new_value = tuning_data['new_value']
            success = True
            error_message = None
            
            try:
                # Check if we have permission for this parameter
                if parameter in [p.value for p in TuningParameter] and not self.permissions.get(parameter, False):
                    self.logger.warning(f"No permission to modify {parameter}. Skipping.")
                    success = False
                    error_message = f"No permission to modify {parameter}"
                
                if parameter == TuningParameter.CPU_GOVERNOR.value:
                    # Set CPU governor
                    cmd = f"echo {new_value} | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
                    subprocess.run(cmd, shell=True, check=True)
                    self.logger.info(f"Applied CPU governor: {new_value}")
                
                elif parameter == TuningParameter.NETWORK_BUFFER.value:
                    # Set network buffer size
                    cmd = f"sudo sysctl -w net.core.rmem_max={new_value} net.core.wmem_max={new_value}"
                    subprocess.run(cmd, shell=True, check=True)
                    self.logger.info(f"Applied network buffer: {new_value}")
                
                elif parameter == TuningParameter.DISK_READ_AHEAD.value:
                    # Set disk read-ahead buffer
                    cmd = f"sudo blockdev --setra {new_value} /dev/sda"
                    subprocess.run(cmd, shell=True, check=True)
                    self.logger.info(f"Applied disk read-ahead: {new_value}")
                
                elif parameter == TuningParameter.IO_SCHEDULER.value:
                    # Set I/O scheduler
                    cmd = f"echo {new_value} | sudo tee /sys/block/sda/queue/scheduler"
                    subprocess.run(cmd, shell=True, check=True)
                    self.logger.info(f"Applied I/O scheduler: {new_value}")
                
                elif parameter == TuningParameter.SWAP_TENDENCY.value:
                    # Set swap tendency (vm.swappiness)
                    cmd = f"sudo sysctl -w vm.swappiness={new_value}"
                    subprocess.run(cmd, shell=True, check=True)
                    self.logger.info(f"Applied swap tendency: {new_value}")
                
                elif parameter == TuningParameter.CACHE_PRESSURE.value:
                    # Set cache pressure (vm.vfs_cache_pressure)
                    cmd = f"sudo sysctl -w vm.vfs_cache_pressure={new_value}"
                    subprocess.run(cmd, shell=True, check=True)
                    self.logger.info(f"Applied cache pressure: {new_value}")
                
                elif parameter == TuningParameter.MEMORY_PRESSURE.value:
                    # This is more complex, as it's not a direct sysctl parameter
                    # For demonstration, we'll adjust the min_free_kbytes
                    if new_value == "high":
                        value = "65536"  # 64MB
                    elif new_value == "critical":
                        value = "131072"  # 128MB
                    else:
                        value = "32768"  # 32MB (normal)
                    
                    cmd = f"sudo sysctl -w vm.min_free_kbytes={value}"
                    subprocess.run(cmd, shell=True, check=True)
                    self.logger.info(f"Applied memory pressure ({new_value}): vm.min_free_kbytes={value}")
                
                elif parameter == TuningParameter.PROCESS_PRIORITY.value:
                    # This would typically adjust nice values for specific processes
                    # For demonstration, we'll adjust the default nice value
                    # Note: This is simplified; real implementation would target specific processes
                    if int(new_value) < 0:
                        # Requires sudo for negative nice values (higher priority)
                        cmd = f"sudo renice {new_value} -p $$"
                    else:
                        cmd = f"renice {new_value} -p $$"
                    subprocess.run(cmd, shell=True, check=True)
                    self.logger.info(f"Applied process priority: {new_value}")
                
                else:
                    self.logger.warning(f"Unknown parameter: {parameter}")
                    success = False
                    error_message = f"Unknown parameter: {parameter}"
            
            except Exception as e:
                self.logger.error(f"Error applying system change: {str(e)}")
                success = False
                error_message = str(e)
            
            if success:
                # Get metrics after applying tuning
                metrics_after = await self.get_current_metrics()
                
                # Update active tunings
                self.active_tunings[tuning_data['parameter']] = tuning_data
                self.tuning_history.append(tuning_data)
                
                return {
                    'success': True,
                    'metrics_before': metrics_before,
                    'metrics_after': metrics_after,
                    'action': tuning_data
                }
            else:
                return {
                    'success': False,
                    'error': error_message
                }
                
        except Exception as e:
            self.logger.error(f"Error applying tuning: {str(e)}")
            return None

    async def get_tuning_recommendations(self):
        """Get tuning recommendations based on current metrics"""
        try:
            # Initialize system state if this is the first call
            await self._initialize_system_state()
            
            # Refresh permissions to ensure we have the latest status
            self.permissions = check_required_permissions()
            
            metrics = await self.get_current_metrics()
            if not metrics:
                return []
            
            recommendations = []
            current_time = datetime.now()
        
            # CPU Usage Recommendations
            if metrics['cpu_usage'] > 80:
                recommendations.append(TuningAction(
                    parameter=TuningParameter.CPU_GOVERNOR,
                    current_value='ondemand',
                    new_value='performance',
                    confidence=0.85,
                    impact_score=0.7,
                    timestamp=current_time,
                    reason="High CPU usage detected - switching to performance mode"
                ))
            elif metrics['cpu_usage'] < 20:
                recommendations.append(TuningAction(
                    parameter=TuningParameter.CPU_GOVERNOR,
                    current_value='performance',
                    new_value='powersave',
                    confidence=0.75,
                    impact_score=0.5,
                    timestamp=current_time,
                    reason="Low CPU usage detected - enabling power saving"
                ))

            # Memory Management
            if metrics['memory_usage'] > 75:
                recommendations.append(TuningAction(
                    parameter=TuningParameter.MEMORY_PRESSURE,
                    current_value='normal',
                    new_value='aggressive',
                    confidence=0.80,
                    impact_score=0.6,
                    timestamp=current_time,
                    reason="High memory usage - increasing memory pressure"
                ))
                recommendations.append(TuningAction(
                    parameter=TuningParameter.SWAP_TENDENCY,
                    current_value='60',
                    new_value='40',
                    confidence=0.75,
                    impact_score=0.5,
                    timestamp=current_time,
                    reason="High memory usage - adjusting swap tendency"
                ))

            # I/O Scheduler Recommendations
            if metrics['disk_usage'] > 70:
                recommendations.append(TuningAction(
                    parameter=TuningParameter.IO_SCHEDULER,
                    current_value='cfq',
                    new_value='deadline',
                    confidence=0.70,
                    impact_score=0.6,
                    timestamp=current_time,
                    reason="High disk usage - optimizing I/O scheduler"
                ))
                recommendations.append(TuningAction(
                    parameter=TuningParameter.DISK_READ_AHEAD,
                    current_value='256',
                    new_value='512',
                    confidence=0.65,
                    impact_score=0.4,
                    timestamp=current_time,
                    reason="High disk usage - increasing read-ahead buffer"
                ))

            # Process Priority Adjustments
            if metrics['cpu_usage'] > 60 and metrics['process_count'] > 100:
                recommendations.append(TuningAction(
                    parameter=TuningParameter.PROCESS_PRIORITY,
                    current_value='0',
                    new_value='-5',
                    confidence=0.75,
                    impact_score=0.5,
                    timestamp=current_time,
                    reason="High process count - adjusting process priorities"
                ))

            # Cache Pressure
            if metrics['memory_usage'] > 60 and metrics['disk_usage'] > 50:
                recommendations.append(TuningAction(
                    parameter=TuningParameter.CACHE_PRESSURE,
                    current_value='100',
                    new_value='150',
                    confidence=0.70,
                    impact_score=0.4,
                    timestamp=current_time,
                    reason="High memory and disk usage - adjusting cache pressure"
                ))

            # Network Buffer Optimization
            if metrics['network_usage'] > 70:
                recommendations.append(TuningAction(
                    parameter=TuningParameter.NETWORK_BUFFER,
                    current_value='256',
                    new_value='512',
                    confidence=0.65,
                    impact_score=0.4,
                    timestamp=current_time,
                    reason="High network usage - increasing network buffer"
                ))

            # Combined Conditions
            if (metrics['cpu_usage'] > 70 and 
                metrics['memory_usage'] > 70 and 
                metrics['disk_usage'] > 70):
                # System under heavy load - aggressive optimization
                recommendations.append(TuningAction(
                    parameter=TuningParameter.PROCESS_PRIORITY,
                    current_value='0',
                    new_value='-10',
                    confidence=0.90,
                    impact_score=0.8,
                    timestamp=current_time,
                    reason="System under heavy load - aggressive process priority adjustment"
                ))
                recommendations.append(TuningAction(
                    parameter=TuningParameter.MEMORY_PRESSURE,
                    current_value='normal',
                    new_value='critical',
                    confidence=0.85,
                    impact_score=0.7,
                    timestamp=current_time,
                    reason="System under heavy load - critical memory pressure"
                ))

            # Sort recommendations by confidence and impact
            recommendations.sort(
                key=lambda x: (x.confidence * x.impact_score), 
                reverse=True
            )
            
            # Filter recommendations based on permissions
            filtered_recommendations = []
            for rec in recommendations:
                param_name = rec.parameter.value
                # Convert parameter enum value to permission key
                perm_key = param_name.lower()
                
                # Add recommendation only if we have permission or it's not in our permission list
                if perm_key not in self.permissions or self.permissions[perm_key]:
                    filtered_recommendations.append(rec)
                else:
                    self.logger.info(f"Filtering out recommendation for {param_name} due to missing permission")
            
            return filtered_recommendations[:5]  # Return top 5 most impactful recommendations that we can apply
        except Exception as e:
            self.logger.error(f"Error getting tuning recommendations: {str(e)}")
            return []   