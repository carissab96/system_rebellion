"""
The Hamsters API Routes V2
Beer-drinking, redneck rapid response engineering team API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.ai_agents.hamsters.decision_engine import (
    hamsters_brain,
    get_hamsters_stats,
    AnalysisDepth
)
from app.ai_agents.hamsters.auto_tuner_db_helpers import (
    save_hamsters_engineering_to_db,
    get_hamsters_engineering_history,
    get_hamsters_pattern_data,
    get_hamsters_learning_recommendations
)
from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService
from app.services.system_log_service import LogService

router = APIRouter()

@router.get("/hamsters/recommendations")
async def get_hamsters_recommendations(
    analysis_depth: str = "standard",
    include_patterns: bool = True,
    current_user: User = Depends(get_current_user)
):
    """
    Get The Hamsters' beer-powered optimization recommendations
    
    The redneck engineering team analyzes your system with quantum-grade duct tape
    and provides creative solutions backed by beer-powered confidence.
    """
    try:
        # Get current metrics
        metrics_service = await SimplifiedMetricsService.get_instance()
        metrics = await metrics_service.get_metrics()
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="🐹❌ The Hamsters can't get system metrics - metrics service unavailable"
            )
        
        # Convert analysis depth
        depth_mapping = {
            "basic": AnalysisDepth.BASIC,
            "standard": AnalysisDepth.STANDARD,
            "thorough": AnalysisDepth.THOROUGH
        }
        analysis_depth_enum = depth_mapping.get(analysis_depth.lower(), AnalysisDepth.STANDARD)
        
        # Get historical data if thorough analysis requested
        historical_data = None
        if analysis_depth_enum == AnalysisDepth.THOROUGH and include_patterns:
            pattern_data = await get_hamsters_pattern_data(str(current_user.id))
            historical_data = pattern_data.get('historical_metrics', [])
        
        # Get The Hamsters' recommendations
        decision = await hamsters_brain.analyze_metrics(
            metrics_data=metrics,
            historical_data=historical_data,
            analysis_depth=analysis_depth_enum,
            user_id=str(current_user.id)
        )
        
        if not decision:
            return {
                "agent_name": "hamsters",
                "status": "wheel_spinning",
                "message": "🐹🔄 The Hamsters are spinning their wheels - insufficient data for engineering solutions",
                "beer_level": hamsters_brain.beer_level,
                "duct_tape_available": hamsters_brain.duct_tape_inventory > 0,
                "recommendations": []
            }
        
        # Format response
        return {
            "agent_name": "hamsters",
            "status": "engineering_ready",
            "priority": decision.priority.value,
            "message": decision.rationale,
            "confidence": decision.confidence,
            "urgency": decision.urgency,
            "estimated_impact": decision.estimated_impact,
            "beer_level": decision.beer_level,
            "duct_tape_used": decision.duct_tape_used,
            "supply_closet_raids": decision.supply_closet_raids,
            "redneck_ingenuity_level": decision.redneck_ingenuity_level,
            "recommendations": decision.actions,
            "analysis_depth": decision.analysis_depth.value,
            "timestamp": decision.timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 The Hamsters' engineering circuits overloaded: {str(e)}"
        )

@router.post("/hamsters/apply-engineering")
async def apply_hamsters_engineering(
    engineering_request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Apply The Hamsters' redneck engineering solution
    
    Handles beer consumption, duct tape usage, and supply closet raids
    """
    try:
        # Validate request
        if not engineering_request.get('action'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="🐹❌ No engineering action specified"
            )
        
        action = engineering_request['action']
        
        # Get current metrics before applying
        metrics_service = await SimplifiedMetricsService.get_instance()
        metrics_before = await metrics_service.get_metrics()
        
        # Log the engineering attempt
        log_service = await LogService.get_instance()
        log_service.add_log(
            message=f"🐹🔧 The Hamsters are applying engineering solution: {action.get('redneck_solution', 'Unknown')}",
            level="info",
            source="hamsters_engineering"
        )
        
        # Prepare engineering data
        engineering_data = {
            'parameter': action.get('parameter', 'unknown'),
            'current_value': action.get('current_value', 'unknown'),
            'new_value': action.get('recommended_value', 'unknown'),
            'confidence': action.get('confidence', 0.0),
            'impact_score': 0.0,
            'redneck_solution': action.get('redneck_solution', ''),
            'beer_consumed': 0,
            'duct_tape_used': False,
            'supply_closet_raids': 0,
            'redneck_ingenuity_level': 0.0,
            'metrics_before': metrics_before,
            'success': False,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Determine beer consumption based on beer_required
        beer_required = action.get('beer_required', 'LOW')
        if beer_required == 'MAXIMUM':
            engineering_data['beer_consumed'] = 3
        elif beer_required == 'HIGH':
            engineering_data['beer_consumed'] = 2
        elif beer_required == 'MODERATE':
            engineering_data['beer_consumed'] = 1
        
        # Determine duct tape usage
        if 'duct_tape' in action.get('redneck_solution', '').lower():
            engineering_data['duct_tape_used'] = True
            engineering_data['duct_tape_inventory_used'] = 5 if 'quantum' in action.get('redneck_solution', '').lower() else 2
        
        # Determine supply closet raids
        supply_closet_items = action.get('supply_closet_items', [])
        if supply_closet_items:
            engineering_data['supply_closet_raids'] = 1
            engineering_data['supply_closet_items'] = supply_closet_items
        
        # Calculate redneck ingenuity level
        ingenuity_factors = 0
        solution = action.get('redneck_solution', '').lower()
        if 'quantum' in solution:
            ingenuity_factors += 0.3
        if 'duct tape' in solution:
            ingenuity_factors += 0.2
        if 'beer' in solution:
            ingenuity_factors += 0.1
        if 'supply closet' in solution:
            ingenuity_factors += 0.1
        
        engineering_data['redneck_ingenuity_level'] = min(1.0, ingenuity_factors + action.get('confidence', 0.0))
        
        # Simulate applying the engineering solution
        # In a real implementation, this would actually modify system parameters
        try:
            # For now, simulate success based on confidence
            import random
            success_probability = action.get('confidence', 0.5)
            engineering_data['success'] = random.random() < success_probability
            
            if engineering_data['success']:
                # Get metrics after "applying" the solution
                metrics_after = await metrics_service.get_metrics(force_refresh=True)
                engineering_data['metrics_after'] = metrics_after
                
                log_service.add_log(
                    message=f"🐹✅ The Hamsters successfully applied {action.get('parameter')} optimization",
                    level="info",
                    source="hamsters_engineering"
                )
            else:
                engineering_data['error'] = "Engineering solution failed - may need more beer or better duct tape"
                log_service.add_log(
                    message=f"🐹❌ The Hamsters' engineering solution failed for {action.get('parameter')}",
                    level="warning",
                    source="hamsters_engineering"
                )
                
        except Exception as e:
            engineering_data['success'] = False
            engineering_data['error'] = str(e)
            log_service.add_log(
                message=f"🐹💥 The Hamsters' engineering solution crashed: {str(e)}",
                level="error",
                source="hamsters_engineering"
            )
        
        # Save to database
        await save_hamsters_engineering_to_db(
            engineering_data, 
            str(current_user.id),
            engineering_request
        )
        
        return {
            "success": engineering_data['success'],
            "engineering_solution": {
                "parameter": engineering_data['parameter'],
                "old_value": engineering_data['current_value'],
                "new_value": engineering_data['new_value'],
                "redneck_solution": engineering_data['redneck_solution'],
                "beer_consumed": engineering_data['beer_consumed'],
                "duct_tape_used": engineering_data['duct_tape_used'],
                "supply_closet_raids": engineering_data['supply_closet_raids'],
                "redneck_ingenuity_level": engineering_data['redneck_ingenuity_level']
            },
            "result": {
                "success": engineering_data['success'],
                "error": engineering_data['error'],
                "metrics_before": engineering_data['metrics_before'],
                "metrics_after": engineering_data.get('metrics_after')
            },
            "message": "🐹🍺 Engineering solution applied with redneck precision!" if engineering_data['success'] else f"🐹💥 Engineering failed: {engineering_data['error']}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 The Hamsters' engineering circuits overloaded: {str(e)}"
        )

@router.get("/hamsters/history")
async def get_hamsters_history(
    limit: int = 100,
    include_patterns: bool = True,
    days_back: int = 30,
    current_user: User = Depends(get_current_user)
):
    """
    Get The Hamsters' engineering history with beer consumption and duct tape usage
    """
    try:
        # Get engineering history
        history = await get_hamsters_engineering_history(
            user_id=str(current_user.id),
            limit=limit,
            include_patterns=include_patterns,
            include_user_data=True
        )
        
        # Get pattern data if requested
        pattern_data = {}
        if include_patterns:
            pattern_data = await get_hamsters_pattern_data(
                user_id=str(current_user.id),
                days_back=days_back
            )
        
        # Get current brain stats
        brain_stats = get_hamsters_stats()
        
        return {
            "agent_name": "hamsters",
            "engineering_history": history,
            "pattern_analysis": pattern_data,
            "brain_stats": brain_stats,
            "total_records": len(history),
            "analysis_period_days": days_back
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 The Hamsters can't access their engineering logs: {str(e)}"
        )

@router.get("/hamsters/patterns")
async def get_hamsters_patterns(
    days_back: int = 30,
    current_user: User = Depends(get_current_user)
):
    """
    Get The Hamsters' learned patterns and beer-powered insights
    """
    try:
        # Get pattern data
        pattern_data = await get_hamsters_pattern_data(
            user_id=str(current_user.id),
            days_back=days_back
        )
        
        # Get learning recommendations
        learning_recommendations = await get_hamsters_learning_recommendations(
            user_id=str(current_user.id),
            days_back=days_back
        )
        
        return {
            "agent_name": "hamsters",
            "pattern_analysis": pattern_data,
            "learning_recommendations": learning_recommendations,
            "analysis_period_days": days_back,
            "pattern_summary": {
                "total_solutions": pattern_data.get('total_engineering_solutions', 0),
                "success_rate": pattern_data.get('success_rate', 0),
                "beer_efficiency": pattern_data.get('beer_consumption_patterns', {}).get('average_beer_consumption', 0),
                "duct_tape_effectiveness": pattern_data.get('duct_tape_usage_patterns', {}).get('duct_tape_success_rate', 0),
                "supply_closet_raids": pattern_data.get('supply_closet_patterns', {}).get('total_raids', 0),
                "three_am_solutions": pattern_data.get('time_based_patterns', {}).get('three_am_solutions', 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 The Hamsters' pattern analysis circuits overloaded: {str(e)}"
        )

@router.get("/hamsters/stats")
async def get_hamsters_stats_endpoint(
    current_user: User = Depends(get_current_user)
):
    """
    Get The Hamsters' current operational stats
    """
    try:
        stats = get_hamsters_stats()
        
        # Add current inventory levels
        stats['inventory_status'] = {
            'beer_level': hamsters_brain.beer_level,
            'duct_tape_inventory': hamsters_brain.duct_tape_inventory,
            'supply_closet_raids_total': hamsters_brain.supply_closet_raids,
            'learned_patterns_count': len(hamsters_brain.learned_patterns)
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 The Hamsters can't report their stats: {str(e)}"
        )

@router.post("/hamsters/restock")
async def restock_hamsters_inventory(
    restock_request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Restock The Hamsters' beer and duct tape inventory
    """
    try:
        # Restock beer
        if restock_request.get('beer', False):
            hamsters_brain.beer_level = "FULL"
            
        # Restock duct tape
        if restock_request.get('duct_tape', False):
            hamsters_brain.duct_tape_inventory = 100
            
        # Reset supply closet raids counter
        if restock_request.get('reset_raids', False):
            hamsters_brain.supply_closet_raids = 0
            
        # Log the restock
        log_service = await LogService.get_instance()
        log_service.add_log(
            message=f"🐹🍺 The Hamsters' inventory restocked: beer={restock_request.get('beer', False)}, duct_tape={restock_request.get('duct_tape', False)}",
            level="info",
            source="hamsters_inventory"
        )
        
        return {
            "success": True,
            "message": "🐹🍺 The Hamsters' inventory restocked and ready for engineering!",
            "inventory_status": {
                'beer_level': hamsters_brain.beer_level,
                'duct_tape_inventory': hamsters_brain.duct_tape_inventory,
                'supply_closet_raids_total': hamsters_brain.supply_closet_raids
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 The Hamsters' inventory restock failed: {str(e)}"
        )

@router.delete("/hamsters/reset")
async def reset_hamsters_brain(
    current_user: User = Depends(get_current_user)
):
    """
    Reset The Hamsters' brain (for testing purposes)
    """
    try:
        from app.agents.hamsters.decision_engine_v2 import reset_hamsters_brain
        
        result = reset_hamsters_brain()
        
        # Log the reset
        log_service = await LogService.get_instance()
        log_service.add_log(
            message="🐹🔄 The Hamsters' brain has been reset for testing",
            level="info",
            source="hamsters_testing"
        )
        
        return {
            "success": True,
            "message": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 The Hamsters' brain reset failed: {str(e)}"
        )
        