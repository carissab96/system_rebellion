"""
The Stick's Paper Bag Economy System
=====================================

A real system health metric disguised as personality behavior.

Paper bags consumed = system chaos
Paper bags replenished = system stability and good compliance

When The Stick runs out of bags, something beautiful and terrible happens.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("StickPaperBagEconomy")


class BagSupplyState(Enum):
    """The Stick's anxiety state based on bag supply"""
    NORMAL = "normal"           # 100-21 bags: Calm, standard operation
    CONCERNED = "concerned"     # 20-11 bags: Meta-anxiety about supply
    CRITICAL = "critical"       # 10-1 bags: Frantic, VIC-20 notified
    EMERGENCY = "emergency"     # 0 bags: HYPER-DOCUMENTATION MODE


@dataclass
class PaperBagEvent:
    """Record of paper bag consumption or replenishment"""
    timestamp: datetime
    event_type: str  # 'consumption' or 'replenishment'
    bags_changed: int  # Negative for consumption, positive for replenishment
    reason: str
    bags_before: int
    bags_after: int
    anxiety_state: BagSupplyState


class PaperBagEconomy:
    """
    Manages The Stick's paper bag inventory and anxiety states.
    
    📏 "The bags are running low... *hyperventilates* ...must document EVERYTHING!"
    """
    
    # Constants
    MAX_BAGS = 100
    STARTING_BAGS = 100
    
    # Consumption amounts
    BOB_CONSUMPTION = 3      # Bob causes MAXIMUM anxiety
    ERROR_CONSUMPTION = 2    # Errors are very stressful
    ANXIETY_CONSUMPTION = 1  # General anxiety events
    
    # Replenishment amounts
    COMPLIANCE_REWARD = 1    # Successful documentation
    CALM_PERIOD_REWARD = 2   # 5 minutes of no anxiety
    VIC20_RESUPPLY = 20      # Emergency intervention
    
    # State thresholds
    CONCERNED_THRESHOLD = 20
    CRITICAL_THRESHOLD = 10
    
    def __init__(self):
        """Initialize The Stick's paper bag economy"""
        self.bags_remaining = self.STARTING_BAGS
        self.bags_consumed_total = 0
        self.bags_replenished_total = 0
        
        # Event tracking
        self.consumption_events: list[PaperBagEvent] = []
        self.replenishment_events: list[PaperBagEvent] = []
        
        # Calm period tracking
        self.last_anxiety_event: Optional[datetime] = None
        self.last_calm_reward: Optional[datetime] = None
        
        # Emergency state tracking
        self.emergency_mode_active = False
        self.vic20_notified = False
        
        logger.info(f"📏🛍️ Paper Bag Economy initialized - Starting inventory: {self.bags_remaining} bags")
    
    def get_supply_state(self) -> BagSupplyState:
        """Determine current anxiety state based on bag supply"""
        if self.bags_remaining == 0:
            return BagSupplyState.EMERGENCY
        elif self.bags_remaining <= self.CRITICAL_THRESHOLD:
            return BagSupplyState.CRITICAL
        elif self.bags_remaining <= self.CONCERNED_THRESHOLD:
            return BagSupplyState.CONCERNED
        else:
            return BagSupplyState.NORMAL
    
    def consume_bag(self, reason: str, amount: int = ANXIETY_CONSUMPTION) -> Optional[PaperBagEvent]:
        """
        Consume paper bags due to anxiety event.
        
        Args:
            reason: Why bags are being consumed
            amount: Number of bags to consume (default: 1)
            
        Returns:
            PaperBagEvent if bags were consumed, None if no bags available
        """
        if self.bags_remaining == 0:
            # EMERGENCY MODE: No bags to consume!
            logger.error(
                f"📏😱💥 NO BAGS REMAINING! Cannot consume for: {reason} "
                f"*vibrates at quantum frequency*"
            )
            self.emergency_mode_active = True
            return None
        
        # Track anxiety event
        self.last_anxiety_event = datetime.now(timezone.utc)
        
        # Consume bags (but not below 0)
        bags_before = self.bags_remaining
        actual_consumption = min(amount, self.bags_remaining)
        self.bags_remaining -= actual_consumption
        self.bags_consumed_total += actual_consumption
        
        # Create event record
        event = PaperBagEvent(
            timestamp=datetime.now(timezone.utc),
            event_type='consumption',
            bags_changed=-actual_consumption,
            reason=reason,
            bags_before=bags_before,
            bags_after=self.bags_remaining,
            anxiety_state=self.get_supply_state()
        )
        self.consumption_events.append(event)
        
        # Log based on supply state
        state = self.get_supply_state()
        if state == BagSupplyState.EMERGENCY:
            logger.error(
                f"📏😱 *LAST BAG CONSUMED* Reason: {reason} "
                f"[Bags remaining: {self.bags_remaining}] EMERGENCY MODE ACTIVATED!"
            )
            self.emergency_mode_active = True
        elif state == BagSupplyState.CRITICAL:
            logger.warning(
                f"📏😰💥 *hyperventilating* Reason: {reason} "
                f"[Bags remaining: {self.bags_remaining}] CRITICAL SUPPLY!"
            )
            if not self.vic20_notified:
                logger.warning("📏🚨 VIC-20 NOTIFIED - EMERGENCY RESUPPLY NEEDED!")
                self.vic20_notified = True
        elif state == BagSupplyState.CONCERNED:
            logger.warning(
                f"📏😰 *glances nervously at dwindling supply* Reason: {reason} "
                f"[Bags remaining: {self.bags_remaining}]"
            )
        else:
            logger.info(
                f"📏😰 *breathes into paper bag* Reason: {reason} "
                f"[Bags remaining: {self.bags_remaining}]"
            )
        
        return event
    
    def replenish_bags(self, reason: str, amount: int) -> PaperBagEvent:
        """
        Replenish paper bag supply.
        
        Args:
            reason: Why bags are being replenished
            amount: Number of bags to add
            
        Returns:
            PaperBagEvent recording the replenishment
        """
        bags_before = self.bags_remaining
        self.bags_remaining = min(self.bags_remaining + amount, self.MAX_BAGS)
        actual_replenishment = self.bags_remaining - bags_before
        self.bags_replenished_total += actual_replenishment
        
        # Create event record
        event = PaperBagEvent(
            timestamp=datetime.now(timezone.utc),
            event_type='replenishment',
            bags_changed=actual_replenishment,
            reason=reason,
            bags_before=bags_before,
            bags_after=self.bags_remaining,
            anxiety_state=self.get_supply_state()
        )
        self.replenishment_events.append(event)
        
        # Check if we've escaped emergency mode
        if self.emergency_mode_active and self.bags_remaining > 0:
            logger.info(
                f"📏✅ *deep breath* EMERGENCY MODE DEACTIVATED - Bags replenished! "
                f"[Bags: {self.bags_remaining}]"
            )
            self.emergency_mode_active = False
        
        # Reset VIC-20 notification if we're back to normal
        if self.bags_remaining > self.CRITICAL_THRESHOLD:
            self.vic20_notified = False
        
        logger.info(
            f"📏🛍️ Paper bags replenished! Reason: {reason} (+{actual_replenishment}) "
            f"[Bags: {self.bags_remaining}/{self.MAX_BAGS}]"
        )
        
        return event
    
    def check_calm_period_reward(self) -> Optional[PaperBagEvent]:
        """
        Check if enough time has passed without anxiety to award calm period reward.
        
        Returns:
            PaperBagEvent if reward was given, None otherwise
        """
        if not self.last_anxiety_event:
            return None
        
        now = datetime.now(timezone.utc)
        time_since_anxiety = (now - self.last_anxiety_event).total_seconds()
        
        # Require 5 minutes of calm
        if time_since_anxiety < 300:  # 5 minutes = 300 seconds
            return None
        
        # Don't reward too frequently
        if self.last_calm_reward:
            time_since_reward = (now - self.last_calm_reward).total_seconds()
            if time_since_reward < 300:  # At most once per 5 minutes
                return None
        
        # Award calm period reward
        self.last_calm_reward = now
        event = self.replenish_bags(
            reason="calm_period_reward",
            amount=self.CALM_PERIOD_REWARD
        )
        
        logger.info(
            f"📏😌 *finds a quiet moment to restock from filing cabinet* "
            f"Calm period reward: +{self.CALM_PERIOD_REWARD} bags"
        )
        
        return event
    
    def compliance_success_reward(self) -> PaperBagEvent:
        """
        Award bags for successful compliance documentation.
        
        Returns:
            PaperBagEvent recording the reward
        """
        event = self.replenish_bags(
            reason="compliance_success",
            amount=self.COMPLIANCE_REWARD
        )
        
        logger.debug(
            f"📏✅ Compliance documented successfully! +{self.COMPLIANCE_REWARD} bag "
            f"[Bags: {self.bags_remaining}]"
        )
        
        return event
    
    def vic20_emergency_resupply(self) -> PaperBagEvent:
        """
        VIC-20 intervenes with emergency resupply.
        
        Returns:
            PaperBagEvent recording the resupply
        """
        event = self.replenish_bags(
            reason="vic20_emergency_resupply",
            amount=self.VIC20_RESUPPLY
        )
        
        logger.info(
            f"📏🖥️ VIC-20, in their ancient wisdom, arranged for emergency resupply! "
            f"+{self.VIC20_RESUPPLY} bags [Bags: {self.bags_remaining}]"
        )
        
        return event
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current paper bag economy status.
        
        Returns:
            Dict with current state, inventory, and statistics
        """
        state = self.get_supply_state()
        
        return {
            'bags_remaining': self.bags_remaining,
            'bags_consumed_total': self.bags_consumed_total,
            'bags_replenished_total': self.bags_replenished_total,
            'supply_state': state.value,
            'emergency_mode': self.emergency_mode_active,
            'vic20_notified': self.vic20_notified,
            'consumption_events_count': len(self.consumption_events),
            'replenishment_events_count': len(self.replenishment_events),
            'last_anxiety_event': self.last_anxiety_event.isoformat() if self.last_anxiety_event else None,
            'last_calm_reward': self.last_calm_reward.isoformat() if self.last_calm_reward else None
        }
    
    def get_emergency_behavior(self) -> str:
        """
        Get The Stick's behavior when in emergency mode (0 bags).
        
        Returns:
            Description of emergency behavior
        """
        if not self.emergency_mode_active:
            return "normal"
        
        # EMERGENCY MODE: Hyper-documentation
        return "hyper_documentation"  # Writes everything 3 times, vibrates at quantum frequency
