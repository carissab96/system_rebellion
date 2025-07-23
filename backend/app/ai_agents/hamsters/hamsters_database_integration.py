"""
Database integration for Hamster infrastructure operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.hamsters_models import (
    HamsterIntervention,
    HamsterCommunicationLog,
    DuctTapeUsageLog,
    BeerConsumptionLog,
    SupplyClosetRaid,
    InfrastructureMetrics
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
            intervention = HamsterIntervention(
                type=intervention_data['type'],
                status=intervention_data['status'],
                steve_action=intervention_data['steve_action'],
                bob_action=intervention_data['bob_action'],
                carl_action=intervention_data['carl_action'],
                beer_consumed=intervention_data['beer_consumed'],
                tools_used=intervention_data['tools_used'],
                space_freed_gb=intervention_data.get('space_freed_gb', 0),
                started_at=datetime.utcnow()
            )
            
            self.db.add(intervention)
            await self.db.commit()
            
            return {
                'status': 'success',
                'intervention_id': intervention.id,
                'message': 'Intervention logged successfully'
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                'status': 'error',
                'message': f'Failed to log intervention: {str(e)}'
            }
    
    async def log_communication(
        self,
        source_hamster: str,
        squeaks: str,
        translation: str,
        target_agent: Optional[str] = None
    ) -> None:
        """Log Hamster communication attempts"""
        try:
            comm_log = HamsterCommunicationLog(
                source_hamster=source_hamster,
                audible_squeaks=squeaks,
                human_translation=translation,
                target_agent=target_agent,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(comm_log)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            # Hamsters don't care if logging fails
            
    async def track_duct_tape_usage(
        self,
        grade: str,
        strips_used: int,
        purpose: str,
        used_by: str = "carl"
    ) -> None:
        """Track duct tape consumption"""
        try:
            usage = DuctTapeUsageLog(
                grade=grade,
                strips_used=strips_used,
                purpose=purpose,
                used_by=used_by,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(usage)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            
    async def log_beer_consumption(
        self,
        hamster_name: str,
        beers: int,
        occasion: str
    ) -> None:
        """Track beer consumption for operational metrics"""
        try:
            consumption = BeerConsumptionLog(
                hamster_name=hamster_name,
                beers_consumed=beers,
                occasion=occasion,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(consumption)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            
    async def get_recent_interventions(
        self,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get recent intervention history"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            
            query = select(HamsterIntervention).where(
                HamsterIntervention.started_at >= since
            ).order_by(HamsterIntervention.started_at.desc())
            
            result = await self.db.execute(query)
            interventions = result.scalars().all()
            
            return [
                {
                    'id': i.id,
                    'type': i.type,
                    'status': i.status,
                    'space_freed_gb': i.space_freed_gb,
                    'beer_consumed': i.beer_consumed,
                    'duration': (i.completed_at - i.started_at).seconds if i.completed_at else None
                }
                for i in interventions
            ]
            
        except Exception as e:
            return []
            
    async def get_infrastructure_metrics(
        self,
        metric_type: str
    ) -> Dict[str, Any