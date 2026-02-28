#!/usr/bin/env python3
"""
Predictive Engine

Forecasts future metric state and recommends proactive action.
"Memory is at 72% now, but will hit 88% in 35 minutes. Act now gently
to prevent emergency intervention later."
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta, timezone
import statistics
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learned_thresholds import MetricPatternHistory
from .learned_thresholds import LearnedThresholds


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class MetricForecast:
    """Prediction of future metric value"""
    metric_name: str
    current_value: float
    
    # Predictions
    forecast_15min: float
    forecast_30min: float
    forecast_1hr: float
    
    # Confidence
    confidence: float  # 0.0-1.0
    forecast_method: str  # 'linear', 'pattern', 'hybrid'
    
    # Risk assessment
    will_cross_threshold: bool
    threshold_name: Optional[str]  # 'warning', 'critical', 'emergency'
    time_to_threshold: Optional[float]  # Minutes
    
    # Reasoning
    reasoning: str
    historical_pattern_matches: int


@dataclass
class ProactiveRecommendation:
    """Recommendation to act proactively"""
    action_type: str  # 'proactive'
    metric: str
    current_value: float
    predicted_value: float
    time_to_threshold: float
    threshold_name: str
    reasoning: str
    recommended_severity: float


class PredictiveEngine:
    """
    Predict future state and recommend proactive action.
    
    Uses:
    - Recent trend (linear extrapolation)
    - Historical patterns (similar situations before)
    - Time-of-day patterns (batch jobs, traffic patterns)
    """
    
    def __init__(
        self, 
        db_session: AsyncSession, 
        learned_thresholds: LearnedThresholds,
        system_id: str,
        agent_name: str = "meth_snail"
    ):
        self.db = db_session
        self.thresholds = learned_thresholds
        self.system_id = system_id
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{agent_name}.predictive_engine")
        
        # Minimum confidence threshold for proactive action
        self.min_confidence_for_proactive = 0.6
    
    async def forecast(
        self,
        current_metrics: Dict[str, float],
        recent_history: List[Dict[str, float]],
        context: Dict[str, Any]
    ) -> List[MetricForecast]:
        """
        Forecast where metrics will be in 15min, 30min, 1hr.
        
        Args:
            current_metrics: Current metric values
            recent_history: Last N measurements (ideally 10-15 minutes)
            context: Time of day, day of week, etc.
            
        Returns:
            List of forecasts for each metric
        """
        
        forecasts = []
        
        for metric_name, current_value in current_metrics.items():
            # Only forecast percentage/usage metrics
            if not (metric_name.endswith('_usage') or metric_name.endswith('_percent')):
                continue
            
            forecast = await self._forecast_metric(
                metric_name, current_value, recent_history, context
            )
            
            if forecast:
                forecasts.append(forecast)
        
        return forecasts
    
    async def _forecast_metric(
        self,
        metric_name: str,
        current_value: float,
        recent_history: List[Dict[str, float]],
        context: Dict[str, Any]
    ) -> Optional[MetricForecast]:
        """Forecast a single metric"""
        
        # Method 1: Linear extrapolation from recent trend
        linear_forecast = self._linear_extrapolation(
            metric_name, current_value, recent_history
        )
        
        if not linear_forecast:
            return None
        
        # Method 2: Pattern matching from historical data
        pattern_forecast = await self._pattern_based_forecast(
            metric_name, current_value, context
        )
        
        # Combine forecasts
        if pattern_forecast and pattern_forecast['confidence'] >= 0.5:
            # Hybrid: blend linear and pattern-based
            forecast_15min = (linear_forecast['15min'] * 0.4 + pattern_forecast['15min'] * 0.6)
            forecast_30min = (linear_forecast['30min'] * 0.4 + pattern_forecast['30min'] * 0.6)
            forecast_1hr = (linear_forecast['1hr'] * 0.4 + pattern_forecast['1hr'] * 0.6)
            confidence = 0.7
            method = 'hybrid'
            reasoning = f"Combined linear trend and {pattern_forecast['matches']} historical pattern matches"
            pattern_matches = pattern_forecast['matches']
        else:
            # Linear only
            forecast_15min = linear_forecast['15min']
            forecast_30min = linear_forecast['30min']
            forecast_1hr = linear_forecast['1hr']
            confidence = 0.4
            method = 'linear'
            reasoning = f"Linear extrapolation (growth rate: {linear_forecast['growth_rate']:.2f}%/min)"
            pattern_matches = 0
        
        # Check if will cross threshold
        will_cross, threshold_name, time_to_threshold = await self._check_threshold_crossing(
            metric_name, current_value, forecast_15min, forecast_30min, forecast_1hr
        )
        
        if will_cross:
            reasoning += f" → will cross {threshold_name} in {time_to_threshold:.0f}min"
        
        return MetricForecast(
            metric_name=metric_name,
            current_value=current_value,
            forecast_15min=forecast_15min,
            forecast_30min=forecast_30min,
            forecast_1hr=forecast_1hr,
            confidence=confidence,
            forecast_method=method,
            will_cross_threshold=will_cross,
            threshold_name=threshold_name,
            time_to_threshold=time_to_threshold,
            reasoning=reasoning,
            historical_pattern_matches=pattern_matches
        )
    
    def _linear_extrapolation(
        self,
        metric_name: str,
        current_value: float,
        recent_history: List[Dict[str, float]]
    ) -> Optional[Dict[str, float]]:
        """
        Simple linear trend extrapolation.
        
        Calculates growth rate from recent history and projects forward.
        """
        
        if len(recent_history) < 3:
            # Not enough history
            return None
        
        # Extract values for this metric
        values = []
        for h in recent_history:
            if metric_name in h:
                values.append(h[metric_name])
        
        if len(values) < 3:
            return None
        
        values.append(current_value)
        
        # Calculate growth rate (% per minute)
        # Assuming measurements are roughly 1 minute apart
        growth_rates = []
        for i in range(1, len(values)):
            if values[i-1] > 0:
                rate = (values[i] - values[i-1]) / values[i-1] * 100
                growth_rates.append(rate)
        
        if not growth_rates:
            return None
        
        # Use weighted average of absolute deltas (recent weighted more)
        # Convert percentage growth rates back to absolute change per minute
        absolute_rates = []
        for i in range(1, len(values)):
            absolute_rates.append(values[i] - values[i-1])  # Absolute change per interval
        
        if not absolute_rates:
            return None
        
        weights = [i + 1 for i in range(len(absolute_rates))]  # 1, 2, 3, 4...
        weighted_sum = sum(r * w for r, w in zip(absolute_rates, weights))
        weight_total = sum(weights)
        avg_change_per_min = weighted_sum / weight_total if weight_total > 0 else 0.0
        
        # Linear extrapolation (additive, not compound)
        forecast_15min = current_value + (avg_change_per_min * 15)
        forecast_30min = current_value + (avg_change_per_min * 30)
        forecast_1hr = current_value + (avg_change_per_min * 60)
        
        # Cap at 0-100% for percentage metrics
        return {
            '15min': min(100.0, max(0.0, forecast_15min)),
            '30min': min(100.0, max(0.0, forecast_30min)),
            '1hr': min(100.0, max(0.0, forecast_1hr)),
            'growth_rate': avg_change_per_min  # Now in absolute units per minute
        }
    
    async def _pattern_based_forecast(
        self,
        metric_name: str,
        current_value: float,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, float]]:
        """
        Find similar historical patterns and forecast based on what happened then.
        
        "Last Tuesday at 2pm, memory was at 72% and hit 88% in 40 minutes.
        Today is Tuesday at 2pm and memory is at 71%. Predict similar trajectory."
        """
        
        # Query for similar patterns
        similar_patterns = await self._query_similar_patterns(
            metric_name, current_value, context
        )
        
        if not similar_patterns or len(similar_patterns) < 3:
            return None
        
        # Average the outcomes from similar patterns
        forecasts_15min = [p.value_15min_later for p in similar_patterns if p.value_15min_later is not None]
        forecasts_30min = [p.value_30min_later for p in similar_patterns if p.value_30min_later is not None]
        forecasts_1hr = [p.value_1hr_later for p in similar_patterns if p.value_1hr_later is not None]
        
        if not forecasts_15min:
            return None
        
        # Calculate confidence based on consistency
        variance_15min = statistics.stdev(forecasts_15min) if len(forecasts_15min) > 1 else 0
        confidence = max(0.3, 1.0 - (variance_15min / 100.0))  # Lower variance = higher confidence
        
        return {
            '15min': statistics.mean(forecasts_15min),
            '30min': statistics.mean(forecasts_30min) if forecasts_30min else statistics.mean(forecasts_15min),
            '1hr': statistics.mean(forecasts_1hr) if forecasts_1hr else statistics.mean(forecasts_15min),
            'confidence': confidence,
            'matches': len(similar_patterns)
        }
    
    async def _query_similar_patterns(
        self,
        metric_name: str,
        current_value: float,
        context: Dict[str, Any]
    ) -> List[MetricPatternHistory]:
        """
        Query database for similar historical patterns.
        
        Similar means:
        - Same metric
        - Similar starting value (±5%)
        - Similar time of day (±2 hours)
        - Similar day of week
        """
        
        cutoff_date = utc_now().replace(tzinfo=None) - timedelta(days=60)
        
        # Build filters
        filters = [
            MetricPatternHistory.system_id == self.system_id,
            MetricPatternHistory.metric_name == metric_name,
            MetricPatternHistory.starting_value.between(current_value - 5, current_value + 5),
            MetricPatternHistory.starting_timestamp >= cutoff_date
        ]
        
        # Time of day filter (if provided) — handles midnight wraparound
        if 'time_of_day' in context:
            hour = context['time_of_day']
            low = (hour - 2) % 24
            high = (hour + 2) % 24
            if low <= high:
                filters.append(
                    func.extract('hour', MetricPatternHistory.starting_timestamp).between(low, high)
                )
            else:
                # Wraps midnight: e.g. hour=1 → low=23, high=3
                from sqlalchemy import or_
                filters.append(
                    or_(
                        func.extract('hour', MetricPatternHistory.starting_timestamp) >= low,
                        func.extract('hour', MetricPatternHistory.starting_timestamp) <= high
                    )
                )
        
        result = await self.db.execute(
            select(MetricPatternHistory).where(
                and_(*filters)
            ).order_by(MetricPatternHistory.starting_timestamp.desc()).limit(20)
        )
        
        return result.scalars().all()
    
    async def _check_threshold_crossing(
        self,
        metric_name: str,
        current_value: float,
        forecast_15min: float,
        forecast_30min: float,
        forecast_1hr: float
    ) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Check if metric will cross a learned threshold.
        
        Returns: (will_cross, threshold_name, time_to_threshold)
        """
        
        # Get learned thresholds for this metric
        warning = await self.thresholds.get_threshold(metric_name, 'warning')
        critical = await self.thresholds.get_threshold(metric_name, 'critical')
        emergency = await self.thresholds.get_threshold(metric_name, 'emergency')
        
        # Check each forecast horizon
        if forecast_15min >= emergency:
            return True, 'emergency', 15.0
        elif forecast_30min >= emergency:
            return True, 'emergency', 30.0
        elif forecast_1hr >= emergency:
            return True, 'emergency', 60.0
        elif forecast_15min >= critical:
            return True, 'critical', 15.0
        elif forecast_30min >= critical:
            return True, 'critical', 30.0
        elif forecast_1hr >= critical:
            return True, 'critical', 60.0
        elif forecast_15min >= warning:
            return True, 'warning', 15.0
        elif forecast_30min >= warning:
            return True, 'warning', 30.0
        elif forecast_1hr >= warning:
            return True, 'warning', 60.0
        
        return False, None, None
    
    async def should_act_proactively(
        self,
        forecasts: List[MetricForecast]
    ) -> Optional[ProactiveRecommendation]:
        """
        Determine if we should act NOW to prevent future problem.
        
        Returns recommendation or None if no proactive action needed.
        """
        
        for forecast in forecasts:
            if not forecast.will_cross_threshold:
                continue
            
            # Only act proactively if confidence is high enough
            if forecast.confidence < self.min_confidence_for_proactive:
                self.logger.debug(
                    f"🔮 {forecast.metric_name} forecast shows threshold crossing but "
                    f"confidence too low ({forecast.confidence:.2f} < {self.min_confidence_for_proactive})"
                )
                continue
            
            # If will cross critical/emergency threshold in < 30 minutes, act now
            if forecast.threshold_name in ['critical', 'emergency'] and forecast.time_to_threshold < 30:
                
                # Calculate recommended severity (lower than if already critical)
                if forecast.time_to_threshold < 15:
                    recommended_severity = 0.7  # Urgent but not emergency
                else:
                    recommended_severity = 0.6  # Medium severity
                
                self.logger.info(
                    f"🔮 PROACTIVE RECOMMENDATION: {forecast.metric_name} at {forecast.current_value:.1f}% "
                    f"will hit {forecast.threshold_name} in {forecast.time_to_threshold:.0f}min "
                    f"(confidence: {forecast.confidence:.2f})"
                )
                
                return ProactiveRecommendation(
                    action_type='proactive',
                    metric=forecast.metric_name,
                    current_value=forecast.current_value,
                    predicted_value=getattr(forecast, f'forecast_{int(forecast.time_to_threshold)}min', forecast.forecast_30min),
                    time_to_threshold=forecast.time_to_threshold,
                    threshold_name=forecast.threshold_name,
                    reasoning=(
                        f"{forecast.metric_name} at {forecast.current_value:.1f}% now, "
                        f"will hit {forecast.threshold_name} threshold in {forecast.time_to_threshold:.0f} minutes "
                        f"({forecast.forecast_method} forecast, confidence: {forecast.confidence:.2f}). "
                        f"Acting now with gentle intervention to prevent emergency later."
                    ),
                    recommended_severity=recommended_severity
                )
            
            # If will cross warning threshold in < 60 minutes, consider proactive action
            elif forecast.threshold_name == 'warning' and forecast.time_to_threshold < 60:
                
                # Only act if confidence is very high for warning-level proactive action
                if forecast.confidence >= 0.75:
                    
                    self.logger.info(
                        f"🔮 PROACTIVE RECOMMENDATION: {forecast.metric_name} at {forecast.current_value:.1f}% "
                        f"will hit warning in {forecast.time_to_threshold:.0f}min "
                        f"(high confidence: {forecast.confidence:.2f})"
                    )
                    
                    return ProactiveRecommendation(
                        action_type='proactive',
                        metric=forecast.metric_name,
                        current_value=forecast.current_value,
                        predicted_value=forecast.forecast_1hr,
                        time_to_threshold=forecast.time_to_threshold,
                        threshold_name=forecast.threshold_name,
                        reasoning=(
                            f"{forecast.metric_name} at {forecast.current_value:.1f}% now, "
                            f"will hit warning threshold in {forecast.time_to_threshold:.0f} minutes "
                            f"({forecast.forecast_method} forecast, high confidence: {forecast.confidence:.2f}). "
                            f"Gentle proactive action recommended."
                        ),
                        recommended_severity=0.5  # Low-medium severity
                    )
        
        return None
    
    async def record_pattern(
        self,
        metric_name: str,
        starting_value: float,
        context: Dict[str, Any]
    ) -> str:
        """
        Start recording a pattern.
        
        Returns pattern_id to update later with future values.
        """
        
        # Create context fingerprint
        context_fingerprint = self._create_context_fingerprint(context)
        
        # Create pattern record
        pattern = MetricPatternHistory(
            system_id=self.system_id,
            metric_name=metric_name,
            starting_value=starting_value,
            starting_timestamp=utc_now().replace(tzinfo=None),
            context=context,
            context_fingerprint=context_fingerprint
        )
        
        self.db.add(pattern)
        await self.db.flush()
        
        return str(pattern.id)
    
    async def update_pattern(
        self,
        pattern_id: str,
        value_15min: Optional[float] = None,
        value_30min: Optional[float] = None,
        value_1hr: Optional[float] = None
    ):
        """Update a pattern record with future values"""
        
        result = await self.db.execute(
            select(MetricPatternHistory).where(
                MetricPatternHistory.id == int(pattern_id)
            )
        )
        pattern = result.scalar_one_or_none()
        
        if not pattern:
            self.logger.warning(f"Pattern {pattern_id} not found")
            return
        
        if value_15min is not None:
            pattern.value_15min_later = value_15min
        if value_30min is not None:
            pattern.value_30min_later = value_30min
        if value_1hr is not None:
            pattern.value_1hr_later = value_1hr
        
        await self.db.flush()
        
        self.logger.debug(
            f"📚 Updated pattern {pattern_id}: "
            f"{pattern.metric_name} {pattern.starting_value:.1f}% → "
            f"15min: {value_15min:.1f}%, 30min: {value_30min:.1f}%, 1hr: {value_1hr:.1f}%"
        )
    
    def _create_context_fingerprint(self, context: Dict[str, Any]) -> str:
        """Create fingerprint for context matching"""
        
        parts = []
        
        if 'time_of_day' in context:
            # Bin into 4-hour blocks
            hour = context['time_of_day']
            block = (hour // 4) * 4
            parts.append(f"hour:{block}")
        
        if 'day_of_week' in context:
            parts.append(f"dow:{context['day_of_week']}")
        
        if 'system_load' in context:
            load = context['system_load']
            if load < 0.3:
                parts.append("load:low")
            elif load < 0.7:
                parts.append("load:medium")
            else:
                parts.append("load:high")
        
        return "|".join(parts) if parts else "default"
    
    async def get_forecast_accuracy(self, metric_name: str) -> Dict[str, Any]:
        """
        Calculate forecast accuracy by comparing predictions to actual outcomes.
        """
        
        cutoff_date = utc_now().replace(tzinfo=None) - timedelta(days=30)
        
        result = await self.db.execute(
            select(MetricPatternHistory).where(
                and_(
                    MetricPatternHistory.system_id == self.system_id,
                    MetricPatternHistory.metric_name == metric_name,
                    MetricPatternHistory.starting_timestamp >= cutoff_date,
                    MetricPatternHistory.value_15min_later.isnot(None)
                )
            )
        )
        patterns = result.scalars().all()
        
        if not patterns:
            return {
                'metric_name': metric_name,
                'accuracy': 'no_data',
                'sample_size': 0
            }
        
        # Calculate average error (for patterns where we have actual outcomes)
        errors_15min = []
        for p in patterns:
            if p.value_15min_later is not None:
                # Simple linear prediction from starting value
                predicted = p.starting_value  # Placeholder - would use actual forecast
                actual = p.value_15min_later
                error = abs(predicted - actual)
                errors_15min.append(error)
        
        avg_error = statistics.mean(errors_15min) if errors_15min else 0.0
        
        return {
            'metric_name': metric_name,
            'avg_error_15min': avg_error,
            'sample_size': len(patterns),
            'accuracy': 'good' if avg_error < 5.0 else 'learning'
        }
