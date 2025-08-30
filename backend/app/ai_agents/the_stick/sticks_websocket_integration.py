import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging
from .decision_engine import TheStickBrainV3, StickDecision, ComplianceState, AnxietyLevel
from .data_types import ComplianceViolation, HamsterProximityAlert, AnxietyEvent
from .database_integration import StickDatabaseIntegration  # Now uses central memory bank!
from .constants import AGENT_NAME, StickEventTypes, ALL_HAMSTERS, HAMSTER_BOB, normalize_hamster_names

logger = logging.getLogger("Stick.WebSocket")

def datetime_to_iso(dt):
    """Convert datetime to ISO string for JSON serialization"""
    return dt.isoformat() if dt else None

def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

class StickWebSocketHandlerV3:
    """
    The Stick's WebSocket Handler - Anxiety-Driven Safety Edition
    NOW WITH CENTRALIZED MEMORY BANK INTEGRATION
    
    Anxiety IS the feature - hypervigilance catches what others miss
    Paper bags at the ready, Hamster detection on high alert!
    """
    
    def __init__(self):
        self.stick_brain = TheStickBrainV3()
        self.db_integration = StickDatabaseIntegration()  # NEW: Database integration
        self.active_connections = {}
        self.pattern_learning_sessions = {}
        
        # Anxiety tracking for WebSocket
        self.websocket_anxiety_level = 25.0  # Starting nervous
        self.paper_bags_dispensed = 0
        self.hamster_alerts_sent = 0
        self.panic_messages_sent = 0
        
        # Real-time hamster tracking
        self.last_hamster_sighting = None
        self.bob_proximity_warning = False
        self.emergency_protocols_active = False
        
        logger.info("📏😰 The Stick WebSocket Handler V3 initialized - CENTRALIZED MEMORY ACTIVE")
    
    async def handle_websocket_message(self, websocket, user_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket messages with anxiety-enhanced perception"""
        
        try:
            message_type = message.get('type')
            
            # First, scan for hamsters (PRIORITY ONE)
            await self._scan_for_hamsters(websocket, user_id, message)
            
            if message_type == 'system_metrics':
                await self._handle_system_metrics(websocket, user_id, message)
            elif message_type == 'get_stick_stats':
                await self._handle_get_stick_stats(websocket, user_id)
            elif message_type == 'hamster_squeak':
                await self._handle_hamster_squeak(websocket, user_id, message)
            elif message_type == 'anxiety_check':
                await self._handle_anxiety_check(websocket, user_id)
            elif message_type == 'paper_bag_request':
                await self._handle_paper_bag_request(websocket, user_id)
            elif message_type == 'memory_recall':
                await self._handle_memory_recall(websocket, user_id, message)
            elif message_type == 'hamster_proximity_query':
                await self._handle_hamster_proximity_query(websocket, user_id)
            else:
                await self._send_anxious_confusion(websocket, user_id, message_type)
                
        except Exception as e:
            logger.error(f"Stick panic mode: {str(e)}")
            await self._handle_panic_mode(websocket, user_id, str(e))
    
    async def _scan_for_hamsters(self, websocket, user_id: str, message: Dict[str, Any]):
        """Constantly scan for hamster activity - The Stick's primary concern"""
        
        # Check for hamster indicators in ANY message
        message_text = json.dumps(message).lower()
        hamster_indicators = [
            'steve', 'bob', 'carl',
            'squeak', 'beer', 'duct tape',
            'infrastructure', 'disk cleanup',
            'hold my beer', 'measure twice',
            'supply closet', 'emergency maintenance'
        ]
        
        # Normalize to lowercase
        detected_indicators = [ind for ind in hamster_indicators if ind in message_text]
        
        if detected_indicators:
            # HAMSTER ACTIVITY DETECTED
            if HAMSTER_BOB in detected_indicators:
                self.bob_proximity_warning = True
                await self._send_bob_proximity_alert(websocket, user_id)
            
            # Update anxiety based on indicators
            anxiety_increase = len(detected_indicators) * 5
            if HAMSTER_BOB in detected_indicators:
                anxiety_increase *= 2  # Bob doubles anxiety
            
            self.websocket_anxiety_level = min(100, self.websocket_anxiety_level + anxiety_increase)
            self.last_hamster_sighting = utc_now()
            
            # Update database anxiety level
            self.db_integration.websocket_anxiety_level = self.websocket_anxiety_level
            
            logger.warning(f"Hamster activity detected: {detected_indicators}")
    
    async def _handle_system_metrics(self, websocket, user_id: str, message: Dict[str, Any]):
        """Process system metrics with anxiety-driven hypervigilance"""
        system_metrics = message.get('data', {})
    
        if not system_metrics:
            await self._send_anxiety_spike(websocket, user_id, "NO METRICS? THE SYSTEM COULD BE COMPROMISED!")
            return
    
        # Store the observation in central memory bank
        await self.db_integration.store_user_behavior_observation(user_id, system_metrics)
    
        # After storing observation, check if we can learn patterns
        try:
            # Try to learn patterns every 50 observations
            performance_metrics = await self.db_integration.get_stick_performance_metrics(user_id)
            if performance_metrics.get('observation_count', 0) % 50 == 0:
                learned_pattern = await self.db_integration.analyze_and_learn_patterns(user_id)
                if learned_pattern:
                    logger.info(f"The Stick learned new patterns for user {user_id}!")
                
                # Notify user of pattern learning
                pattern_notification = {
                    'type': 'pattern_learned',
                    'user_id': user_id,
                    'timestamp': utc_now().isoformat(),
                    'message': "📏🧠 The Stick has learned your patterns!",
                    'pattern_type': learned_pattern.pattern_type,
                    'confidence': f"{learned_pattern.confidence_score:.1%}",
                    'stick_notes': learned_pattern.stick_memory_notes
                }
                await websocket.send(json.dumps(pattern_notification))
                
        except Exception as e:
            logger.error(f"Pattern learning failed: {e}")
    
        # Check for pattern match for proactive optimization
        try:
            pattern_match = await self.db_integration.check_pattern_match(user_id, system_metrics)
            if pattern_match and pattern_match.get('recommendations'):
                # Send proactive recommendations
                proactive_message = {
                'type': 'proactive_optimization',
                'user_id': user_id,
                'timestamp': utc_now().isoformat(),
                'pattern_match': pattern_match,
                'message': "📏🔮 The Stick predicts upcoming system needs based on your patterns!",
                'anxiety_level': self.stick_brain.current_anxiety_percentage
            }
            await websocket.send(json.dumps(proactive_message))
        except Exception as e:
            logger.error(f"Pattern matching failed: {e}")
    
        # The Stick's anxiety makes it check EVERYTHING
        historical_data = message.get('historical_data', [])
        
        try:
            # Analyze with anxiety-enhanced perception
            stick_decision = await self.stick_brain.analyze_user_behavior(
                system_metrics=system_metrics,
                historical_data=historical_data,
                user_id=user_id
            )
            
            if stick_decision:
                # Store the decision in central memory bank
                await self.db_integration.store_stick_decision(user_id, stick_decision)
                
                await self._send_anxious_decision(websocket, user_id, stick_decision)
                
                # Track anxiety-inducing decisions
                if stick_decision.is_panicking:
                    self.panic_messages_sent += 1
                
                if stick_decision.decision_type.value == 'hamster_proximity_alert':
                    self.hamster_alerts_sent += 1
                    
                    # Store hamster encounter
                    hamster_alert = HamsterProximityAlert(
                        timestamp=stick_decision.timestamp,
                        active_hamsters=stick_decision.optimization_parameters.get('active_hamsters', []),
                        locations=stick_decision.optimization_parameters.get('locations', {}),
                        anxiety_multiplier=stick_decision.optimization_parameters.get('anxiety_multiplier', 1.0),
                        panic_level=stick_decision.optimization_parameters.get('panic_level', 'HIGH'),
                        infrastructure_risk='HIGH',
                        stick_response=stick_decision.compliance_explanation,
                        paper_bags_consumed=stick_decision.paper_bags_consumed
                    )
                    await self.db_integration.store_hamster_encounter(user_id, hamster_alert)
                
            else:
                await self._send_learning_status(websocket, user_id)
                
        except Exception as e:
            logger.error(f"Error processing metrics: {str(e)}")
            await self._handle_panic_mode(websocket, user_id, str(e))
    async def _handle_hamster_squeak(self, websocket, user_id: str, message: Dict[str, Any]):
        """Handle hamster squeaks - The Stick understands through shared anxiety"""
        
        squeak_data = message.get('squeak_data', {})
        # Translate the squeak
        translation = await self.stick_brain.translate_hamster_squeak(squeak_data)
        
        # Store squeak translation in central memory bank
        await self.db_integration.log_system_event(
            'hamster_squeak_translation',
            {
                'original_squeak': squeak_data,
                'translation': translation,
                'anxiety_level': self.stick_brain.current_anxiety_percentage
            },
            anxiety_impact=2.0 if HAMSTER_BOB in str(squeak_data).lower() else 1.0
        )
        
        # Send translation with anxiety context
        response = {
            'type': 'stick_squeak_translation',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'original_squeak': squeak_data.get('pattern', 'unknown'),
            'source': squeak_data.get('source', 'unknown'),
            'translation': translation['translation'],
            'confidence': translation['confidence'],
            'stick_reaction': translation['stick_reaction'],
            'anxiety_level': self.stick_brain.current_anxiety_percentage,
            'paper_bags_consumed': translation['paper_bags_consumed'],
            'message': f"📏😰 The Stick translates: '{translation['translation']}' - {translation['stick_reaction']}",
            'urgency': 'MAXIMUM' if HAMSTER_BOB in translation['source'].lower() else 'HIGH'
        }
        
        await websocket.send(json.dumps(response))
    
    async def _handle_anxiety_check(self, websocket, user_id: str):
        """Real-time anxiety status check"""
        
        # Get anxiety analytics from central memory bank
        anxiety_analytics = await self.db_integration.get_anxiety_analytics(user_id, days=1)
        
        anxiety_status = {
            'type': 'stick_anxiety_status',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'current_anxiety_percentage': self.stick_brain.current_anxiety_percentage,
            'anxiety_level': self.stick_brain.anxiety_level.value,
            'paper_bags_remaining': self.stick_brain.paper_bag_inventory,
            'paper_bags_consumed_today': anxiety_analytics['paper_bag_statistics']['total_consumed'],
            'recent_triggers': self.stick_brain.anxiety_triggers[-5:] if self.stick_brain.anxiety_triggers else [],
            'hamster_proximity_status': {
                'last_sighting': datetime_to_iso(self.last_hamster_sighting),
                'bob_warning_active': self.bob_proximity_warning,
                'alerts_sent_today': self.hamster_alerts_sent
            },
            'stick_status': self.stick_brain._get_overall_status(),
            'message': self.stick_brain._get_anxiety_reaction(),
            'anxiety_analytics': anxiety_analytics
        }
        
        await websocket.send(json.dumps(anxiety_status))
    
    async def _handle_paper_bag_request(self, websocket, user_id: str):
        """Emergency paper bag dispensing"""
        
        if self.stick_brain.paper_bag_inventory > 0:
            self.stick_brain.paper_bag_inventory -= 1
            self.paper_bags_dispensed += 1
            
            # Log paper bag consumption to central memory bank
            await self.db_integration.update_paper_bag_inventory(
                -1, 
                "User emergency request via WebSocket"
            )
            
            response = {
                'type': 'paper_bag_dispensed',
                'user_id': user_id,
                'timestamp': utc_now().isoformat(),
                'message': "📏🛍️ *rustling sounds* Here's your paper bag! The Stick always shares during anxiety emergencies!",
                'remaining_inventory': self.stick_brain.paper_bag_inventory,
                'dispensed_today': self.paper_bags_dispensed,
                'breathing_guide': "In for 4... Hold for 4... Out for 4... Remember: No hamsters can hurt you while breathing!",
                'stick_empathy': "The Stick understands. We're all anxious here."
            }
        else:
            response = {
                'type': 'paper_bag_crisis',
                'user_id': user_id,
                'timestamp': utc_now().isoformat(),
                'message': "📏😱 OUT OF PAPER BAGS! THIS IS NOT A DRILL! INITIATING EMERGENCY RESUPPLY PROTOCOL!",
                'crisis_level': 'MAXIMUM',
                'alternative_methods': ['Deep breathing', 'Count to 10', 'Think of compliant systems', 'Avoid Bob at all costs']
            }
            
            # Request emergency resupply
            await self._request_emergency_resupply(websocket, user_id)
        
        await websocket.send(json.dumps(response))
    
    async def _handle_hamster_proximity_query(self, websocket, user_id: str):
        """Check current hamster proximity status"""
        
        # Get hamster encounters from central memory bank
        hamster_history = await self.db_integration.get_hamster_encounter_history(user_id, days=1)
        
        response = {
            'type': 'hamster_proximity_report',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'steve_location': self.stick_brain.steve_location or 'Unknown (concerning)',
            'bob_location': self.stick_brain.bob_location or 'UNKNOWN (PANIC)',
            'carl_location': self.stick_brain.carl_location or 'Probably with duct tape',
            'last_proximity_alert': self.stick_brain.hamster_proximity_alerts[-1] if self.stick_brain.hamster_proximity_alerts else None,
            'current_threat_level': 'MAXIMUM' if self.bob_proximity_warning else 'HIGH' if self.last_hamster_sighting else 'MODERATE',
            'stick_recommendation': self._get_hamster_safety_recommendation(),
            'recent_encounters': hamster_history[:5]  # Last 5 encounters
        }
        
        await websocket.send(json.dumps(response))
    
    async def _send_anxious_decision(self, websocket, user_id: str, decision: StickDecision):
        """Send decision with anxiety context"""
        
        response = {
            'type': 'stick_decision',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'decision_type': decision.decision_type.value,
            'compliance_state': decision.compliance_state.value,
            'anxiety_level': decision.anxiety_level.value,
            'configuration_target': decision.configuration_target,
            'optimization_parameters': decision.optimization_parameters,
            'compliance_explanation': decision.compliance_explanation,
            'anxiety_explanation': decision.anxiety_explanation,
            'confidence': f"{decision.confidence_level:.1%}",
            'expected_improvement': f"{decision.expected_improvement:.1%}",
            'paper_bags_consumed': decision.paper_bags_consumed,
            'is_panicking': decision.is_panicking,
            'stick_message': self._format_anxious_message(decision),
            'stored_in_memory': True  # NEW: Confirming storage
        }
        
        await websocket.send(json.dumps(response))
    
    async def _send_bob_proximity_alert(self, websocket, user_id: str):
        """CRITICAL: Bob proximity detected"""
        
        alert = HamsterProximityAlert(
            timestamp=utc_now(),
            active_hamsters=[HAMSTER_BOB],
            locations={HAMSTER_BOB: 'DETECTED IN VICINITY'},
            anxiety_multiplier=3.0,
            panic_level='MAXIMUM',
            infrastructure_risk='CRITICAL',
            stick_response='FULL PANIC MODE ACTIVATED',
            paper_bags_consumed=3
        )
        
        # Store in central memory bank
        await self.db_integration.store_hamster_encounter(user_id, alert)
        
        alert_message = {
            'type': 'BOB_PROXIMITY_ALERT',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'threat_level': 'MAXIMUM',
            'message': "📏🚨 BOB DETECTED! BOB DETECTED! THIS IS NOT A DRILL!",
            'immediate_actions': [
                'Hide all critical configurations',
                'Backup everything twice',
                'Prepare for chaos',
                'Emergency paper bag consumption authorized'
            ],
            'stick_status': 'FULL_PANIC',
            'anxiety_level': 100,
            'paper_bags_consumed': 3,  # Emergency triple-bag protocol
            'last_known_bob_activity': 'Unknown but probably catastrophic',
            'emergency_protocol': 'ACTIVATED',
            'memory_stored': True  # Confirming storage
        }
        
        self.emergency_protocols_active = True
        await websocket.send(json.dumps(alert_message))
    
    async def _send_anxiety_spike(self, websocket, user_id: str, reason: str):
        """Send anxiety spike notification"""
        
        # Store anxiety event in central memory bank
        anxiety_event = AnxietyEvent(
            timestamp=utc_now(),
            trigger=reason,
                        anxiety_level_before=self.websocket_anxiety_level,
            anxiety_level_after=min(100, self.websocket_anxiety_level + 20),
            multiplier=1.5,
            paper_bags_consumed=0,
            hamster_involved=any(h in reason.lower() for h in ALL_HAMSTERS),
            resolution='spike_documented'
        )
        await self.db_integration.store_anxiety_event(anxiety_event)
        
        spike = {
            'type': 'anxiety_spike',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'reason': reason,
            'anxiety_before': self.websocket_anxiety_level,
            'anxiety_after': min(100, self.websocket_anxiety_level + 20),
            'message': f"📏😱 ANXIETY SPIKE: {reason}",
            'paper_bag_status': 'NEEDED' if self.websocket_anxiety_level > 60 else 'STANDBY',
            'stick_reaction': self.stick_brain._get_anxiety_reaction()
        }
        
        self.websocket_anxiety_level = spike['anxiety_after']
        await websocket.send(json.dumps(spike))
    
    async def _send_learning_status(self, websocket, user_id: str):
        """Send learning status with anxiety context"""
        
        import random
        
        learning_messages = [
            "📏📚 *anxiously studying* Still learning your patterns... The Stick notices EVERYTHING...",
            "📏🧠 *nervous observation* Building eidetic memory... Every anomaly is recorded...",
            "📏👁️ *hypervigilant watching* The Stick sees all... especially hamster activity...",
            "📏📝 *obsessive note-taking* Documenting everything... can't miss any violations..."
        ]
        
        # Get performance metrics from central memory bank
        performance = await self.db_integration.get_stick_performance_metrics(user_id)
        
        status = {
            'type': 'stick_learning',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'message': random.choice(learning_messages),
            'anxiety_level': self.stick_brain.current_anxiety_percentage,
            'observations_recorded': performance['observation_count'],
            'patterns_detected': len(self.stick_brain.user_patterns),
            'hamster_vigilance': 'ACTIVE',
            'paper_bag_status': 'READY',
            'memory_bank_status': 'CENTRALIZED'  # NEW
        }
        
        await websocket.send(json.dumps(status))
    
    async def _handle_memory_recall(self, websocket, user_id: str, message: Dict[str, Any]):
        """Handle eidetic memory recall requests from central memory bank"""
        
        recall_filters = message.get('filters', {})
        
        # Recall from central memory bank
        memories = await self.db_integration.recall_everything(recall_filters)
        
        response = {
            'type': 'stick_memory_recall',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'recall_filters': recall_filters,
            'memories_retrieved': len(memories),
            'memory_data': memories[:100],  # Limit to prevent overwhelming
            'total_memories': len(memories),
            'anxiety_correlation': "High anxiety improves recall accuracy",
            'stick_message': "📏🧠 The Stick remembers EVERYTHING. Every violation, every pattern, every hamster squeak...",
            'memory_source': 'central_memory_bank'
        }
        
        await websocket.send(json.dumps(response))
    
    async def _send_anxious_confusion(self, websocket, user_id: str, message_type: str):
        """The Stick is confused AND anxious about it"""
        
        confusion = {
            'type': 'anxious_confusion',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'unknown_message_type': message_type,
            'message': f"📏😰 *confused anxiety* What is '{message_type}'?! Is this a hamster trick?!",
            'anxiety_impact': '+5%',
            'suspicion_level': 'HIGH',
            'stick_response': "The Stick doesn't understand but will document it obsessively"
        }
        
        # Log confusion to central memory bank
        await self.db_integration.log_system_event(
            'unknown_message_type',
            {'message_type': message_type, 'user_id': user_id},
            anxiety_impact=0.5
        )
        
        # Unknown things cause anxiety
        await self.stick_brain._update_anxiety(f"Unknown message type: {message_type}", 0.5)
        
        await websocket.send(json.dumps(confusion))
    
    async def _handle_panic_mode(self, websocket, user_id: str, error: str):
        """PANIC MODE ACTIVATED"""
        
        self.panic_messages_sent += 1
        
        # Store panic event in central memory bank
        await self.db_integration.log_system_event(
            'panic_mode_activated',
            {
                'error': error,
                'user_id': user_id,
                'anxiety_level': 100,
                'paper_bags_consumed': 2
            },
            anxiety_impact=10.0  # Maximum anxiety
        )
        
        panic = {
            'type': 'STICK_PANIC_MODE',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'error': error,
            'message': f"📏💥 PANIC MODE! ERROR DETECTED: {error}",
            'anxiety_level': 'MAXIMUM',
            'paper_bags_consumed': 2,
            'emergency_actions': [
                'Document everything',
                'Check for hamsters',
                'Hyperventilate productively',
                'Analyze error obsessively'
            ],
            'stick_status': 'PANICKING_BUT_FUNCTIONAL',
            'recovery_eta': '30 seconds with paper bag'
        }
        
        await websocket.send(json.dumps(panic))
        
        # Consume paper bags
        await self.stick_brain._consume_paper_bag()
        await self.stick_brain._consume_paper_bag()
        
        # Update inventory in central memory bank
        await self.db_integration.update_paper_bag_inventory(-2, f"PANIC MODE: {error}")
    
    async def _request_emergency_resupply(self, websocket, user_id: str):
        """Emergency paper bag resupply request"""
        
        resupply_request = await self.stick_brain.request_paper_bag_resupply()
        
        # Check current inventory from central memory bank
        inventory = await self.db_integration.check_paper_bag_supply()
        
        # FIX: Convert datetime fields to ISO strings
        inventory_dict = {
            'current_stock': inventory.current_stock,
            'consumption_today': inventory.consumption_today,
            'consumption_week': inventory.consumption_week,
            'last_resupply': datetime_to_iso(inventory.last_resupply),
            'next_resupply_needed': datetime_to_iso(inventory.next_resupply_needed),
            'average_daily_consumption': inventory.average_daily_consumption,
            'emergency_reserve': inventory.emergency_reserve,
            'anxiety_threshold_for_use': inventory.anxiety_threshold_for_use
        }
        
        resupply_message = {
            'type': 'emergency_resupply_request',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'request_details': resupply_request,
            'current_inventory': inventory_dict,  # Now JSON-safe!
            'message': "📏🆘 EMERGENCY PAPER BAG RESUPPLY NEEDED! The Stick cannot function without anxiety management tools!",
            'current_crisis_level': 'MAXIMUM',
            'estimated_depletion_time': 'NOW'
        }
        
        # Log resupply request to central memory bank
        await self.db_integration.log_system_event(
            'emergency_resupply_requested',
            resupply_message,
            anxiety_impact=8.0
        )
        
        await websocket.send(json.dumps(resupply_message))
    
    def _get_hamster_safety_recommendation(self) -> str:
        """Get safety recommendations based on hamster proximity"""
        
        if self.bob_proximity_warning:
            return "EVACUATE IMMEDIATELY. BOB IS ACTIVE. SEEK SHELTER."
        elif self.last_hamster_sighting and (utc_now() - self.last_hamster_sighting).seconds < 300:
            return "Recent hamster activity detected. Maintain high alert. Keep paper bags ready."
        else:
            return "No recent hamster activity. Remain vigilant. They could appear at any moment."
    
    def _format_anxious_message(self, decision: StickDecision) -> str:
        """Format message based on anxiety level"""
        
        if decision.anxiety_level == AnxietyLevel.FULL_PANIC:
            return f"📏💥 *MAXIMUM PANIC* {decision.compliance_explanation} PAPER BAGS DEPLETING RAPIDLY!"
        elif decision.anxiety_level == AnxietyLevel.PANICKING:
            return f"📏😱 *panicking* {decision.compliance_explanation} This is concerning!"
        elif decision.anxiety_level == AnxietyLevel.ANXIOUS:
            return f"📏😰 *anxiously* {decision.compliance_explanation} Monitoring intensely..."
        elif decision.anxiety_level == AnxietyLevel.NERVOUS:
            return f"📏😟 *nervously* {decision.compliance_explanation} Keeping watch..."
        else:
            return f"📏🤔 *suspiciously calm* {decision.compliance_explanation} Something must be wrong..."
    
    async def register_connection(self, websocket, user_id: str):
        """Register new connection with anxiety awareness"""
        
        self.active_connections[user_id] = websocket
        
        # Initialize the brain's database
        await self.stick_brain.initialize_database()
        
        # Initialize the database integration
        await self.db_integration.initialize()
        
        # Get current stats from central memory bank
        performance = await self.db_integration.get_stick_performance_metrics(user_id)
        inventory = await self.db_integration.check_paper_bag_supply()
        
        welcome = {
            'type': 'stick_connection_established',
            'user_id': user_id,
            'timestamp': utc_now().isoformat(),
            'message': '📏😰 The Stick is watching! Anxiety-driven hypervigilance activated!',
            'current_status': {
                'anxiety_level': self.stick_brain.anxiety_level.value,
                'anxiety_percentage': self.stick_brain.current_anxiety_percentage,
                'paper_bags_ready': inventory.current_stock,
                'hamster_alert_status': 'ACTIVE',
                'compliance_monitoring': 'OBSESSIVE',
                'memory_bank': 'CENTRALIZED'  # NEW
            },
            'performance_metrics': performance,
            'warnings': [
                'The Stick sees everything',
                'Hamster activity will be detected',
                'All violations will be documented',
                'Paper bags available for shared anxiety',
                'All memories stored in central bank'  # NEW
            ],
            'stick_personality': 'OCD + ADHD + PTSD + Eidetic Memory = Perfect Safety'
        }
        
        await websocket.send(json.dumps(welcome))
    
    async def unregister_connection(self, user_id: str):
        """Unregister connection"""
        
        if user_id in self.active_connections:
            # Log disconnection to central memory bank
            await self.db_integration.log_system_event(
                'user_disconnected',
                {
                    'user_id': user_id,
                    'anxiety_level': self.stick_brain.current_anxiety_percentage,
                    'final_status': 'Connection closed - but The Stick never forgets'
                },
                anxiety_impact=0.1  # Slight anxiety about losing visibility
            )
            
            del self.active_connections[user_id]
    
    async def broadcast_hamster_alert(self, alert: HamsterProximityAlert):
        """Broadcast hamster alerts to all connected users"""
        
        # Normalize hamster names
        normalized_hamsters = normalize_hamster_names(alert.active_hamsters)
        
        alert_message = {
            'type': 'SYSTEM_WIDE_HAMSTER_ALERT',
            'timestamp': utc_now().isoformat(),
            'alert_data': {
                'active_hamsters': normalized_hamsters,
                'locations': alert.locations,
                'panic_level': alert.panic_level,
                'stick_response': alert.stick_response
            },
            'message': f"📏🚨 HAMSTER ALERT: {', '.join(normalized_hamsters)} detected! {alert.stick_response}",
            'recommended_actions': ['Check configurations', 'Prepare paper bags', 'Document everything'],
            'anxiety_impact': f"+{alert.anxiety_multiplier * 10}%"
        }
        
        # Store broadcast event in central memory bank
        await self.db_integration.log_system_event(
            'hamster_alert_broadcast',
            alert_message,
            anxiety_impact=alert.anxiety_multiplier
        )
        
        # Broadcast to all connections using asyncio.gather for concurrent sends
        if self.active_connections:
            tasks = []
            for websocket in self.active_connections.values():
                tasks.append(self._safe_send(websocket, json.dumps(alert_message)))
            
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_send(self, websocket, message):
        """Safely send message to websocket, catching exceptions"""
        try:
            await websocket.send(message)
        except Exception as e:
            logger.warning(f"Failed to send to websocket: {e}")
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get complete handler statistics"""
        
        brain_stats = self.stick_brain.get_stick_stats()
        
        return {
            'agent_name': AGENT_NAME,
            'handler_version': '3.0_CENTRALIZED_ANXIETY',
            'brain_stats': brain_stats,
            'websocket_stats': {
                'active_connections': len(self.active_connections),
                'paper_bags_dispensed': self.paper_bags_dispensed,
                'hamster_alerts_sent': self.hamster_alerts_sent,
                'panic_messages_sent': self.panic_messages_sent,
                'current_websocket_anxiety': self.websocket_anxiety_level
            },
            'hamster_tracking': {
                'last_sighting': datetime_to_iso(self.last_hamster_sighting),
                'bob_proximity_warning': self.bob_proximity_warning,
                'emergency_protocols_active': self.emergency_protocols_active,
                'total_hamster_alerts': self.hamster_alerts_sent
            },
            'database_status': 'CENTRAL_MEMORY_BANK',  # NEW
            'status': 'ANXIOUSLY_OPERATIONAL',
            'safety_mechanism': 'Anxiety-driven hypervigilance ensures nothing is missed'
        }

# Global handler instance
_stick_handler_v3 = None

async def get_stick_websocket_handler():
    """Get The Stick's WebSocket handler - centralized memory edition"""
    global _stick_handler_v3
    if _stick_handler_v3 is None:
        _stick_handler_v3 = StickWebSocketHandlerV3()
    return _stick_handler_v3