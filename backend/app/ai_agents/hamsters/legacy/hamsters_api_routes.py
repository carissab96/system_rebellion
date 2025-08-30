# hamsters_api_routes.py - Repurposed for infrastructure management
"""
The Hamsters API Routes - Direct Infrastructure Access
Because sometimes you need to call in the specialists at 3am
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from datetime import datetime

from app.ai_agents.hamsters.decision_engine import (
    analyze_infrastructure,
    handle_emergency,
    get_hamster_stats,
    restock_supplies
)

router = APIRouter(prefix="/api/hamsters", tags=["hamsters"])

@router.post("/emergency-intervention")
async def emergency_intervention(
    crisis_type: str,
    severity: str = "HIGH",
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    3am emergency call - wake the Hamsters!
    
    Crisis types: disk_full, fragmentation_critical, hardware_failure, mystery_noise
    """
    try:
        result = await handle_emergency(crisis_type, severity)
        return {
            "status": "success",
            "message": "*SQUEAK* ON IT! *SQUEAK*",
            "intervention": result,
            "human_translation": f"Hamsters responding to {crisis_type}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hamsters confused: {str(e)}")

@router.post("/disk-cleanup")
async def request_disk_cleanup(
    target_path: Optional[str] = None,
    aggressive: bool = False,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Request disk cleanup - Hamsters will evaluate and clean
    """
    cleanup_type = "aggressive_cleanup" if aggressive else "standard_cleanup"
    return {
        "status": "queued",
        "cleanup_type": cleanup_type,
        "hamster_response": "*squeak* BEER *squeak* DELETE *squeak*",
        "human_translation": f"Hamsters will perform {cleanup_type}",
        "estimated_duration": "Two beers"
    }

@router.get("/supply-closet-inventory")
async def check_supply_closet() -> Dict[str, Any]:
    """
    Check what's in the supply closet
    """
    return {
        "duct_tape": {
            "regular": 50,
            "premium": 20,
            "quantum": 5,
            "carls_special": 1
        },
        "mystery_tools": [
            "thing_that_goes_beep",
            "the_good_screwdriver",
            "bobs_favorite_wrench"
        ],
        "beer_status": "Well stocked",
        "last_inventory": "Steve counted everything twice"
    }

@router.get("/beer-status")
async def get_beer_status() -> Dict[str, Any]:
    """
    Critical operational metric
    """
    stats = get_hamster_stats()
    return {
        "collective_beer_level": stats['collective_stats']['beer_level'],
        "individual_consumption": {
            "steve": stats['individual_stats']['steve']['beer_count'],
            "bob": stats['individual_stats']['bob']['beer_count'],
            "carl": stats['individual_stats']['carl']['beer_count']
        },
        "operational_status": "OPTIMAL" if stats['collective_stats']['beer_level'] == 'optimal' else "NEED_ADJUSTMENT",
        "is_3am": stats['collective_stats']['is_prime_time']
    }

@router.post("/restock-supplies")
async def restock_hamster_supplies() -> Dict[str, Any]:
    """
    Restock beer and duct tape
    """
    result = restock_supplies()
    return {
        "status": "success",
        "message": result,
        "hamster_response": "*happy squeaking*"
    }