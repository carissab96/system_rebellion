#!/usr/bin/env python3
"""
Terry's Reasoning Engine - Root Cause Analysis

Terry v2 doesn't just see "CPU is high" - he understands WHY:
- Memory thrashing (swap usage killing CPU)
- I/O wait (disk bottleneck)
- CPU-bound (pure computation)
- Network-bound (network activity causing CPU load)

Then combines root cause analysis with historical learning to make informed decisions.

ML-ENHANCED: Uses pattern validation, anomaly detection, and temporal clustering
for statistically validated decisions.
"""

import logging
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger('TerryReasoning')

# Import ML components (graceful fallback if unavailable)
try:
    from app.ml.pattern_recognition.pattern_validator import PatternValidator
    from app.ml.context.pattern_learning import PatternLearner
    from app.ml.context.advanced_patterns import AdvancedPatternDetector
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML components unavailable: {e}")
    ML_AVAILABLE = False

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class RootCauseAnalysis:
    """Result of root cause analysis"""
    cause: str  # 'cpu_bound', 'memory_thrashing', 'io_wait', 'network_bound', 'unknown'
    confidence: float  # 0.0 - 1.0
    evidence: Dict[str, Any]
    top_culprits: List[Dict[str, Any]] = field(default_factory=list)
    explanation: str = ""


@dataclass
class HistoricalLearning:
    """What Terry learned from similar past situations"""
    similar_situations_found: int
    match_level: Optional[int]  # 1, 2, or 3 (which fingerprint level matched)
    what_worked_before: List[str] = field(default_factory=list)
    what_failed_before: List[str] = field(default_factory=list)
    success_rates: Dict[str, float] = field(default_factory=dict)
    most_successful_action: Optional[str] = None
    confidence_boost: float = 0.0


@dataclass
class ReasoningResult:
    """Terry's complete analysis and decision"""
    
    # Root cause
    root_cause: str
    root_cause_confidence: float
    evidence: Dict[str, Any]
    top_culprits: List[Dict[str, Any]]
    
    # Historical learning
    similar_situations: int
    match_level: Optional[int]
    what_worked_before: List[str]
    what_failed_before: List[str]
    
    # Decision
    recommended_action: str
    action_confidence: float
    alternatives: List[Dict[str, str]]
    
    # Reasoning chain
    reasoning: str
    followed_vic20: bool
    override_reason: Optional[str] = None
    
    # Timestamp
    timestamp: str = field(default_factory=lambda: utc_now().isoformat())


