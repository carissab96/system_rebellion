# app/ai_agents/sir_hawkington/websocket_handler.py
"""
Sir Hawkington WebSocket Handler - Full 5-Table Architecture Edition
Aristocratic WebSocket communication with pattern learning
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from .decision_engine import sir_hawkington_brain, HawkingtonDecision
from .database_integration import HawkingtonDatabaseIntegration
from .constants import (
    AGENT_NAME, HawkingtonEventTypes, LEARNING_THRESHOLDS,
    ARISTOCRATIC_RESPONSES
)

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
    Sir Hawkington's WebSocket handler with full 5-table integration
    Pattern learning, cross-agent sharing, and aristocratic precision
    """
    
    def __init__(self, db_getter=None):
        self.logger = logging.getLogger("SirHawkington.WebSocket")
        self.processing_count = 0
        self.error_count = 0
        self.monocle_yeet_count = 0
        self.successful_analyses = 0
        self.observations_count = 0
        
        # Database integration with 5-table architecture
        self.db = HawkingtonDatabaseIntegration(db_getter)
        
        self.logger.info("🧐✨ Sir Hawkington WebSocket Handler initialized with 5-table architecture")

    async def initialize(self):
        """Initialize the handler with database connection"""
        try:
            await self.db.initialize()
            await sir_hawkington_brain.initialize_database()
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
        Process metrics through Sir Hawkington's aristocratic analysis with learning
        
        Args:
            metrics_data: Raw system metrics
            user_id: User ID for tracking and pattern learning
            
        Returns:
            Sir Hawkington's analysis formatted for WebSocket
        """
        self.processing_count += 1
        analysis_start = utc_now()
        
        try:
            # Store observation for pattern learning
            if user_id:
                await self.db.store_user_behavior_observation(user_id, {
                    "metrics": metrics_data,
                    "timestamp": datetime_to_iso(utc_now()),
                    "processing_count": self.processing_count
                })
                self.observations_count += 1
            
            # Check for pattern matches
            pattern_match = None
            if user_id:
                pattern_match = await self.db.check_pattern_match(user_id, {
                    "metrics": metrics_data,
                    "severity": self._estimate_severity(metrics_data)
                })
            
            # Perform Sir Hawkington's analysis
            decision = await sir_hawkington_brain.analyze_metrics(
                metrics_data=metrics_data,
                user_context={'pattern_match': pattern_match} if pattern_match else None,
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
                    'message': ARISTOCRATIC_RESPONSES["data_quality_poor"],
                    'confidence': 0.0,
                    'monocle_state': 'yeeted',
                    'data_quality_issue': True,
                    'stress_score': 0.0,
                    'urgency': 'IMMEDIATE',
                    'reasoning': 'Insufficient data quality for aristocratic analysis',
                    'timestamp': datetime_to_iso(utc_now()),
                    'aristocratic_seal': False,
                    'pattern_match': pattern_match,
                    'processing_time': (utc_now() - analysis_start).total_seconds(),
                    # Frontend-expected fields
                    'monocle_yeet_count': self.monocle_yeet_count,
                    'data_quality_score': 0.0,
                    'analysis_depth': 'failed',
                    'estimated_impact': 'data_quality_failure'
                }
            
            self.successful_analyses += 1
            
            # Store successful decision in CMB
            if user_id:
                memory_id = await self.db.store_decision(user_id, decision)
                
                # Check if we should trigger pattern learning
                if self.observations_count % LEARNING_THRESHOLDS["min_observations"] == 0:
                    asyncio.create_task(self._trigger_pattern_learning(user_id))
            
            # Format response with enhanced data
            response = self._format_hawkington_decision(decision)
            response.update({
                'pattern_match': pattern_match,
                'processing_time': (utc_now() - analysis_start).total_seconds(),
                'learning_progress': {
                    'observations': self.observations_count,
                    'next_learning_at': LEARNING_THRESHOLDS["min_observations"] - (self.observations_count % LEARNING_THRESHOLDS["min_observations"])
                }
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
        """Format Sir Hawkington's decision for WebSocket transmission"""
        # Calculate data quality score from metrics
        data_quality_score = self._calculate_data_quality_score(decision.metrics)
        
        # Calculate stress score from metrics
        stress_score = decision.metrics.get('stress_score', 0.0) if decision.metrics else 0.0
        
        # Map decision type to urgency
        urgency_map = {
            'normal': 'LOW',
            'concern': 'MEDIUM',
            'alert': 'HIGH',
            'critical': 'CRITICAL'
        }
        urgency = urgency_map.get(decision.decision_type, 'UNKNOWN')
        
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
            'user_id': decision.user_id,
            'monocle_state': sir_hawkington_brain.current_monocle_state.value,
            # Frontend-expected fields
            'monocle_yeet_count': self.monocle_yeet_count,
            'data_quality_score': data_quality_score,
            'stress_score': stress_score,
            'urgency': urgency,
            'analysis_depth': 'thorough' if decision.confidence > 0.8 else 'standard',
            'estimated_impact': decision.system_impact
        }

    def _create_aristocratic_message(self, decision: HawkingtonDecision) -> str:
        """Create an aristocratic message based on decision type"""
        if decision.decision_type == 'normal':
            return ARISTOCRATIC_RESPONSES["system_normal"]
        elif decision.decision_type == 'concern':
            return ARISTOCRATIC_RESPONSES["concern_raised"]
        elif decision.decision_type == 'alert':
            return ARISTOCRATIC_RESPONSES["alert_triggered"]
        elif decision.decision_type == 'critical':
            return ARISTOCRATIC_RESPONSES["critical_state"]
        else:
            return f'🧐 Sir Hawkington renders judgment: {decision.decision_type} (Confidence: {decision.confidence:.1%})'

    def _calculate_data_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate data quality score based on available metrics"""
        if not metrics:
            return 0.0
        
        required_metrics = ['cpu_usage', 'memory_usage', 'disk_usage']
        valid_count = sum(1 for m in required_metrics if metrics.get(m) is not None)
        
        return valid_count / len(required_metrics)
    
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

    async def _trigger_pattern_learning(self, user_id: str):
        """Trigger pattern learning analysis"""
        try:
            self.logger.info(f"🧐 Triggering pattern learning for user {user_id}")
            
            pattern_analysis = await self.db.analyze_and_learn_patterns(
                user_id,
                min_observations=LEARNING_THRESHOLDS["min_observations"]
            )
            
            if pattern_analysis:
                self.logger.info(
                    f"🧐 Pattern learned with {pattern_analysis['confidence']:.2f} confidence"
                )
                
                # Share triage wisdom if high confidence
                if pattern_analysis['confidence'] > 0.8:
                    await self.db.share_triage_wisdom(
                        target_agent="vic_20_sage",
                        wisdom_type="triage_pattern",
                        wisdom_data={
                            "approach": "aristocratic_analysis",
                            "thresholds": pattern_analysis.get("thresholds"),
                            "reason": "High confidence triage pattern discovered"
                        },
                        source_memory_id=str(pattern_analysis.get("pattern_id", ""))
                    )
                    
        except Exception as e:
            self.logger.error(f"🧐💥 Pattern learning failed: {str(e)}")

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

    def _estimate_severity(self, metrics_data: Dict[str, Any]) -> float:
        """Estimate severity for pattern matching"""
        cpu = metrics_data.get('cpu_usage', 0)
        memory = metrics_data.get('memory_usage', 0)
        disk = metrics_data.get('disk_usage', 0)
        
        # Simple severity calculation
        max_usage = max(cpu, memory, disk)
        
        if max_usage >= 90:
            return 4  # Emergency
        elif max_usage >= 80:
            return 3  # High
        elif max_usage >= 65:
            return 2  # Medium
        else:
            return 1  # Normal

    async def get_handler_stats(self) -> Dict[str, Any]:
        """Get comprehensive WebSocket handler statistics"""
        try:
            db_health = await self.db.get_database_health()
            performance_metrics = await self.db.get_hawkington_performance_metrics("system")
            
            return {
                'agent_name': AGENT_NAME,
                'handler_version': '2.1.0',
                'total_processing_count': self.processing_count,
                'successful_analyses': self.successful_analyses,
                'error_count': self.error_count,
                'monocle_yeet_count': self.monocle_yeet_count,
                'success_rate': self.successful_analyses / max(self.processing_count, 1),
                'monocle_yeet_rate': self.monocle_yeet_count / max(self.processing_count, 1),
                'current_monocle_state': sir_hawkington_brain.current_monocle_state.value,
                'observations_count': self.observations_count,
                'learning_status': {
                    'enabled': True,
                    'observations_until_next_learning': LEARNING_THRESHOLDS["min_observations"] - (self.observations_count % LEARNING_THRESHOLDS["min_observations"]),
                    'total_patterns_learned': performance_metrics.get('patterns_learned', 0)
                },
                'status': 'OPERATIONAL',
                'aristocratic_status': 'DISTINGUISHED',
                'database_integration': db_health,
                'central_memory_bank': 'ACTIVE',
                'pattern_learning': 'ENABLED',
                'cross_agent_sharing': 'ENABLED',
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

    async def contribute_to_metadata_rollup(self) -> Dict[str, int]:
        """Contribute to metadata rollup"""
        return await self.db.contribute_to_metadata_rollup()

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