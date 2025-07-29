"""
The Hamsters API Routes V3
Steve, Bob, and Carl's Infrastructure Chaos Engineering Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.ai_agents.hamsters.decision_engine_sbcV3 import (
    hamsters_brain,
    analyze_infrastructure,
    handle_emergency,
    get_hamster_stats,
    restock_supplies,
    HamstersPriority
)
from app.ai_agents.hamsters.hamsters_database_integration import HamstersDatabaseIntegration
from app.ai_agents.hamsters.hamsters_websocket_integration import broadcast_hamster_event
from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService
from app.services.system_log_service import LogService

router = APIRouter()

@router.get("/hamsters/recommendations")
async def get_hamsters_recommendations(
    infrastructure_focus: str = "general",  # general, disk, memory, thermal
    include_squeaks: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get The Hamsters' infrastructure recommendations
    
    Steve (careful), Bob (wild), and Carl (duct tape expert) analyze your 
    infrastructure with beer-powered wisdom and quantum-grade duct tape.
    
    Returns both squeaks and human translations.
    """
    try:
        # Get current metrics
        metrics_service = await SimplifiedMetricsService.get_instance()
        metrics = await metrics_service.get_metrics()
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="🐹❌ *confused squeaking* Can't see the infrastructure!"
            )
        
        # Focus on specific infrastructure area if requested
        if infrastructure_focus == "disk":
            metrics = {"disk": metrics.get("disk", {}), "system": metrics.get("system", {})}
        elif infrastructure_focus == "memory":
            metrics = {"memory": metrics.get("memory", {}), "system": metrics.get("system", {})}
        elif infrastructure_focus == "thermal":
            metrics = {"system": metrics.get("system", {}), "temperature": metrics.get("temperature", {})}
        
        # Get The Hamsters' analysis
        decision = await analyze_infrastructure(
            metrics_data=metrics,
            user_id=str(current_user.id)
        )
        
        if not decision:
            return {
                "agent_name": "hamsters",
                "status": "all_good",
                "message": "*squeak* BEER BREAK *squeak*",
                "human_translation": "Infrastructure running smoothly - time for beer!",
                "individual_assessments": {
                    "steve": "Everything looks stable",
                    "bob": "Nothing to break... I mean fix!",
                    "carl": "Duct tape inventory preserved"
                },
                "beer_level": hamsters_brain.current_beer_level.value,
                "recommendations": []
            }
        
        # Log the decision
        db_integration = HamstersDatabaseIntegration(db)
        await db_integration.log_intervention({
            'type': decision.intervention_type,
            'status': 'recommended',
            'steve_action': decision.steve_assessment,
            'bob_action': decision.bob_suggestion,
            'carl_action': decision.carl_calculation,
            'beer_consumed': 0,
            'tools_used': decision.tools_required,
            'user_id': str(current_user.id)
        })
        
        # Format response with both squeaks and translations
        response = {
            "agent_name": "hamsters",
            "status": "intervention_needed",
            "priority": decision.priority.value,
            "hamster_communications": {
                "actual_squeaks": decision.actual_squeaks if include_squeaks else "[squeaks hidden]",
                "human_translation": decision.human_translation
            },
            "individual_assessments": {
                "steve": decision.steve_assessment,
                "bob": decision.bob_suggestion,
                "carl": decision.carl_calculation
            },
            "telepathic_consensus": decision.telepathic_consensus,
            "confidence": decision.confidence,
            "urgency": decision.urgency,
            "intervention_type": decision.intervention_type,
            "tools_required": decision.tools_required,
            "beer_consumption_estimate": decision.beer_consumption_estimate,
            "duct_tape_grade": decision.duct_tape_grade.value,
            "estimated_duration": decision.estimated_duration,
            "timestamp": decision.timestamp.isoformat()
        }
        
        # Add WebSocket notification
        await broadcast_hamster_event({
            'type': 'recommendation',
            'priority': decision.priority.value,
            'squeaks': decision.actual_squeaks,
            'translation': decision.human_translation
        })
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 *panicked squeaking* The Hamsters are confused: {str(e)}"
        )

