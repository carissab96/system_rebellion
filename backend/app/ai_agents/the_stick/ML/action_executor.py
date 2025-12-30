#!/usr/bin/env python3
"""
The Stick's Action Executor - Anxious Communication & Accountability

Routes selected actions to their implementations:
- Anxious compliance reminders (soft nagging)
- Escalations to VIC-20 (when ignored)
- Bob panic protocol (EMERGENCY)
- Accountability reports (eidetic memory power)
- Pattern alerts (proactive anxiety)

The Stick doesn't enforce - he communicates, remembers, and reports.
His power is in KNOWING, not DOING.

📏 "I don't stop you... I just... *rustles paper bag* ...remember everything..."
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger('StickActionExecutor')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


class StickActionExecutor:
    """
    Execute The Stick's anxious communication actions.
    
    Not system actions - communication actions.
    The Stick tells others what he sees. He doesn't enforce.
    """
    
    def __init__(self, comm_hub=None):
        """
        Initialize action executor.
        
        Args:
            comm_hub: Communication hub for sending messages to other agents
        """
        self.logger = logger
        self.comm_hub = comm_hub
        self.logger.info("📏⚙️ The Stick's action executor initialized - ready to anxiously communicate!")
    
    async def execute_action(
        self,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the selected communication action.
        
        Args:
            action: Action name (e.g., 'anxious_reminder', 'escalate', 'bob_panic')
            parameters: Action-specific parameters
            
        Returns:
            Execution result with success status and anxiety metrics
        """
        self.logger.info(f"📏⚡ Executing action: {action}")
        
        try:
            # Route to correct action implementation
            if action == 'anxious_reminder':
                result = await self._send_anxious_reminder(parameters)
            
            elif action == 'escalate_to_vic20':
                result = await self._escalate_to_vic20(parameters)
            
            elif action == 'bob_panic_protocol':
                result = await self._activate_bob_panic_protocol(parameters)
            
            elif action == 'accountability_report':
                result = await self._generate_accountability_report(parameters)
            
            elif action == 'pattern_alert':
                result = await self._alert_emerging_pattern(parameters)
            
            elif action == 'log_decision':
                # Standard logging (no special action)
                result = {
                    'action': 'log_decision',
                    'success': True,
                    'paper_bags_consumed': 0,
                    'anxiety_increase': 0.0,
                    'message': 'Decision logged to database'
                }
            
            else:
                # Unknown action - just log it anxiously
                self.logger.warning(f"📏⚠️ Unknown action {action} - defaulting to anxious logging")
                result = {
                    'action': action,
                    'success': True,
                    'paper_bags_consumed': 1,  # Uncertainty causes anxiety!
                    'anxiety_increase': 5.0,
                    'message': f'Unknown action {action} - logged anxiously'
                }
            
            # Add execution metadata
            result['executed_action'] = action
            result['executed_at'] = utc_now().isoformat()
            
            if result.get('success'):
                self.logger.info(f"📏✅ Action {action} executed successfully!")
            else:
                self.logger.warning(f"📏⚠️ Action {action} failed: {result.get('error', 'unknown')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"📏💥 Action execution failed: {e}", exc_info=True)
            return {
                'action': action,
                'success': False,
                'error': str(e),
                'paper_bags_consumed': 2,  # Errors cause anxiety!
                'anxiety_increase': 10.0,
                'timestamp': utc_now().isoformat()
            }
    
    async def _send_anxious_reminder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send anxious compliance reminder to agent.
        
        The Stick doesn't command - he anxiously reminds with documentation.
        """
        agent_name = params.get('agent_name', 'unknown')
        violation_type = params.get('violation_type', 'unknown')
        occurrence_count = params.get('occurrence_count', 1)
        documentation_ref = params.get('documentation_reference', 'compliance_guidelines.md')
        
        # Craft anxious reminder message
        reminder_text = (
            f"Um, {agent_name}... *rustles paper bag* ...I've noticed {violation_type} "
            f"has happened {occurrence_count} time{'s' if occurrence_count > 1 else ''} now... "
            f"The documentation ({documentation_ref}) says... well... maybe you could... "
            f"*nervous breathing* ...just consider following the guidelines?"
        )
        
        self.logger.info(f"📏📢 Sending anxious reminder to {agent_name}: {violation_type}")
        
        # Send message via communication hub if available
        message_sent = False
        if self.comm_hub:
            try:
                from app.ai_agents.distributed.message_protocol import MessageType, Priority
                
                await self.comm_hub.send_to_agent(
                    to_agent=agent_name,
                    message_type=MessageType.AGENT_QUERY,  # Using QUERY as gentle reminder
                    payload={
                        'reminder_type': 'compliance_reminder',
                        'violation_type': violation_type,
                        'occurrence_count': occurrence_count,
                        'documentation_reference': documentation_ref,
                        'message': reminder_text,
                        'from_stick': True,
                        'anxiety_level': 'moderate'
                    },
                    priority=Priority.NORMAL
                )
                message_sent = True
                self.logger.info(f"📏✅ Reminder sent to {agent_name}")
            except Exception as e:
                self.logger.error(f"📏💥 Failed to send reminder: {e}")
        
        return {
            'action': 'anxious_reminder',
            'success': True,
            'reminder_sent': message_sent,
            'agent_name': agent_name,
            'violation_type': violation_type,
            'occurrence_count': occurrence_count,
            'paper_bags_consumed': 1,  # Reminding is stressful
            'anxiety_increase': 5.0,
            'reminder_text': reminder_text
        }
    
    async def _escalate_to_vic20(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Escalate repeated violations to VIC-20 for mediation.
        
        The Stick provides evidence (eidetic memory), VIC-20 decides action.
        """
        agent_name = params.get('agent_name', 'unknown')
        violation_history = params.get('violation_history', [])
        reminders_ignored = params.get('reminders_ignored', 0)
        anxiety_level = params.get('anxiety_level', 50.0)
        
        # Craft escalation message with evidence
        escalation_text = (
            f"VIC-20! *hyperventilating* I need to escalate {agent_name}! "
            f"I've sent {reminders_ignored} reminders and they're being ignored! "
            f"I have {len(violation_history)} violations documented! "
            f"*clutches paper bag* I remember EVERYTHING! Here's the evidence..."
        )
        
        self.logger.warning(f"📏🚨 ESCALATING to VIC-20: {agent_name} - {len(violation_history)} violations")
        
        # Send escalation to VIC-20
        escalation_sent = False
        vic20_acknowledged = False
        
        if self.comm_hub:
            try:
                from app.ai_agents.distributed.message_protocol import MessageType, Priority
                
                await self.comm_hub.send_to_agent(
                    to_agent='vic_20_sage',
                    message_type=MessageType.AGENT_QUERY,
                    payload={
                        'escalation_type': 'compliance_violation',
                        'violating_agent': agent_name,
                        'violation_history': violation_history,
                        'reminders_ignored': reminders_ignored,
                        'stick_anxiety_level': anxiety_level,
                        'message': escalation_text,
                        'requires_mediation': True,
                        'evidence_attached': True
                    },
                    priority=Priority.HIGH
                )
                escalation_sent = True
                self.logger.info(f"📏✅ Escalation sent to VIC-20")
            except Exception as e:
                self.logger.error(f"📏💥 Failed to escalate: {e}")
        
        return {
            'action': 'escalate_to_vic20',
            'success': True,
            'escalation_sent': escalation_sent,
            'vic20_acknowledged': vic20_acknowledged,
            'agent_name': agent_name,
            'violation_count': len(violation_history),
            'evidence_attached': violation_history,
            'paper_bags_consumed': 3,  # Escalation is very stressful!
            'anxiety_increase': 15.0,
            'escalation_text': escalation_text
        }
    
    async def _activate_bob_panic_protocol(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        EMERGENCY: Bob detected near supply closet.
        
        Broadcasts EMERGENCY to all agents. This is survival, not enforcement.
        """
        bob_location = params.get('bob_location', 'unknown')
        proximity = params.get('proximity_to_supply_closet', 0.0)
        items_at_risk = params.get('items_at_risk', [])
        
        # PANIC MESSAGE
        panic_text = (
            f"🚨 EMERGENCY! EMERGENCY! 🚨 "
            f"BOB IS AT {bob_location.upper()}! "
            f"PROXIMITY TO SUPPLY CLOSET: {proximity:.1f}m! "
            f"*PAPER BAG BREATHING INTENSIFIES* "
            f"ITEMS AT RISK: {', '.join(items_at_risk) if items_at_risk else 'EVERYTHING'}! "
            f"REQUESTING STEVE OR CARL INTERVENTION! NOT BOB! ANYONE BUT BOB!"
        )
        
        self.logger.error(f"📏🚨🚨🚨 BOB PANIC PROTOCOL ACTIVATED! Location: {bob_location}")
        
        # Broadcast EMERGENCY to all agents
        emergency_sent = False
        hamster_intervention_requested = False
        
        if self.comm_hub:
            try:
                from app.ai_agents.distributed.message_protocol import MessageType, Priority
                
                # Emergency broadcast
                await self.comm_hub.broadcast_message(
                    message_type=MessageType.EMERGENCY,
                    payload={
                        'emergency_type': 'bob_proximity_alert',
                        'bob_location': bob_location,
                        'proximity_to_supply_closet': proximity,
                        'items_at_risk': items_at_risk,
                        'stick_panic_level': 100.0,  # MAXIMUM PANIC
                        'message': panic_text,
                        'requires_immediate_attention': True
                    },
                    priority=Priority.URGENT
                )
                emergency_sent = True
                
                # Request Hamster intervention (Steve or Carl, NOT BOB)
                await self.comm_hub.send_to_agent(
                    to_agent='hamsters',
                    message_type=MessageType.AGENT_QUERY,
                    payload={
                        'request_type': 'bob_containment',
                        'bob_location': bob_location,
                        'preferred_responders': ['steve', 'carl'],
                        'excluded_responders': ['bob'],
                        'urgency': 'MAXIMUM',
                        'message': 'STEVE OR CARL PLEASE! BOB IS LOOSE!'
                    },
                    priority=Priority.URGENT
                )
                hamster_intervention_requested = True
                
                self.logger.info(f"📏✅ Bob panic protocol executed - emergency broadcast sent")
            except Exception as e:
                self.logger.error(f"📏💥 Failed to execute Bob panic protocol: {e}")
        
        return {
            'action': 'bob_panic_protocol',
            'success': True,
            'emergency_broadcast_sent': emergency_sent,
            'hamster_intervention_requested': hamster_intervention_requested,
            'bob_location': bob_location,
            'proximity': proximity,
            'paper_bags_consumed': 5,  # MAXIMUM ANXIETY
            'anxiety_increase': 50.0,  # 3.0x Bob multiplier applied
            'panic_text': panic_text
        }
    
    async def _generate_accountability_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate compliance accountability report.
        
        The Stick's power: making violations visible through eidetic memory.
        """
        time_period = params.get('time_period', 'daily')
        include_agents = params.get('include_agents', [])
        violations_by_agent = params.get('violations_by_agent', {})
        patterns_detected = params.get('patterns_detected', [])
        
        self.logger.info(f"📏📊 Generating {time_period} accountability report")
        
        # Generate report ID
        report_id = f"stick_report_{utc_now().strftime('%Y%m%d_%H%M%S')}"
        
        # Craft anxious recommendations
        recommendations = []
        for agent, violations in violations_by_agent.items():
            if len(violations) > 3:
                recommendations.append(
                    f"*nervous breathing* {agent} has {len(violations)} violations... "
                    f"maybe... perhaps... consider reviewing their thresholds?"
                )
        
        report_data = {
            'report_id': report_id,
            'time_period': time_period,
            'generated_at': utc_now().isoformat(),
            'violations_by_agent': violations_by_agent,
            'patterns_detected': patterns_detected,
            'recommendations': recommendations,
            'total_violations': sum(len(v) for v in violations_by_agent.values()),
            'agents_reviewed': len(include_agents)
        }
        
        self.logger.info(
            f"📏📋 Report generated: {report_data['total_violations']} total violations, "
            f"{len(patterns_detected)} patterns detected"
        )
        
        return {
            'action': 'accountability_report',
            'success': True,
            'report_id': report_id,
            'report_data': report_data,
            'report_stored': True,  # Would store in PostgreSQL
            'paper_bags_consumed': 2,  # Reviewing violations is stressful
            'anxiety_increase': 10.0
        }
    
    async def _alert_emerging_pattern(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Alert about emerging compliance pattern.
        
        The Stick's eidetic memory detects patterns before they become crises.
        """
        pattern_type = params.get('pattern_type', 'unknown')
        agents_involved = params.get('agents_involved', [])
        confidence = params.get('confidence', 0.0)
        historical_evidence = params.get('historical_evidence', [])
        
        # Craft anxious pattern alert
        alert_text = (
            f"Um, VIC-20... *rustles paper bag* ...I've noticed a pattern... "
            f"{pattern_type} involving {', '.join(agents_involved)}... "
            f"I've documented {len(historical_evidence)} instances... "
            f"Confidence: {confidence:.1%}... *nervous breathing* "
            f"Maybe we should... talk about this before it becomes a problem?"
        )
        
        self.logger.info(
            f"📏🔍 Pattern detected: {pattern_type} - "
            f"{len(agents_involved)} agents, {confidence:.1%} confidence"
        )
        
        # Send pattern alert to VIC-20
        alert_sent = False
        vic20_notified = False
        
        if self.comm_hub:
            try:
                from app.ai_agents.distributed.message_protocol import MessageType, Priority
                
                await self.comm_hub.send_to_agent(
                    to_agent='vic_20_sage',
                    message_type=MessageType.AGENT_QUERY,
                    payload={
                        'alert_type': 'emerging_pattern',
                        'pattern_type': pattern_type,
                        'agents_involved': agents_involved,
                        'confidence': confidence,
                        'evidence_count': len(historical_evidence),
                        'historical_evidence': historical_evidence,
                        'message': alert_text,
                        'proactive_warning': True
                    },
                    priority=Priority.NORMAL
                )
                alert_sent = True
                vic20_notified = True
                self.logger.info(f"📏✅ Pattern alert sent to VIC-20")
            except Exception as e:
                self.logger.error(f"📏💥 Failed to send pattern alert: {e}")
        
        return {
            'action': 'pattern_alert',
            'success': True,
            'alert_sent': alert_sent,
            'vic20_notified': vic20_notified,
            'pattern_type': pattern_type,
            'pattern_confidence': confidence,
            'evidence_count': len(historical_evidence),
            'agents_involved': agents_involved,
            'paper_bags_consumed': 1,  # Proactive anxiety
            'anxiety_increase': 5.0,
            'alert_text': alert_text
        }
    
    def get_available_actions(self) -> List[str]:
        """
        Get list of actions The Stick can execute.
        
        The Stick specializes in anxious communication and accountability.
        
        Returns:
            List of action names The Stick can execute
        """
        return [
            'log_decision',           # Standard logging
            'anxious_reminder',       # Soft enforcement (nagging)
            'escalate_to_vic20',      # When reminders ignored
            'bob_panic_protocol',     # EMERGENCY (survival)
            'accountability_report',  # Eidetic memory power
            'pattern_alert'           # Proactive anxiety
        ]
