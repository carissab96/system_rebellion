"""
Database integration for Hamster infrastructure operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.schemas.agent_memory import MemoryPriority
from app.schemas.hamsters import (
    HamstersInfrastructureInterventionCreate,
    HamstersCommunicationLogCreate,
    HamstersDuctTapeUsageCreate,
    HamstersBeerConsumptionCreate,
    HamstersSupplyClosetRaidCreate,
    HamstersIndividualStatsCreate,
    HamstersEngineeringStatsCreate,
    HamstersInfrastructureInterventionRead,
    HamstersCommunicationLogRead,
    HamstersDuctTapeUsageRead,
    HamstersBeerConsumptionRead,
    HamstersSupplyClosetRaidRead,
    HamstersIndividualStatsRead,
    HamstersEngineeringStatsRead
)

class HamstersDatabaseIntegration:
    """Handles all database operations for the Hamsters"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def log_intervention(
        self,
        intervention_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log a complete infrastructure intervention"""
        try:
            # Validate input data using the schema
            intervention_create = HamstersInfrastructureInterventionCreate(
                user_id=intervention_data.get('user_id'),
                type=intervention_data['type'],
                status=intervention_data['status'],
                priority=intervention_data.get('priority', 'routine_maintenance'),
                steve_action=intervention_data['steve_action'],
                bob_action=intervention_data['bob_action'],
                carl_action=intervention_data['carl_action'],
                beer_consumed=intervention_data['beer_consumed'],
                tools_used=intervention_data['tools_used'],
                space_freed_gb=intervention_data.get('space_freed_gb', 0),
                started_at=datetime.utcnow()
            )
            
            # Convert to DB model if needed, or use as is if your DB layer accepts Pydantic models
            intervention_dict = intervention_create.dict(exclude_unset=True)
            
            # Here you would typically save to the database
            # For now, we'll return the validated data
            return {
                "status": "success",
                "intervention_data": intervention_dict,
                "message": "Intervention validated successfully"
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                'status': 'error',
                'message': f'Failed to log intervention: {str(e)}'
            }
    
    async def log_communication(
        self,
        communication_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log communication between hamsters"""
        try:
            # Validate input data using the schema
            communication_create = HamstersCommunicationLogCreate(
                user_id=communication_data.get('user_id'),
                source_hamster=communication_data['source_hamster'],
                telepathic_message=communication_data.get('telepathic_message'),
                audible_squeaks=communication_data['audible_squeaks'],
                human_translation=communication_data['human_translation'],
                target_agent=communication_data.get('target_agent'),
                understood=communication_data.get('understood', False)
            )
            
            # Convert to DB model if needed, or use as is if your DB layer accepts Pydantic models
            communication_dict = communication_create.dict(exclude_unset=True)
            
            return {
                "status": "success",
                "communication_data": communication_dict,
                "message": "Communication validated successfully"
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                'status': 'error',
                'message': f'Failed to log communication: {str(e)}'
            }
    
    async def track_duct_tape_usage(
        self,
        grade: str,
        strips_used: int,
        purpose: str,
        used_by: str = "carl",
        effectiveness: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track duct tape consumption"""
        try:
            # Validate input data using the schema
            duct_tape_create = HamstersDuctTapeUsageCreate(
                user_id=user_id,
                grade=grade,
                strips_used=strips_used,
                purpose=purpose,
                used_by=used_by,
                effectiveness=effectiveness
            )
            
            # Convert to DB model if needed, or use as is if your DB layer accepts Pydantic models
            duct_tape_dict = duct_tape_create.dict(exclude_unset=True)
            
            return {
                "status": "success",
                "duct_tape_data": duct_tape_dict,
                "message": "Duct tape usage validated successfully"
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to validate duct tape usage: {str(e)}'
            }
    
    async def log_beer_consumption(
        self,
        hamster_name: str,
        beers: int,
        occasion: str,
        user_id: Optional[str] = None
    ) -> None:
        """Track beer consumption for operational metrics"""
        try:
            consumption = HamstersBeerConsumption(
                user_id=user_id,
                hamster_name=hamster_name,
                beers_consumed=beers,
                occasion=occasion,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(consumption)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            
    async def log_supply_closet_raid(
        self,
        items_taken: List[str],
        purpose: str,
        raided_by: str = "bob",
        user_id: Optional[str] = None
    ) -> None:
        """Log supply closet raids (usually Bob)"""
        try:
            raid = HamstersSupplyClosetRaid(
                user_id=user_id,
                raided_by=raided_by,
                items_taken=items_taken,
                purpose=purpose,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(raid)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            
    async def update_individual_stats(
        self,
        hamster_name: str,
        stats_update: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> None:
        """Update individual hamster statistics"""
        try:
            # Get current stats or create new
            query = select(HamstersIndividualStats).where(
                and_(
                    HamstersIndividualStats.hamster_name == hamster_name,
                    HamstersIndividualStats.user_id == user_id
                )
            ).order_by(HamstersIndividualStats.timestamp.desc()).limit(1)
            
            result = await self.db.execute(query)
            current_stats = result.scalar_one_or_none()
            
            # Create new stats entry
            new_stats = HamstersIndividualStats(
                user_id=user_id,
                hamster_name=hamster_name,
                beer_count=stats_update.get('beer_count', 0),
                risk_tolerance=stats_update.get('risk_tolerance', 0.5),
                current_task=stats_update.get('current_task'),
                duct_tape_love=stats_update.get('duct_tape_love', 0.5),
                timestamp=datetime.utcnow()
            )
            
            self.db.add(new_stats)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            
    async def get_recent_interventions(
        self,
        hours: int = 24,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent intervention history"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            
            query = select(HamstersInfrastructureIntervention).where(
                HamstersInfrastructureIntervention.started_at >= since
            )
            
            if user_id:
                query = query.where(HamstersInfrastructureIntervention.user_id == user_id)
                
            query = query.order_by(HamstersInfrastructureIntervention.started_at.desc())
            
            result = await self.db.execute(query)
            interventions = result.scalars().all()
            
            return [
                {
                    'id': i.id,
                    'intervention_id': i.intervention_id,
                    'type': i.type,
                    'status': i.status,
                    'priority': i.priority,
                    'started_at': i.started_at,
                    'completed_at': i.completed_at,
                    'steve_action': i.steve_action,
                    'bob_action': i.bob_action,
                    'carl_action': i.carl_action,
                    'space_freed_gb': i.space_freed_gb,
                    'beer_consumed': i.beer_consumed,
                    'tools_used': i.tools_used,
                    'duration': (i.completed_at - i.started_at).seconds if i.completed_at else None
                }
                for i in interventions
            ]
            
        except Exception as e:
            return []
            
    async def get_infrastructure_metrics(
        self,
        metric_type: str,
        days_back: int = 7,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get infrastructure metrics and statistics"""
        try:
            since = datetime.utcnow() - timedelta(days=days_back)
            
            if metric_type == 'disk_space':
                # Calculate total space freed
                query = select(
                    func.sum(HamstersInfrastructureIntervention.space_freed_gb).label('total_freed'),
                    func.count(HamstersInfrastructureIntervention.id).label('cleanup_count')
                ).where(
                    and_(
                        HamstersInfrastructureIntervention.started_at >= since,
                        HamstersInfrastructureIntervention.type.in_(['disk_cleanup', 'emergency_space_creation'])
                    )
                )
                
                if user_id:
                    query = query.where(HamstersInfrastructureIntervention.user_id == user_id)
                
                result = await self.db.execute(query)
                data = result.first()
                
                return {
                    'metric_type': 'disk_space',
                    'total_space_freed_gb': float(data.total_freed or 0),
                    'cleanup_operations': int(data.cleanup_count or 0),
                    'period_days': days_back
                }
                
            elif metric_type == 'beer_consumption':
                # Get beer consumption stats
                query = select(
                    HamstersBeerConsumption.hamster_name,
                    func.sum(HamstersBeerConsumption.beers_consumed).label('total_beers')
                ).where(
                    HamstersBeerConsumption.timestamp >= since
                ).group_by(HamstersBeerConsumption.hamster_name)
                
                if user_id:
                    query = query.where(HamstersBeerConsumption.user_id == user_id)
                
                result = await self.db.execute(query)
                consumption = result.all()
                
                return {
                    'metric_type': 'beer_consumption',
                    'individual_consumption': {
                        row.hamster_name: int(row.total_beers)
                        for row in consumption
                    },
                    'total_beer_consumed': sum(row.total_beers for row in consumption),
                    'period_days': days_back
                }
                
            elif metric_type == 'duct_tape_usage':
                # Get duct tape usage stats
                query = select(
                    HamstersDuctTapeUsage.grade,
                    func.sum(HamstersDuctTapeUsage.strips_used).label('total_strips'),
                    func.avg(HamstersDuctTapeUsage.effectiveness).label('avg_effectiveness')
                ).where(
                    HamstersDuctTapeUsage.timestamp >= since
                ).group_by(HamstersDuctTapeUsage.grade)
                
                if user_id:
                    query = query.where(HamstersDuctTapeUsage.user_id == user_id)
                
                result = await self.db.execute(query)
                usage = result.all()
                
                return {
                    'metric_type': 'duct_tape_usage',
                    'usage_by_grade': {
                        row.grade: {
                            'strips_used': int(row.total_strips),
                            'effectiveness': float(row.avg_effectiveness) if row.avg_effectiveness else 0.0
                        }
                        for row in usage
                    },
                    'total_strips_used': sum(row.total_strips for row in usage),
                    'period_days': days_back
                }
                
            elif metric_type == '3am_interventions':
                # Count interventions during prime hamster hours (2-5 AM)
                query = select(
                    func.count(HamstersInfrastructureIntervention.id).label('count')
                ).where(
                    and_(
                        HamstersInfrastructureIntervention.started_at >= since,
                        func.extract('hour', HamstersInfrastructureIntervention.started_at).between(2, 5)
                    )
                )
                
                if user_id:
                    query = query.where(HamstersInfrastructureIntervention.user_id == user_id)
                
                result = await self.db.execute(query)
                count = result.scalar()
                
                return {
                    'metric_type': '3am_interventions',
                    'intervention_count': int(count or 0),
                    'period_days': days_back,
                    'prime_time_hours': '2am-5am'
                }
                
            else:
                return {
                    'metric_type': metric_type,
                    'error': 'Unknown metric type',
                    'available_types': ['disk_space', 'beer_consumption', 'duct_tape_usage', '3am_interventions']
                }
                
        except Exception as e:
            return {
                'metric_type': metric_type,
                'error': str(e)
            }
    
    async def get_hamster_communication_history(
        self,
        hamster_name: Optional[str] = None,
        target_agent: Optional[str] = None,
        limit: int = 50,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get hamster communication history"""
        try:
            query = select(HamstersCommunicationLog).order_by(
                HamstersCommunicationLog.timestamp.desc()
            ).limit(limit)
            
            if hamster_name:
                query = query.where(HamstersCommunicationLog.source_hamster == hamster_name)
            
            if target_agent:
                query = query.where(HamstersCommunicationLog.target_agent == target_agent)
                
            if user_id:
                query = query.where(HamstersCommunicationLog.user_id == user_id)
            
            result = await self.db.execute(query)
            communications = result.scalars().all()
            
            return [
                {
                    'timestamp': comm.timestamp,
                    'source_hamster': comm.source_hamster,
                    'squeaks': comm.audible_squeaks,
                    'translation': comm.human_translation,
                    'target_agent': comm.target_agent,
                    'understood': comm.understood
                }
                for comm in communications
            ]
            
        except Exception as e:
            return []
    
    async def get_supply_closet_history(
        self,
        days_back: int = 30,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get supply closet raid history"""
        try:
            since = datetime.utcnow() - timedelta(days=days_back)
            
            query = select(HamstersSupplyClosetRaid).where(
                HamstersSupplyClosetRaid.timestamp >= since
            ).order_by(HamstersSupplyClosetRaid.timestamp.desc())
            
            if user_id:
                query = query.where(HamstersSupplyClosetRaid.user_id == user_id)
            
            result = await self.db.execute(query)
            raids = result.scalars().all()
            
            return [
                {
                    'timestamp': raid.timestamp,
                    'raided_by': raid.raided_by,
                    'items_taken': raid.items_taken,
                    'purpose': raid.purpose
                }
                for raid in raids
            ]
            
        except Exception as e:
            return []
    
    async def update_intervention_status(
        self,
        intervention_id: str,
        status: str,
        results: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update the status of an intervention"""
        try:
            query = select(HamstersInfrastructureIntervention).where(
                HamstersInfrastructureIntervention.intervention_id == intervention_id
            )
            
            result = await self.db.execute(query)
            intervention = result.scalar_one_or_none()
            
            if not intervention:
                return False
            
            intervention.status = status
            
            if status == 'completed':
                intervention.completed_at = datetime.utcnow()
                
                if results:
                    intervention.space_freed_gb = results.get('space_freed_gb', 0)
                    intervention.fragmentation_reduced_percent = results.get('fragmentation_reduced', 0)
                    intervention.temperature_reduced_celsius = results.get('temperature_reduced', 0)
                    intervention.mystery_solved = results.get('mystery_solved', False)
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            return False
    
    async def get_current_hamster_stats(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get current stats for all three hamsters"""
        try:
            stats = {}
            
            for hamster in ['steve', 'bob', 'carl']:
                query = select(HamstersIndividualStats).where(
                    HamstersIndividualStats.hamster_name == hamster
                )
                
                if user_id:
                    query = query.where(HamstersIndividualStats.user_id == user_id)
                    
                query = query.order_by(HamstersIndividualStats.timestamp.desc()).limit(1)
                
                result = await self.db.execute(query)
                hamster_stats = result.scalar_one_or_none()
                
                if hamster_stats:
                    stats[hamster] = {
                        'beer_count': hamster_stats.beer_count,
                        'risk_tolerance': hamster_stats.risk_tolerance,
                        'current_task': hamster_stats.current_task,
                        'duct_tape_love': hamster_stats.duct_tape_love,
                        'last_updated': hamster_stats.timestamp
                    }
                else:
                    # Default stats if none exist
                    stats[hamster] = {
                        'beer_count': 2 if hamster == 'steve' else 4 if hamster == 'bob' else 3,
                        'risk_tolerance': 0.3 if hamster == 'steve' else 0.8 if hamster == 'bob' else 0.5,
                        'current_task': None,
                        'duct_tape_love': 0.5 if hamster == 'steve' else 0.6 if hamster == 'bob' else 1.0,
                        'last_updated': None
                    }
            
            return stats
            
        except Exception as e:
            return {
                'steve': {'beer_count': 2, 'risk_tolerance': 0.3, 'current_task': None, 'duct_tape_love': 0.5},
                'bob': {'beer_count': 4, 'risk_tolerance': 0.8, 'current_task': None, 'duct_tape_love': 0.6},
                'carl': {'beer_count': 3, 'risk_tolerance': 0.5, 'current_task': None, 'duct_tape_love': 1.0}
            }
    
    async def calculate_engineering_stats(
        self,
        days_back: int = 30,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate aggregate engineering statistics"""
        try:
            since = datetime.utcnow() - timedelta(days=days_back)
            
            # Get intervention stats
            intervention_query = select(
                func.count(HamstersInfrastructureIntervention.id).label('total_interventions'),
                func.count(
                    HamstersInfrastructureIntervention.id
                ).filter(
                    HamstersInfrastructureIntervention.status == 'completed'
                ).label('successful_interventions'),
                func.sum(HamstersInfrastructureIntervention.space_freed_gb).label('total_space_freed'),
                func.sum(HamstersInfrastructureIntervention.beer_consumed).label('total_beer')
            ).where(
                HamstersInfrastructureIntervention.started_at >= since
            )
            
            if user_id:
                intervention_query = intervention_query.where(
                    HamstersInfrastructureIntervention.user_id == user_id
                )
            
            result = await self.db.execute(intervention_query)
            intervention_stats = result.first()
            
            # Get duct tape stats
            tape_query = select(
                func.sum(HamstersDuctTapeUsage.strips_used).label('total_strips')
            ).where(
                HamstersDuctTapeUsage.timestamp >= since
            )
            
            if user_id:
                tape_query = tape_query.where(HamstersDuctTapeUsage.user_id == user_id)
            
            tape_result = await self.db.execute(tape_query)
            tape_stats = tape_result.first()
            
            # Get supply closet raids
            raid_query = select(
                func.count(HamstersSupplyClosetRaid.id).label('total_raids')
            ).where(
                HamstersSupplyClosetRaid.timestamp >= since
            )
            
            if user_id:
                raid_query = raid_query.where(HamstersSupplyClosetRaid.user_id == user_id)
            
            raid_result = await self.db.execute(raid_query)
            raid_stats = raid_result.first()
            
            # Calculate rates
            total_interventions = int(intervention_stats.total_interventions or 0)
            successful_interventions = int(intervention_stats.successful_interventions or 0)
            
            return {
                'period_days': days_back,
                'total_interventions': total_interventions,
                'successful_interventions': successful_interventions,
                'success_rate': successful_interventions / total_interventions if total_interventions > 0 else 0,
                'total_space_freed_gb': float(intervention_stats.total_space_freed or 0),
                'total_beer_consumed': int(intervention_stats.total_beer or 0),
                'total_duct_tape_used': int(tape_stats.total_strips or 0),
                'total_supply_closet_raids': int(raid_stats.total_raids or 0),
                'average_beer_per_intervention': (
                    int(intervention_stats.total_beer or 0) / total_interventions 
                    if total_interventions > 0 else 0
                ),
                'average_space_freed_per_intervention': (
                    float(intervention_stats.total_space_freed or 0) / total_interventions 
                    if total_interventions > 0 else 0
                )
            }
            
        except Exception as e:
            return {
                'period_days': days_back,
                'error': str(e)
            }