@router.post("/hamsters/apply-engineering")
async def apply_hamsters_engineering(
    engineering_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Apply The Hamsters' infrastructure solution
    
    Steve supervises, Bob executes enthusiastically, Carl applies duct tape.
    Requires consensus (at least 2/3 hamsters must agree).
    """
    try:
        # Validate request
        intervention_type = engineering_request.get('intervention_type')
        if not intervention_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="🐹❌ *confused squeaking* What are we fixing?"
            )
        
        # Check hamster consensus
        steve_agrees = engineering_request.get('steve_approved', False)
        bob_agrees = engineering_request.get('bob_approved', True)  # Bob always agrees
        carl_agrees = engineering_request.get('carl_approved', False)
        
        consensus_count = sum([steve_agrees, bob_agrees, carl_agrees])
        if consensus_count < 2:
            return {
                "success": False,
                "message": "*argumentative squeaking*",
                "human_translation": "The Hamsters can't agree on the approach",
                "hamster_votes": {
                    "steve": steve_agrees,
                    "bob": bob_agrees,
                    "carl": carl_agrees
                },
                "suggestion": "Need at least 2 hamsters to agree"
            }
        
        # Get current metrics before applying
        metrics_service = await SimplifiedMetricsService.get_instance()
        metrics_before = await metrics_service.get_metrics()
        
        # Log the engineering attempt
        log_service = await LogService.get_instance()
        log_service.add_log(
            message=f"🐹🔧 The Hamsters are applying {intervention_type}",
            level="info",
            source="hamsters_engineering"
        )
        
        # Apply the infrastructure fix
        result = await hamsters_brain.perform_infrastructure_magic(
            intervention_type,
            metrics_before
        )
        
        # Get metrics after
        metrics_after = await metrics_service.get_metrics(force_refresh=True)
        
        # Save to database
        db_integration = HamstersDatabaseIntegration(db)
        await db_integration.log_intervention({
            'type': intervention_type,
            'status': 'completed' if result['success'] else 'failed',
            'steve_action': result['hamster_actions'].get('steve', ''),
            'bob_action': result['hamster_actions'].get('bob', ''),
            'carl_action': result['hamster_actions'].get('carl', ''),
            'beer_consumed': result['beer_consumed'],
            'tools_used': engineering_request.get('tools', []),
            'space_freed_gb': result.get('space_freed', 0),
            'user_id': str(current_user.id)
        })
        
        # Track duct tape usage
        await db_integration.track_duct_tape_usage(
            grade=engineering_request.get('duct_tape_grade', 'regular'),
            strips_used=result.get('duct_tape_strips', 1),
            purpose=intervention_type,
            used_by='carl'
        )
        
        # Track beer consumption
        beer_per_hamster = result['beer_consumed'] / 3
        for hamster in ['steve', 'bob', 'carl']:
            await db_integration.log_beer_consumption(
                hamster_name=hamster,
                beers=int(beer_per_hamster * (1.2 if hamster == 'bob' else 0.8 if hamster == 'steve' else 1)),
                occasion=intervention_type
            )
        
        # Broadcast success
        background_tasks.add_task(
            broadcast_hamster_event,
            {
                'type': 'intervention_complete',
                'intervention': intervention_type,
                'success': result['success'],
                'squeaks': result['communication']['hamster_celebration'],
                'translation': result['communication']['human_readable']
            }
        )
        
        return {
            "success": result['success'],
            "intervention_type": intervention_type,
            "hamster_actions": result['hamster_actions'],
            "hamster_communication": {
                "celebration": result['communication']['hamster_celebration'],
                "human_readable": result['communication']['human_readable']
            },
            "metrics_improvement": {
                "space_freed": result.get('space_freed', 0),
                "improvements": result.get('improvements', {})
            },
            "resources_consumed": {
                "beer": result['beer_consumed'],
                "duct_tape": result.get('carl_duct_tape_application', 'standard application')
            },
            "duration": str(result['end_time'] - result['start_time'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 *panicked squeaking* Engineering failed: {str(e)}"
        )

@router.post("/hamsters/emergency")
async def hamster_emergency_response(
    background_tasks: BackgroundTasks,
    crisis_type: str,
    severity: str = "HIGH",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    3AM EMERGENCY CALL - WAKE THE HAMSTERS!
    
    Crisis types: disk_full, fragmentation_critical, hardware_failure, 
                  thermal_event, mystery_noise
    """
    try:
        # Validate crisis
        valid_crises = ['disk_full', 'fragmentation_critical', 'hardware_failure', 
                       'thermal_event', 'mystery_noise']
        
        if crisis_type not in valid_crises:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown crisis. Valid types: {valid_crises}"
            )
        
        # WAKE THE HAMSTERS!
        result = await handle_emergency(crisis_type, severity)
        
        # Log emergency intervention
        db_integration = HamstersDatabaseIntegration(db)
        await db_integration.log_intervention({
            'type': f'emergency_{crisis_type}',
            'status': 'in_progress',
            'steve_action': result['hamster_response']['steve_action'],
            'bob_action': result['hamster_response']['bob_action'],
            'carl_action': result['hamster_response']['carl_action'],
            'beer_consumed': 6,  # Emergency consumption
                'tools_used': result['hamster_response']['tools_deployed'],
            'user_id': str(current_user.id)
        })
        
        # Emergency beer consumption
        await db_integration.log_beer_consumption('steve', 3, f'emergency_{crisis_type}')
        await db_integration.log_beer_consumption('bob', 5, f'emergency_{crisis_type}')
        await db_integration.log_beer_consumption('carl', 4, f'emergency_{crisis_type}')
        
        # Broadcast emergency
        background_tasks.add_task(
            broadcast_hamster_event,
            {
                'type': 'emergency_response',
                'crisis': crisis_type,
                'severity': severity,
                'status': 'HAMSTERS_RESPONDING',
                'message': '*LOUD EMERGENCY SQUEAKING*'
            }
        )
        
        return {
            "status": "emergency_response_active",
            "crisis_type": crisis_type,
            "severity": severity,
            "hamster_response": result['hamster_response'],
            "communication": result['communication_log'],
            "estimated_resolution": result['hamster_response'].get('expected_result', 'Unknown'),
            "message": "🐹🚨 THE HAMSTERS ARE ON IT!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 Emergency response failed: {str(e)}"
        )

