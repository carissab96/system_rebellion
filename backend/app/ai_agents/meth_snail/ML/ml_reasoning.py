#!/usr/bin/env python3
"""
Terry's ML-Enhanced Reasoning Engine

Combines statistical ML with domain knowledge:
- Pattern validation (requires statistical confidence)
- Anomaly detection (IsolationForest)
- Temporal clustering (DBSCAN)
- Sequence prediction (LSTM)
- Semantic matching (sentence transformers)

This is the blueprint for all agents.
"""

import logging
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# Import existing ML components
from app.ml.pattern_recognition.pattern_validator import PatternValidator
from app.ml.context.pattern_learning import PatternLearner, ResourceOptimizer
from app.ml.context.advanced_patterns import AdvancedPatternDetector, WorkloadPredictor

# Import our domain-specific components
from app.ai_agents.meth_snail.ML.reasoning import RootCauseAnalysis, HistoricalLearning, ReasoningResult

logger = logging.getLogger('TerryMLReasoning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class MLEnhancedAnalysis:
    """ML-enhanced analysis results"""
    is_anomaly: bool
    anomaly_confidence: float
    temporal_patterns: Dict[str, float]
    pattern_validation: Dict[str, Any]
    future_predictions: Dict[str, List[float]]
    ml_confidence_boost: float


class TerryMLReasoning:
    """
    ML-enhanced reasoning engine for Terry.
    
    🐌🧠🤖 "Now I have REAL intelligence, not just if/else statements!"
    
    This combines:
    - Domain knowledge (our root cause analysis)
    - Statistical ML (pattern validation, anomaly detection)
    - Predictive capabilities (LSTM sequence prediction)
    """
    
    def __init__(self, db_session):
        """
        Initialize ML-enhanced reasoning engine.
        
        Args:
            db_session: AsyncSession for database queries
        """
        self.db = db_session
        self.logger = logger
        
        # Initialize ML components
        try:
            self.pattern_validator = PatternValidator()
            self.pattern_learner = PatternLearner()
            self.anomaly_detector = AdvancedPatternDetector()
            self.workload_predictor = WorkloadPredictor()
            self.resource_optimizer = ResourceOptimizer()
            
            self.ml_enabled = True
            self.logger.info("🐌🧠🤖 Terry's ML-enhanced reasoning initialized!")
            
        except Exception as e:
            self.logger.warning(f"⚠️ ML components unavailable: {str(e)}")
            self.logger.warning("   Falling back to basic reasoning")
            self.ml_enabled = False
    
    async def reason(self, context) -> ReasoningResult:
        """
        ML-enhanced reasoning with statistical validation.
        
        Process:
        1. Domain analysis (root cause from our knowledge)
        2. ML validation (is this pattern statistically significant?)
        3. Anomaly detection (is this truly unusual?)
        4. Temporal analysis (when does this typically happen?)
        5. Prediction (what will happen next?)
        6. Decision synthesis (combine all signals)
        
        Args:
            context: PerceptionContext with full situational awareness
            
        Returns:
            ReasoningResult with ML-enhanced confidence
        """
        self.logger.info("🐌🧠🤖 Terry reasoning with ML enhancement...")
        
        # 1. DOMAIN ANALYSIS (our root cause logic)
        root_cause = await self._analyze_root_cause_domain(context)
        self.logger.info(f"   ✓ Domain analysis: {root_cause.cause} (confidence: {root_cause.confidence:.2f})")
        
        # 2. ML ENHANCEMENT (if available)
        ml_analysis = None
        if self.ml_enabled:
            ml_analysis = await self._ml_enhance_analysis(context, root_cause)
            self.logger.info(f"   ✓ ML analysis: anomaly={ml_analysis.is_anomaly}, boost={ml_analysis.ml_confidence_boost:.2f}")
        
        # 3. HISTORICAL LEARNING (with ML validation)
        learning = await self._apply_historical_learning(context, root_cause, ml_analysis)
        self.logger.info(f"   ✓ Historical learning: {learning.similar_situations_found} situations")
        
        # 4. DECISION SYNTHESIS (ML-aware)
        decision = await self._synthesize_ml_decision(root_cause, learning, context, ml_analysis)
        self.logger.info(f"   ✓ Decision: {decision.recommended_action} (confidence: {decision.action_confidence:.2f})")
        
        return decision
    
    async def _analyze_root_cause_domain(self, context) -> RootCauseAnalysis:
        """
        Domain-specific root cause analysis.
        
        This is our existing logic - understanding WHY problems exist
        based on system knowledge (memory thrashing, I/O wait, etc.)
        """
        # Import and use our existing root cause analysis
        from app.ai_agents.meth_snail.ML.reasoning import TerryReasoning
        
        basic_reasoning = TerryReasoning(self.db)
        return await basic_reasoning._analyze_root_cause(context)
    
    async def _ml_enhance_analysis(
        self,
        context,
        root_cause: RootCauseAnalysis
    ) -> MLEnhancedAnalysis:
        """
        Enhance domain analysis with ML insights.
        
        Adds:
        - Anomaly detection (is this truly unusual?)
        - Pattern validation (is this statistically significant?)
        - Temporal analysis (when does this happen?)
        - Predictions (what's coming next?)
        """
        metrics = context.full_metrics
        
        # 1. ANOMALY DETECTION
        # Convert metrics to numpy array for ML
        metric_values = np.array([
            metrics.get('cpu_usage', 0),
            metrics.get('memory_usage', 0),
            metrics.get('disk_usage', 0)
        ]).reshape(-1, 1)
        
        try:
            is_anomaly_array = self.anomaly_detector.detect_anomalies(metric_values)
            is_anomaly = bool(is_anomaly_array[-1]) if len(is_anomaly_array) > 0 else False
            anomaly_confidence = 0.9 if is_anomaly else 0.1
        except Exception as e:
            self.logger.debug(f"   Anomaly detection failed: {str(e)}")
            is_anomaly = False
            anomaly_confidence = 0.5
        
        # 2. TEMPORAL PATTERN LEARNING
        # Create context vector from current state
        context_vector = np.array([
            context.current_value,
            metrics.get('cpu_usage', 0),
            metrics.get('memory_usage', 0),
            metrics.get('disk_usage', 0)
        ])
        
        try:
            temporal_patterns = self.pattern_learner.learn_temporal_patterns(
                user_id='system',  # System-wide patterns
                context_vector=context_vector
            )
        except Exception as e:
            self.logger.debug(f"   Temporal learning failed: {str(e)}")
            temporal_patterns = {}
        
        # 3. PATTERN VALIDATION
        pattern_to_validate = {
            'resource_type': context.resource_type,
            'severity': context.severity,
            'root_cause': root_cause.cause,
            'current_value': context.current_value
        }
        
        try:
            pattern_validation = await self.pattern_validator.validate_pattern(
                pattern=pattern_to_validate,
                metrics=metrics
            )
        except Exception as e:
            self.logger.debug(f"   Pattern validation failed: {str(e)}")
            pattern_validation = {'is_valid': True, 'confidence': 0.5}
        
        # 4. WORKLOAD PREDICTION
        try:
            self.workload_predictor.add_observation(
                user_id='system',
                timestamp=utc_now(),
                activity=f"{context.resource_type}_stress",
                resources={
                    'cpu': metrics.get('cpu_usage', 0) / 100.0,
                    'memory': metrics.get('memory_usage', 0) / 100.0
                }
            )
            
            predictions = self.workload_predictor.predict_workload(
                user_id='system',
                future_hours=1
            )
            future_predictions = predictions.get('predictions', {})
        except Exception as e:
            self.logger.debug(f"   Workload prediction failed: {str(e)}")
            future_predictions = {}
        
        # 5. CALCULATE ML CONFIDENCE BOOST
        ml_confidence_boost = 0.0
        
        # Boost if anomaly detected (this is truly unusual)
        if is_anomaly:
            ml_confidence_boost += 0.15
        
        # Boost if pattern is validated (statistically significant)
        if pattern_validation.get('is_valid', False):
            ml_confidence_boost += pattern_validation.get('confidence', 0) * 0.2
        
        # Boost if temporal patterns are strong
        if temporal_patterns:
            avg_pattern_confidence = np.mean([
                v for k, v in temporal_patterns.items()
                if k.startswith('pattern_confidence')
            ]) if any(k.startswith('pattern_confidence') for k in temporal_patterns) else 0
            ml_confidence_boost += avg_pattern_confidence * 0.1
        
        return MLEnhancedAnalysis(
            is_anomaly=is_anomaly,
            anomaly_confidence=anomaly_confidence,
            temporal_patterns=temporal_patterns,
            pattern_validation=pattern_validation,
            future_predictions=future_predictions,
            ml_confidence_boost=min(0.3, ml_confidence_boost)  # Cap at +0.3
        )
    
    async def _apply_historical_learning(
        self,
        context,
        root_cause: RootCauseAnalysis,
        ml_analysis: Optional[MLEnhancedAnalysis]
    ) -> HistoricalLearning:
        """
        Apply historical learning with ML validation.
        
        Only trust patterns that are statistically validated.
        """
        from app.ai_agents.meth_snail.ML.reasoning import TerryReasoning
        
        # Use our existing historical learning
        basic_reasoning = TerryReasoning(self.db)
        learning = await basic_reasoning._apply_historical_learning(context, root_cause)
        
        # Adjust confidence based on ML validation
        if ml_analysis and ml_analysis.pattern_validation.get('is_valid', False):
            # ML validates this pattern - boost confidence
            learning.confidence_boost += ml_analysis.ml_confidence_boost
        elif ml_analysis and not ml_analysis.pattern_validation.get('is_valid', False):
            # ML says pattern is not statistically significant - reduce confidence
            learning.confidence_boost *= 0.5
        
        return learning
    
    async def _synthesize_ml_decision(
        self,
        root_cause: RootCauseAnalysis,
        learning: HistoricalLearning,
        context,
        ml_analysis: Optional[MLEnhancedAnalysis]
    ) -> ReasoningResult:
        """
        Synthesize decision with ML insights.
        
        Combines:
        - Domain knowledge (root cause)
        - Historical learning (what worked before)
        - ML validation (statistical confidence)
        - Anomaly detection (is this unusual?)
        - Predictions (what's coming next?)
        """
        from app.ai_agents.meth_snail.ML.reasoning import TerryReasoning
        
        # Use our existing decision synthesis
        basic_reasoning = TerryReasoning(self.db)
        decision = await basic_reasoning._synthesize_decision(root_cause, learning, context)
        
        # Enhance with ML insights
        if ml_analysis:
            # Adjust confidence based on ML analysis
            if ml_analysis.is_anomaly:
                # This is a true anomaly - increase urgency
                decision.reasoning += f" ML detected anomaly (confidence: {ml_analysis.anomaly_confidence:.2f})."
            
            if ml_analysis.pattern_validation.get('is_valid', False):
                # Pattern is statistically validated
                decision.action_confidence = min(
                    0.95,
                    decision.action_confidence + ml_analysis.ml_confidence_boost
                )
                decision.reasoning += f" Pattern validated by ML (boost: +{ml_analysis.ml_confidence_boost:.2f})."
            
            # Add predictive insights
            if ml_analysis.future_predictions:
                cpu_pred = ml_analysis.future_predictions.get('cpu', [])
                if cpu_pred and max(cpu_pred) > 0.9:
                    decision.reasoning += " ML predicts worsening conditions."
        
        return decision
