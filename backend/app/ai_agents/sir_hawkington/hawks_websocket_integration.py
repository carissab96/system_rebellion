# app/ai_agents/sir_hawkington/websocket_handler.py
"""
Sir Hawkington WebSocket Handler - Central Memory Bank Edition
Aristocratic WebSocket communication with proper central memory integration
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from .decision_engine import sir_hawkington_brain, HawkingtonDecision
from .database_integration import HawkingtonDatabaseIntegration
from .constants import HawkingtonEventTypes, AGENT_NAME

# Production-ready UTC helper
def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

# JSON serialization helper for WebSocket
def datetime_to_iso(dt):
    """Convert datetime to ISO string for JSON serialization"""
    return dt.isoformat() if dt else None

logger = logging.getLogger("SirHawkington.WebSocket")

class SirHawkingtonWebSocketHandler:
    """
    Sir Hawkington's WebSocket handler with central memory bank integration
    Production-ready with proper error handling and pattern learning
    """
    
    def __init__(self, db_getter=None):
        self.logger = logging.getLogger("SirHawkington.WebSocket")
        self.processing_count = 0
        self.error_count = 0
        self.monocle_yeet_count = 0
        self.successful_analyses = 0
        
        # Database integration for central memory bank
        self.db = HawkingtonDatabaseIntegration(db_getter)
        
        self.logger.info("🧐✨ Sir Hawkington WebSocket Handler with Central Memory Bank initialized")

    async def initialize(self):
        """Initialize the handler with database connection"""
        try:
            await self.db.initialize()
            self.logger.info("🧐 WebSocket handler initialized with aristocratic precision")
        except Exception as e:
            self.logger.error(f"🧐💥 Handler initialization failed: {str(e)}")
            raise

    async def process_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process metrics through Sir Hawkington's aristocratic analysis with central memory
        
        Args:
            metrics_data: Raw system metrics
            user_id: User ID for tracking and pattern learning
            
        Returns:
            Sir Hawkington's analysis formatted for WebSocket
        """
        self.processing_count += 1
        analysis_start = utc_now()
        
        try:
            # Get user patterns for enhanced analysis
            user_patterns = {}
            if user_id:
                user_patterns = await self.db.check_pattern_match(user_id, metrics_data)
            
            # Perform Sir Hawkington's analysis
            decision = await sir_hawkington_brain.analyze_metrics(
                metrics_data=metrics_data,
                user_context={'patterns': user_patterns},
                user_id=user_id
            )
            
            if decision is None:
                # MONOCLE YEETED
                self.monocle_yeet_count += 1
                
                # Store monocle yeet incident
                if user_id:
                    await self._store_monocle_yeet_incident(user_id, metrics_data)
                
                self.logger.warning(f"🧐💥 Sir Hawkington has yeeted his monocle - insufficient data quality")
                
                return {
                    'agent_name': AGENT_NAME,
                    'decision_type': 'monocle_yeeted',
                    'message': '🧐💥 I say! The data quality is most unsatisfactory. *yeets monocle*',
                    'confidence': 0.0,
                    'monocle_state': 'yeeted',
                    'data_quality_issue': True,
                    'stress_score': 0.0,
                    'urgency': 'IMMEDIATE',
                    'reasoning': 'Insufficient data quality for aristocratic analysis',
                    'timestamp': datetime_to_iso(utc_now()),
                    'aristocratic_seal': False,
                    'user_patterns': user_patterns,
                    'processing_time': (utc_now() - analysis_start).total_seconds()
                }
            
            self.successful_analyses += 1
            
            # Store successful decision in central memory bank
            if user_id:
                await self._store_successful_analysis(user_id, decision, metrics_data)
                
                # Learn from this interaction
                await self._learn_from_interaction(user_id, decision, user_patterns)
            
            # Format response with enhanced data
            response = self._format_hawkington_decision(decision)
            response.update({
                'user_patterns': user_patterns,
                'processing_time': (utc_now() - analysis_start).total_seconds(),
                'pattern_matches': len(user_patterns) > 0
            })
            
            return response
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"🧐❌ Sir Hawkington processing failed: {str(e)}")
            
            return {
                'agent_name': AGENT_NAME,
                'decision_type': 'error',
                'message': f'🧐💥 Most regrettable! An error has occurred: {str(e)}',
                'confidence': 0.0,
                'error': True,
                'monocle_state': 'cracked',
                'timestamp': datetime_to_iso(utc_now()),
                'aristocratic_seal': False,
                'processing_time': (utc_now() - analysis_start).total_seconds()
            }

    def _format_hawkington_decision(self, decision: HawkingtonDecision) -> Dict[str, Any]:
        """Format Sir Hawkington's decision with aristocratic precision"""
        return {
            'agent_name': AGENT_NAME,
            'decision_id': decision.decision_id,
            'decision_type': decision.decision_type,
            'message': self._create_aristocratic_message(decision),
            'confidence': round(decision.confidence, 3),
            'reasoning': decision.reasoning,
            'system_impact': decision.system_impact,
            'timestamp': datetime_to_iso(decision.timestamp),
            'aristocratic_seal': True,
            'metrics_analyzed': self._sanitize_metrics_for_websocket(decision.metrics),
            'user_id': decision.user_id
        }

    def _create_aristocratic_message(self, decision: HawkingtonDecision) -> str:
        """Create an aristocratic message based on decision type"""
        message_templates = {
            'normal': '🧐 Sir Hawkington observes with aristocratic satisfaction - all systems operating within acceptable parameters.',
            'concern': f'🧐 Sir Hawkington adjusts his monocle with measured concern - system requires attention (Confidence: {decision.confidence:.1%}).',
            'alert': f'🧐⚠️ Sir Hawkington\'s monocle has fogged with serious concern! System alert detected (Confidence: {decision.confidence:.1%}).',
            'critical': f'🧐🚨 Sir Hawkington has YEETED his monocle in aristocratic horror! CRITICAL SYSTEM ISSUE (Confidence: {decision.confidence:.1%}).'
        }
        
        return message_templates.get(decision.decision_type, 
            f'🧐 Sir Hawkington renders judgment: {decision.decision_type} (Confidence: {decision.confidence:.1%})')

    def _sanitize_metrics_for_websocket(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metrics for WebSocket transmission with JSON-safe serialization"""
        sanitized = {}
        for key, value in metrics.items():
            if isinstance(value, datetime):
                sanitized[key] = datetime_to_iso(value)
            elif isinstance(value, (int, float, str, bool, type(None))):
                sanitized[key] = value
            elif isinstance(value, (list, dict)):
                sanitized[key] = value  # JSON serializable
            else:
                sanitized[key] = str(value)  # Convert to string as fallback
        return sanitized

    async def _store_monocle_yeet_incident(self, user_id: str, metrics_data: Dict[str, Any]):
        """Store monocle yeet incident in central memory bank"""
        try:
            incident_data = {
                'timestamp': utc_now(),
                'reason': 'Data quality beneath aristocratic standards',
                'yeet_intensity': 'concerned',
                'missing_metrics': self._identify_missing_metrics(metrics_data),
                'invalid_metrics': self._identify_invalid_metrics(metrics_data)
            }
            
            await self.db.store_monocle_yeet_incident(user_id, incident_data)
            
        except Exception as e:
            self.logger.error(f"🧐💥 Failed to store monocle yeet incident: {str(e)}")

    async def _store_successful_analysis(self, user_id: str, decision: HawkingtonDecision, metrics_data: Dict[str, Any]):
        """Store successful analysis in central memory bank"""
        try:
            # Store the decision directly - no intermediate types needed
            await self.db.store_decision(user_id, decision)
            
        except Exception as e:
            self.logger.error(f"🧐💥 Failed to store successful analysis: {str(e)}")

    async def _learn_from_interaction(self, user_id: str, decision: HawkingtonDecision, user_patterns: Dict[str, Any]):
        """Learn patterns from user interactions"""
        try:
            # Store pattern observation with metrics data
            await self.db.store_user_behavior_observation(user_id, decision.metrics)
            
            # Try to learn patterns every 25 observations
            performance_metrics = await self.db.get_hawkington_performance_metrics(user_id)
            if performance_metrics.get('observation_count', 0) % 25 == 0:
                learned_pattern = await self.db.analyze_and_learn_patterns(user_id)
                
                if learned_pattern:
                    self.logger.info(f"🧐 Sir Hawkington has discerned new patterns for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"🧐💥 Failed to learn from interaction: {str(e)}")

    def _identify_missing_metrics(self, metrics_data: Dict[str, Any]) -> List[str]:
        """Identify missing critical metrics"""
        critical_metrics = ['cpu_usage', 'memory_usage', 'disk_usage']
        missing = []
        
        for metric in critical_metrics:
            if metrics_data.get(metric) is None:
                missing.append(metric)
        
        return missing

    def _identify_invalid_metrics(self, metrics_data: Dict[str, Any]) -> List[str]:
        """Identify invalid metric values"""
        invalid = []
        
        for metric, value in metrics_data.items():
            if metric in ['cpu_usage', 'memory_usage', 'disk_usage']:
                if not isinstance(value, (int, float)) or not (0 <= value <= 100):
                    invalid.append(f"{metric}={value}")
        
        return invalid

    def _determine_analysis_priority(self, decision_type: str) -> int:
        """Determine priority based on decision type - returns integer for central memory bank"""
        priority_map = {
            'critical': 5,  # CRITICAL
            'alert': 4,     # HIGH
            'concern': 3,   # MEDIUM
            'normal': 2     # LOW
        }
        return priority_map.get(decision_type, 3)  # Default to MEDIUM

    def _create_metrics_snapshot(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a clean metrics snapshot for storage"""
        snapshot = {}
        key_metrics = ['cpu_usage', 'memory_usage', 'disk_usage', 'process_count']
        
        for metric in key_metrics:
            if metric in metrics_data:
                snapshot[metric] = metrics_data[metric]
        
        # Add network data if available
        if 'network' in metrics_data:
            snapshot['network_available'] = True
            network_data = metrics_data['network']
            if isinstance(network_data, dict):
                snapshot['network_bytes_sent'] = network_data.get('bytes_sent')
                snapshot['network_bytes_recv'] = network_data.get('bytes_recv')
        
        snapshot['snapshot_timestamp'] = datetime_to_iso(utc_now())
        return snapshot

    async def get_handler_stats(self) -> Dict[str, Any]:
        """Get comprehensive WebSocket handler statistics"""
        try:
            db_health = await self.db.get_database_health()
            
            return {
                'agent_name': AGENT_NAME,
                'handler_version': '2.0.0',
                'total_processing_count': self.processing_count,
                'successful_analyses': self.successful_analyses,
                'error_count': self.error_count,
                'monocle_yeet_count': self.monocle_yeet_count,
                                'success_rate': self.successful_analyses / max(self.processing_count, 1),
                'monocle_yeet_rate': self.monocle_yeet_count / max(self.processing_count, 1),
                'current_monocle_state': sir_hawkington_brain.current_monocle_state.value,
                'status': 'OPERATIONAL',
                'aristocratic_status': 'DISTINGUISHED',
                'database_integration': db_health,
                'central_memory_bank': 'ACTIVE',
                'pattern_learning': 'ENABLED',
                'last_updated': datetime_to_iso(utc_now())
            }
        except Exception as e:
            self.logger.error(f"🧐💥 Failed to get handler stats: {str(e)}")
            return {
                'agent_name': AGENT_NAME,
                'status': 'ERROR',
                'error': str(e),
                'last_updated': datetime_to_iso(utc_now())
            }

    async def broadcast_to_users(self, user_data_list: List[Dict[str, Any]]):
        """
        Broadcast analysis results to multiple users concurrently
        Production-ready with proper error handling
        """
        if not user_data_list:
            return
        
        async def process_user_data(user_data):
            try:
                user_id = user_data.get('user_id')
                metrics = user_data.get('metrics', {})
                websocket = user_data.get('websocket')
                
                if not all([user_id, metrics, websocket]):
                    return
                
                # Process metrics
                result = await self.process_metrics(metrics, user_id)
                
                # Send to WebSocket with JSON-safe serialization
                await websocket.send_json(result)
                
            except Exception as e:
                self.logger.error(f"🧐💥 Failed to process user {user_data.get('user_id', 'unknown')}: {str(e)}")
        
        # Process all users concurrently
        await asyncio.gather(
            *[process_user_data(user_data) for user_data in user_data_list],
            return_exceptions=True
        )

# Global handler instance
_hawkington_handler: Optional[SirHawkingtonWebSocketHandler] = None
_handler_lock = asyncio.Lock()

async def get_hawkington_websocket_handler(db_getter=None):
    """Get global WebSocket handler instance with thread-safe initialization"""
    global _hawkington_handler
    
    if _hawkington_handler is None:
        async with _handler_lock:
            # Double-check pattern for thread safety
            if _hawkington_handler is None:
                _hawkington_handler = SirHawkingtonWebSocketHandler(db_getter)
                await _hawkington_handler.initialize()
    
    return _hawkington_handler