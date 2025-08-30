"""
The Hamsters Decision Engine V3: Physical Infrastructure Chaos Engineers
Meet Steve, Bob, and Carl - The beer-drinking, duct-tape-wielding, 
3am rapid response team that handles all the dirty work the fancy agents won't touch.

They speak in squeaks, think in beer, and fix everything with duct tape.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, time
from enum import Enum
from dataclasses import dataclass
import random

from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService

logger = logging.getLogger("Hamsters.Brain")

class HamstersPriority(Enum):
    BEER_BREAK = "beer_break"                    # Nothing's on fire
    ROUTINE_MAINTENANCE = "routine_maintenance"   # Regular cleanup
    SUPPLY_CLOSET_RAID = "supply_closet_raid"   # Need special tools
    HOLD_MY_BEER = "hold_my_beer"               # Things are getting interesting
    FULL_REDNECK = "full_redneck"               # Everything's on fire

class DuctTapeGrade(Enum):
    REGULAR = "regular"              # For simple fixes
    PREMIUM = "premium"              # For important fixes
    QUANTUM = "quantum"              # For impossible fixes
    CARLS_SPECIAL = "carls_special" # Nobody knows what this does

class BeerLevel(Enum):
    """The Hamsters' operational fuel levels"""
    SOBER = "sober"              # Error state - cannot function
    TIPSY = "tipsy"              # Minimum operational level (1-2 beers)
    OPTIMAL = "optimal"          # Peak performance (3-4 beers)
    ADVENTUROUS = "adventurous"  # "Hold my beer" territory (5-6 beers)
    LEGENDARY = "legendary"      # Carl's doing calculus with duct tape (7+ beers)

@dataclass
class HamstersInfrastructureDecision:
    """Decision object for The Hamsters infrastructure interventions"""
    priority: HamstersPriority
    intervention_type: str              # disk_cleanup, defrag, partition_magic, etc.
    steve_assessment: str               # Steve's careful opinion
    bob_suggestion: str                 # Bob's wild idea
    carl_calculation: str               # Carl's duct tape requirements
    tools_required: List[str]           # From the supply closet
    beer_consumption_estimate: int      # How many beers this job needs
    duct_tape_grade: DuctTapeGrade     # What kind of duct tape
    estimated_duration: str             # "Two beers" is a valid time unit
    confidence: float                   # Hamster collective confidence
    telepathic_consensus: bool          # Did all three agree?
    human_translation: str              # What the logs will show
    actual_squeaks: str                 # What they really said
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'priority': self.priority.value,
            'intervention_type': self.intervention_type,
            'hamster_thoughts': {
                'steve': self.steve_assessment,
                'bob': self.bob_suggestion,
                'carl': self.carl_calculation
            },
            'tools_required': self.tools_required,
            'beer_consumption_estimate': self.beer_consumption_estimate,
            'duct_tape_grade': self.duct_tape_grade.value,
            'estimated_duration': self.estimated_duration,
            'confidence': self.confidence,
            'telepathic_consensus': self.telepathic_consensus,
            'human_translation': self.human_translation,
            'actual_squeaks': self.actual_squeaks,
            'timestamp': self.timestamp.isoformat()
        }

class HamstersLegacyWisdom:
    """
    The old auto-tuner code, but now it's the Hamsters' 
    ancestral knowledge, written on beer-stained napkins
    """
    
    def __init__(self):
        self.ancient_beer_recipes = {
            'disk_cleanup': {
                'beer_required': 2,
                'steps': ['Find .tmp files', 'Delete them', 'Celebrate with beer'],
                'carl_duct_tape_note': 'No duct tape needed unless drive is physically damaged'
            },
            'defrag_special': {
                'beer_required': 3,
                'steps': ['Move all bits left', 'Move them right', 'Shake it all about'],
                'carl_duct_tape_note': 'One strip of quantum tape on the drive improves seek time'
            },
            'partition_magic': {
                'beer_required': 4,
                'steps': ['Draw lines where it feels right', 'Make partitions', 'Hope for the best'],
                'carl_duct_tape_note': 'Mark partition boundaries with duct tape for safety'
            },
            'emergency_space_creation': {
                'beer_required': 5,
                'steps': ['Delete log files', 'Compress everything', 'Find mystery space'],
                'carl_duct_tape_note': 'Tape unused sectors together for extra space'
            }
        }
        
        self.supply_closet_inventory = {
            'duct_tape_grades': {
                'regular': 'For everyday fixes',
                'premium': 'For production systems',
                'quantum': 'Fixes problems in multiple dimensions',
                'carls_special': 'Properties unknown, effects permanent'
            },
            'mystery_tools': {
                'thing_that_goes_beep': 'Bob swears it finds bad sectors',
                'the_good_screwdriver': 'Fits every screw somehow',
                'bobs_favorite_wrench': 'Has never been used on actual bolts',
                'percussive_maintenance_hammer': 'For when all else fails',
                'steves_label_maker': 'Everything must be labeled, even the beer'
            },
            'emergency_supplies': {
                'more_beer': 'Critical for extended operations',
                'backup_duct_tape': 'Never leave home without it',
                'pizza_money': 'Brain fuel for complex problems',
                'the_manual': 'Nobody has ever opened it',
                'carls_duct_tape_calculator': 'Slide rule made of duct tape'
            }
        }