class TerryReasoning:
    """
    Terry's reasoning engine - analyzing root causes and making decisions.
    
    🐌🧠 "Now I understand WHY things are broken, not just THAT they're broken!"
    """
    
    def __init__(self, db_session):
        """
        Initialize reasoning engine with ML enhancement.
        
        Args:
            db_session: AsyncSession for database queries
        """
        self.db = db_session
        self.logger = logger
        
        # Initialize ML components if available
        self.ml_enabled = ML_AVAILABLE
        if self.ml_enabled:
            try:
                self.pattern_validator = PatternValidator()
                self.pattern_learner = PatternLearner()
                self.anomaly_detector = AdvancedPatternDetector()
                self.logger.info("🐌🧠🤖 Terry's ML-enhanced reasoning initialized!")
            except Exception as e:
                self.logger.warning(f"ML initialization failed: {e}, falling back to basic reasoning")
                self.ml_enabled = False
        else:
            self.logger.info("🐌🧠 Terry's reasoning engine initialized (ML unavailable)")
    
    async def reason(self, context) -> ReasoningResult:
        """
        Analyze the situation and determine best action.
        
        ML-ENHANCED: Adds pattern validation, anomaly detection, and temporal clustering
        
        This is where Terry goes from reactive to intelligent:
        - Analyzes WHY the problem exists (root cause)
        - ML validates this is a real pattern (not noise)
        - Detects if this is an anomaly (truly unusual)
        - Learns from similar past situations
        - Synthesizes a decision based on evidence + history + ML validation
        
        Args:
            context: PerceptionContext with full situational awareness
            
        Returns:
            ReasoningResult with complete analysis and decision
        """
        self.logger.info("🐌🧠 Terry reasoning about the situation...")
        
        # 1. ROOT CAUSE ANALYSIS (domain knowledge)
        root_cause = await self._analyze_root_cause(context)
        self.logger.info(f"   ✓ Root cause: {root_cause.cause} (confidence: {root_cause.confidence:.2f})")
        
        # 2. ML VALIDATION (if available)
        ml_boost = 0.0
        is_anomaly = False
        
        if self.ml_enabled:
            # Validate this pattern is statistically significant
            pattern_validation = await self._validate_pattern_ml(context, root_cause)
            
            # Detect if this is an anomaly
            is_anomaly = await self._detect_anomaly_ml(context)
            
            if pattern_validation['is_valid']:
                ml_boost = pattern_validation['confidence'] * 0.2
                self.logger.info(f"   ✓ ML validated pattern (boost: +{ml_boost:.2f})")
            else:
                self.logger.info(f"   ⚠️ ML says pattern not statistically significant (samples: {pattern_validation.get('sample_count', 0)})")
            
            if is_anomaly:
                self.logger.info(f"   🚨 ML detected anomaly - this is truly unusual!")
        
        # 3. HISTORICAL LEARNING (with ML boost)
        learning = await self._apply_historical_learning(context, root_cause)
        learning.confidence_boost += ml_boost
        self.logger.info(f"   ✓ Found {learning.similar_situations_found} similar situations (match level: {learning.match_level})")
        
        # 4. DECISION SYNTHESIS (ML-aware)
        decision = await self._synthesize_decision(root_cause, learning, context)
        
        # Add ML insights to reasoning
        if self.ml_enabled and is_anomaly:
            decision.reasoning += " ML detected anomaly."
        
        self.logger.info(f"   ✓ Decision: {decision.recommended_action} (confidence: {decision.action_confidence:.2f})")
        
        return decision
    
    async def _validate_pattern_ml(self, context, root_cause) -> Dict[str, Any]:
        """
        Validate pattern using ML PatternValidator.
        
        Requires 85% confidence and 5+ samples before trusting pattern.
        """
        from app.ai_agents.meth_snail.ML.ml_helpers import validate_pattern_ml
        return await validate_pattern_ml(self.pattern_validator, context, root_cause)
    
    async def _detect_anomaly_ml(self, context) -> bool:
        """
        Detect if current metrics are anomalous using IsolationForest.
        """
        from app.ai_agents.meth_snail.ML.ml_helpers import detect_anomaly_ml
        return await detect_anomaly_ml(self.anomaly_detector, context)
    
    async def _analyze_root_cause(self, context) -> RootCauseAnalysis:
        """
        Determine WHY the resource is stressed.
        
        Not just "CPU is high" but "CPU is high BECAUSE of memory thrashing"
        
        Args:
            context: PerceptionContext with full metrics
            
        Returns:
            RootCauseAnalysis with cause, confidence, and evidence
        """
        metrics = context.full_metrics
        resource_type = context.resource_type
        
        if resource_type == 'cpu':
            return await self._analyze_cpu_stress(metrics, context)
        elif resource_type == 'memory':
            return await self._analyze_memory_stress(metrics, context)
        elif resource_type == 'disk':
            return await self._analyze_disk_stress(metrics, context)
        elif resource_type == 'network':
            return await self._analyze_network_stress(metrics, context)
        else:
            return RootCauseAnalysis(
                cause='unknown',
                confidence=0.0,
                evidence={},
                explanation=f"Unknown resource type: {resource_type}"
            )
    
    async def _analyze_cpu_stress(self, metrics: Dict[str, Any], context) -> RootCauseAnalysis:
        """
        Analyze CPU stress to determine root cause.
        
        Possibilities:
        - Memory thrashing (high swap usage)
        - I/O wait (high disk I/O)
        - Network-bound (high network activity)
        - CPU-bound (pure computation)
        """
        cpu_data = metrics.get('cpu', {})
        memory_data = metrics.get('memory', {})
        disk_data = metrics.get('disk', {})
        network_data = metrics.get('network', {})
        
        top_processes = cpu_data.get('top_processes', [])
        cpu_usage = context.current_value
        
        # Get key metrics
        memory_percent = memory_data.get('percent', 0)
        swap_percent = memory_data.get('swap_percent', 0)
        disk_read = disk_data.get('read_bytes', 0)
        disk_write = disk_data.get('write_bytes', 0)
        disk_io_total = disk_read + disk_write
        network_sent = network_data.get('bytes_sent', 0)
        network_recv = network_data.get('bytes_recv', 0)
        
        # CASE 1: Memory Thrashing
        # High swap + high memory = thrashing
        if swap_percent > 80 and memory_percent > 85:
            return RootCauseAnalysis(
                cause='memory_thrashing',
                confidence=0.95,
                evidence={
                    'swap_percent': swap_percent,
                    'memory_percent': memory_percent,
                    'cpu_usage': cpu_usage,
                    'indicator': 'High swap usage indicates memory thrashing'
                },
                top_culprits=top_processes[:3] if top_processes else [],
                explanation=(
                    f"CPU stress caused by memory thrashing. "
                    f"Swap at {swap_percent:.1f}%, memory at {memory_percent:.1f}%. "
                    f"System is swapping to disk, killing CPU performance."
                )
            )
        
        # CASE 2: I/O Wait
        # High disk I/O suggests CPU waiting on disk
        if disk_io_total > 500_000_000:  # > 500MB/s
            return RootCauseAnalysis(
                cause='io_wait',
                confidence=0.85,
                evidence={
                    'disk_io_total': disk_io_total,
                    'disk_read': disk_read,
                    'disk_write': disk_write,
                    'cpu_usage': cpu_usage,
                    'indicator': 'High disk I/O suggests CPU waiting on disk operations'
                },
                top_culprits=top_processes[:3] if top_processes else [],
                explanation=(
                    f"CPU stress caused by I/O wait. "
                    f"Disk I/O at {disk_io_total / 1_000_000:.1f} MB/s. "
                    f"CPU spending time waiting for disk operations."
                )
            )
        
        # CASE 3: Network-bound
        # High network activity with CPU stress
        network_total = network_sent + network_recv
        if network_total > 100_000_000:  # > 100MB
            return RootCauseAnalysis(
                cause='network_bound',
                confidence=0.75,
                evidence={
                    'network_total': network_total,
                    'network_sent': network_sent,
                    'network_recv': network_recv,
                    'cpu_usage': cpu_usage,
                    'indicator': 'High network activity correlates with CPU stress'
                },
                top_culprits=top_processes[:3] if top_processes else [],
                explanation=(
                    f"CPU stress related to network activity. "
                    f"Network traffic at {network_total / 1_000_000:.1f} MB. "
                    f"CPU handling network I/O."
                )
            )
        
        # CASE 4: CPU-bound (pure computation)
        # High CPU with no other obvious bottlenecks
        return RootCauseAnalysis(
            cause='cpu_bound',
            confidence=0.80,
            evidence={
                'cpu_usage': cpu_usage,
                'memory_percent': memory_percent,
                'swap_percent': swap_percent,
                'disk_io': disk_io_total,
                'indicator': 'High CPU without other bottlenecks suggests pure computation'
            },
            top_culprits=top_processes[:3] if top_processes else [],
            explanation=(
                f"CPU stress from pure computation. "
                f"CPU at {cpu_usage:.1f}% with no memory/disk/network bottlenecks. "
                f"Processes are CPU-intensive."
            )
        )
    
    async def _analyze_memory_stress(self, metrics: Dict[str, Any], context) -> RootCauseAnalysis:
        """Analyze memory stress root cause"""
        memory_data = metrics.get('memory', {})
        
        memory_percent = context.current_value
        swap_percent = memory_data.get('swap_percent', 0)
        
        if swap_percent > 50:
            return RootCauseAnalysis(
                cause='memory_leak',
                confidence=0.85,
                evidence={'memory_percent': memory_percent, 'swap_percent': swap_percent},
                explanation=f"Memory stress with {swap_percent:.1f}% swap usage suggests memory leak"
            )
        
        return RootCauseAnalysis(
            cause='memory_pressure',
            confidence=0.75,
            evidence={'memory_percent': memory_percent},
            explanation=f"High memory usage at {memory_percent:.1f}%"
        )
    
    async def _analyze_disk_stress(self, metrics: Dict[str, Any], context) -> RootCauseAnalysis:
        """Analyze disk stress root cause"""
        disk_data = metrics.get('disk', {})
        
        return RootCauseAnalysis(
            cause='disk_full',
            confidence=0.80,
            evidence={'disk_percent': context.current_value},
            explanation=f"Disk usage at {context.current_value:.1f}%"
        )
    
    async def _analyze_network_stress(self, metrics: Dict[str, Any], context) -> RootCauseAnalysis:
        """Analyze network stress root cause"""
        network_data = metrics.get('network', {})
        
        return RootCauseAnalysis(
            cause='network_congestion',
            confidence=0.75,
            evidence={'network_rate': context.current_value},
            explanation=f"High network activity"
        )
    
    async def _apply_historical_learning(
        self,
        context,
        root_cause: RootCauseAnalysis
    ) -> HistoricalLearning:
        """
        Learn from similar past situations.
        
        Query historical learning records to see what worked/failed before.
        """
        from app.ai_agents.meth_snail.ML.situation_fingerprint import SituationFingerprint, FingerprintMatcher
        
        # Generate fingerprints for this situation
        fingerprints = SituationFingerprint.generate(
            resource_type=context.resource_type,
            severity=context.severity,
            root_cause=root_cause.cause,
            full_metrics=context.full_metrics
        )
        
        # Query similar situations
        matcher = FingerprintMatcher(self.db)
        results = await matcher.find_similar_situations(fingerprints, agent_name='meth_snail')
        
        records = results['records']
        match_level = results['match_level']
        
        if not records:
            return HistoricalLearning(
                similar_situations_found=0,
                match_level=None
            )
        
        # Analyze what worked and what failed
        what_worked = []
        what_failed = []
        success_rates = {}
        
        for record in records:
            action = record['action']
            
            # Track success rates per action
            if action not in success_rates:
                success_rates[action] = {'successes': 0, 'failures': 0}
            
            if record['success']:
                success_rates[action]['successes'] += 1
                if action not in what_worked:
                    what_worked.append(action)
            else:
                success_rates[action]['failures'] += 1
                if action not in what_failed:
                    what_failed.append(action)
        
        # Calculate success rates
        action_rates = {}
        for action, counts in success_rates.items():
            total = counts['successes'] + counts['failures']
            action_rates[action] = counts['successes'] / total if total > 0 else 0.0
        
        # Find most successful action
        most_successful = None
        if action_rates:
            most_successful = max(action_rates.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence boost based on match level and data quantity
        confidence_boost = 0.0
        if match_level == 3 and len(records) >= 5:
            confidence_boost = 0.2  # Exact match with good data
        elif match_level == 2 and len(records) >= 3:
            confidence_boost = 0.1  # Medium match with some data
        elif match_level == 1:
            confidence_boost = 0.05  # Broad match
        
        return HistoricalLearning(
            similar_situations_found=len(records),
            match_level=match_level,
            what_worked_before=what_worked,
            what_failed_before=what_failed,
            success_rates=action_rates,
            most_successful_action=most_successful,
            confidence_boost=confidence_boost
        )
    
    async def _synthesize_decision(
        self,
        root_cause: RootCauseAnalysis,
        learning: HistoricalLearning,
        context
    ) -> ReasoningResult:
        """
        Synthesize final decision from root cause + historical learning.
        
        Combines:
        - Root cause analysis (what's wrong)
        - Historical learning (what worked before)
        - VIC-20's recommendation (coordinator's view)
        - Terry's personality (meth-fueled bias toward cache clears)
        """
        vic20_action = context.vic20_recommendation.get('action', 'unknown')
        vic20_confidence = context.vic20_recommendation.get('confidence', 0.5)
        
        # Start with historical learning if available
        if learning.most_successful_action and learning.confidence_boost > 0:
            recommended_action = learning.most_successful_action
            confidence = learning.success_rates.get(recommended_action, 0.5)
            confidence += learning.confidence_boost
            followed_vic20 = (recommended_action == vic20_action)
            
            reasoning = (
                f"Based on {learning.similar_situations_found} similar situations "
                f"(match level {learning.match_level}), {recommended_action} has "
                f"{confidence:.0%} success rate. Root cause: {root_cause.cause}. "
                f"{root_cause.explanation}"
            )
            
            override_reason = None if followed_vic20 else (
                f"Historical data shows {recommended_action} works better than "
                f"VIC-20's {vic20_action} for this situation"
            )
        else:
            # No historical data - follow VIC-20 but with low confidence
            recommended_action = vic20_action
            confidence = vic20_confidence * 0.7  # Reduced confidence without history
            followed_vic20 = True
            
            reasoning = (
                f"No historical data for this situation. Following VIC-20's "
                f"recommendation: {vic20_action}. Root cause: {root_cause.cause}. "
                f"{root_cause.explanation}"
            )
            
            override_reason = None
        
        # Build alternatives list
        alternatives = []
        if learning.what_worked_before:
            for action in learning.what_worked_before:
                if action != recommended_action:
                    rate = learning.success_rates.get(action, 0.0)
                    alternatives.append({
                        'action': action,
                        'success_rate': f"{rate:.0%}",
                        'reason': f"Worked in {learning.similar_situations_found} similar situations"
                    })
        
        # Add VIC-20's recommendation as alternative if we're overriding
        if not followed_vic20:
            alternatives.append({
                'action': vic20_action,
                'success_rate': f"{vic20_confidence:.0%}",
                'reason': "VIC-20's recommendation"
            })
        
        return ReasoningResult(
            root_cause=root_cause.cause,
            root_cause_confidence=root_cause.confidence,
            evidence=root_cause.evidence,
            top_culprits=root_cause.top_culprits,
            similar_situations=learning.similar_situations_found,
            match_level=learning.match_level,
            what_worked_before=learning.what_worked_before,
            what_failed_before=learning.what_failed_before,
            recommended_action=recommended_action,
            action_confidence=min(0.95, confidence),  # Cap at 0.95
            alternatives=alternatives,
            reasoning=reasoning,
            followed_vic20=followed_vic20,
            override_reason=override_reason,
            timestamp=utc_now().isoformat()
        )
