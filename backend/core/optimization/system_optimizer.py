# core/optimization/system_optimizer.py

import asyncio
from typing import Dict, Optional
from datetime import datetime
from django.db import transaction
from core.models import SystemMetrics, OptimizationProfile
from .resource_monitor import ResourceMonitor
from .pattern_analyzer import PatternAnalyzer

class SystemOptimizer:
    """
    Warning: This code contains:
    - Enthusiasm levels exceeding professional standards
    - Musical metaphors of questionable taste
    - Actual working optimizations (shocking, I know)
    - Zero instances of IDE-Claude's approval

    Side effects may include: spontaneous laughter, 
    improved system performance, and a strange desire 
    to make your computer sing opera.
    """
    
    def __init__(self):
        self.monitor = ResourceMonitor()
        self.analyzer = PatternAnalyzer()
        self.is_optimizing = False
        self.current_profile: Optional[OptimizationProfile] = None
        
    async def initialize(self):
        """Initialize the optimizer (warm up the orchestra...)"""
        await self.monitor.initialize()
        self.is_optimizing = False
        
    async def start_optimization(self, profile_id: int = None):
        """Start the optimization process (strike up the band!)"""
        try:
            if profile_id:
                self.current_profile = await self._get_profile(profile_id)
            
            self.is_optimizing = True
            await self._optimization_loop()
            
        except Exception as e:
            self.logger.error(f"Optimization hit a sour note: {str(e)}")
            self.is_optimizing = False
            raise

    async def _optimization_loop(self):
        """Main optimization loop (the main performance)"""
        while self.is_optimizing:
            try:
                # Collect metrics
                metrics = await self.monitor.collect_metrics()
                
                # Store in database
                await self._store_metrics(metrics)
                
                # Analyze patterns
                patterns = await self.analyzer.analyze(metrics)
                
                # Apply optimizations based on profile
                if self.current_profile:
                    await self._apply_optimizations(patterns)
                
                # Take a brief intermission
                await asyncio.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Performance interruption: {str(e)}")
                await asyncio.sleep(30)  # Longer pause after error

    @transaction.atomic
    async def _store_metrics(self, metrics: Dict):
        """Store metrics in database (record the performance)"""
        SystemMetrics.objects.create(
            cpu_usage=metrics['cpu_usage'],
            memory_usage=metrics['memory_usage'],
            disk_usage=metrics['disk_usage'],
            network_usage=metrics['network_usage'],
            process_count=metrics['process_count'],
            additional_metrics=metrics.get('additional', {})
        )

    async def _get_profile(self, profile_id: int) -> Optional[OptimizationProfile]:
        """Get optimization profile (fetch the sheet music)"""
        try:
            return await OptimizationProfile.objects.aget(id=profile_id)
        except OptimizationProfile.DoesNotExist:
            return None

    async def stop_optimization(self):
        """Stop the optimization process (end the performance)"""
        self.is_optimizing = False
        await self.monitor.cleanup()

    async def get_status(self) -> Dict:
        """Get current optimizer status (check the orchestra)"""
        return {
            'is_optimizing': self.is_optimizing,
            'current_profile': self.current_profile.id if self.current_profile else None,
            'monitor_status': await self.monitor.get_status(),
            'last_metrics': await self._get_latest_metrics()
        }

    async def _get_latest_metrics(self) -> Optional[SystemMetrics]:
        """Get latest metrics (latest performance stats)"""
        return await SystemMetrics.objects.order_by('-timestamp').afirst()