@router.get("/hamsters/history")
async def get_hamsters_history(
    limit: int = 100,
    include_communications: bool = True,
    days_back: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get The Hamsters' intervention history
    Includes beer consumption, duct tape usage, and squeak translations
    """
    try:
        db_integration = HamstersDatabaseIntegration(db)
        
        # Get intervention history
        interventions = await db_integration.get_recent_interventions(hours=days_back * 24)
        
        # Get communication logs if requested
        communications = []
        if include_communications:
            # This would fetch from hamster_communication_log table
            pass
        
        # Get current stats
        stats = get_hamster_stats()
        
        # Calculate totals
        total_beer = sum(i.get('beer_consumed', 0) for i in interventions)
        total_space_freed = sum(i.get('space_freed_gb', 0) for i in interventions)
        
        return {
            "agent_name": "hamsters",
            "intervention_history": interventions,
            "communication_logs": communications,
            "current_status": stats,
            "summary": {
                "total_interventions": len(interventions),
                "total_beer_consumed": total_beer,
                "total_space_freed_gb": total_space_freed,
                "average_duration": "Two beers",
                "most_common_intervention": "disk_cleanup",
                "three_am_interventions": sum(1 for i in interventions if 2 <= datetime.fromisoformat(str(i.get('started_at', ''))).hour <= 5)
            },
            "individual_stats": stats['individual_stats'],
            "analysis_period_days": days_back
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 Can't access history: {str(e)}"
        )

@router.get("/hamsters/communication-log")
async def get_hamster_communications(
    target_agent: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get The Hamsters' communication attempts
    See what they've been squeaking about and who understood them
    """
    try:
        # Get recent squeaks from brain
        recent_squeaks = hamsters_brain.squeak_history[-limit:]
        
        # Get telepathic conversations
        telepathic_log = hamsters_brain.telepathic_log[-limit:]
        
        # Filter by target agent if specified
        if target_agent:
            recent_squeaks = [s for s in recent_squeaks if s.get('target_agent') == target_agent]
        
        return {
            "agent_name": "hamsters",
            "communication_summary": {
                "total_squeaks": len(hamsters_brain.squeak_history),
                "understood_by_stick": True,  # Empathy
                "understood_by_qsp": True,    # Telepathy
                "understood_by_others": False
            },
            "recent_communications": recent_squeaks,
            "telepathic_conversations": telepathic_log,
            "translation_note": "Only The Stick (through empathy) and QSP (telepathically) understand Hamster squeaks"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 Communication logs inaccessible: {str(e)}"
        )

@router.get("/hamsters/supply-closet")
async def check_supply_closet(
    current_user: User = Depends(get_current_user)
):
    """
    Check The Hamsters' supply closet inventory
    """
    try:
        stats = get_hamster_stats()
        carl_inventory = stats['individual_stats']['carl']['duct_tape_inventory']
        
        return {
            "agent_name": "hamsters",
            "supply_closet_status": {
                "duct_tape_inventory": carl_inventory,
                "beer_status": stats['collective_stats']['beer_level'],
                "mystery_tools": [
                    "thing_that_goes_beep",
                    "the_good_screwdriver",
                    "bobs_favorite_wrench",
                    "percussive_maintenance_hammer",
                    "steves_label_maker"
                ],
                "emergency_supplies": {
                    "pizza_money": "available",
                    "backup_duct_tape": "hidden by carl",
                    "the_manual": "unopened",
                    "emergency_beer": "for medicinal purposes only"
                },
                "last_raid": f"{stats['collective_stats']['supply_closet_raids']} raids today"
            },
            "carl_notes": "Quantum duct tape should only be used in emergencies"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 Supply closet locked: {str(e)}"
        )

@router.post("/hamsters/restock")
async def restock_hamsters_inventory(
    restock_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Restock The Hamsters' beer and duct tape inventory
    Essential for continued operations
    """
    try:
        # Call restock function
        result = restock_supplies()
        
        # Log the restock
        log_service = await LogService.get_instance()
        items_restocked = []
        
        if restock_request.get('beer', False):
            items_restocked.append("beer")
        if restock_request.get('duct_tape', False):
            items_restocked.append("duct tape")
        if restock_request.get('mystery_tools', False):
            items_restocked.append("mystery tools")
            
        log_service.add_log(
            message=f"🐹🍺 Hamster supplies restocked: {', '.join(items_restocked)}",
            level="info",
            source="hamsters_inventory"
        )
        
        # Get updated stats
        stats = get_hamster_stats()
        
        return {
            "success": True,
            "message": result,
            "inventory_status": {
                "steve": {
                    "beer_count": stats['individual_stats']['steve']['beer_count'],
                    "status": "Ready for careful engineering"
                },
                "bob": {
                    "beer_count": stats['individual_stats']['bob']['beer_count'],
                    "status": "Has several wild ideas"
                },
                "carl": {
                    "beer_count": stats['individual_stats']['carl']['beer_count'],
                    "duct_tape_inventory": stats['individual_stats']['carl']['duct_tape_inventory'],
                    "status": "Duct tape optimally distributed"
                }
            },
            "collective_readiness": stats['collective_stats']['beer_level']
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 Restock failed: {str(e)}"
        )

@router.get("/hamsters/stats")
async def get_hamsters_stats_endpoint(
    current_user: User = Depends(get_current_user)
):
    """
    Get The Hamsters' current operational stats
    Individual stats for Steve, Bob, and Carl
    """
    try:
        stats = get_hamster_stats()
        
        # Add interpretive information
        stats['operational_assessment'] = {
            "steve_status": "Measuring twice, duct-taping once" if stats['individual_stats']['steve']['beer_count'] <= 3 else "Getting adventurous",
            "bob_status": "Ready for chaos" if stats['individual_stats']['bob']['beer_count'] >= 3 else "Needs more beer",
            "carl_status": f"{stats['individual_stats']['carl']['duct_tape_inventory']['quantum']} quantum tapes remaining",
            "collective_readiness": "OPTIMAL" if stats['collective_stats']['beer_level'] == 'optimal' else stats['collective_stats']['beer_level'],
            "is_3am": stats['collective_stats']['is_prime_time'],
            "recommendation": "Ready for infrastructure chaos!" if stats['collective_stats']['beer_level'] == 'optimal' else "May need beer adjustment"
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 Stats unavailable: {str(e)}"
        )

@router.delete("/hamsters/reset")
async def reset_hamsters_brain(
    confirm: bool = False,
    current_user: User = Depends(get_current_user)
):
    """
    Reset The Hamsters' brain (for testing purposes)
    WARNING: This will reset Steve, Bob, and Carl to default states
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="🐹⚠️ Set confirm=true to reset the Hamsters"
            )
        
        # Reset the brain
        global hamsters_brain
        from app.ai_agents.hamsters.decision_engine import HamstersBrainV3
        hamsters_brain = HamstersBrainV3()
        
        # Log the reset
        log_service = await LogService.get_instance()
        log_service.add_log(
            message="🐹🔄 The Hamsters' brain has been reset - Steve, Bob, and Carl are ready!",
            level="info",
            source="hamsters_testing"
        )
        
        return {
            "success": True,
            "message": "🐹🍺 The Hamsters' brain reset - beer restocked, duct tape reloaded!",
            "hamster_status": {
                "steve": "Cautiously optimistic",
                "bob": "Ready for anything",
                "carl": "Duct tape inventory verified"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🐹💥 Brain reset failed: {str(e)}"
        )