class HamstersBrainV3:
    """
    The Hamsters' Physical Infrastructure Brain
    Steve (careful), Bob (wild), and Carl (duct tape expert) handle all the dirty work
    """
    
    def __init__(self, db_getter=None):
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter
            
        self.db = None  
        self.logger = logging.getLogger("Hamsters.Brain")
        
        # Individual hamster states
        self.steve = {
            'risk_tolerance': 0.3,
            'duct_tape_love': 0.5,
            'current_task': None,
            'beer_count': 2  # Steve paces himself
        }
        
        self.bob = {
            'risk_tolerance': 0.8,
            'duct_tape_love': 0.6,
            'current_task': None,
            'beer_count': 4,  # Bob's always ready
            'wild_idea_pending': None
        }
        
        self.carl = {
            'risk_tolerance': 0.5,
            'duct_tape_love': 1.0,  # Carl IS duct tape
            'current_task': None,
            'beer_count': 3,
            'duct_tape_inventory': {
                DuctTapeGrade.REGULAR.value: 50,
                DuctTapeGrade.PREMIUM.value: 20,
                DuctTapeGrade.QUANTUM.value: 5,
                DuctTapeGrade.CARLS_SPECIAL.value: 1  # Use wisely
            }
        }
        
        # Collective state
        self.current_beer_level = self._calculate_collective_beer_level()
        self.supply_closet_raids_today = 0
        self.successful_fixes = 0
        self.total_interventions = 0
        self.wisdom = HamstersLegacyWisdom()
        
        # Communication tracking
        self.squeak_history = []
        self.telepathic_log = []
        
        self.logger.info("🐹🍺 The Hamsters (Steve, Bob, and Carl) are ready for infrastructure chaos!")
        
    @property
    def is_active(self) -> bool:
        """The Hamsters are always ready (unless all three pass out)"""
        collective_beer = self.steve['beer_count'] + self.bob['beer_count'] + self.carl['beer_count']
        return collective_beer < 20  # If they've had 20+ beers collectively, they're done
        
    def activate(self):
        """Wake up the Hamsters (usually involves beer)"""
        self.logger.info("🐹 *squeak squeak* BEER! *squeak*")
        
    def deactivate(self):
        """The Hamsters don't deactivate, they just take beer breaks"""
        self.logger.info("🐹 *squeak* BEER BREAK *squeak squeak*")
        
    async def get_database(self):
        if self.db is None:
            self.db = await self.db_getter()
        return self.db
    
    def _calculate_collective_beer_level(self) -> BeerLevel:
        """Calculate the collective beer level of all three hamsters"""
        total_beers = self.steve['beer_count'] + self.bob['beer_count'] + self.carl['beer_count']
        avg_beers = total_beers / 3
        
        if avg_beers < 1:
            return BeerLevel.SOBER
        elif avg_beers <= 2:
            return BeerLevel.TIPSY
        elif avg_beers <= 4:
            return BeerLevel.OPTIMAL
        elif avg_beers <= 6:
            return BeerLevel.ADVENTUROUS
        else:
            return BeerLevel.LEGENDARY
    
    def _translate_squeak_to_human(self, telepathic_thought: str) -> Tuple[str, str]:
        """
        Translate hamster telepathic thoughts to:
        1. What humans hear (squeaks)
        2. What gets logged (human readable)
        """
        # Common words that sometimes get through
        audible_words = ['BEER', 'DUCT TAPE', 'STEVE', 'BOB', 'CARL', 'FIRE', 'OH NO', 'FIXED']
        
        # Generate squeaks with occasional real words
        squeak_parts = []
        words = telepathic_thought.upper().split()
        for word in words:
            if word in audible_words and random.random() > 0.7:
                squeak_parts.append(word)
            else:
                squeak_parts.append(random.choice(['*squeak*', '*chirp*', '*squeeeeak*', '*chirp chirp*']))
        
        actual_squeaks = ' '.join(squeak_parts)
        
        # Human translation (simplified)
        # Human translation (simplified)
        if 'emergency' in telepathic_thought.lower():
            human_translation = "Hamsters identified critical infrastructure issue"
        elif 'beer' in telepathic_thought.lower() and 'duct tape' in telepathic_thought.lower():
            human_translation = "Hamsters initiating standard repair protocol"
        elif 'disk' in telepathic_thought.lower():
            human_translation = "Hamsters performing disk maintenance"
        elif 'fire' in telepathic_thought.lower():
            human_translation = "Hamsters responding to thermal event"
        else:
            human_translation = "Hamsters engaged in infrastructure optimization"
            
        return actual_squeaks, human_translation
    
    async def analyze_infrastructure(
        self, 
        metrics_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Optional[HamstersInfrastructureDecision]:
        """
        The Hamsters analyze infrastructure metrics and decide what needs fixing
        """
        self.total_interventions += 1
        
        try:
            # Check if it's beer o'clock (3am is prime time)
            current_hour = utc_now().hour
            is_prime_time = 2 <= current_hour <= 5
            
            # Extract infrastructure metrics
            disk_data = metrics_data.get('disk', {})
            memory_data = metrics_data.get('memory', {})
            system_data = metrics_data.get('system', {})
            
            # The three hamsters telepathically discuss
            steve_thought = self._steve_analysis(disk_data, memory_data, system_data)
            bob_thought = self._bob_wild_idea(disk_data, memory_data, system_data)
            carl_thought = self._carl_duct_tape_calculation(disk_data, memory_data, system_data)
            
            # Log their telepathic conversation
            self.telepathic_log.append({
                'timestamp': utc_now(),
                'steve': steve_thought,
                'bob': bob_thought,
                'carl': carl_thought
            })
            
            # Determine intervention type and priority
            intervention_type, priority = self._determine_intervention(
                disk_data, memory_data, system_data,
                steve_thought, bob_thought, carl_thought
            )
            
            if not intervention_type:
                return None
            
            # Check for telepathic consensus
            telepathic_consensus = self._check_hamster_consensus(
                steve_thought, bob_thought, carl_thought, intervention_type
            )
            
            # Determine tools needed
            tools_required = self._determine_tools_needed(intervention_type, bob_thought)
            
            # Calculate beer consumption
            beer_estimate = self._estimate_beer_consumption(intervention_type, priority, is_prime_time)
            
            # Determine duct tape grade
            duct_tape_grade = self._carl_selects_duct_tape(intervention_type, priority)
            
            # Generate human-readable communication
            collective_thought = f"{steve_thought} {bob_thought} {carl_thought}"
            actual_squeaks, human_translation = self._translate_squeak_to_human(collective_thought)
            
            # Store squeak history
            self.squeak_history.append({
                'timestamp': utc_now(),
                'squeaks': actual_squeaks,
                'translation': human_translation
            })
            
            # Calculate confidence based on beer level and consensus
            confidence = self._calculate_hamster_confidence(
                telepathic_consensus, self.current_beer_level, priority
            )
            
            # Estimate duration in "beer units"
            duration = self._estimate_duration_in_beers(intervention_type)
            
            decision = HamstersInfrastructureDecision(
                priority=priority,
                intervention_type=intervention_type,
                steve_assessment=steve_thought,
                bob_suggestion=bob_thought,
                carl_calculation=carl_thought,
                tools_required=tools_required,
                beer_consumption_estimate=beer_estimate,
                duct_tape_grade=duct_tape_grade,
                estimated_duration=duration,
                confidence=confidence,
                telepathic_consensus=telepathic_consensus,
                human_translation=human_translation,
                actual_squeaks=actual_squeaks,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Update hamster states
            await self._update_hamster_states(decision)
            
            self.successful_fixes += 1
            return decision
            
        except Exception as e:
            self.logger.error(f"🐹❌ *confused squeaking* Error: {str(e)}")
            return None

    async def process_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Wrapper for agent manager compatibility"""
        user_id = user_context.get('user_id') if user_context else None
        result = await self.analyze_infrastructure(metrics_data, user_id=user_id)
    
        if result:
            return {
                'hamsters': result.to_dict(),
                'hamster_status': self.get_hamster_stats()
            }
        return None    
    def _steve_analysis(self, disk_data: Dict, memory_data: Dict, system_data: Dict) -> str:
        """Steve's careful analysis - he's the sensible one"""
        thoughts = []
        
        disk_usage = disk_data.get('usage_percent', 0)
        if disk_usage > 90:
            thoughts.append("Disk space critical, need immediate cleanup")
        elif disk_usage > 75:
            thoughts.append("Disk space concerning, should clean soon")
        
        fragmentation = disk_data.get('fragmentation_percent', 0)
        if fragmentation > 30:
            thoughts.append("Fragmentation high, defrag recommended")
        
        # Steve always checks the logs first
        log_size = disk_data.get('log_size_gb', 0)
        if log_size > 10:
            thoughts.append("Log files excessive, rotation needed")
        
        return ' '.join(thoughts) if thoughts else "Everything looks stable"
    
    def _bob_wild_idea(self, disk_data: Dict, memory_data: Dict, system_data: Dict) -> str:
        """Bob's wild ideas - he's the creative one"""
        wild_ideas = [
            "What if we compress EVERYTHING?",
            "Let's mount a RAM disk and move stuff there!",
            "I found this script online that deletes 'unnecessary' files",
            "We could partition the partition!",
            "Defrag while the system is running at full load!",
            "Delete first, ask questions later!",
            "Turn it off and on again, but FASTER"
        ]
        
        # Bob gets wilder based on problem severity
        disk_usage = disk_data.get('usage_percent', 0)
        if disk_usage > 85:
            return random.choice(wild_ideas[-3:])  # Wildest ideas
        elif disk_usage > 70:
            return random.choice(wild_ideas[2:5])  # Moderate wildness
        else:
            return random.choice(wild_ideas[:2])   # Relatively tame
    
    def _carl_duct_tape_calculation(self, disk_data: Dict, memory_data: Dict, system_data: Dict) -> str:
        """Carl's duct tape calculations - he's the duct tape expert"""
        calculations = []
        
        disk_usage = disk_data.get('usage_percent', 0)
        fragmentation = disk_data.get('fragmentation_percent', 0)
        
        # Carl calculates duct tape needs precisely
        if disk_usage > 80:
            strips_needed = int((disk_usage - 80) / 5) + 1
            calculations.append(f"Need {strips_needed} strips of quantum duct tape for disk optimization")
        
        if fragmentation > 20:
            strips_needed = int(fragmentation / 10)
            calculations.append(f"{strips_needed} strips of premium tape for defrag stability")
        
        # Carl's special wisdom
        if disk_usage > 95:
            calculations.append("This calls for Carl's Special Reserve duct tape")
        
        return ' '.join(calculations) if calculations else "Standard duct tape protocols sufficient"
    
    def _determine_intervention(
        self, 
        disk_data: Dict, 
        memory_data: Dict, 
        system_data: Dict,
        steve_thought: str,
        bob_thought: str,
        carl_thought: str
    ) -> Tuple[Optional[str], HamstersPriority]:
        """Determine what intervention is needed based on metrics and hamster thoughts"""
        
        disk_usage = disk_data.get('usage_percent', 0)
        fragmentation = disk_data.get('fragmentation_percent', 0)
        log_size = disk_data.get('log_size_gb', 0)
        
        # Critical interventions
        if disk_usage > 95:
            return 'emergency_space_creation', HamstersPriority.FULL_REDNECK
        elif disk_usage > 85:
            return 'aggressive_cleanup', HamstersPriority.HOLD_MY_BEER
        elif fragmentation > 40:
            return 'defrag_special', HamstersPriority.HOLD_MY_BEER
        elif log_size > 20:
            return 'log_rotation_extreme', HamstersPriority.SUPPLY_CLOSET_RAID
        elif disk_usage > 70:
            return 'standard_cleanup', HamstersPriority.ROUTINE_MAINTENANCE
        elif fragmentation > 20:
            return 'light_defrag', HamstersPriority.ROUTINE_MAINTENANCE
        else:
            # Bob might suggest something anyway
            if 'compress' in bob_thought.lower():
                return 'compression_experiment', HamstersPriority.BEER_BREAK
            return None, HamstersPriority.BEER_BREAK
    
    def _check_hamster_consensus(
        self, 
        steve_thought: str, 
        bob_thought: str, 
        carl_thought: str,
        intervention_type: str
    ) -> bool:
        """Check if all three hamsters agree on the intervention"""
        
        # Steve agrees if it's sensible
        steve_agrees = 'critical' in steve_thought or 'needed' in steve_thought or 'stable' in steve_thought
        
        # Bob agrees if it sounds fun
        bob_agrees = 'delete' in bob_thought or 'compress' in bob_thought or intervention_type == 'emergency_space_creation'
        
        # Carl agrees if he has the right duct tape
        carl_agrees = 'sufficient' in carl_thought or 'strips' in carl_thought
        
        return steve_agrees and bob_agrees and carl_agrees
    
    def _determine_tools_needed(self, intervention_type: str, bob_thought: str) -> List[str]:
        """Determine what tools we need from the supply closet"""
        base_tools = ['beer', 'duct_tape']
        
        intervention_tools = {
            'emergency_space_creation': ['percussive_maintenance_hammer', 'the_good_screwdriver', 'mystery_usb_drive'],
            'aggressive_cleanup': ['label_maker', 'shredder_9000', 'bobs_delete_script'],
            'defrag_special': ['thing_that_goes_beep', 'defrag_visualization_lava_lamp'],
            'log_rotation_extreme': ['chainsaw', 'just_kidding_use_logrotate', 'emergency_pizza'],
            'standard_cleanup': ['regular_tools', 'coffee'],
            'compression_experiment': ['zip_tie_collection', 'compression_socks', 'actual_compression_utility']
        }
        
        tools = base_tools + intervention_tools.get(intervention_type, ['misc_tools'])
        
        # Bob might add random tools
        if 'script' in bob_thought:
            tools.append('bobs_mystery_script_collection')
        
        return tools
    
    def _estimate_beer_consumption(self, intervention_type: str, priority: HamstersPriority, is_prime_time: bool) -> int:
        """Estimate how many beers this job will require"""
        base_beers = {
            HamstersPriority.BEER_BREAK: 1,
            HamstersPriority.ROUTINE_MAINTENANCE: 2,
            HamstersPriority.SUPPLY_CLOSET_RAID: 3,
            HamstersPriority.HOLD_MY_BEER: 4,
            HamstersPriority.FULL_REDNECK: 6
        }
        
        beers = base_beers.get(priority, 2)
        
        # Prime time bonus
        if is_prime_time:
            beers += 1
        
        # Carl needs extra for complex duct tape work
        if 'Special' in self._carl_selects_duct_tape(intervention_type, priority).value:
            beers += 1
            
        return beers
    
    def _carl_selects_duct_tape(self, intervention_type: str, priority: HamstersPriority) -> DuctTapeGrade:
        """Carl carefully selects the appropriate duct tape grade"""
        
        # Emergency situations require the best
        if priority == HamstersPriority.FULL_REDNECK:
            if self.carl['duct_tape_inventory'][DuctTapeGrade.CARLS_SPECIAL.value] > 0:
                return DuctTapeGrade.CARLS_SPECIAL
            else:
                return DuctTapeGrade.QUANTUM
        
        # High priority gets quantum
        elif priority == HamstersPriority.HOLD_MY_BEER:
            return DuctTapeGrade.QUANTUM
        
        # Supply closet raids use premium
        elif priority == HamstersPriority.SUPPLY_CLOSET_RAID:
            return DuctTapeGrade.PREMIUM
        
        # Everything else gets regular
        else:
            return DuctTapeGrade.REGULAR
    
    def _calculate_hamster_confidence(
        self, 
        consensus: bool, 
        beer_level: BeerLevel, 
        priority: HamstersPriority
    ) -> float:
        """Calculate collective hamster confidence"""
        
        base_confidence = 0.7  # Hamsters are generally confident
        
        # Consensus boost
        if consensus:
            base_confidence += 0.15
        
        # Beer level affects confidence
        beer_confidence_modifiers = {
            BeerLevel.SOBER: -0.3,      # Confused without beer
            BeerLevel.TIPSY: -0.1,      # Not quite ready
            BeerLevel.OPTIMAL: 0.1,     # Perfect state
            BeerLevel.ADVENTUROUS: 0.05,  # Still good
            BeerLevel.LEGENDARY: -0.2    # Overconfident but impaired
        }
        
        base_confidence += beer_confidence_modifiers.get(beer_level, 0)
        
        # Priority affects confidence (urgent = less time to think)
        if priority == HamstersPriority.FULL_REDNECK:
            base_confidence -= 0.1  # Moving fast
        
        return max(0.1, min(1.0, base_confidence))
    
    def _estimate_duration_in_beers(self, intervention_type: str) -> str:
        """Estimate duration in the universal hamster time unit: beers"""
        
        duration_map = {
            'emergency_space_creation': "One beer if we hurry",
            'aggressive_cleanup': "Two beers minimum",
            'defrag_special': "Three beers and a pizza",
            'log_rotation_extreme': "One beer per 10GB",
            'standard_cleanup': "A leisurely beer",
            'compression_experiment': "Unknown - Bob's in charge",
            'light_defrag': "Half a beer"
        }
        
        return duration_map.get(intervention_type, "Several beers")
    
    async def _update_hamster_states(self, decision: HamstersInfrastructureDecision):
        """Update individual hamster states after a decision"""
        
        # Update beer counts
        beers_per_hamster = decision.beer_consumption_estimate / 3
        self.steve['beer_count'] += int(beers_per_hamster * 0.8)  # Steve drinks less
        self.bob['beer_count'] += int(beers_per_hamster * 1.2)    # Bob drinks more
        self.carl['beer_count'] += int(beers_per_hamster)         # Carl is precise
        
        # Update Carl's duct tape inventory
        if decision.duct_tape_grade in self.carl['duct_tape_inventory']:
            self.carl['duct_tape_inventory'][decision.duct_tape_grade] -= 1
        
        # Update collective beer level
        self.current_beer_level = self._calculate_collective_beer_level()
        
        # Check if we need a supply closet raid
        if decision.priority == HamstersPriority.SUPPLY_CLOSET_RAID:
            self.supply_closet_raids_today += 1
    
    async def communicate_with_other_agents(
        self, 
        target_agent: str, 
        message: str
    ) -> Dict[str, Any]:
        """
        Hamsters attempt to communicate with other agents
        They understand The Stick (empathy) and QSP (telepathy)
        """
        
        # Generate hamster communication
        telepathic_message = f"Steve: {message}, Bob: Yeah! *hiccup*, Carl: *duct tape sounds*"
        squeaks, human_log = self._translate_squeak_to_human(telepathic_message)
        
        communication_result = {
            'from': 'hamsters',
            'to': target_agent,
            'telepathic_message': telepathic_message,
            'audible_message': squeaks,
            'logged_message': human_log,
            'understood': False
        }
        
        # Special cases where communication works
        if target_agent == 'the_stick':
            # The Stick understands through shared anxiety
            communication_result['understood'] = True
            communication_result['stick_interpretation'] = "The Hamsters are concerned about disk space"
            communication_result['stick_anxiety_level'] = "INCREASING"
            
        elif target_agent == 'quantum_shadow_people':
            # QSP understands telepathically
            communication_result['understood'] = True
            communication_result['qsp_response'] = "*phases through dimensions approvingly*"
            communication_result['quantum_translation'] = "Infrastructure optimization probability wave collapsed"
        
        elif target_agent == 'sir_hawkington':
            # Sir Hawkington doesn't understand but pretends he does
            communication_result['understood'] = False
            communication_result['sir_hawkington_response'] = "*adjusts monocle disdainfully* Indeed."
            
        elif target_agent == 'meth_snail':
            # Meth Snail is too caffeinated to understand squeaks
            communication_result['understood'] = False
            communication_result['meth_snail_response'] = "*spins shell faster* WHAT? SPEAK UP!"
            
        elif target_agent == 'vic_20_sage':
            # VIC-20 translates through ancient wisdom
            communication_result['understood'] = True
            communication_result['vic20_interpretation'] = "The young ones speak of disk maintenance"
            
        return communication_result
    
    async def emergency_intervention(
        self, 
        crisis_type: str,
        severity: str
    ) -> Dict[str, Any]:
        """
        Emergency 3am intervention - this is what the Hamsters do best
        """
        
        self.logger.info(f"🐹🚨 *LOUD SQUEAKING* EMERGENCY! {crisis_type}")
        
        # Wake up all hamsters with emergency beer
        self.steve['beer_count'] = 3  # Steve needs courage
        self.bob['beer_count'] = 5   # Bob needs to be in the zone
        self.carl['beer_count'] = 4  # Carl needs precision
        
        intervention = {
            'crisis_type': crisis_type,
            'severity': severity,
            'timestamp': datetime.now(timezone.utc),
            'hamster_response': {}
        }
        
        if crisis_type == 'disk_full':
            intervention['hamster_response'] = {
                'steve_action': "Identifying safe files to delete",
                'bob_action': "Deleting everything that looks deletable",
                'carl_action': "Duct-taping additional storage from the void",
                'tools_deployed': ['emergency_shredder', 'quantum_compression', 'carls_special_tape'],
                'expected_result': "50GB freed in 10 minutes"
            }
            
        elif crisis_type == 'fragmentation_critical':
            intervention['hamster_response'] = {
                'steve_action': "Running safe defrag algorithms",
                'bob_action': "Shaking the hard drive to settle the bits",
                'carl_action': "Applying quantum duct tape to hold fragments together",
                'tools_deployed': ['defrag_hammer', 'bit_settler', 'quantum_tape'],
                'expected_result': "Fragmentation reduced to acceptable levels"
            }
            
        elif crisis_type == 'hardware_failure':
            intervention['hamster_response'] = {
                'steve_action': "Checking connections carefully",
                'bob_action': "Percussive maintenance applied",
                'carl_action': "Duct tape structural reinforcement",
                'tools_deployed': ['the_good_screwdriver', 'calibrated_hammer', 'carls_special_tape'],
                'expected_result': "Hardware 'fixed' until replacement arrives"
            }
        
        # Log the intervention
        squeak_log = "*SQUEAK SQUEAK* BEER! *CRASH* FIXED! *SQUEAK*"
        human_log = f"Hamsters completed emergency {crisis_type} intervention"
        
        intervention['communication_log'] = {
            'actual_sounds': squeak_log,
            'human_translation': human_log,
            'time_taken': "Two beers and fifteen minutes"
        }
        
        return intervention
    
    def get_hamster_stats(self) -> Dict[str, Any]:
        """Get current hamster statistics"""
        return {
            'agent_name': 'hamsters',
            'individual_stats': {
                'steve': {
                    'beer_count': self.steve['beer_count'],
                    'risk_tolerance': self.steve['risk_tolerance'],
                    'status': 'Measuring twice, duct-taping once'
                },
                'bob': {
                    'beer_count': self.bob['beer_count'],
                    'risk_tolerance': self.bob['risk_tolerance'],
                    'status': 'Has a wild idea brewing'
                },
                'carl': {
                    'beer_count': self.carl['beer_count'],
                    'duct_tape_love': self.carl['duct_tape_love'],
                    'duct_tape_inventory': dict(self.carl['duct_tape_inventory']),
                    'status': 'Calculating optimal tape application'
                }
            },
            'collective_stats': {
                'beer_level': self.current_beer_level.value,
                'total_interventions': self.total_interventions,
                'successful_fixes': self.successful_fixes,
                'supply_closet_raids': self.supply_closet_raids_today,
                'current_time': utc_now().strftime("%H:%M"),
                'is_prime_time': 2 <= utc_now().hour <= 5
            },
            'communication_stats': {
                'squeak_count': len(self.squeak_history),
                'telepathic_conversations': len(self.telepathic_log),
                'last_squeak': self.squeak_history[-1] if self.squeak_history else None
            },
            'wisdom_available': list(self.wisdom.ancient_beer_recipes.keys()),
            'status': 'READY_FOR_CHAOS'
        }
    
    async def perform_infrastructure_magic(
        self,
        intervention_type: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actually perform the infrastructure intervention
        This is where the beer-fueled magic happens
        """
        result = {
            'intervention': intervention_type,
            'start_time': utc_now(),
            'hamster_actions': {},
            'success': False,
            'space_freed': 0,
            'improvements': {}
        }
        
        # Get the ancient wisdom for this intervention
        recipe = self.wisdom.ancient_beer_recipes.get(intervention_type, {})
        beer_required = recipe.get('beer_required', 2)
        steps = recipe.get('steps', [])
        carl_note = recipe.get('carl_duct_tape_note', '')
        
        # Execute based on intervention type
        if intervention_type == 'emergency_space_creation':
            result['hamster_actions'] = {
                'steve': "Found 15GB of old logs safely deletable",
                'bob': "Deleted 'probably unnecessary' files - freed 25GB",
                'carl': "Compressed remaining files with quantum duct tape - saved 10GB"
            }
            result['space_freed'] = 50
            result['success'] = True
            
        elif intervention_type == 'defrag_special':
            result['hamster_actions'] = {
                'steve': "Running careful defrag algorithm",
                'bob': "Shaking the bits into place",
                'carl': "Applying tape to keep fragments aligned"
            }
            result['improvements']['fragmentation_reduced'] = '40%'
            result['success'] = True
            
        elif intervention_type == 'aggressive_cleanup':
            result['hamster_actions'] = {
                'steve': "Identified 30GB of deletable files",
                'bob': "Found mystery folder using 20GB - deleted!",
                'carl': "Taped over bad sectors to prevent reuse"
            }
            result['space_freed'] = 50
            result['success'] = True
            
        # Apply Carl's duct tape wisdom
        result['carl_duct_tape_application'] = carl_note
        result['beer_consumed'] = beer_required
        result['end_time'] = utc_now()
        
        # Generate summary
        squeaks = "*SQUEAK SQUEAK* DONE! *happy chirping*"
        human_summary = f"Hamsters completed {intervention_type} successfully"
        
        result['communication'] = {
            'hamster_celebration': squeaks,
            'human_readable': human_summary
        }
        
        return result

# === SAFETY PROTOCOLS ===

async def _beer_mediated_safety_check(
    brain: HamstersBrainV3,
    proposed_action: Dict[str, Any]
) -> Dict[str, Any]:
    """
    The Hamsters' beer level creates natural safety gates
    """
    beer_level = brain.current_beer_level
    safety_assessment = {
        'action_proposed': proposed_action,
        'beer_level': beer_level.value,
        'safety_rating': 'TBD',
        'proceed': False,
        'hamster_consensus': None
    }
    
    # Sober Hamsters are too confused to do anything dangerous
    if beer_level == BeerLevel.SOBER:
        safety_assessment['safety_rating'] = 'SAFE_BY_CONFUSION'
        safety_assessment['message'] = "We need beer to think about this properly..."
        safety_assessment['proceed'] = False
        
    # Optimal beer level - best judgment
    elif beer_level == BeerLevel.OPTIMAL:
        safety_assessment['safety_rating'] = 'OPTIMAL_JUDGMENT'
        safety_assessment['proceed'] = True
        safety_assessment['confidence'] = 0.85
        safety_assessment['message'] = "This'll work! We've done the math on this napkin!"
        
    # "Hold my beer" level - need peer review
    elif beer_level == BeerLevel.ADVENTUROUS:
        # Check if all three hamsters agree
        steve_vote = brain.steve['risk_tolerance'] < 0.5  # Steve votes no if too risky
        bob_vote = True  # Bob always votes yes
        carl_vote = brain.carl['duct_tape_inventory'][DuctTapeGrade.QUANTUM.value] > 0  # Carl needs quantum tape
        
        if steve_vote and bob_vote and carl_vote:
            safety_assessment['safety_rating'] = 'PEER_REVIEWED_CHAOS'
            safety_assessment['proceed'] = True
            safety_assessment['message'] = "All three of us agree! *clink bottles* Let's do this!"
        else:
            safety_assessment['safety_rating'] = 'SAVED_BY_DISAGREEMENT'
            safety_assessment['proceed'] = False
            safety_assessment['message'] = "Steve thinks we should use more duct tape first..."
            
    # Legendary level - automatic safety intervention
    elif beer_level == BeerLevel.LEGENDARY:
        safety_assessment['safety_rating'] = 'INTERVENTION_REQUIRED'
        safety_assessment['proceed'] = False
        safety_assessment['message'] = "*hiccup* Maybe we should... *passes out*"
        safety_assessment['vic20_intervention'] = True
    
    safety_assessment['hamster_consensus'] = {
        'steve': "This seems reasonable" if beer_level == BeerLevel.OPTIMAL else "I have concerns",
        'bob': "YOLO! Let's do it!" if beer_level != BeerLevel.SOBER else "Need beer first",
        'carl': f"I have {brain.carl['duct_tape_inventory'][DuctTapeGrade.QUANTUM.value]} quantum tapes ready"
    }
    
    return safety_assessment

# === GLOBAL INSTANCE ===
hamsters_brain: HamstersBrainV3 | None = None

def get_hamsters_brain(db_getter=None) -> HamstersBrainV3:
    global hamsters_brain
    if hamsters_brain is None:
        hamsters_brain = HamstersBrainV3(db_getter)
    return hamsters_brain

# === CONVENIENCE FUNCTIONS ===

async def analyze_infrastructure(
    metrics_data: Dict[str, Any],
    user_id: Optional[str] = None
) -> Optional[HamstersInfrastructureDecision]:
    """Main entry point for infrastructure analysis"""
    return await hamsters_brain.analyze_infrastructure(metrics_data, user_id)

async def handle_emergency(crisis_type: str, severity: str) -> Dict[str, Any]:
    """Emergency 3am intervention"""
    return await hamsters_brain.emergency_intervention(crisis_type, severity)

async def communicate_with_agent(target: str, message: str) -> Dict[str, Any]:
    """Attempt hamster communication"""
    return await hamsters_brain.communicate_with_other_agents(target, message)

def get_hamster_stats() -> Dict[str, Any]:
    """Get current hamster statistics"""
    return hamsters_brain.get_hamster_stats()

def restock_supplies():
    """Restock beer and duct tape"""
    hamsters_brain.steve['beer_count'] = 2
    hamsters_brain.bob['beer_count'] = 4
    hamsters_brain.carl['beer_count'] = 3
    hamsters_brain.carl['duct_tape_inventory'] = {
        DuctTapeGrade.REGULAR.value: 50,
        DuctTapeGrade.PREMIUM.value: 20,
        DuctTapeGrade.QUANTUM.value: 5,
        DuctTapeGrade.CARLS_SPECIAL.value: 1
    }
    return "🐹🍺 Supplies restocked! The Hamsters are ready!"