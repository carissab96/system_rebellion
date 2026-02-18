"""
The Stick's Validation Configuration
Configurable thresholds with maturity progression
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ValidationConfig:
    """Validation thresholds with maturity progression"""
    
    # Initial thresholds (cold start - permissive)
    min_effectiveness: float = 0.4
    min_similarity: float = 0.7
    min_success_rate: float = 0.5
    max_age_hours: int = 48
    
    # Mature thresholds (after 30 days - tightened)
    mature_min_effectiveness: float = 0.6
    mature_min_similarity: float = 0.7  # unchanged
    mature_min_success_rate: float = 0.7
    mature_max_age_hours: int = 24
    
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
                'threshold_state': 'mature'
            }
        else:
            return {
                'min_effectiveness': self.min_effectiveness,
                'min_similarity': self.min_similarity,
                'min_success_rate': self.min_success_rate,
                'max_age_hours': self.max_age_hours,
                'threshold_state': 'initial'
            }
    
    def set_maturity_date(self, start_date: Optional[datetime] = None):
        """Set maturity date from start date + days_until_mature"""
        start = start_date or datetime.now(timezone.utc)
        self.maturity_date = start + timedelta(days=self.days_until_mature)

# Global config instance
VALIDATION_CONFIG = ValidationConfig()
