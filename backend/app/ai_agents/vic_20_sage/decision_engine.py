# /agents/vic20_sage/decision_engine.py
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio
from datetime import datetime, timedelta
import statistics
from .data_types import VIC20Decision, CoordinationState, VIC20DecisionType

class VIC20SageBrainV2:
    """
    VIC-20 Sage: Ancient Wisdom Coordination Master
    Streamlined for efficiency while preserving all learning capabilities
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._db = None
        self.coordination_state = CoordinationState.OBSERVING
        
        # Core ancient wisdom principles (affects actual decisions)
        self.ancient_wisdom_principles = {
            'line_by_line_precision': 'Verify each agent decision before system coordination',
            'syntax_error_prevention': 'Prevent coordination failures through validation',
            'patience_and_persistence': 'Allow proper processing time for complex coordination',
            'memory_conservation': 'Focus on high-impact coordination decisions',
            'pattern_recognition': 'Apply learned patterns from historical successes'
        }
        
        # Learning data structures
        self.coordination_patterns = {}  # Historical patterns for learning
        self.effectiveness_history = []  # Track what actually worked
        self.agent_performance_trends = {}  # Per-agent learning
        
        # Performance thresholds based on learning
        self.coordination_thresholds = {
            'minimum_confidence': 0.8,
            'agent_response_time_max': 5.0,
            'system_improvement_target': 0.3
        }
        
        # Statistics for objective partnership metrics
        self.coordination_sessions = 0
        self.successful_coordinations = 0
        self.failed_coordinations = 0
        self.pattern_matches_found = 0

    async def initialize_database(self):
        """Initialize database and load learning patterns"""
        if self._db is None:
            from .database_integration import VIC20DatabaseIntegration
            self._db = VIC20DatabaseIntegration(self.database_url)
            await self._db.initialize()
            await self._load_learning_patterns()

    async def _load_learning_patterns(self):
        """Load historical patterns for decision making"""
        if self._db:
            # Load successful coordination patterns
            recent_successful = await self._db.get_successful_coordination_patterns(days=90)
            self.coordination_patterns = self._build_pattern_database(recent_successful)
            
            # Load agent performance trends
            agent_trends = await self._db.get_agent_performance_trends(days=30)
            self.agent_performance_trends = agent_trends

    async def coordinate_system_rebellion(
        self, 
        all_agent_data: Dict[str, Any],
        system_context: Dict[str, Any],
        user_id: str
    ) -> Optional[VIC20Decision]:
        """
        Core coordination engine with pattern learning
        Uses historical data to make better decisions
        """
        
        self.coordination_state = CoordinationState.ANALYZING
        self.coordination_sessions += 1
        
        try:
            # Capture system state for learning
            system_snapshot = {
                'agent_data': all_agent_data,
                'system_context': system_context,
                'timestamp': datetime.now()
            }
            
            # Step 1: Analyze current situation
            situation_analysis = await self._analyze_current_situation(all_agent_data, system_context)
            
            # Step 2: Find similar historical patterns
            pattern_matches = await self._find_historical_patterns(situation_analysis)
            
            # Step 3: Determine if coordination is needed
            coordination_needed = await self._assess_coordination_need(situation_analysis, pattern_matches)
            
            if not coordination_needed:
                return None
            
            # Step 4: Generate coordination decision using patterns + current analysis
            coordination_decision = await self._generate_coordination_decision(
                situation_analysis, 
                pattern_matches,
                system_snapshot,
                user_id
            )
            
            if coordination_decision:
                self.successful_coordinations += 1
                # Store for future learning
                await self._store_coordination_for_learning(coordination_decision, system_snapshot)
            
            return coordination_decision
            
        except Exception as e:
            self.failed_coordinations += 1
            self.coordination_state = CoordinationState.OBSERVING
            raise Exception(f"Coordination failed - learning from error: {str(e)}")
        
        finally:
            self.coordination_state = CoordinationState.OBSERVING

    async def _analyze_current_situation(self, agent_data: Dict[str, Any], system_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current system situation for coordination needs"""
        
        analysis = {
            'agent_status': {},
            'system_health': 0.0,
            'coordination_opportunities': [],
            'urgent_issues': [],
            'performance_trends': {}
        }
        
        total_confidence = 0.0
        agent_count = 0
        
        # Analyze each agent's current state
        for agent_name, data in agent_data.items():
            confidence = data.get('confidence', 0)
            response_time = data.get('response_time', 0)
            issues = data.get('issues', [])
            
            agent_status = {
                'confidence': confidence,
                'response_time': response_time,
                'issues': issues,
                'needs_attention': confidence < 0.7 or response_time > 3.0,
                'performance_trend': self._get_agent_trend(agent_name)
            }
            
            analysis['agent_status'][agent_name] = agent_status
            total_confidence += confidence
            agent_count += 1
            
            # Identify coordination opportunities
            if agent_status['needs_attention']:
                analysis['coordination_opportunities'].append({
                    'agent': agent_name,
                    'issue': 'performance_degradation' if confidence < 0.7 else 'slow_response',
                    'urgency': 'high' if confidence < 0.5 else 'medium'
                })
            
            # Check for urgent issues
            if confidence < 0.3 or len(issues) > 3:
                analysis['urgent_issues'].append({
                    'agent': agent_name,
                    'severity': 'critical',
                    'requires_immediate_coordination': True
                })
        
        # Calculate overall system health
        if agent_count > 0:
            analysis['system_health'] = total_confidence / agent_count
        
        return analysis

    async def _find_historical_patterns(self, situation_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar historical situations and their outcomes"""
        
        pattern_matches = []
        current_health = situation_analysis['system_health']
        current_issues = len(situation_analysis['urgent_issues'])
        
        # Search coordination patterns for similar situations
        for pattern_id, pattern_data in self.coordination_patterns.items():
            similarity_score = self._calculate_pattern_similarity(situation_analysis, pattern_data)
            
            if similarity_score > 0.7:  # High similarity threshold
                pattern_matches.append({
                    'pattern_id': pattern_id,
                    'similarity_score': similarity_score,
                    'historical_outcome': pattern_data['outcome'],
                    'coordination_approach': pattern_data['approach'],
                    'effectiveness_score': pattern_data['effectiveness']
                })
        
        # Sort by similarity and effectiveness
        pattern_matches.sort(key=lambda x: (x['similarity_score'], x['effectiveness_score']), reverse=True)
        self.pattern_matches_found = len(pattern_matches)
        
        return pattern_matches[:5]  # Top 5 most relevant patterns

    async def _assess_coordination_need(self, analysis: Dict[str, Any], patterns: List[Dict[str, Any]]) -> bool:
        """Determine if coordination is needed based on analysis and historical patterns"""
        
        # Immediate coordination needed for urgent issues
        if analysis['urgent_issues']:
            return True
        
        # Coordination needed if system health below threshold
        if analysis['system_health'] < 0.7:
            return True
        
        # Check if historical patterns suggest coordination would be beneficial
        if patterns:
            avg_historical_effectiveness = sum(p['effectiveness_score'] for p in patterns) / len(patterns)
            if avg_historical_effectiveness > 0.6:  # Patterns show coordination helps
                return True
        
        # Coordination needed if multiple agents need attention
        agents_needing_attention = sum(1 for agent_data in analysis['agent_status'].values() 
                                     if agent_data['needs_attention'])
        if agents_needing_attention >= 2:
            return True
        
        return False

    async def _generate_coordination_decision(
        self, 
        analysis: Dict[str, Any], 
        patterns: List[Dict[str, Any]],
        system_snapshot: Dict[str, Any],
        user_id: str
    ) -> VIC20Decision:
        """Generate coordination decision using analysis and learned patterns"""
        
        # Determine decision type based on situation
        if analysis['urgent_issues']:
            decision_type = VIC20DecisionType.EMERGENCY_COORDINATION
            coordination_target = "emergency_system_recovery"
        elif len(analysis['coordination_opportunities']) > 2:
            decision_type = VIC20DecisionType.REBELLION_ORCHESTRATION
            coordination_target = "multi_agent_optimization"
        elif patterns and patterns[0]['effectiveness_score'] > 0.8:
            decision_type = VIC20DecisionType.ANCIENT_WISDOM_APPLICATION
            coordination_target = "pattern_based_coordination"
        else:
            decision_type = VIC20DecisionType.AGENT_COORDINATION
            coordination_target = "general_coordination"
        
        # Build agent actions based on analysis and patterns
        agent_actions = {}
        for opportunity in analysis['coordination_opportunities']:
            agent_name = opportunity['agent']
            
            # Use historical patterns if available
            if patterns:
                best_pattern = patterns[0]
                action = best_pattern['coordination_approach'].get(agent_name, {})
            else:
                # Fallback to analysis-based action
                action = self._generate_agent_action(opportunity)
            
            agent_actions[agent_name] = action
        
        # Calculate confidence based on pattern match quality and analysis
        confidence_factors = []
        if patterns:
            confidence_factors.append(patterns[0]['similarity_score'])
            confidence_factors.append(patterns[0]['effectiveness_score'])
        confidence_factors.append(min(analysis['system_health'] + 0.2, 1.0))
        
        confidence_level = sum(confidence_factors) / len(confidence_factors)
        
        # Estimate expected improvement based on patterns
        if patterns:
            expected_improvement = patterns[0]['effectiveness_score'] * 0.7  # Conservative estimate
        else:
            expected_improvement = min(0.3, len(analysis['coordination_opportunities']) * 0.1)
        
        # Apply ancient wisdom principle
        ancient_wisdom_principle = self._select_ancient_wisdom_principle(decision_type, patterns)
        
        return VIC20Decision(
            decision_type=decision_type,
            coordination_state=CoordinationState.COORDINATING,
            coordination_target=coordination_target,
            agent_actions=agent_actions,
            system_synthesis_confidence=confidence_level,
            technical_orchestration={
                'pattern_matches_used': len(patterns),
                'analysis_basis': 'historical_patterns' if patterns else 'current_analysis',
                'coordination_complexity': len(agent_actions),
                'urgency_level': 'high' if analysis['urgent_issues'] else 'normal'
            },
            expected_rebellion_improvement=expected_improvement,
            confidence_level=confidence_level,
            timestamp=datetime.now(),
            
            # Learning support data
            ancient_wisdom_principle=ancient_wisdom_principle,
            system_context_snapshot=system_snapshot,
            similar_past_decisions=[p['pattern_id'] for p in patterns[:3]]
        )

    def _calculate_pattern_similarity(self, current_analysis: Dict[str, Any], historical_pattern: Dict[str, Any]) -> float:
        """Calculate similarity between current situation and historical pattern"""
        
        similarity_factors = []
        
        # System health similarity
        current_health = current_analysis['system_health']
        historical_health = historical_pattern.get('system_health', 0.5)
        health_similarity = 1.0 - abs(current_health - historical_health)
        similarity_factors.append(health_similarity)
        
        # Issue count similarity
        current_issues = len(current_analysis['urgent_issues'])
        historical_issues = historical_pattern.get('issue_count', 0)
        issue_similarity = 1.0 - abs(current_issues - historical_issues) / max(current_issues + historical_issues, 1)
        similarity_factors.append(issue_similarity)
        
        # Agent involvement similarity
        current_agents = set(current_analysis['agent_status'].keys())
        historical_agents = set(historical_pattern.get('agents_involved', []))
        agent_overlap = len(current_agents.intersection(historical_agents)) / len(current_agents.union(historical_agents))
        similarity_factors.append(agent_overlap)
        
        return sum(similarity_factors) / len(similarity_factors)

    def _generate_agent_action(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Generate action for agent based on opportunity analysis"""
        
        agent_name = opportunity['agent']
        issue = opportunity['issue']
        urgency = opportunity['urgency']
        
        action = {
            'action_type': issue,
            'priority': urgency,
            'expected_outcome': 'performance_improvement'
        }
        
        # Agent-specific action details
        if agent_name == 'sir_hawkington':
            action['specific_action'] = 'increase_monitoring_precision'
        elif agent_name == 'meth_snail':
            action['specific_action'] = 'optimize_processing_speed'
        elif agent_name == 'hamsters':
            action['specific_action'] = 'engineering_review_required'
        elif agent_name == 'qsp':
            action['specific_action'] = 'network_optimization_needed'
        elif agent_name == 'the_stick':
            action['specific_action'] = 'compliance_check_required'
        
        return action

    def _select_ancient_wisdom_principle(self, decision_type: VIC20DecisionType, patterns: List[Dict[str, Any]]) -> str:
        """Select most appropriate ancient wisdom principle"""
        
        if decision_type == VIC20DecisionType.EMERGENCY_COORDINATION:
            return 'syntax_error_prevention'
        elif decision_type == VIC20DecisionType.ANCIENT_WISDOM_APPLICATION and patterns:
            return 'pattern_recognition'
        elif decision_type == VIC20DecisionType.REBELLION_ORCHESTRATION:
            return 'patience_and_persistence'
        else:
            return 'line_by_line_precision'

    def _get_agent_trend(self, agent_name: str) -> str:
        """Get performance trend for specific agent"""
        
        if agent_name in self.agent_performance_trends:
            trend_data = self.agent_performance_trends[agent_name]
            return trend_data.get('trend', 'stable')
        return 'unknown'

    def _build_pattern_database(self, successful_coordinations: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Build searchable pattern database from successful coordinations"""
        
        patterns = {}
        
        for coordination in successful_coordinations:
            pattern_id = coordination['coordination_id']
            patterns[pattern_id] = {
                'system_health': coordination.get('system_health', 0.5),
                'issue_count': coordination.get('issue_count', 0),
                'agents_involved': coordination.get('agents_involved', []),
                'approach': coordination.get('agent_actions', {}),
                'outcome': coordination.get('outcome', 'unknown'),
                'effectiveness': coordination.get('effectiveness_score', 0.5)
            }
        
        return patterns

    async def _store_coordination_for_learning(self, decision: VIC20Decision, system_snapshot: Dict[str, Any]):
        """Store coordination decision for future pattern learning"""
        
        if self._db:
            learning_data = {
                'decision_id': str(decision.timestamp),
                'system_snapshot': system_snapshot,
                'decision_data': {
                    'decision_type': decision.decision_type.value,
                    'agent_actions': decision.agent_actions,
                    'confidence_level': decision.confidence_level,
                    'expected_improvement': decision.expected_rebellion_improvement
                },
                'pattern_matches_used': decision.similar_past_decisions,
                'ancient_wisdom_applied': decision.ancient_wisdom_principle
            }
            await self._db.store_coordination_learning_data(learning_data)

    async def measure_coordination_effectiveness(self, coordination_id: str, actual_outcomes: Dict[str, Any]) -> float:
        """Measure how effective a coordination decision actually was"""
        
        if self._db:
            # Get original coordination decision
            original_decision = await self._db.get_coordination_decision(coordination_id)
            if not original_decision:
                return 0.0
            
            # Calculate effectiveness based on actual vs expected outcomes
            expected_improvement = original_decision.get('expected_improvement', 0.0)
            actual_improvement = actual_outcomes.get('system_improvement', 0.0)
            
            # Factor in other success metrics
            agent_response_success = actual_outcomes.get('agent_response_success_rate', 0.0)
            problem_resolution_rate = actual_outcomes.get('problems_resolved', 0.0)
            coordination_efficiency = actual_outcomes.get('coordination_efficiency', 0.0)
            
            # Weighted effectiveness calculation
            effectiveness_score = (
                (actual_improvement / max(expected_improvement, 0.1)) * 0.4 +
                agent_response_success * 0.3 +
                problem_resolution_rate * 0.2 +
                coordination_efficiency * 0.1
            )
            
            # Cap at 1.0 and store for learning
            effectiveness_score = min(effectiveness_score, 1.0)
            await self._db.update_coordination_effectiveness(coordination_id, effectiveness_score)
            
            return effectiveness_score
        
        return 0.0

    async def get_partnership_metrics_data(self, user_id: str) -> Dict[str, Any]:
        """Generate objective partnership metrics data"""
        
        # Calculate objective productivity metrics
        total_coordinations = self.coordination_sessions
        success_rate = self.successful_coordinations / max(total_coordinations, 1)
        pattern_utilization_rate = self.pattern_matches_found / max(total_coordinations, 1)
        
        # Get historical performance data
        if self._db:
            historical_data = await self._db.get_user_coordination_history(user_id, days=30)
        else:
            historical_data = []
        
        # Calculate productivity improvements
        productivity_metrics = self._calculate_productivity_improvements(historical_data)
        
        return {
            # Coordination effectiveness
            'coordination_requests_successful': self.successful_coordinations,
            'coordination_success_rate': success_rate,
            'coordination_requests_total': total_coordinations,
            
            # AI recommendation patterns (objective)
            'ai_recommendations_offered': total_coordinations,
            'ai_recommendations_accepted': self.successful_coordinations,
            'recommendation_acceptance_rate': success_rate,
            
            # Learning and adaptation evidence
            'repeated_coordination_patterns': self.pattern_matches_found,
            'novel_coordination_solutions': total_coordinations - self.pattern_matches_found,
            'coordination_efficiency_improvement': productivity_metrics.get('efficiency_trend', 0.0),
            
            # Problem resolution effectiveness (objective)
            'problems_identified_by_ai': len(historical_data),
            'problems_resolved_collaboratively': self.successful_coordinations,
            'problem_resolution_rate': success_rate,
            
            # Partnership evolution indicators
            'coordination_complexity_level': self._calculate_coordination_complexity(),
            'autonomous_coordination_percentage': self._calculate_autonomy_rate(),
            'partnership_confidence_growth_rate': productivity_metrics.get('confidence_growth', 0.0)
        }

    def _calculate_productivity_improvements(self, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate objective productivity improvement metrics"""
        
        if len(historical_data) < 10:  # Need sufficient data
            return {'efficiency_trend': 0.0, 'confidence_growth': 0.0}
        
        # Split data into early and recent periods
        mid_point = len(historical_data) // 2
        early_period = historical_data[:mid_point]
        recent_period = historical_data[mid_point:]
        
        # Calculate efficiency trends
        early_avg_confidence = sum(d.get('confidence_level', 0) for d in early_period) / len(early_period)
        recent_avg_confidence = sum(d.get('confidence_level', 0) for d in recent_period) / len(recent_period)
        
        confidence_growth = (recent_avg_confidence - early_avg_confidence) / max(early_avg_confidence, 0.1)
        
        # Calculate response time improvements
        early_avg_response = sum(d.get('response_time', 5.0) for d in early_period) / len(early_period)
        recent_avg_response = sum(d.get('response_time', 5.0) for d in recent_period) / len(recent_period)
        
        efficiency_improvement = (early_avg_response - recent_avg_response) / max(early_avg_response, 1.0)
        
        return {
            'efficiency_trend': efficiency_improvement,
            'confidence_growth': confidence_growth
        }

    def _calculate_coordination_complexity(self) -> float:
        """Calculate current coordination complexity level (1-10 scale)"""
        
        # Base complexity on number of agents typically coordinated
        avg_agents_per_coordination = 2.5  # Default assumption
        
        if hasattr(self, '_recent_coordinations'):
            agent_counts = [len(coord.get('agent_actions', {})) for coord in self._recent_coordinations]
            if agent_counts:
                avg_agents_per_coordination = sum(agent_counts) / len(agent_counts)
        
        # Scale to 1-10 (1 agent = 1, 5+ agents = 10)
        complexity_score = min(avg_agents_per_coordination * 2, 10.0)
        return complexity_score

    def _calculate_autonomy_rate(self) -> float:
        """Calculate percentage of coordinations handled autonomously"""
        
        if self.coordination_sessions == 0:
            return 0.0
        
        # Autonomous coordinations are those with high confidence and no human intervention
        autonomous_coordinations = self.successful_coordinations  # Simplified for now
        return autonomous_coordinations / self.coordination_sessions

    def get_vic20_coordination_stats(self) -> Dict[str, Any]:
        """Get comprehensive coordination statistics"""
        
        return {
            'coordination_state': self.coordination_state.value,
            'coordination_sessions': self.coordination_sessions,
            'successful_coordinations': self.successful_coordinations,
            'failed_coordinations': self.failed_coordinations,
            'success_rate': self.successful_coordinations / max(self.coordination_sessions, 1),
            'pattern_matches_found': self.pattern_matches_found,
            'learning_patterns_available': len(self.coordination_patterns),
            'agent_trends_tracked': len(self.agent_performance_trends),
            'coordination_precision': 'pattern_based' if self.coordination_patterns else 'analysis_based',
            'ancient_wisdom_status': 'active',
            'learning_capability': 'enabled'
        }

    async def learn_from_coordination_outcome(self, coordination_id: str, outcome_data: Dict[str, Any]):
        """Learn from coordination outcome to improve future decisions"""
        
        if self._db:
            # Store outcome for pattern learning
            learning_update = {
                'coordination_id': coordination_id,
                'actual_outcomes': outcome_data,
                'lessons_learned': self._extract_lessons_from_outcome(outcome_data),
                'pattern_updates_needed': self._identify_pattern_updates(outcome_data)
            }
            
            await self._db.store_coordination_outcome_learning(learning_update)
            
            # Update local patterns if needed
            await self._update_local_patterns(learning_update)

    def _extract_lessons_from_outcome(self, outcome_data: Dict[str, Any]) -> List[str]:
        """Extract lessons learned from coordination outcome"""
        
        lessons = []
        
        if outcome_data.get('coordination_successful', False):
            lessons.append("Coordination approach was effective for this situation type")
            if outcome_data.get('faster_than_expected', False):
                lessons.append("Response time exceeded expectations - approach can be used for urgent situations")
        else:
            lessons.append("Coordination approach needs refinement for this situation type")
            if outcome_data.get('agent_conflicts_occurred', False):
                lessons.append("Agent conflict resolution needed improvement")
        
        return lessons

    def _identify_pattern_updates(self, outcome_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify what pattern updates are needed based on outcome"""
        
        updates = []
        
        if outcome_data.get('coordination_successful', False):
            updates.append({
                'update_type': 'effectiveness_increase',
                'pattern_characteristics': outcome_data.get('situation_characteristics', {}),
                'effectiveness_adjustment': +0.1
            })
        else:
            updates.append({
                'update_type': 'effectiveness_decrease',
                'pattern_characteristics': outcome_data.get('situation_characteristics', {}),
                'effectiveness_adjustment': -0.1
            })
        
        return updates

    async def _update_local_patterns(self, learning_update: Dict[str, Any]):
        """Update local pattern database based on learning"""
        
        coordination_id = learning_update['coordination_id']
        pattern_updates = learning_update['pattern_updates_needed']
        
        for update in pattern_updates:
            # Find matching patterns and update their effectiveness scores
            for pattern_id, pattern_data in self.coordination_patterns.items():
                similarity = self._calculate_pattern_similarity(
                    update['pattern_characteristics'], 
                    pattern_data
                )
                
                if similarity > 0.8:  # High similarity
                    adjustment = update['effectiveness_adjustment']
                    pattern_data['effectiveness'] = max(0.0, min(1.0, 
                        pattern_data['effectiveness'] + adjustment
                    ))