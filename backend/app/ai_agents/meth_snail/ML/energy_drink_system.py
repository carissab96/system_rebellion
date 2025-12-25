#!/usr/bin/env python3
"""
Terry's Energy Drink Authorization System

When Terry wants to override VIC-20 with aggressive actions, he needs energy drinks.
Sir Hawkington monitors Terry's caffeine intake and can VETO if Terry's had too many.

This is a PERSONALITY BEHAVIOR - it makes Terry TERRY, not just an optimization algorithm.
"""

import logging
from typing import Optional
from datetime import datetime, timezone

from app.ai_agents.meth_snail.data_types import (
    EnergyDrinkRequest,
    EnergyDrinkAuthorization,
    EnergyDrinkType,
)

logger = logging.getLogger('TerryEnergyDrinks')

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(timezone.utc)


class EnergyDrinkSystem:
    """
    Manages Terry's energy drink consumption and authorization.
    
    🐌☕ "I need caffeine to override VIC-20!"
    """
    
    def __init__(self):
        self.energy_drinks_today = 0
        self.last_energy_drink_time: Optional[datetime] = None
        self.total_energy_drinks = 0
        self.hawk_vetoes = 0
        
        logger.info("🐌☕ Energy drink system initialized")
    
    async def request_authorization(
        self,
        action: str,
        reason: str,
        user_id: str = "system"
    ) -> EnergyDrinkAuthorization:
        """
        Request energy drink authorization from Sir Hawkington.
        
        Args:
            action: The aggressive action Terry wants to take
            reason: Why Terry needs to override
            user_id: User ID for tracking
            
        Returns:
            EnergyDrinkAuthorization (approved or denied)
        """
        # Calculate time since last energy drink
        time_since_last = None
        if self.last_energy_drink_time:
            delta = utc_now() - self.last_energy_drink_time
            time_since_last = int(delta.total_seconds() / 60)  # minutes
        
        # Build authorization request
        request = EnergyDrinkRequest(
            user_id=user_id,
            energy_drink_type=EnergyDrinkType.ENERGY_DRINK,
            caffeine_mg=160.0,  # Standard energy drink
            consumption_reason=reason,
            current_jitter_level=0.5,  # TODO: Track actual jitter
            energy_drinks_consumed_today=self.energy_drinks_today,
            time_since_last_drink_minutes=time_since_last,
            optimization_urgency="immediate",
            timestamp=utc_now()
        )
        
        logger.info(
            f"🐌☕ Requesting energy drink authorization:\n"
            f"   Action: {action}\n"
            f"   Reason: {reason}\n"
            f"   Today's count: {self.energy_drinks_today}\n"
            f"   Time since last: {time_since_last} min"
        )
        
        # Call Sir Hawkington's authorization system
        try:
            from ..sir_hawkington.triage_engine import SirHawkingtonTriageEngine
            
            hawk = SirHawkingtonTriageEngine()
            authorization = await hawk.authorize_energy_drink(request)
            
            if authorization.authorized:
                self._consume_energy_drink(authorization)
                logger.info(
                    f"🐌✅ AUTHORIZED by {authorization.authorized_by}! "
                    f"*chugs {authorization.recommended_type.value if authorization.recommended_type else 'energy drink'}*"
                )
            else:
                self.hawk_vetoes += 1
                logger.warning(
                    f"🐌❌ HAWK VETO: {authorization.authorization_notes}\n"
                    f"   Total vetoes: {self.hawk_vetoes}"
                )
            
            return authorization
            
        except Exception as e:
            logger.error(f"🐌💥 Failed to get Hawk authorization: {e}")
            
            # EMERGENCY OVERRIDE - Hawk unavailable
            # Terry can proceed but with caution
            authorization = EnergyDrinkAuthorization(
                request_id=str(id(request)),
                authorized=True,
                authorized_by="emergency_override",
                authorization_notes=f"Hawk unavailable - emergency override granted (Error: {str(e)})",
                recommended_caffeine_mg=80.0,  # Half dose for safety
                recommended_type=EnergyDrinkType.COFFEE,
                safety_warnings=["Hawk authorization system unavailable", "Proceed with caution"],
                timestamp=utc_now()
            )
            
            self._consume_energy_drink(authorization)
            
            return authorization
    
    def _consume_energy_drink(self, authorization: EnergyDrinkAuthorization) -> None:
        """
        Record energy drink consumption.
        
        Args:
            authorization: The approved authorization
        """
        self.energy_drinks_today += 1
        self.total_energy_drinks += 1
        self.last_energy_drink_time = utc_now()
        
        logger.info(
            f"🐌☕💨 Energy drink #{self.energy_drinks_today} consumed! "
            f"(Total: {self.total_energy_drinks})"
        )
    
    def get_stats(self) -> dict:
        """Get energy drink consumption stats"""
        return {
            'energy_drinks_today': self.energy_drinks_today,
            'total_energy_drinks': self.total_energy_drinks,
            'hawk_vetoes': self.hawk_vetoes,
            'last_drink_time': self.last_energy_drink_time.isoformat() if self.last_energy_drink_time else None
        }
    
    def reset_daily_count(self) -> None:
        """Reset daily energy drink count (called at midnight)"""
        logger.info(f"🐌🌅 New day! Resetting energy drink count (was {self.energy_drinks_today})")
        self.energy_drinks_today = 0
