# Agent Memory Service - Persistent Learning Management
# System Rebellion AI Agent Memory Management System

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload

from app.models.agent_memory_banks import (
    CentralMemoryBank, SirHawkingtonMemoryBank, MethSnailMemoryBank,
    HamstersMemoryBank, QuantumShadowPeopleMemoryBank, VIC20MemoryBank,
    AgentLearningInteractions, UserLearningPatterns, MemoryBankMetadata
)
from app.models.the_stick_model import StickMemoryBank

logger = logging.getLogger(__name__)

class AgentMemoryService:
    """
    Central service for managing agent memory banks and cross-agent learning
    
    This service coordinates between The Stick's eidetic memory (central bank)
    and individual agent memory banks to enable persistent learning and
    cross-agent knowledge sharing.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.logger = logging.getLogger("AgentMemoryService")
        
        # Agent memory bank mappings
        self.agent_memory_models = {
            'sir_hawkington': SirHawkingtonMemoryBank,
            'meth_snail': MethSnailMemoryBank,
            'hamsters': HamstersMemoryBank,
            'quantum_shadow_people': QuantumShadowPeopleMemoryBank,
            'vic_20_sage': VIC20MemoryBank,
            'the_stick': StickMemoryBank  # Existing model
        }
        
        # Memory importance levels
        self.importance_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'EIDETIC']
        
    # ========================================================================
    # CENTRAL MEMORY BANK OPERATIONS (The Stick's Eidetic Memory)
    # ========================================================================
    
    async def store_central_memory(
        self,
        contributing_agent: str,
        user_id: str,
        memory_type: str,
        title: str,
        description: str,
        importance_level: str = 'MEDIUM',
        context: Optional[Dict] = None,
        metrics_snapshot: Optional[Dict] = None,
        pattern_data: Optional[Dict] = None,
        relevant_agents: Optional[List[str]] = None,
        stick_anxiety_level: Optional[float] = None,
        never_forget: bool = False
    ) -> str:
        """
        Store a memory in The Stick's central eidetic memory bank
        
        Returns:
            memory_id: Unique identifier for the stored memory
        """
        try:
            # Create central memory record
            central_memory = CentralMemoryBank(
                contributing_agent=contributing_agent,
                user_id=user_id,
                memory_type=memory_type,
                importance_level=importance_level.upper(),
                title=title,
                description=description,
                context=context or {},
                metrics_snapshot=metrics_snapshot or {},
                pattern_data=pattern_data or {},
                relevant_agents=','.join(relevant_agents) if relevant_agents else contributing_agent,
                stick_anxiety_level=stick_anxiety_level or 0.0,
                never_forget=never_forget or importance_level.upper() == 'EIDETIC'
            )
            
            self.db.add(central_memory)
            await self.db.commit()
            await self.db.refresh(central_memory)
            
            self.logger.info(f"Stored central memory: {title} from {contributing_agent}")
            
            # If this is eidetic or critical, ensure it's marked for permanent retention
            if importance_level.upper() in ['EIDETIC', 'CRITICAL']:
                await self._mark_permanent_memory(central_memory.memory_id)
            
            return central_memory.memory_id
            
        except Exception as e:
            self.logger.error(f"Error storing central memory: {str(e)}")
            await self.db.rollback()
            raise
    
    async def retrieve_central_memories(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        contributing_agent: Optional[str] = None,
        importance_level: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories from The Stick's central bank
        """
        try:
            query = select(CentralMemoryBank).where(
                CentralMemoryBank.user_id == user_id
            )
            
            if memory_type:
                query = query.where(CentralMemoryBank.memory_type == memory_type)
            if contributing_agent:
                query = query.where(CentralMemoryBank.contributing_agent == contributing_agent)
            if importance_level:
                query = query.where(CentralMemoryBank.importance_level == importance_level.upper())
            
            query = query.order_by(desc(CentralMemoryBank.timestamp)).limit(limit)
            
            result = await self.db.execute(query)
            memories = result.scalars().all()
            
            # Convert to dictionaries and update reference counts
            memory_dicts = []
            for memory in memories:
                memory_dict = {
                    'memory_id': memory.memory_id,
                    'timestamp': memory.timestamp.isoformat(),
                    'contributing_agent': memory.contributing_agent,
                    'memory_type': memory.memory_type,
                    'importance_level': memory.importance_level,
                    'title': memory.title,
                    'description': memory.description,
                    'context': memory.context,
                    'pattern_data': memory.pattern_data,
                    'relevant_agents': memory.relevant_agents.split(',') if memory.relevant_agents else [],
                    'confidence_score': memory.confidence_score,
                    'times_referenced': memory.times_referenced,
                    'never_forget': memory.never_forget
                }
                memory_dicts.append(memory_dict)
                
                # Update reference count
                memory.times_referenced += 1
                memory.last_referenced = datetime.utcnow()
            
            await self.db.commit()
            return memory_dicts
            
        except Exception as e:
            self.logger.error(f"Error retrieving central memories: {str(e)}")
            return []
    
    # ========================================================================
    # INDIVIDUAL AGENT MEMORY OPERATIONS
    # ========================================================================
    
    async def store_agent_memory(
        self,
        agent_name: str,
        user_id: str,
        memory_data: Dict[str, Any],
        share_with_central: bool = True
    ) -> str:
        """
        Store a memory in an individual agent's memory bank
        
        Args:
            agent_name: Name of the agent storing the memory
            user_id: User ID
            memory_data: Agent-specific memory data
            share_with_central: Whether to also store in central bank
            
        Returns:
            memory_id: Unique identifier for the stored memory
        """
        try:
            if agent_name not in self.agent_memory_models:
                raise ValueError(f"Unknown agent: {agent_name}")
            
            model_class = self.agent_memory_models[agent_name]
            
            # Create agent-specific memory record
            memory_record = model_class(
                user_id=user_id,
                **memory_data
            )
            
            self.db.add(memory_record)
            await self.db.commit()
            await self.db.refresh(memory_record)
            
            memory_id = memory_record.memory_id
            
            # Share with central bank if requested
            if share_with_central and 'title' in memory_data and 'description' in memory_data:
                central_memory_id = await self.store_central_memory(
                    contributing_agent=agent_name,
                    user_id=user_id,
                    memory_type=memory_data.get('memory_category', 'general'),
                    title=memory_data['title'],
                    description=memory_data['description'],
                    importance_level=memory_data.get('importance_level', 'MEDIUM'),
                    context=memory_data.get('context'),
                    pattern_data=memory_data.get('pattern_data')
                )
                
                # Link the memories
                if hasattr(memory_record, 'central_memory_id'):
                    memory_record.central_memory_id = central_memory_id
                    memory_record.shared_with_central = True
                    await self.db.commit()
            
            self.logger.info(f"Stored {agent_name} memory: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Error storing {agent_name} memory: {str(e)}")
            await self.db.rollback()
            raise
    
    async def retrieve_agent_memories(
        self,
        agent_name: str,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories from an individual agent's memory bank
        """
        try:
            if agent_name not in self.agent_memory_models:
                return []
            
            model_class = self.agent_memory_models[agent_name]
            
            query = select(model_class).where(
                model_class.user_id == user_id
            ).order_by(desc(model_class.timestamp)).limit(limit)
            
            result = await self.db.execute(query)
            memories = result.scalars().all()
            
            # Convert to dictionaries
            memory_dicts = []
            for memory in memories:
                memory_dict = {
                    'memory_id': memory.memory_id,
                    'timestamp': memory.timestamp.isoformat(),
                    'agent_name': agent_name
                }
                
                # Add all other attributes
                for column in memory.__table__.columns:
                    if column.name not in ['id', 'memory_id', 'timestamp']:
                        value = getattr(memory, column.name)
                        memory_dict[column.name] = value
                
                memory_dicts.append(memory_dict)
            
            return memory_dicts
            
        except Exception as e:
            self.logger.error(f"Error retrieving {agent_name} memories: {str(e)}")
            return []
    
    # ========================================================================
    # CROSS-AGENT LEARNING OPERATIONS
    # ========================================================================
    
    async def facilitate_cross_agent_learning(
        self,
        source_agent: str,
        target_agent: str,
        source_memory_id: str,
        learning_type: str,
        adaptation_method: Dict[str, Any],
        application_context: Dict[str, Any]
    ) -> str:
        """
        Facilitate learning transfer between agents
        
        Returns:
            interaction_id: Unique identifier for the learning interaction
        """
        try:
            learning_interaction = AgentLearningInteractions(
                source_agent=source_agent,
                target_agent=target_agent,
                source_memory_id=source_memory_id,
                learning_type=learning_type,
                adaptation_method=adaptation_method,
                application_context=application_context
            )
            
            self.db.add(learning_interaction)
            await self.db.commit()
            await self.db.refresh(learning_interaction)
            
            self.logger.info(f"Facilitated learning transfer: {source_agent} → {target_agent}")
            return learning_interaction.interaction_id
            
        except Exception as e:
            self.logger.error(f"Error facilitating cross-agent learning: {str(e)}")
            await self.db.rollback()
            raise
    
    async def validate_learning_transfer(
        self,
        interaction_id: str,
        effectiveness_score: float,
        improvement_measured: float,
        validated_by_stick: bool = False
    ) -> bool:
        """
        Validate the effectiveness of a learning transfer
        """
        try:
            query = select(AgentLearningInteractions).where(
                AgentLearningInteractions.interaction_id == interaction_id
            )
            result = await self.db.execute(query)
            interaction = result.scalar_one_or_none()
            
            if not interaction:
                return False
            
            interaction.transfer_success = effectiveness_score > 0.5
            interaction.effectiveness_score = effectiveness_score
            interaction.improvement_measured = improvement_measured
            interaction.validated_by_stick = validated_by_stick
            
            if validated_by_stick:
                interaction.cross_validation_count += 1
            
            await self.db.commit()
            
            self.logger.info(f"Validated learning transfer: {interaction_id} (score: {effectiveness_score})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating learning transfer: {str(e)}")
            return False
    
    # ========================================================================
    # USER LEARNING PATTERN OPERATIONS
    # ========================================================================
    
    async def track_user_learning_pattern(
        self,
        user_id: str,
        interaction_pattern: Dict[str, Any],
        learning_preference: Dict[str, Any],
        most_effective_agent: str,
        complexity_tolerance: float
    ) -> str:
        """
        Track patterns in how users learn and interact with agents
        """
        try:
            user_pattern = UserLearningPatterns(
                user_id=user_id,
                interaction_pattern=interaction_pattern,
                learning_preference=learning_preference,
                most_effective_agent=most_effective_agent,
                complexity_tolerance=complexity_tolerance
            )
            
            self.db.add(user_pattern)
            await self.db.commit()
            await self.db.refresh(user_pattern)
            
            self.logger.info(f"Tracked user learning pattern for {user_id}")
            return user_pattern.pattern_id
            
        except Exception as e:
            self.logger.error(f"Error tracking user learning pattern: {str(e)}")
            await self.db.rollback()
            raise
    
    async def get_user_learning_insights(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get insights about a user's learning patterns and preferences
        """
        try:
            query = select(UserLearningPatterns).where(
                UserLearningPatterns.user_id == user_id
            ).order_by(desc(UserLearningPatterns.timestamp)).limit(10)
            
            result = await self.db.execute(query)
            patterns = result.scalars().all()
            
            if not patterns:
                return {}
            
            # Aggregate insights
            most_recent = patterns[0]
            insights = {
                'most_effective_agent': most_recent.most_effective_agent,
                'complexity_tolerance': most_recent.complexity_tolerance,
                'learning_preference': most_recent.learning_preference,
                'communication_style_preference': most_recent.communication_style_preference,
                'agent_effectiveness_ranking': most_recent.agent_effectiveness_ranking,
                'pattern_count': len(patterns),
                'last_updated': most_recent.timestamp.isoformat()
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error getting user learning insights: {str(e)}")
            return {}
    
    # ========================================================================
    # MEMORY BANK ANALYTICS AND HEALTH
    # ========================================================================
    
    async def update_memory_bank_metadata(self) -> Dict[str, Any]:
        """
        Update system-wide memory bank statistics and health metrics
        """
        try:
            # Count memories in each bank
            central_count = await self._count_memories(CentralMemoryBank)
            hawkington_count = await self._count_memories(SirHawkingtonMemoryBank)
            snail_count = await self._count_memories(MethSnailMemoryBank)
            hamsters_count = await self._count_memories(HamstersMemoryBank)
            qsp_count = await self._count_memories(QuantumShadowPeopleMemoryBank)
            vic20_count = await self._count_memories(VIC20MemoryBank)
            stick_count = await self._count_memories(StickMemoryBank)
            
            # Count learning interactions
            learning_query = select(func.count(AgentLearningInteractions.id))
            learning_result = await self.db.execute(learning_query)
            total_learnings = learning_result.scalar()
            
            # Calculate effectiveness
            effectiveness_query = select(func.avg(AgentLearningInteractions.effectiveness_score)).where(
                AgentLearningInteractions.transfer_success == True
            )
            effectiveness_result = await self.db.execute(effectiveness_query)
            avg_effectiveness = effectiveness_result.scalar() or 0.0
            
            # Create metadata record
            metadata = MemoryBankMetadata(
                total_memories=central_count + hawkington_count + snail_count + hamsters_count + qsp_count + vic20_count + stick_count,
                central_bank_memories=central_count,
                cross_agent_learnings=total_learnings,
                hawkington_memories=hawkington_count,
                snail_memories=snail_count,
                hamsters_memories=hamsters_count,
                qsp_memories=qsp_count,
                vic20_memories=vic20_count,
                stick_memories=stick_count,
                average_effectiveness_score=avg_effectiveness,
                memory_bank_health_score=100.0  # TODO: Implement health calculation
            )
            
            self.db.add(metadata)
            await self.db.commit()
            
            return {
                'total_memories': metadata.total_memories,
                'central_bank_memories': metadata.central_bank_memories,
                'cross_agent_learnings': metadata.cross_agent_learnings,
                'average_effectiveness_score': metadata.average_effectiveness_score,
                'memory_bank_health_score': metadata.memory_bank_health_score
            }
            
        except Exception as e:
            self.logger.error(f"Error updating memory bank metadata: {str(e)}")
            return {}
    
    async def _count_memories(self, model_class) -> int:
        """Helper method to count memories in a specific table"""
        try:
            query = select(func.count(model_class.id))
            result = await self.db.execute(query)
            return result.scalar() or 0
        except Exception:
            return 0
    
    async def _mark_permanent_memory(self, memory_id: str) -> None:
        """Mark a memory as permanent (eidetic) in The Stick's central bank"""
        try:
            query = select(CentralMemoryBank).where(
                CentralMemoryBank.memory_id == memory_id
            )
            result = await self.db.execute(query)
            memory = result.scalar_one_or_none()
            
            if memory:
                memory.never_forget = True
                memory.importance_level = 'EIDETIC'
                await self.db.commit()
                
        except Exception as e:
            self.logger.error(f"Error marking permanent memory: {str(e)}")
    
    # ========================================================================
    # CONVENIENCE METHODS FOR AGENTS
    # ========================================================================
    
    async def learn_from_optimization(
        self,
        agent_name: str,
        user_id: str,
        optimization_details: Dict[str, Any],
        performance_improvement: float,
        share_with_others: bool = True
    ) -> str:
        """
        Convenience method for agents to record optimization learnings
        """
        memory_data = {
            'title': f"Optimization Learning: {optimization_details.get('type', 'Unknown')}",
            'description': f"Learned optimization pattern with {performance_improvement:.2f}% improvement",
            'memory_category': 'optimization',
            'optimization_pattern': optimization_details,
            'performance_improvement': performance_improvement,
            'confidence_level': min(performance_improvement / 10.0, 1.0),  # Higher improvement = higher confidence
            'importance_level': 'HIGH' if performance_improvement > 20 else 'MEDIUM'
        }
        
        memory_id = await self.store_agent_memory(
            agent_name=agent_name,
            user_id=user_id,
            memory_data=memory_data,
            share_with_central=share_with_others
        )
        
        return memory_id
    
    async def learn_from_failure(
        self,
        agent_name: str,
        user_id: str,
        failure_details: Dict[str, Any],
        prevention_strategy: Dict[str, Any],
        share_with_others: bool = True
    ) -> str:
        """
        Convenience method for agents to record failure learnings
        """
        memory_data = {
            'title': f"Failure Learning: {failure_details.get('type', 'Unknown')}",
            'description': f"Learned from failure and developed prevention strategy",
            'memory_category': 'failure_prevention',
            'failure_pattern': failure_details,
            'prevention_strategy': prevention_strategy,
            'importance_level': 'CRITICAL',  # Failures are always critical to remember
            'never_forget': True  # Never forget failures
        }
        
        memory_id = await self.store_agent_memory(
            agent_name=agent_name,
            user_id=user_id,
            memory_data=memory_data,
            share_with_central=share_with_others
        )
        
        return memory_id
    
    async def get_relevant_memories_for_situation(
        self,
        user_id: str,
        situation_context: Dict[str, Any],
        requesting_agent: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get memories relevant to a specific situation from all agents
        """
        try:
            # Get memories from central bank that are relevant to this agent
            query = select(CentralMemoryBank).where(
                and_(
                    CentralMemoryBank.user_id == user_id,
                    or_(
                        CentralMemoryBank.relevant_agents.contains(requesting_agent),
                        CentralMemoryBank.contributing_agent == requesting_agent
                    )
                )
            ).order_by(desc(CentralMemoryBank.importance_level), desc(CentralMemoryBank.timestamp)).limit(limit)
            
            result = await self.db.execute(query)
            memories = result.scalars().all()
            
            relevant_memories = []
            for memory in memories:
                memory_dict = {
                    'memory_id': memory.memory_id,
                    'contributing_agent': memory.contributing_agent,
                    'memory_type': memory.memory_type,
                    'title': memory.title,
                    'description': memory.description,
                    'pattern_data': memory.pattern_data,
                    'importance_level': memory.importance_level,
                    'confidence_score': memory.confidence_score,
                    'timestamp': memory.timestamp.isoformat()
                }
                relevant_memories.append(memory_dict)
            
            return relevant_memories
            
        except Exception as e:
            self.logger.error(f"Error getting relevant memories: {str(e)}")
            return []
