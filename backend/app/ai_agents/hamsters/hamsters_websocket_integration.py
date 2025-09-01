# app/ai_agents/hamsters/websocket_handler.py
"""
The Hamsters WebSocket Handler V3 - Central Memory Bank Edition
Steve, Bob, and Carl's Infrastructure Communication System
Now with pattern learning and cross-agent coordination!
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import random
import asyncio

from .decision_engine_sbcV3 import (
    hamsters_brain,
    analyze_infrastructure,
    get_hamster_stats,
    BeerLevel
)
from .database_integration import HamstersDatabaseIntegration
from .constants import AGENT_NAME, HamstersEventTypes, ALL_HAMSTERS

logger = logging.getLogger("Hamsters.WebSocket")

def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

def datetime_to_iso(dt):
    """Convert datetime to ISO string for JSON serialization"""
    return dt.isoformat() if dt else None

class HamstersWebSocketHandler:
    """
    Dedicated WebSocket handler for The Hamsters with Central Memory Bank
    
    Translates Steve, Bob, and Carl's squeaks into WebSocket messages
    Includes pattern learning and cross-agent communication
    """
    
    def __init__(self, db_getter=None):
        self.logger = logging.getLogger("Hamsters.WebSocket")
        self.processing_count = 0
        self.error_count = 0
        self.wheel_spin_count = 0
        self.successful_interventions = 0
        
        # Database integration for central memory bank
        self.db = HamstersDatabaseIntegration(db_getter)
        
        # Track individual hamster communications
        self.steve_squeaks = 0
        self.bob_squeaks = 0
        self.carl_squeaks = 0
        
        # Communication patterns
        self.squeak_patterns = {
            'normal': ['*squeak*', '*chirp*', '*squeak squeak*'],
            'excited': ['*SQUEAK!*', '*excited chirping*', '*rapid squeaking*'],
            'emergency': ['*LOUD SQUEAKING*', '*ALARM SQUEAKS*', '*PANIC CHIRPS*'],
            'happy': ['*happy squeaking*', '*content chirps*', '*satisfied squeak*']
        }
        
        self.logger.info("🐹🍺 The Hamsters WebSocket Handler V3 initialized with Central Memory Bank!")
    
    async def initialize(self):
        """Initialize the handler with database connection"""
        try:
            await self.db.initialize()
            self.logger.info("🐹 WebSocket handler initialized with beer-powered database")
        except Exception as e:
            self.logger.error(f"🐹💥 Handler initialization failed: {str(e)}")
            raise
    
    async def process_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process metrics through The Hamsters' infrastructure analysis
        Returns both squeaks and human-readable translations
        """
        self.processing_count += 1
        
        try:
            # Store behavior observation for pattern learning
            if user_id:
                await self.db.store_user_behavior_observation(user_id, metrics_data)
                
                # Check for pattern matches
                pattern_match = await self.db.check_pattern_match(user_id, metrics_data)
                
                # Learn patterns every 50 observations
                performance = await self.db.get_hamster_performance_metrics(user_id)
                if performance.get('observation_count', 0) % 50 == 0:
                    learned_pattern = await self.db.analyze_and_learn_patterns(user_id)
                    if learned_pattern:
                        self.logger.info(f"🐹 Hamsters learned infrastructure pattern for user {user_id}")
            
            # Get infrastructure decision
            decision = await analyze_infrastructure(metrics_data, user_id)
            
            if decision is None:
                # WHEEL SPINNING - no intervention needed
                self.wheel_spin_count += 1
                
                # Generate appropriate squeaks
                squeaks = self._generate_idle_squeaks()
                
                return {
                    'agent_name': AGENT_NAME,
                    'decision_type': 'all_clear',
                    'message': squeaks['combined'],
                    'human_translation': 'Infrastructure running smoothly - beer break time!',
                    'individual_squeaks': squeaks['individual'],
                    'confidence': 0.0,
                    'wheel_state': 'spinning',
                    'intervention_needed': False,
                    'current_activity': 'monitoring',
                    'hamster_status': await self._get_hamster_status(),
                    'pattern_match': pattern_match if user_id else None,
                    'timestamp': datetime_to_iso(utc_now()),
                    'stored_in_memory': True
                }
            
            self.successful_interventions += 1
            
            # Store the decision in central memory bank
            if user_id:
                decision_data = {
                    'decision_id': str(decision.timestamp.timestamp()),
                    'intervention_type': decision.intervention_type,
                    'priority': decision.priority.value,
                    'steve_assessment': decision.steve_assessment,
                    'bob_suggestion': decision.bob_suggestion,
                    'carl_calculation': decision.carl_calculation,
                    'telepathic_consensus': decision.telepathic_consensus,
                    'confidence': decision.confidence,
                    'tools_required': decision.tools_required,
                    'beer_consumption_estimate': decision.beer_consumption_estimate,
                    'duct_tape_grade': decision.duct_tape_grade.value,
                    'actual_squeaks': decision.actual_squeaks,
                    'human_translation': decision.human_translation,
                    'estimated_duration': decision.estimated_duration,
                    'urgency': decision.urgency
                }
                
                await self.db.store_collective_decision(user_id, decision_data)
            
            return await self._format_infrastructure_decision(decision, pattern_match if user_id else None)
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"🐹❌ The Hamsters are confused: {str(e)}")
            
            # Generate error squeaks
            error_squeaks = self._generate_error_squeaks()
            
            return {
                'agent_name': AGENT_NAME,
                'decision_type': 'error',
                'message': error_squeaks['combined'],
                'human_translation': f'Infrastructure analysis failed: {str(e)}',
                'individual_squeaks': error_squeaks['individual'],
                'confidence': 0.0,
                'error': True,
                'wheel_state': 'jammed',
                'hamster_status': {
                    'steve': 'concerned',
                    'bob': 'confused',
                    'carl': 'checking duct tape'
                },
                'timestamp': datetime_to_iso(utc_now())
            }
    
    async def _format_infrastructure_decision(
        self, 
        decision,
        pattern_match: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format The Hamsters' infrastructure decision for WebSocket"""
        
        # Get current hamster stats
        stats = get_hamster_stats()
        
        # Track individual communications
        self.steve_squeaks += 1
        self.bob_squeaks += 1
        self.carl_squeaks += 1
        
        response = {
            'agent_name': AGENT_NAME,
            'decision_type': decision.priority.value,
            'intervention_type': decision.intervention_type,
            
            # Communications
            'message': decision.actual_squeaks,
            'human_translation': decision.human_translation,
            'individual_assessments': {
                'steve': decision.steve_assessment,
                                'bob': decision.bob_suggestion,
                'carl': decision.carl_calculation
            },
            
            # Decision details
            'confidence': round(decision.confidence, 3),
            'urgency': decision.urgency,
            'telepathic_consensus': decision.telepathic_consensus,
            'tools_required': decision.tools_required,
            'beer_consumption_estimate': decision.beer_consumption_estimate,
            'duct_tape_grade': decision.duct_tape_grade.value,
            'estimated_duration': decision.estimated_duration,
            
            # Current status
            'hamster_status': await self._get_hamster_status(),
            'collective_beer_level': stats['collective_stats']['beer_level'],
            'is_3am': stats['collective_stats']['is_prime_time'],
            
            # Pattern learning
            'pattern_context': pattern_match if pattern_match else None,
            
            # WebSocket specific
            'timestamp': datetime_to_iso(decision.timestamp),
            'requires_immediate_action': decision.priority.value in ['hold_my_beer', 'full_redneck'],
            'broadcast_priority': self._determine_broadcast_priority(decision.priority.value),
            'stored_in_memory': True
        }
        
        # Add pattern-based recommendations if available
        if pattern_match and pattern_match.get('has_matches'):
            response['pattern_recommendations'] = pattern_match.get('recommendations', [])
            response['pattern_confidence'] = pattern_match.get('best_match', {}).get('confidence', 0)
        
        return response
    
    async def get_handler_stats(self) -> Dict[str, Any]:
        """Get The Hamsters' WebSocket handler statistics"""
        try:
            db_health = await self.db.get_database_health()
            performance = await self.db.get_hamster_performance_metrics(days=7)
            
            return {
                'agent_name': AGENT_NAME,
                'handler_version': '3.0.0',
                'total_processing_count': self.processing_count,
                'successful_interventions': self.successful_interventions,
                'error_count': self.error_count,
                'wheel_spin_count': self.wheel_spin_count,
                'success_rate': self.successful_interventions / max(self.processing_count, 1),
                'individual_communication_stats': {
                    'steve_squeaks': self.steve_squeaks,
                    'bob_squeaks': self.bob_squeaks,
                    'carl_squeaks': self.carl_squeaks
                },
                'performance_metrics': performance,
                'database_integration': db_health,
                'central_memory_bank': 'ACTIVE',
                'pattern_learning': 'ENABLED',
                'status': 'OPERATIONAL',
                'infrastructure_monitoring': 'ACTIVE',
                'last_updated': datetime_to_iso(utc_now())
            }
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to get handler stats: {str(e)}")
            return {
                'agent_name': AGENT_NAME,
                'status': 'ERROR',
                'error': str(e),
                'last_updated': datetime_to_iso(utc_now())
            }
    
    # ... (rest of the methods remain the same)

# Global handler instance
_hamsters_handler: Optional[HamstersWebSocketHandler] = None
_handler_lock = asyncio.Lock()

async def get_hamsters_websocket_handler(db_getter=None):
    """Get global WebSocket handler instance with thread-safe initialization"""
    global _hamsters_handler
    
    if _hamsters_handler is None:
        async with _handler_lock:
            # Double-check pattern for thread safety
            if _hamsters_handler is None:
                _hamsters_handler = HamstersWebSocketHandler(db_getter)
                await _hamsters_handler.initialize()
    
    return _hamsters_handler