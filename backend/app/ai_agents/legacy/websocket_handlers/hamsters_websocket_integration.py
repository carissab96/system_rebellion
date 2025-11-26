# app/ai_agents/hamsters/websocket_handler.py
"""
The Hamsters WebSocket Handler V3 - Central Memory Bank Edition
Steve, Bob, and Carl's Infrastructure Communication System
Now with pattern learning and cross-agent coordination!
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import random

from .decision_engine_sbcV3 import (
    hamsters_brain,
    analyze_infrastructure,
    get_hamster_stats,
    BeerLevel
)
from app.ai_agents.hamsters.hamsters_database_integration import HamstersDatabaseIntegration
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
                    "decision_id": uuid4().hex,         # unique
                    "decision_timestamp": decision.timestamp.isoformat(),
                    "intervention_type": decision.intervention_type,
                    "priority": decision.priority.value,
                    "steve_assessment": decision.steve_assessment,
                    "bob_suggestion": decision.bob_suggestion,
                    "carl_calculation": decision.carl_calculation,
                    "telepathic_consensus": decision.telepathic_consensus,
                    "confidence": decision.confidence,
                    "tools_required": decision.tools_required,
                    "beer_consumption_estimate": decision.beer_consumption_estimate,
                    "duct_tape_grade": decision.duct_tape_grade.value,
                    "actual_squeaks": decision.actual_squeaks,
                    'human_translation': decision.human_translation,
                    "estimated_duration": int(decision.estimated_duration) if isinstance(decision.estimated_duration, (int, float)) else str(decision.estimated_duration),
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
    
    def _generate_idle_squeaks(self) -> Dict[str, Any]:
        """Generate squeaks when hamsters are idle"""
        steve_squeak = random.choice(self.squeak_patterns['normal']) + " *sips beer carefully*"
        bob_squeak = random.choice(self.squeak_patterns['happy']) + " BEER!"
        carl_squeak = "*organizing duct tape* " + random.choice(self.squeak_patterns['normal'])
        
        # Increment individual squeak counters
        self.steve_squeaks += 1
        self.bob_squeaks += 1
        self.carl_squeaks += 1
        
        return {
            'individual': {
                'steve': steve_squeak,
                'bob': bob_squeak,
                'carl': carl_squeak
            },
            'combined': f"{steve_squeak} {bob_squeak} {carl_squeak}"
        }
    
    def _generate_error_squeaks(self) -> Dict[str, Any]:
        """Generate squeaks when there's an error"""
        steve_squeak = "*worried squeaking*"
        bob_squeak = "*confused chirping* WHAT HAPPENED?"
        carl_squeak = "*drops duct tape* *concerned squeak*"
        
        # Increment individual squeak counters
        self.steve_squeaks += 1
        self.bob_squeaks += 1
        self.carl_squeaks += 1
        
        return {
            'individual': {
                'steve': steve_squeak,
                'bob': bob_squeak,
                'carl': carl_squeak
            },
            'combined': f"{steve_squeak} {bob_squeak} {carl_squeak}"
        }
    
    async def _get_hamster_status(self) -> Dict[str, Any]:
        """Get current status of each hamster"""
        stats = get_hamster_stats()
        
        return {
            'steve': {
                'beer_count': stats['individual_stats']['steve']['beer_count'],
                'status': stats['individual_stats']['steve']['status'],
                'mood': self._determine_steve_mood(stats['individual_stats']['steve']['beer_count'])
            },
            'bob': {
                'beer_count': stats['individual_stats']['bob']['beer_count'],
                'status': stats['individual_stats']['bob']['status'],
                'mood': self._determine_bob_mood(stats['individual_stats']['bob']['beer_count'])
            },
            'carl': {
                'beer_count': stats['individual_stats']['carl']['beer_count'],
                'duct_tape_inventory': stats['individual_stats']['carl']['duct_tape_inventory'],
                'status': stats['individual_stats']['carl']['status'],
                'mood': 'focused on duct tape'
            }
        }
    
    def _determine_steve_mood(self, beer_count: int) -> str:
        """Determine Steve's mood based on beer consumption"""
        if beer_count < 2:
            return "needs beer for courage"
        elif beer_count <= 3:
            return "carefully optimistic"
        else:
            return "unusually adventurous"
    
    def _determine_bob_mood(self, beer_count: int) -> str:
        """Determine Bob's mood based on beer consumption"""
        if beer_count < 3:
            return "needs more beer"
        elif beer_count <= 5:
            return "ready for chaos"
        else:
            return "maximum wildness"
    
    def _determine_broadcast_priority(self, priority: str) -> str:
        """Determine WebSocket broadcast priority"""
        priority_map = {
            'beer_break': 'low',
            'routine_maintenance': 'normal',
            'supply_closet_raid': 'normal',
            'hold_my_beer': 'high',
            'full_redneck': 'critical'
        }
        return priority_map.get(priority, 'normal')
    
    async def handle_emergency_broadcast(
        self, 
        crisis_type: str, 
        severity: str
    ) -> Dict[str, Any]:
        """Handle emergency broadcasts - WAKE THE HAMSTERS!"""
        
        # Generate emergency squeaks
        emergency_squeaks = {
            'steve': "*ALARM SQUEAK* Everyone stay calm!",
            'bob': "*EXCITED SQUEAKING* This is what we trained for!",
            'carl': "*grabs all the duct tape* EMERGENCY PROTOCOLS!"
        }
        
        combined_squeaks = " ".join(emergency_squeaks.values())
        
        return {
            'agent_name': AGENT_NAME,
            'broadcast_type': 'emergency',
            'crisis_type': crisis_type,
            'severity': severity,
            'message': combined_squeaks,
            'human_translation': f'Hamsters responding to {crisis_type} emergency!',
            'individual_responses': emergency_squeaks,
            'status': 'MOBILIZING',
            'estimated_response_time': 'Two beers',
            'timestamp': datetime_to_iso(utc_now())
        }
    
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
    
    async def broadcast_to_hamsters(self, message: Dict[str, Any]):
        """
        Broadcast messages to all hamsters for collective decision making
        """
        # Telepathic communication between hamsters
        telepathic_response = {
            'steve': self._steve_telepathic_response(message),
            'bob': self._bob_telepathic_response(message),
            'carl': self._carl_telepathic_response(message)
        }
        
        # Check for consensus
        consensus = self._check_telepathic_consensus(telepathic_response)
        
        return {
            'agent_name': AGENT_NAME,
            'message_type': 'telepathic_broadcast',
            'original_message': message,
            'individual_responses': telepathic_response,
            'consensus_reached': consensus,
            'collective_decision': self._form_collective_decision(telepathic_response, consensus),
            'timestamp': datetime_to_iso(utc_now())
        }
    
    def _steve_telepathic_response(self, message: Dict[str, Any]) -> str:
        """Steve's careful telepathic response"""
        if 'emergency' in str(message).lower():
            return "We should assess the situation carefully before acting"
        elif 'disk' in str(message).lower():
            return "I've calculated we can safely free up significant space"
        else:
            return "Let me think about this..."
    
    def _bob_telepathic_response(self, message: Dict[str, Any]) -> str:
        """Bob's enthusiastic telepathic response"""
        if 'emergency' in str(message).lower():
            return "THIS IS AWESOME! Let's fix EVERYTHING!"
        elif 'disk' in str(message).lower():
            return "Delete it all! We'll sort it out later!"
        else:
            return "Whatever it is, I'm ready!"
    
    def _carl_telepathic_response(self, message: Dict[str, Any]) -> str:
        """Carl's duct tape focused telepathic response"""
        if 'emergency' in str(message).lower():
            return "I'll need the quantum tape for this one"
        elif 'disk' in str(message).lower():
            return "Three strips of premium tape should stabilize the sectors"
        else:
            return "How much duct tape will we need?"
    
    def _check_telepathic_consensus(self, responses: Dict[str, str]) -> bool:
        """Check if hamsters reached telepathic consensus"""
        # Simple consensus: at least 2 hamsters must be positive
        positive_responses = 0
        for response in responses.values():
            if any(word in response.lower() for word in ['yes', 'ready', 'let', 'should', 'need']):
                positive_responses += 1
        
        return positive_responses >= 2
    
    def _form_collective_decision(self, responses: Dict[str, str], consensus: bool) -> str:
        """Form collective decision based on telepathic responses"""
        if consensus:
            return "The Hamsters have reached consensus - proceeding with intervention!"
        else:
            return "The Hamsters need more beer to reach consensus"

# Global handler instance with thread-safe initialization
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

# Broadcast helper for other parts of the system
async def broadcast_hamster_event(event_data: Dict[str, Any]):
    """Broadcast hamster events to WebSocket clients"""
    handler = await get_hamsters_websocket_handler()
    
    # Add hamster-specific formatting
    event_data['agent_name'] = AGENT_NAME
    event_data['timestamp'] = datetime_to_iso(utc_now())
    
    # Add squeaks if not present
    if 'message' not in event_data:
        event_data['message'] = '*squeak squeak*'
    
    # Add individual hamster reactions
    if 'individual_reactions' not in event_data:
        event_data['individual_reactions'] = {
            'steve': '*thoughtful squeak*',
            'bob': '*excited chirping*',
            'carl': '*duct tape rustling*'
        }
    
    # This would integrate with your WebSocket broadcast system
    logger.info(f"🐹📢 Broadcasting: {event_data.get('message_type', event_data.get('type', unknown))}")
    
    return event_data