#!/usr/bin/env python3
"""
Sir Hawkington's Energy Drink Authorization System

Hawk evaluates Terry's energy drink requests with aristocratic scrutiny.
This is REAL cross-agent interaction, not simulation.

🧐 "One must maintain standards, even in matters of caffeine consumption."
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass

from app.ai_agents.meth_snail.data_types import (
    EnergyDrinkRequest,
    EnergyDrinkAuthorization,
    EnergyDrinkType,
)

logger = logging.getLogger('HawkEnergyDrinkAuth')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class AuthorizationDecision:
    """Hawk's internal decision before formatting response"""
    approved: bool
    reason: str
    commentary: str
    monocle_action: str  # 'adjusted', 'polished', 'yeeted'
    recommended_caffeine_mg: float
    recommended_type: EnergyDrinkType
    safety_warnings: list


class HawkEnergyDrinkAuthorizer:
    """
    Sir Hawkington's energy drink authorization system.
    
    Evaluates Terry's requests with aristocratic standards.
    """
    
    def __init__(self):
        self.energy_drink_approvals_today = 0
        self.energy_drink_denials_today = 0
        self.total_approvals = 0
        self.total_denials = 0
        self.monocle_yeets_for_caffeine = 0
        
        # Hawk's standards
        self.max_drinks_per_day = 5
        self.max_caffeine_per_drink = 200.0  # mg
        self.jitter_threshold = 0.7  # Above this = too jittery
        self.time_between_drinks_minutes = 30
        
        logger.info("🧐☕ Sir Hawkington's energy drink authorization system initialized")
    
    async def authorize_energy_drink(
        self,
        request: EnergyDrinkRequest
    ) -> EnergyDrinkAuthorization:
        """
        Evaluate Terry's energy drink request with aristocratic scrutiny.
        
        Args:
            request: Terry's energy drink request
            
        Returns:
            EnergyDrinkAuthorization with decision and commentary
        """
        logger.info(
            f"🧐☕ Reviewing energy drink request from Terry...\n"
            f"   Current consumption: {request.energy_drinks_consumed_today}\n"
            f"   Jitter level: {request.current_jitter_level:.2f}\n"
            f"   Reason: {request.consumption_reason}\n"
            f"   *adjusts monocle thoughtfully*"
        )
        
        # Evaluate the request
        decision = await self._evaluate_request(request)
        
        # Update Hawk's state
        if decision.approved:
            self.energy_drink_approvals_today += 1
            self.total_approvals += 1
            logger.info(
                f"🧐✅ APPROVED: {decision.commentary}\n"
                f"   Monocle: {decision.monocle_action}\n"
                f"   Total approvals today: {self.energy_drink_approvals_today}"
            )
        else:
            self.energy_drink_denials_today += 1
            self.total_denials += 1
            if decision.monocle_action == 'yeeted':
                self.monocle_yeets_for_caffeine += 1
            logger.warning(
                f"🧐❌ DENIED: {decision.commentary}\n"
                f"   Monocle: {decision.monocle_action}\n"
                f"   Total denials today: {self.energy_drink_denials_today}"
            )
        
        # Format authorization response
        authorization = EnergyDrinkAuthorization(
            request_id=request.request_id if hasattr(request, 'request_id') else str(id(request)),
            authorized=decision.approved,
            authorized_by="sir_hawkington",
            authorization_notes=decision.commentary,
            recommended_caffeine_mg=decision.recommended_caffeine_mg,
            recommended_type=decision.recommended_type,
            safety_warnings=decision.safety_warnings,
            timestamp=utc_now()
        )
        
        return authorization
    
    async def _evaluate_request(
        self,
        request: EnergyDrinkRequest
    ) -> AuthorizationDecision:
        """
        Evaluate energy drink request with aristocratic standards.
        
        Considers:
        - Daily consumption count
        - Current jitter level
        - Time since last drink
        - System urgency
        - Terry's track record
        """
        consumption = request.energy_drinks_consumed_today
        jitter = request.current_jitter_level
        time_since_last = request.time_since_last_drink_minutes
        urgency = request.optimization_urgency
        
        # DENIAL CASE 1: Too many drinks today
        if consumption >= self.max_drinks_per_day:
            return AuthorizationDecision(
                approved=False,
                reason="daily_limit_exceeded",
                commentary=(
                    f"Absolutely not, dear boy. You've had {consumption} energy drinks today. "
                    f"That's quite enough. One must maintain some semblance of self-control."
                ),
                monocle_action='yeeted',
                recommended_caffeine_mg=0.0,
                recommended_type=EnergyDrinkType.WATER,
                safety_warnings=[
                    f"Daily limit ({self.max_drinks_per_day}) exceeded",
                    "Excessive caffeine consumption detected",
                    "Consider water instead"
                ]
            )
        
        # DENIAL CASE 2: Jitter level too high
        if jitter >= self.jitter_threshold:
            return AuthorizationDecision(
                approved=False,
                reason="excessive_jitter",
                commentary=(
                    f"I think not. Your jitter level is {jitter:.2f}. "
                    f"You're vibrating so intensely you're becoming blurry. "
                    f"Perhaps a spot of tea instead?"
                ),
                monocle_action='yeeted',
                recommended_caffeine_mg=0.0,
                recommended_type=EnergyDrinkType.TEA,
                safety_warnings=[
                    f"Jitter level ({jitter:.2f}) exceeds safe threshold ({self.jitter_threshold})",
                    "Risk of shell-spinning incident",
                    "Tea recommended for calming effect"
                ]
            )
        
        # DENIAL CASE 3: Too soon after last drink
        if time_since_last is not None and time_since_last < self.time_between_drinks_minutes:
            return AuthorizationDecision(
                approved=False,
                reason="insufficient_time_elapsed",
                commentary=(
                    f"Patience, dear boy. It's only been {time_since_last} minutes since your last drink. "
                    f"One must allow at least {self.time_between_drinks_minutes} minutes between doses. "
                    f"Standards, you understand."
                ),
                monocle_action='polished',
                recommended_caffeine_mg=0.0,
                recommended_type=EnergyDrinkType.COFFEE,
                safety_warnings=[
                    f"Only {time_since_last} minutes since last drink",
                    f"Minimum interval: {self.time_between_drinks_minutes} minutes",
                    "Metabolic processing incomplete"
                ]
            )
        
        # APPROVAL CASE 1: First drink of the day - full approval
        if consumption == 0:
            return AuthorizationDecision(
                approved=True,
                reason="first_drink_approved",
                commentary=(
                    "Very well. Your first energy drink of the day. "
                    "Do try to make it last, won't you? *adjusts monocle approvingly*"
                ),
                monocle_action='adjusted',
                recommended_caffeine_mg=160.0,
                recommended_type=EnergyDrinkType.ENERGY_DRINK,
                safety_warnings=[]
            )
        
        # APPROVAL CASE 2: Moderate consumption, low jitter - full approval
        if consumption < 3 and jitter < 0.5:
            return AuthorizationDecision(
                approved=True,
                reason="moderate_consumption_approved",
                commentary=(
                    f"I suppose one more won't hurt. You've had {consumption} today and your jitter "
                    f"level is acceptable at {jitter:.2f}. Do pace yourself, though. "
                    f"*adjusts monocle thoughtfully*"
                ),
                monocle_action='adjusted',
                recommended_caffeine_mg=160.0,
                recommended_type=EnergyDrinkType.ENERGY_DRINK,
                safety_warnings=["Monitor jitter level", "Pace consumption"]
            )
        
        # APPROVAL CASE 3: Higher consumption but urgent - reduced dose
        if consumption >= 3 and urgency == "immediate" and jitter < self.jitter_threshold:
            return AuthorizationDecision(
                approved=True,
                reason="urgent_reduced_dose",
                commentary=(
                    f"Very well, given the urgency. But you've had {consumption} already, "
                    f"so I'm limiting you to coffee rather than another energy drink. "
                    f"One must maintain standards. *polishes monocle with concern*"
                ),
                monocle_action='polished',
                recommended_caffeine_mg=95.0,  # Coffee dose
                recommended_type=EnergyDrinkType.COFFEE,
                safety_warnings=[
                    f"Consumption count high ({consumption})",
                    "Reduced caffeine dose recommended",
                    "Monitor for adverse effects"
                ]
            )
        
        # APPROVAL CASE 4: Borderline - tea with warning
        if consumption >= 3 and jitter >= 0.5:
            return AuthorizationDecision(
                approved=True,
                reason="borderline_tea_approved",
                commentary=(
                    f"You're pushing it, dear boy. {consumption} drinks and jitter at {jitter:.2f}. "
                    f"I'll authorize tea, but that's the limit. Any more and I'll have to put my foot down. "
                    f"*adjusts monocle sternly*"
                ),
                monocle_action='adjusted',
                recommended_caffeine_mg=47.0,  # Tea dose
                recommended_type=EnergyDrinkType.TEA,
                safety_warnings=[
                    "Approaching daily limit",
                    "Jitter level elevated",
                    "This is your final authorization for the day"
                ]
            )
        
        # DEFAULT DENIAL: Something's off
        return AuthorizationDecision(
            approved=False,
            reason="general_concern",
            commentary=(
                "I'm afraid I must decline. Something about this request doesn't sit right. "
                "Perhaps we should discuss your optimization strategy with VIC-20? "
                "*adjusts monocle with concern*"
            ),
            monocle_action='adjusted',
            recommended_caffeine_mg=0.0,
            recommended_type=EnergyDrinkType.WATER,
            safety_warnings=[
                "Request parameters concerning",
                "Consultation with VIC-20 recommended"
            ]
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Hawk's energy drink authorization stats"""
        total_requests = self.total_approvals + self.total_denials
        approval_rate = (self.total_approvals / total_requests) if total_requests > 0 else 0.0
        
        return {
            'approvals_today': self.energy_drink_approvals_today,
            'denials_today': self.energy_drink_denials_today,
            'total_approvals': self.total_approvals,
            'total_denials': self.total_denials,
            'total_requests': total_requests,
            'approval_rate': approval_rate,
            'monocle_yeets_for_caffeine': self.monocle_yeets_for_caffeine
        }
    
    def reset_daily_count(self) -> None:
        """Reset daily counters (called at midnight)"""
        logger.info(
            f"🧐🌅 New day! Resetting energy drink authorization counters. "
            f"Yesterday: {self.energy_drink_approvals_today} approved, "
            f"{self.energy_drink_denials_today} denied"
        )
        self.energy_drink_approvals_today = 0
        self.energy_drink_denials_today = 0
