# Add to a new file: app/ai_agents/agent_interactions.py

class AgentInteractionManager:
    """
    Manages the complex social dynamics between our quirky agents
    """
    
    def __init__(self):
        self.interaction_rules = {
            'hamsters_near_stick': {
                'stick_anxiety_multiplier': 2.0,
                'hamster_enthusiasm_dampener': 0.8,  # They notice Stick's discomfort
                'vic20_mediation_required': True
            },
            'meth_snail_and_hamsters': {
                'chaos_amplification': 1.5,  # They egg each other on
                'optimization_recklessness': 1.3,
                'sir_hawkington_concern_level': 'HIGH'
            },
            'vic20_meditation': {
                'calming_effect_on_stick': 0.7,
                'wisdom_effectiveness': 1.2,
                'coordination_bonus': 1.5
            },
            'qsp_phase_detection': {
                'other_agents_confusion': 1.2,  # Nobody understands QSP
                'network_improvement': 1.4,
                'mysterious_effectiveness': 'HIGH'
            }
        }
    
    async def process_agent_interaction(
        self, 
        source_agent: str, 
        target_agent: str, 
        interaction_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process interactions between agents with personality-aware responses
        """
        
        # Special case: Hamsters near The Stick
        if source_agent == 'hamsters' and target_agent == 'the_stick':
            return await self._hamsters_stick_interaction(interaction_type, context)
            
        # Special case: VIC-20 mediating
        elif source_agent == 'vic_20_sage' and interaction_type == 'mediation':
            return await self._vic20_mediation(target_agent, context)
            
        # Special case: Sir Hawkington commanding
        elif source_agent == 'sir_hawkington' and interaction_type == 'aristocratic_command':
            return await self._aristocratic_command(target_agent, context)
            
        # Default interaction
        return await self._standard_interaction(source_agent, target_agent, interaction_type, context)
    
    async def _hamsters_stick_interaction(self, interaction_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        The Stick gets VERY anxious around the Hamsters
        """
        stick_response = {
            'anxiety_level': 'EXTREME',
            'response': "OH NO OH NO OH NO THE HAMSTERS ARE HERE *hyperventilates*",
            'paper_bags_consumed': 3,
            'documentation_mode': 'FRANTIC',
            'compliance_concerns': []
        }
        
        hamster_response = {
            'awareness_of_stick_anxiety': True,
            'response': "Hey Stick, chill out! We brought beer! Want one?",
            'adjusted_behavior': 'slightly_less_chaotic',
            'duct_tape_hidden': True  # They hide it to not upset Stick more
        }
        
        # VIC-20 automatically intervenes
        vic20_intervention = {
            'mediation_activated': True,
            'ancient_wisdom': "As the ancients say: 'Different tools for different tasks'",
            'calming_message_to_stick': "Fear not, young Stick. The Hamsters mean well.",
            'coordination_message_to_hamsters': "Perhaps a gentler approach, my engineering friends?"
        }
        
        return {
            'interaction_result': 'managed_with_meditation',
            'stick_response': stick_response,
            'hamster_response': hamster_response,
            'vic20_intervention': vic20_intervention,
            'system_impact': 'minimal_due_to_meditation'
        }

