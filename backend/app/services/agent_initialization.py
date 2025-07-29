# services/agent_initialization.py
async def initialize_agent_memories(user_id: str, db: AsyncSession):
    """Initialize memory banks for all agents for a new user"""
    
    agents = [
        'sir_hawkington',
        'the_stick', 
        'the_hamsters',
        'meth_snail',
        'quantum_shadow_people',
        'vic_20'
    ]
    
    for agent_name in agents:
        memory_bank = AgentMemory(
            user_id=user_id,
            agent_name=agent_name,
            memory_data={
                'initialized_at': datetime.now(timezone.utc).isoformat(),
                'total_interactions': 0,
                'patterns_learned': 0,
                'decisions_made': 0,
                'agent_specific_data': {}
            }
        )
        db.add(memory_bank)
    
    await db.commit()