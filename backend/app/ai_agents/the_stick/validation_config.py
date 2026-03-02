"""
The Stick's Validation Configuration
Configurable thresholds with maturity progression

Validates:
1. Cross-agent learning interactions (original)
2. Terry's learned thresholds (integrated)
3. Terry's action effectiveness patterns (integrated)
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ValidationConfig:
    """Validation thresholds with maturity progression"""
    
    # === Cross-agent learning thresholds (original) ===
    min_effectiveness: float = 0.4
    min_similarity: float = 0.7
    min_success_rate: float = 0.5
    max_age_hours: int = 48
    
    # === Threshold learning validation (NEW) ===
    # OPUS 4.6: Validates Terry's learned threshold adjustments
    min_threshold_sample_size: int = 5       # Minimum data points before trusting a shift
    max_threshold_shift_magnitude: float = 0.15  # Flag shifts larger than 15% in one adjustment
    # e.g., 80% → 95% = 0.15 magnitude = exactly at limit
    # 80% → 96% = 0.16 magnitude = flagged as suspicious
    
    # === Action effectiveness validation (NEW) ===
    # OPUS 4.6: Validates Terry's action effectiveness scoring
    min_action_sample_size: int = 3          # Minimum outcomes before trusting a score
    max_action_score_volatility: float = 0.3  # Flag if score changes by >0.3 between evaluations
    min_action_consistency: float = 0.5       # Score vs raw success rate shouldn't diverge >0.5
    
    # === Mature thresholds (original + NEW) ===
    mature_min_effectiveness: float = 0.6
    mature_min_similarity: float = 0.7
    mature_min_success_rate: float = 0.7
    mature_max_age_hours: int = 24
    mature_min_threshold_sample_size: int = 10  # NEW: Require more data when mature
    mature_min_action_sample_size: int = 5      # NEW: Require more data when mature
    
    # Maturity tracking
    maturity_date: Optional[datetime] = None
    days_until_mature: int = 30
    
    def is_mature(self) -> bool:
        """Check if validation has reached maturity"""
        if not self.maturity_date:
            return False
        return datetime.now(timezone.utc) >= self.maturity_date
    
    def get_active_thresholds(self) -> Dict[str, Any]:
        """Get currently active thresholds based on maturity"""
        if self.is_mature():
            return {
                'min_effectiveness': self.mature_min_effectiveness,
                'min_similarity': self.mature_min_similarity,
                'min_success_rate': self.mature_min_success_rate,
                'max_age_hours': self.mature_max_age_hours,
                'min_threshold_sample_size': self.mature_min_threshold_sample_size,
                'max_threshold_shift_magnitude': self.max_threshold_shift_magnitude,
                'min_action_sample_size': self.mature_min_action_sample_size,
                'max_action_score_volatility': self.max_action_score_volatility,
                'min_action_consistency': self.min_action_consistency,
                'threshold_state': 'mature'
            }
        else:
            return {
                'min_effectiveness': self.min_effectiveness,
                'min_similarity': self.min_similarity,
                'min_success_rate': self.min_success_rate,
                'max_age_hours': self.max_age_hours,
                'min_threshold_sample_size': self.min_threshold_sample_size,
                'max_threshold_shift_magnitude': self.max_threshold_shift_magnitude,
                'min_action_sample_size': self.min_action_sample_size,
                'max_action_score_volatility': self.max_action_score_volatility,
                'min_action_consistency': self.min_action_consistency,
                'threshold_state': 'initial'
            }
    
    def set_maturity_date(self, start_date: Optional[datetime] = None):
        """Set maturity date from start date + days_until_mature"""
        start = start_date or datetime.now(timezone.utc)
        self.maturity_date = start + timedelta(days=self.days_until_mature)

# Global config instance
VALIDATION_CONFIG = ValidationConfig()
