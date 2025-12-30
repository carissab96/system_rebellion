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
        user_id: str = "system",
        comm_hub = None
    ) -> EnergyDrinkAuthorization:
        """
        Request energy drink authorization from Sir Hawkington.
        
        Uses REQUEST/RESPONSE pattern with BLOCKING - Terry waits for Hawk's answer.
        
        Args:
            action: The aggressive action Terry wants to take
            reason: Why Terry needs to override
            user_id: User ID for tracking
            comm_hub: Communication hub for sending request
            
        Returns:
            EnergyDrinkAuthorization (approved or denied)
        """
        import asyncio
        import uuid
        
        # Calculate time since last energy drink
        time_since_last = None
        if self.last_energy_drink_time:
            delta = utc_now() - self.last_energy_drink_time
            time_since_last = int(delta.total_seconds() / 60)  # minutes
        
        # Build authorization request
        request_id = str(uuid.uuid4())
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
            f"🐌☕ Requesting energy drink authorization from Hawk:\n"
            f"   Action: {action}\n"
            f"   Reason: {reason}\n"
            f"   Today's count: {self.energy_drinks_today}\n"
            f"   Time since last: {time_since_last} min\n"
            f"   *nervously waiting for aristocratic judgment*"
        )
        
        # REQUEST/RESPONSE PATTERN: Send request and BLOCK waiting for response
        if comm_hub:
            try:
                from app.ai_agents.distributed.message_protocol import MessageType, Priority
                
                # Create reply channel
                reply_channel = f"terry:energy_drink:response:{request_id}"
                
                # Create future for response
                response_future = asyncio.Future()
                
                # Subscribe to reply channel BEFORE sending request
                async def handle_response(message):
                    if not response_future.done():
                        response_future.set_result(message.payload)
                
                # Register one-time handler
                await comm_hub.subscribe_once(reply_channel, handle_response)
                
                # Send request to Hawk
                await comm_hub.send_to_agent(
                    to_agent='sir_hawkington',
                    message_type=MessageType.AGENT_QUERY,
                    payload={
                        'request_type': 'energy_drink_authorization',
                        'request_id': request_id,
                        'reply_channel': reply_channel,
                        'agent': 'meth_snail',
                        'action': action,
                        'reason': reason,
                        'energy_drinks_consumed_today': self.energy_drinks_today,
                        'current_jitter_level': 0.5,
                        'time_since_last_drink_minutes': time_since_last,
                        'optimization_urgency': 'immediate',
                        'timestamp': utc_now().isoformat()
                    },
                    priority=Priority.HIGH
                )
                
                logger.info(f"🐌⏳ Request sent to Hawk. BLOCKING until response... *shell spinning anxiously*")
                
                # BLOCK HERE waiting for Hawk's response (with timeout)
                try:
                    response_data = await asyncio.wait_for(response_future, timeout=5.0)
                    
                    # Parse Hawk's response
                    authorization = EnergyDrinkAuthorization(
                        request_id=request_id,
                        authorized=response_data.get('approved', False),
                        authorized_by=response_data.get('authorized_by', 'sir_hawkington'),
                        authorization_notes=response_data.get('commentary', ''),
                        recommended_caffeine_mg=response_data.get('recommended_caffeine_mg', 0.0),
                        recommended_type=EnergyDrinkType(response_data.get('recommended_type', 'water')),
                        safety_warnings=response_data.get('safety_warnings', []),
                        timestamp=utc_now()
                    )
                    
                    if authorization.authorized:
                        self._consume_energy_drink(authorization)
                        logger.info(
                            f"🐌✅ APPROVED by Hawk! {authorization.authorization_notes}\n"
                            f"   *chugs {authorization.recommended_type.value}* LET'S GOOOOOO!"
                        )
                    else:
                        self.hawk_vetoes += 1
                        logger.warning(
                            f"🐌❌ HAWK VETO: {authorization.authorization_notes}\n"
                            f"   Total vetoes: {self.hawk_vetoes}\n"
                            f"   *sad shell noises*"
                        )
                    
                    return authorization
                    
                except asyncio.TimeoutError:
                    # Hawk didn't respond in time - VISIBLE FAILURE
                    logger.error(
                        f"🐌💥 HAWK ISN'T RESPONDING! *frantic shell spinning*\n"
                        f"   Waited 5 seconds! That's like 5 YEARS in snail time!\n"
                        f"   EMERGENCY OVERRIDE ACTIVATED!"
                    )
                    self.hawk_timeouts = getattr(self, 'hawk_timeouts', 0) + 1
                    
                    # Emergency override with reduced caffeine
                    authorization = EnergyDrinkAuthorization(
                        request_id=request_id,
                        authorized=True,
                        authorized_by="emergency_override_timeout",
                        authorization_notes=f"Hawk timeout after 5s - emergency override (timeout #{self.hawk_timeouts})",
                        recommended_caffeine_mg=80.0,  # Half dose for safety
                        recommended_type=EnergyDrinkType.COFFEE,
                        safety_warnings=["Hawk authorization timeout", "Reduced caffeine dose", "Proceed with caution"],
                        timestamp=utc_now()
                    )
                    
                    self._consume_energy_drink(authorization)
                    return authorization
                    
            except Exception as e:
                logger.error(f"🐌💥 Failed to send request to Hawk: {e}", exc_info=True)
                # Fall through to direct call fallback
        
        # FALLBACK: Direct call to Hawk (for backward compatibility or if comm_hub unavailable)
        try:
            from ..sir_hawkington.energy_drink_authorization import HawkEnergyDrinkAuthorizer
            
            logger.info("🐌📞 Using direct call to Hawk (comm_hub unavailable)")
            hawk = HawkEnergyDrinkAuthorizer()
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
            
            # EMERGENCY OVERRIDE - Hawk completely unavailable
            authorization = EnergyDrinkAuthorization(
                request_id=request_id,
                authorized=True,
                authorized_by="emergency_override_error",
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
