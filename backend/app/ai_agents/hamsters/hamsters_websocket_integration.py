"""
The Hamsters WebSocket Handler V3
Steve, Bob, and Carl's Infrastructure Communication System
Now with individual hamster squeaks and telepathic consensus!
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import random

from .decision_engine import (
    hamsters_brain,
    analyze_infrastructure,
    get_hamster_stats,
    BeerLevel
)

logger = logging.getLogger("Hamsters.WebSocket")

class HamstersWebSocketHandler:
    """
    Dedicated WebSocket handler for The Hamsters
    
    Translates Steve, Bob, and Carl's squeaks into WebSocket messages
    Includes both audible squeaks and human translations
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Hamsters.WebSocket")
        self.processing_count = 0
        self.error_count = 0
        self.wheel_spin_count = 0
        self.successful_interventions = 0
        
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
        
        self.logger.info("🐹🍺 The Hamsters WebSocket Handler V3 initialized - Steve, Bob, and Carl are ready!")
    
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
            # Get infrastructure decision
            decision = await analyze_infrastructure(metrics_data, user_id)
            
            if decision is None:
                # WHEEL SPINNING - no intervention needed
                self.wheel_spin_count += 1
                
                # Generate appropriate squeaks
                squeaks = self._generate_idle_squeaks()
                
                return {
                    'agent_name': 'hamsters',
                    'decision_type': 'all_clear',
                    'message': squeaks['combined'],
                    'human_translation': 'Infrastructure running smoothly - beer break time!',
                    'individual_squeaks': squeaks['individual'],
                    'confidence': 0.0,
                    'wheel_state': 'spinning',
                    'intervention_needed': False,
                    'current_activity': 'monitoring',
                    'hamster_status': await self._get_hamster_status(),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            self.successful_interventions += 1
            return await self._format_infrastructure_decision(decision)
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"🐹❌ The Hamsters are confused: {str(e)}")
            
            # Generate error squeaks
            error_squeaks = self._generate_error_squeaks()
            
            return {
                'agent_name': 'hamsters',
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
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _format_infrastructure_decision(self, decision) -> Dict[str, Any]:
        """Format The Hamsters' infrastructure decision for WebSocket"""
        
        # Get current hamster stats
        stats = get_hamster_stats()
        
        # Track individual communications
        self.steve_squeaks += 1
        self.bob_squeaks += 1
        self.carl_squeaks += 1
        
        return {
            'agent_name': 'hamsters',
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
            
            # WebSocket specific
            'timestamp': decision.timestamp.isoformat(),
            'requires_immediate_action': decision.priority.value in ['rapid_response', 'full_redneck'],
            'broadcast_priority': self._determine_broadcast_priority(decision.priority.value)
        }
    
    def _generate_idle_squeaks(self) -> Dict[str, Any]:
        """Generate squeaks when hamsters are idle"""
        steve_squeak = random.choice(self.squeak_patterns['normal']) + " *sips beer carefully*"
        bob_squeak = random.choice(self.squeak_patterns['happy']) + " BEER!"
        carl_squeak = "*organizing duct tape* " + random.choice(self.squeak_patterns['normal'])
        
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
            'rapid_response': 'high',
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
            'agent_name': 'hamsters',
            'broadcast_type': 'emergency',
            'crisis_type': crisis_type,
            'severity': severity,
            'message': combined_squeaks,
            'human_translation': f'Hamsters responding to {crisis_type} emergency!',
            'individual_responses': emergency_squeaks,
            'status': 'MOBILIZING',
            'estimated_response_time': 'Two beers',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get The Hamsters' WebSocket handler statistics"""
        return {
            'agent_name': 'hamsters',
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
            'status': 'OPERATIONAL',
            'infrastructure_monitoring': 'ACTIVE'
        }

# Global handler instance
_hamsters_handler = None

async def get_hamsters_websocket_handler():
    global _hamsters_handler
    if _hamsters_handler is None:
        _hamsters_handler = HamstersWebSocketHandler()
    return _hamsters_handler

# Broadcast helper for other parts of the system
async def broadcast_hamster_event(event_data: Dict[str, Any]):
    """Broadcast hamster events to WebSocket clients"""
    handler = await get_hamsters_websocket_handler()
    
    # Add hamster-specific formatting
    event_data['agent_name'] = 'hamsters'
    event_data['timestamp'] = datetime.now(timezone.utc).isoformat()
    
    # Add squeaks if not present
    if 'message' not in event_data:
        event_data['message'] = '*squeak squeak*'
    
    # This would integrate with your WebSocket broadcast system
    logger.info(f"🐹📢 Broadcasting: {event_data.get('type', 'unknown')}")
    
    return event_data
