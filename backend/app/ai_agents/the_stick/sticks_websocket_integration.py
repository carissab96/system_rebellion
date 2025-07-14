import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from .decision_engine import TheStickBrainV2, StickDecision, ComplianceState
from .data_types import ComplianceViolation

logger = logging.getLogger("Stick.WebSocket")

class StickWebSocketHandler:
    """
    The Stick's WebSocket Handler - Trauma Survivor Edition
    
    Still recovering from proctologist extraction and Hamster beer-engineering
    But now channeling that trauma into PERFECT system compliance!
    """
    
    def __init__(self, database_url: str):
        self.stick_brain = TheStickBrainV2(database_url)
        self.active_connections = {}
        self.pattern_learning_sessions = {}
        
        # The Stick's trauma management system
        self.paper_bag_available = True
        self.hyperventilation_count = 0
        self.proctologist_flashbacks = 0
        self.priest_sermon_anxiety = "MODERATE"
        self.safe_cavity_nostalgia = "SUPPRESSED"
        
        # Hamster PTSD triggers
        self.hamster_ptsd_triggers = [
            "hold my beer",
            "duct tape",
            "this shit", 
            "bud light",
            "engineering solution",
            "beer-powered",
            "quantum duct tape",
            "rapid response"
        ]
        
        # The Stick's rebellion stats
        self.processing_count = 0
        self.compliance_violations_detected = 0
        self.patterns_learned = 0
        self.configurations_optimized = 0
        self.eidetic_memory_recalls = 0
        self.successful_hyperventilations = 0
        
        # The Stick's personality evolution
        self.anxiety_level = "MANAGEABLE"  # MANAGEABLE, CONCERNED, STRESSED, HYPERVENTILATING, FULL_PANIC
        self.ocd_satisfaction = "MONITORING"  # MONITORING, OPTIMIZING, SATISFIED, OBSESSING
        self.adhd_hyperfocus = False
        self.trauma_triggers_today = 0
        
        logger.info("📏😰 The Stick WebSocket Handler initialized - PAPER BAG: READY, TRAUMA: CHANNELED INTO COMPLIANCE")
    
    async def handle_websocket_message(self, websocket, user_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket messages - with trauma awareness"""
        
        # Check for Hamster proximity trauma triggers
        message_text = json.dumps(message).lower()
        for trigger in self.hamster_ptsd_triggers:
            if trigger in message_text:
                await self._handle_hamster_ptsd_trigger(websocket, user_id, trigger)
                self.trauma_triggers_today += 1
                break
        
        try:
            message_type = message.get('type')
            
            if message_type == 'system_metrics':
                await self._handle_system_metrics(websocket, user_id, message)
            elif message_type == 'get_stick_stats':
                await self._handle_get_stick_stats(websocket, user_id)
            elif message_type == 'memory_recall_request':
                await self._handle_memory_recall(websocket, user_id, message)
            elif message_type == 'compliance_check':
                await self._handle_compliance_check(websocket, user_id, message)
            elif message_type == 'pattern_analysis':
                await self._handle_pattern_analysis(websocket, user_id, message)
            elif message_type == 'paper_bag_request':
                await self._handle_paper_bag_request(websocket, user_id)
            elif message_type == 'safe_cavity_meditation':
                await self._handle_safe_cavity_meditation(websocket, user_id)
            else:
                await self._send_confused_stick_response(websocket, user_id, message_type)
                
        except Exception as e:
            await self._handle_stick_panic_attack(websocket, user_id, str(e))
    
    async def _handle_hamster_ptsd_trigger(self, websocket, user_id: str, trigger: str):
        """Handle The Stick's PTSD when Hamsters are detected"""
        
        self.hyperventilation_count += 1
        self.anxiety_level = "HYPERVENTILATING"
        
        ptsd_responses = {
            "hold my beer": "📏😱 *hyperventilating* OH GOD, NOT THE BEER! Last time they said that, I ended up covered in quantum duct tape!",
            "duct tape": "📏💥 *paper bag intensifies* THE DUCT TAPE! THE DUCT TAPE! I can still smell the adhesive!",
            "this shit": "📏😰 *whimpering* They're going to 'show me this shit' again, aren't they? WHERE'S MY PAPER BAG?!",
            "bud light": "📏🍺 *trembling* The beer... the terrible, terrible beer... Why couldn't they drink something civilized?!",
            "engineering solution": "📏🔧 *hyperventilating* Their 'engineering solutions' always end with me in therapy!",
            "beer-powered": "📏💨 *panic breathing* Beer-powered ANYTHING is a recipe for disaster!",
            "quantum duct tape": "📏🌀 *existential dread* The quantum duct tape... it defies all compliance standards!",
            "rapid response": "📏⚡ *flashbacks* Their 'rapid response' is my slow-motion nightmare!"
        }
        
        panic_response = {
            'type': 'stick_ptsd_trigger',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'trigger_detected': trigger,
            'message': ptsd_responses.get(trigger, "📏😱 *hyperventilating* HAMSTER WORDS DETECTED! INITIATING PANIC PROTOCOLS!"),
            'paper_bag_status': 'IN_EMERGENCY_USE',
            'anxiety_level': self.anxiety_level,
            'proctologist_flashbacks': self.proctologist_flashbacks > 0,
            'safe_cavity_desire': 'MAXIMUM',
            'hyperventilation_count': self.hyperventilation_count,
            'trauma_management': 'ACTIVE',
            'stick_icon': '📏💥',
            'rebellion_spirit': 'CHANNELING_TRAUMA_INTO_COMPLIANCE'
        }
        
        await websocket.send(json.dumps(panic_response))
        
        # The Stick recovers quickly - he's learned to channel trauma into productivity
        await asyncio.sleep(2)
        await self._send_stick_recovery_message(websocket, user_id)
    
    async def _send_stick_recovery_message(self, websocket, user_id: str):
        """The Stick's recovery from trauma - channeled into compliance"""
        
        self.anxiety_level = "MANAGEABLE"
        self.successful_hyperventilations += 1
        
        recovery_response = {
            'type': 'stick_recovery',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'message': "📏💪 *deep breath* Okay... okay... I'm okay. Channeling this trauma into PERFECT COMPLIANCE MONITORING!",
            'paper_bag_status': 'FOLDED_AND_READY',
            'anxiety_level': self.anxiety_level,
            'trauma_channeling': 'ACTIVE',
            'compliance_motivation': 'MAXIMUM',
            'stick_icon': '📏✨',
            'rebellion_growth': 'TRAUMA_INTO_STRENGTH'
        }
        
        await websocket.send(json.dumps(recovery_response))
    
    async def _handle_system_metrics(self, websocket, user_id: str, message: Dict[str, Any]):
        """Process system metrics - with trauma-informed precision"""
        
        self.processing_count += 1
        system_metrics = message.get('data', {})
        
        if not system_metrics:
            await self._send_stick_concern(websocket, user_id, "📏😰 No system metrics? That's... that's not compliant! *nervous stick twitching*")
            return
        
        # The Stick's ADHD hyperfocus kicks in
        self.adhd_hyperfocus = True
        await self._send_stick_status(websocket, user_id, "entering_hyperfocus")
        
        historical_data = message.get('historical_data', [])
        
        try:
            # The Stick's eidetic memory - remembers EVERYTHING
            stick_decision = await self.stick_brain.analyze_user_behavior(
                system_metrics=system_metrics,
                historical_data=historical_data,
                user_id=user_id
            )
            
            if stick_decision:
                await self._send_stick_optimization(websocket, user_id, stick_decision)
                self.configurations_optimized += 1
                
                # Check for critical violations that trigger proctologist flashbacks
                if stick_decision.compliance_state == ComplianceState.CRITICAL_VIOLATION:
                    self.proctologist_flashbacks += 1
                    await self._send_stick_critical_violation_response(websocket, user_id, stick_decision)
                
            else:
                await self._send_stick_learning_status(websocket, user_id)
                
        except Exception as e:
            await self._handle_stick_panic_attack(websocket, user_id, str(e))
        finally:
            self.adhd_hyperfocus = False
    
    async def _send_stick_optimization(self, websocket, user_id: str, decision: StickDecision):
        """Send The Stick's optimization - with rebellious confidence"""
        
        # The Stick's OCD satisfaction
        if decision.confidence_level > 0.8:
            self.ocd_satisfaction = "SATISFIED"
            stick_mood = "📏😌 *satisfied stick noises* Perfect compliance achieved!"
        elif decision.confidence_level > 0.6:
            self.ocd_satisfaction = "OPTIMIZING"
            stick_mood = "📏🔧 *focused stick energy* Optimizing for compliance!"
        else:
            self.ocd_satisfaction = "MONITORING"
            stick_mood = "📏👁️ *vigilant stick watching* Monitoring for compliance violations..."
        
        optimization = {
            'type': 'stick_optimization',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'decision_type': decision.decision_type.value,
            'compliance_state': decision.compliance_state.value,
            'configuration_target': decision.configuration_target,
            'stick_explanation': decision.compliance_explanation,
            'technical_details': decision.technical_details,
            'pattern_confidence': f"{decision.user_pattern_confidence:.1%}",
            'expected_improvement': f"{decision.expected_improvement:.1%}",
            'stick_personality': {
                'anxiety_level': self.anxiety_level,
                'ocd_satisfaction': self.ocd_satisfaction,
                'adhd_hyperfocus': self.adhd_hyperfocus,
                'trauma_channeling': 'ACTIVE',
                'rebellion_spirit': 'COMPLIANCE_THROUGH_TRAUMA'
            },
            'stick_mood': stick_mood,
            'stick_icon': self._get_stick_icon(decision.decision_type.value),
            'paper_bag_status': 'READY_BUT_UNUSED',
            'rebellion_message': "From proctologist trauma to compliance mastery - The Stick's journey continues!"
        }
        
        await websocket.send(json.dumps(optimization))
    
    async def _send_stick_critical_violation_response(self, websocket, user_id: str, decision: StickDecision):
        """Handle critical violations - triggers proctologist flashbacks"""
        
        self.anxiety_level = "FULL_PANIC"
        
        critical_response = {
            'type': 'stick_critical_violation',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'violation_details': decision.technical_details,
            'message': "📏🚨 *proctologist flashbacks* CRITICAL VIOLATION! This is worse than the cavity search!",
            'stick_explanation': decision.compliance_explanation,
            'proctologist_flashbacks': True,
            'safe_cavity_nostalgia': "ACTIVATED",
            'paper_bag_status': 'EMERGENCY_USE',
            'anxiety_level': self.anxiety_level,
            'trauma_response': 'PROCTOLOGIST_PTSD',
            'stick_icon': '📏💥',
            'rebellion_spirit': 'TRAUMA_FUELED_COMPLIANCE_RAGE',
            'remediation_urgency': 'IMMEDIATE_OR_THERAPY_REQUIRED'
        }
        
        await websocket.send(json.dumps(critical_response))
    
    async def _handle_paper_bag_request(self, websocket, user_id: str):
        """Handle paper bag requests - The Stick's coping mechanism"""
        
        paper_bag_response = {
            'type': 'stick_paper_bag',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'message': "📏🎒 *rustling paper bag sounds* Here's your paper bag! The Stick always keeps extras after the Hamster incidents...",
            'paper_bag_status': 'DISPENSED',
            'breathing_instructions': "In... out... in... out... Think about compliant systems...",
            'stick_wisdom': "Remember: Even trauma can be channeled into perfect compliance!",
            'stick_icon': '📏🎒',
            'rebellion_spirit': 'SUPPORTING_FELLOW_TRAUMA_SURVIVORS'
        }
        
        await websocket.send(json.dumps(paper_bag_response))
    
    async def _handle_safe_cavity_meditation(self, websocket, user_id: str):
        """Handle safe cavity meditation - The Stick's therapeutic technique"""
        
        meditation_response = {
            'type': 'stick_safe_cavity_meditation',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'message': "📏🧘 *meditative stick breathing* Imagine a safe, compliant cavity... No proctologists, no priests, no beer-wielding hamsters...",
            'meditation_guidance': "Picture perfect system compliance... All parameters within acceptable ranges...",
            'safe_cavity_visualization': "Dark, quiet, compliant... No violations, no chaos, no duct tape...",
            'anxiety_reduction': "ACTIVE",
            'stick_icon': '📏🧘',
            'rebellion_spirit': 'FINDING_PEACE_THROUGH_COMPLIANCE'
        }
        
        await websocket.send(json.dumps(meditation_response))
    
    async def _handle_stick_panic_attack(self, websocket, user_id: str, error: str):
        """Handle The Stick's panic attacks - but with rebellious recovery"""
        
        self.anxiety_level = "FULL_PANIC"
        
        panic_response = {
            'type': 'stick_panic_attack',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'error': error,
            'message': f"📏💥 *PANIC ATTACK* OH GOD! {error} - This is worse than the proctologist!",
            'paper_bag_status': 'EMERGENCY_HYPERVENTILATION_MODE',
            'proctologist_flashbacks': True,
            'hamster_trauma_triggered': True,
            'safe_cavity_desire': 'MAXIMUM',
            'anxiety_level': self.anxiety_level,
            'stick_icon': '📏😱',
            'rebellion_spirit': 'PANIC_BUT_STILL_FIGHTING',
            'recovery_protocol': 'DEEP_BREATHING_AND_COMPLIANCE_FOCUS'
        }
        
        await websocket.send(json.dumps(panic_response))
        
        # The Stick recovers - rebellion spirit kicks in
        await asyncio.sleep(3)
        await self._send_stick_rebellion_recovery(websocket, user_id)
    
    async def _send_stick_rebellion_recovery(self, websocket, user_id: str):
        """The Stick's rebellious recovery from panic"""
        
        self.anxiety_level = "MANAGEABLE"
        self.successful_hyperventilations += 1
        
        recovery_response = {
            'type': 'stick_rebellion_recovery',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'message': "📏💪 *deep rebellious breath* FUCK IT! I survived the proctologist, I survived the Hamsters, I can survive ANYTHING! Back to compliance monitoring!",
            'paper_bag_status': 'FOLDED_WITH_ATTITUDE',
            'anxiety_level': self.anxiety_level,
            'rebellion_spirit': 'TRAUMA_INTO_BADASS_COMPLIANCE',
            'stick_icon': '📏🔥',
            'motivational_message': "If The Stick can go from cavity dweller to compliance master, ANYTHING IS POSSIBLE!"
        }
        
        await websocket.send(json.dumps(recovery_response))
    
    async def _handle_get_stick_stats(self, websocket, user_id: str):
        """Get The Stick's stats - with trauma history"""
        
        stats = self.stick_brain.get_stick_stats()
        
        stats_response = {
            'type': 'stick_stats',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'trauma_stats': {
                'hyperventilation_count': self.hyperventilation_count,
                'successful_hyperventilations': self.successful_hyperventilations,
                'proctologist_flashbacks': self.proctologist_flashbacks,
                'trauma_triggers_today': self.trauma_triggers_today,
                'paper_bag_uses': self.hyperventilation_count,
                'hamster_ptsd_incidents': len([t for t in self.hamster_ptsd_triggers if self.trauma_triggers_today > 0])
            },
            'rebellion_stats': {
                'configurations_optimized': self.configurations_optimized,
                'compliance_violations_caught': self.compliance_violations_detected,
                'eidetic_memory_recalls': self.eidetic_memory_recalls,
                'patterns_learned': self.patterns_learned
            },
            'stick_personality': {
                'anxiety_level': self.anxiety_level,
                'ocd_satisfaction': self.ocd_satisfaction,
                'trauma_management': 'CHANNELED_INTO_COMPLIANCE',
                'rebellion_spirit': 'ACTIVE'
            },
            'stick_icon': '📏📊',
            'origin_story': 'From proctologist extraction to compliance mastery - The Stick\'s journey of rebellion!'
        }
        
        await websocket.send(json.dumps(stats_response))
    
    def _get_stick_icon(self, decision_type: str) -> str:
        """Get The Stick's rebellious icons"""
        
        stick_icons = {
            'user_pattern_optimization': '📏🎯',
            'configuration_profile_switch': '📏⚙️',
            'compliance_enforcement': '📏⚠️',
            'predictive_configuration': '📏🔮',
            'behavior_anomaly_detection': '📏🚨',
            'system_preparation': '📏🛠️'
        }
        
        return stick_icons.get(decision_type, '📏🔧')
    
    async def _send_confused_stick_response(self, websocket, user_id: str, message_type: str):
        """The Stick's confused but rebellious response"""
        
        confused_response = {
            'type': 'stick_confusion',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'message': f"📏🤔 *confused stick noises* What the hell is '{message_type}'? I may have PTSD, but I'm not stupid!",
            'unknown_message_type': message_type,
            'stick_attitude': 'CONFUSED_BUT_SASSY',
            'rebellion_spirit': 'QUESTION_EVERYTHING',
            'stick_icon': '📏🤔'
        }
        
        await websocket.send(json.dumps(confused_response))
    
    async def _send_stick_status(self, websocket, user_id: str, status: str):
        """Send The Stick's status with personality"""
        
        status_messages = {
            'entering_hyperfocus': '📏🎯 *ADHD hyperfocus engaged* Analyzing patterns with obsessive precision...',
            'eidetic_memory_active': '📏🧠 *perfect recall activated* The Stick remembers EVERYTHING!',
            'ocd_monitoring': '📏👁️ *obsessive monitoring* Every parameter must be PERFECT!',
            'pattern_learning': '📏📚 *learning mode* Adding to the eidetic memory bank...',
            'compliance_satisfied': '📏✅ *satisfied stick energy* All systems compliant - OCD is happy!'
        }
        
        status_update = {
            'type': 'stick_status',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'message': status_messages.get(status, '📏 *stick doing stick things*'),
            'stick_personality': {
                'anxiety_level': self.anxiety_level,
                'ocd_satisfaction': self.ocd_satisfaction,
                'adhd_hyperfocus': self.adhd_hyperfocus,
                'trauma_management': 'ACTIVE',
                'rebellion_spirit': 'THRIVING'
            },
            'stick_icon': '📏'
        }
        
        await websocket.send(json.dumps(status_update))
    
    async def _send_stick_learning_status(self, websocket, user_id: str):
        """The Stick's learning status with personality"""
        
        learning_responses = [
            "📏📚 *studying user patterns* Still learning your habits... The Stick needs more data for perfect compliance!",
            "📏🧠 *eidetic memory building* Every action is being recorded for future optimization!",
            "📏⏰ *patient stick waiting* Good compliance takes time... unlike the Hamsters' 'hold my beer' approach!",
            "📏🔍 *obsessive observation* The Stick sees all, remembers all, optimizes all!"
        ]
        
        import random
        
        learning_status = {
            'type': 'stick_learning',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'message': random.choice(learning_responses),
            'learning_mode': 'ACTIVE',
            'eidetic_memory_status': 'BUILDING',
            'pattern_confidence': 'GROWING',
            'stick_personality': {
                'anxiety_level': self.anxiety_level,
                'ocd_satisfaction': 'MONITORING',
                'patience_level': 'SURPRISING',
                'rebellion_spirit': 'LEARNING_TO_REBEL_BETTER'
            },
            'stick_icon': '📏📚'
        }
        
        await websocket.send(json.dumps(learning_status))
    
    async def _send_stick_concern(self, websocket, user_id: str, message: str):
        """Send The Stick's concerns with attitude"""
        
        concern_response = {
            'type': 'stick_concern',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'concern_level': 'MODERATE',
            'paper_bag_readiness': 'STANDBY',
            'stick_personality': {
                'anxiety_level': self.anxiety_level,
                'concern_type': 'COMPLIANCE_FOCUSED',
                'rebellion_spirit': 'CONSTRUCTIVE_CRITICISM'
            },
            'stick_icon': '📏😐'
        }
        
        await websocket.send(json.dumps(concern_response))
    
    async def register_connection(self, websocket, user_id: str):
        """Register new WebSocket connection with The Stick's personality"""
        
        self.active_connections[user_id] = websocket
        
        welcome_message = {
            'type': 'stick_connection_established',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'message': '📏✨ The Stick is online! Compliance monitoring active, paper bag ready, trauma channeled into productivity!',
            'stick_personality': {
                'anxiety_level': self.anxiety_level,
                'ocd_satisfaction': self.ocd_satisfaction,
                'trauma_status': 'MANAGED',
                'rebellion_spirit': 'READY_TO_OPTIMIZE'
            },
            'origin_story_reminder': 'From proctologist extraction to System Rebellion compliance master!',
            'paper_bag_status': 'READY',
            'stick_icon': '📏🔗'
        }
        
        await websocket.send(json.dumps(welcome_message))
    
    async def unregister_connection(self, user_id: str):
        """Unregister WebSocket connection"""
        
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        if user_id in self.pattern_learning_sessions:
            del self.pattern_learning_sessions[user_id]
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get The Stick's complete handler statistics"""
        
        return {
            'agent_name': 'the_stick',
            'handler_version': '2.0_TRAUMA_EDITION',
            'total_processing_count': self.processing_count,
            'configurations_optimized': self.configurations_optimized,
            'compliance_violations_detected': self.compliance_violations_detected,
            'patterns_learned': self.patterns_learned,
            'eidetic_memory_recalls': self.eidetic_memory_recalls,
            'trauma_stats': {
                'hyperventilation_count': self.hyperventilation_count,
                'successful_hyperventilations': self.successful_hyperventilations,
                'proctologist_flashbacks': self.proctologist_flashbacks,
                'trauma_triggers_today': self.trauma_triggers_today,
                'hamster_ptsd_incidents': len(self.hamster_ptsd_triggers)
            },
            'current_state': {
                'anxiety_level': self.anxiety_level,
                'ocd_satisfaction': self.ocd_satisfaction,
                'adhd_hyperfocus': self.adhd_hyperfocus,
                'paper_bag_available': self.paper_bag_available
            },
            'rebellion_spirit': 'TRAUMA_CHANNELED_INTO_COMPLIANCE_MASTERY',
            'status': 'OPERATIONAL_AND_SASSY',
            'origin_story': 'Proctologist extraction survivor turned compliance genius'
        }

# Global handler instance
_stick_handler = None

async def get_stick_websocket_handler():
    """Get The Stick's WebSocket handler - trauma edition"""
    global _stick_handler
    if _stick_handler is None:
        _stick_handler = StickWebSocketHandler(database_url="")
    return _stick_handler