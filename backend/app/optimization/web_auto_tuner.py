from django.utils import timezone
from django.core.cache import cache
from asgiref.sync import sync_to_async
from core.models import SystemMetrics, OptimizationResult, SystemAlert
from .auto_tuner import AutoTuner, TuningParameter, TuningAction
from typing import Dict, List, Optional
import logging
import json
import psutil
import asyncio
from datetime import datetime, timedelta

class WebAutoTuner(AutoTuner):
    """Web demo of the SystemOptimizer capabilities.
    
    Showcases the power of our system optimization technology:
    - Real-time system metrics and pattern analysis
    - Intelligent resource optimization strategies
    - Adaptive performance tuning
    - Process-aware resource management
    - Comprehensive system health monitoring
    
    This web demo provides a glimpse of what's possible with 
    the full SystemOptimizer integration.
    """
    
    # Demo configuration
    CACHE_TIMEOUT = 60  # Cache timeout in seconds
    PATTERN_WINDOW = 300  # Pattern analysis window in seconds
    MAX_OPTIMIZATIONS = 5  # Maximum demo optimizations
    
    # System thresholds
    CPU_THRESHOLD = 80  # CPU usage threshold
    MEMORY_THRESHOLD = 75  # Memory usage threshold
    IO_THRESHOLD = 70  # I/O usage threshold
    PROCESS_THRESHOLD = 100  # Process count threshold
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('WebAutoTuner')
    
    def _get_cache_key(self, prefix: str) -> str:
        """Generate a demo-specific cache key."""
        return f'system_optimizer_demo:{prefix}:{timezone.now().strftime("%Y%m%d_%H")}'    

    async def _get_system_state(self) -> Optional[Dict]:
        """Get current system state with pattern analysis.
        
        Demonstrates the SystemOptimizer's ability to:
        1. Collect comprehensive system metrics
        2. Analyze resource usage patterns
        3. Identify optimization opportunities
        4. Track system health trends
        
        Returns:
            Dict containing system state and analysis
        """
        cache_key = self._get_cache_key('system_state')
        cached_state = cache.get(cache_key)
        
        if cached_state:
            self.logger.debug(f"Cache hit for system state: {cache_key}")
            return cached_state
            
        try:
            # Get current system metrics
            metrics = self.get_current_metrics()
            if not metrics:
                return None
                
            # Get historical data for pattern analysis
            history_key = self._get_cache_key('metrics_history')
            metrics_history = cache.get(history_key, [])
            metrics_history.append(metrics)
            
            # Keep last 5 minutes of data
            cutoff_time = datetime.now() - timedelta(seconds=self.PATTERN_WINDOW)
            metrics_history = [m for m in metrics_history if m['timestamp'] > cutoff_time]
            
            # Analyze patterns
            cpu_pattern = self._analyze_pattern([m['cpu_usage'] for m in metrics_history])
            memory_pattern = self._analyze_pattern([m['memory_usage'] for m in metrics_history])
            io_pattern = self._analyze_pattern([m['disk_usage'] for m in metrics_history])
            
            # Get process information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] > 5 or pinfo['memory_percent'] > 5:
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'cpu_usage': pinfo['cpu_percent'],
                            'memory_usage': pinfo['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            state = {
                # Current metrics
                'cpu_usage': metrics['cpu_usage'],
                'memory_usage': metrics['memory_usage'],
                'disk_usage': metrics['disk_usage'],
                'network_usage': metrics['network_usage'],
                'process_count': metrics['process_count'],
                
                # Resource patterns
                'patterns': {
                    'cpu': cpu_pattern,
                    'memory': memory_pattern,
                    'io': io_pattern
                },
                
                # Process analysis
                'top_processes': sorted(processes, 
                                      key=lambda x: x['cpu_usage'] + x['memory_usage'], 
                                      reverse=True)[:5],
                                      
                # System health indicators
                'health_metrics': {
                    'cpu_pressure': self._calculate_pressure(metrics['cpu_usage']),
                    'memory_pressure': self._calculate_pressure(metrics['memory_usage']),
                    'io_pressure': self._calculate_pressure(metrics['disk_usage'])
                },
                
                'timestamp': datetime.now().isoformat()
            }
            
            # Update caches
            cache.set(cache_key, state, self.CACHE_TIMEOUT)
            cache.set(history_key, metrics_history, self.CACHE_TIMEOUT)
            self.logger.debug(f"Updated system state: {len(metrics_history)} historical points")
            return state
            
        except Exception as e:
            self.logger.error(f"Error analyzing system state: {str(e)}")
            return None
            
    def _analyze_pattern(self, values: List[float]) -> Dict:
        """Analyze resource usage patterns"""
        if not values:
            return {'trend': 'stable', 'volatility': 'low'}
            
        # Calculate trend
        avg = sum(values) / len(values)
        trend = values[-1] - avg
        
        # Calculate volatility
        volatility = sum(abs(v - avg) for v in values) / len(values)
        
        return {
            'trend': 'up' if trend > 5 else 'down' if trend < -5 else 'stable',
            'volatility': 'high' if volatility > 10 else 'medium' if volatility > 5 else 'low',
            'average': avg,
            'current': values[-1]
        }
        
    def _calculate_pressure(self, usage: float) -> str:
        """Calculate resource pressure level"""
        if usage > 80:
            return 'critical'
        elif usage > 60:
            return 'high'
        elif usage > 40:
            return 'medium'
        return 'low'

    async def _get_recommendations(self) -> List[TuningAction]:
        """Get web-optimized tuning recommendations with intelligent caching and trend analysis.
        
        Returns:
            List of TuningAction objects with confidence scores and impact predictions
        """
        cache_key = self._get_cache_key('recommendations')
        cached_recs = cache.get(cache_key)
        
        if cached_recs:
            self.logger.debug(f"Cache hit for recommendations: {cache_key}")
            # Reconstruct TuningAction objects from cache with only the required fields
            return [TuningAction(
                parameter=TuningParameter(rec['parameter']),
                current_value=rec['current_value'],
                new_value=rec['new_value'],
                confidence=rec['metrics']['confidence'] / 100,  # Convert back from percentage
                impact_score=rec['metrics']['impact_score'] / 100,
                timestamp=datetime.fromisoformat(rec['timestamp']['iso']),
                reason=rec['reason']
            ) for rec in cached_recs]
            
        try:
            # Get base recommendations
            recs = await self.get_tuning_recommendations()
            
            # Get system state with trends
            state = await self._get_system_state()
            if state and state.get('web_metrics'):
                web_metrics = state['web_metrics']
                trends = state.get('trends', {})
                
                # Response time optimization with trend analysis
                if web_metrics['response_time'] > self.RESPONSE_TIME_THRESHOLD:
                    confidence = 0.8 + (0.1 if trends.get('cpu_trend_direction') == 'up' else 0)
                    recs.append(TuningAction(
                        parameter=TuningParameter.PROCESS_PRIORITY,
                        current_value='0',
                        new_value='-5',
                        confidence=confidence,
                        impact_score=0.7,
                        timestamp=timezone.now(),
                        reason=f"High response time ({web_metrics['response_time']}ms) with {trends.get('cpu_trend_direction', 'stable')} CPU trend"
                    ))
                
                # Error rate optimization with memory trend
                if web_metrics['error_rate'] > self.ERROR_RATE_THRESHOLD:
                    confidence = 0.75 + (0.1 if trends.get('memory_trend_direction') == 'up' else 0)
                    recs.append(TuningAction(
                        parameter=TuningParameter.MEMORY_PRESSURE,
                        current_value='normal',
                        new_value='low',
                        confidence=confidence,
                        impact_score=0.6,
                        timestamp=timezone.now(),
                        reason=f"High error rate ({web_metrics['error_rate']*100:.1f}%) with {trends.get('memory_trend_direction', 'stable')} memory trend"
                    ))
                
                # Active sessions optimization
                if web_metrics['active_sessions'] > self.ACTIVE_SESSIONS_THRESHOLD:
                    recs.append(TuningAction(
                        parameter=TuningParameter.CACHE_PRESSURE,
                        current_value='100',
                        new_value='150',
                        confidence=0.7,
                        impact_score=0.5,
                        timestamp=timezone.now(),
                        reason=f"High active sessions ({web_metrics['active_sessions']}) - optimizing cache"
                    ))
                
                # Bandwidth optimization
                if web_metrics.get('bandwidth_usage', 0) > 80:
                    recs.append(TuningAction(
                        parameter=TuningParameter.NETWORK_BUFFER,
                        current_value='256',
                        new_value='512',
                        confidence=0.7,
                        impact_score=0.5,
                        timestamp=timezone.now(),
                        reason=f"High bandwidth usage ({web_metrics.get('bandwidth_usage')}%) - optimizing network buffer"
                    ))
            
            # Sort recommendations by potential impact
            recs.sort(key=lambda x: x.confidence * x.impact_score, reverse=True)
            
            # Cache the recommendations
            cache.set(cache_key, [self._tuning_to_dict(r) for r in recs], self.CACHE_TIMEOUT)
            self.logger.debug(f"Generated {len(recs)} recommendations")
            return recs
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {str(e)}", exc_info=True)
            return []

    async def _apply_tuning(self, data: Dict) -> Optional[Dict]:
        """Apply a tuning recommendation with rate limiting.
        
        Args:
            data: Dictionary containing tuning parameters
            
        Returns:
            Dictionary containing the result or None if failed
        """
        try:
            # Check rate limit
            self.logger.info(f"Attempting to apply tuning with data: {data}")
            rate_key = self._get_cache_key('tuning_rate')
            attempt_count = cache.get(rate_key, 0)
            
            if attempt_count >= self.MAX_TUNING_ATTEMPTS:
                self.logger.warning("Rate limit exceeded for tuning attempts")
                return None
                
            # Increment attempt counter
            cache.set(rate_key, attempt_count + 1, self.RATE_LIMIT_TIMEOUT)
            
            # Apply the tuning
            result = await self.apply_tuning(data)
            if result:
                # Log successful tuning
                await sync_to_async(SystemAlert.objects.create)(
                    title='Tuning Applied',
                    message=f"Applied tuning: {data.get('parameter')} = {data.get('new_value')}",
                    severity='LOW',
                    user_id=data.get('user_id')  # Make sure to associate with user
                )
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error applying tuning: {str(e)}")
            return None

    def _tuning_to_dict(self, tuning: TuningAction) -> Dict:
        """Convert a TuningAction to a comprehensive web-friendly dictionary.
        
        Args:
            tuning: TuningAction object
            
        Returns:
            Dictionary representation of the tuning action with detailed metrics
        """
        confidence_pct = round(tuning.confidence * 100, 2)
        impact_pct = round(tuning.impact_score * 100, 2)
        improvement_pct = round(tuning.confidence * tuning.impact_score * 100, 1)
        
        return {
            'parameter': tuning.parameter.value,
            'current_value': tuning.current_value,
            'new_value': tuning.new_value,
            'metrics': {
                'confidence': confidence_pct,
                'impact_score': impact_pct,
                'estimated_improvement': improvement_pct
            },
            'display': {
                'confidence': f"{confidence_pct}%",
                'impact': f"{impact_pct}%",
                'improvement': f"{improvement_pct}%"
            },
            'timestamp': {
                'iso': tuning.timestamp.isoformat(),
                'unix': int(tuning.timestamp.timestamp())
            },
            'reason': tuning.reason,
            'priority': 'high' if improvement_pct > 50 else 'medium' if improvement_pct > 25 else 'low',
            'status': 'pending',
            'id': f"{tuning.parameter.value}_{int(tuning.timestamp.timestamp())}"
        }