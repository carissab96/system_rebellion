import logging
import psutil
import json
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any

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
        self._initialize_system_state()

    async def _initialize_system_state(self):
        # Initialize system state here
        pass

    async def get_current_metrics(self) -> Dict:
        """Get current system metrics directly from the system"""
        try:
            return {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_usage': sum(nic.bytes_sent + nic.bytes_recv for nic in psutil.net_io_counters(pernic=True).values()),
                'process_count': len(psutil.pids())
            }
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
            # This is where we'd implement the actual system modifications
            # For now, we'll just simulate success
            success = True
            error_message = None
            
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
            return recommendations[:5]  # Return top 5 most impactful recommendations
        except Exception as e:
            self.logger.error(f"Error getting tuning recommendations: {str(e)}")
            return []   