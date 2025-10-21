# app/ai_agents/sir_hawkington/data_types.py
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class HawkingtonDecision:
    """Data structure for Hawkington decisions - NO IMPORTS NEEDED"""
    decision_id: str
    decision_type: str
    confidence: float
    reasoning: str
    metrics: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    system_impact: Optional[str] = None