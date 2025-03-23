from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Optional
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.system import OptimizationProfile
from app.optimization.auto_tuner import AutoTuner
from app.optimization.resource_monitor import ResourceMonitor
from app.optimization.pattern_analyzer import PatternAnalyzer

router = APIRouter()


@router.get("/metrics/current")
async def get_current_metrics(
    current_user: User = Depends(get_current_user)
):
    """
    Get current system metrics.
    
    Returns real-time metrics about CPU, memory, disk, and network usage.
    """
    monitor = ResourceMonitor()
    metrics = await monitor.collect_metrics()
    return metrics


@router.get("/recommendations")
async def get_optimization_recommendations(
    current_user: User = Depends(get_current_user)
):
    """
    Get optimization recommendations based on current system state.
    
    Analyzes current system metrics and returns recommended tuning actions.
    """
    tuner = AutoTuner()
    recommendations = await tuner.get_tuning_recommendations()
    return [
        {
            "parameter": rec.parameter.value,
            "current_value": rec.current_value,
            "recommended_value": rec.new_value,
            "confidence": rec.confidence,
            "impact_score": rec.impact_score,
            "reason": rec.reason
        }
        for rec in recommendations
    ]


@router.post("/profiles/{profile_id}/apply")
async def apply_optimization_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Apply an optimization profile to the system.
    
    Retrieves the specified profile and applies its settings to the system.
    """
    # Get the profile
    query = select(OptimizationProfile).where(
        OptimizationProfile.id == str(profile_id),
        OptimizationProfile.user_id == current_user.id
    )
    
    result = await db.execute(query)
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization profile not found"
        )
    
    # Initialize the auto-tuner
    tuner = AutoTuner()
    
    # Apply the profile settings
    tuning_results = []
    for setting_key, setting_value in profile.settings.items():
        # Convert profile settings to tuning actions
        try:
            result = await tuner.apply_tuning({
                "parameter": setting_key,
                "current_value": "current",  # This would be replaced with actual current value
                "new_value": setting_value,
                "confidence": 1.0,  # User-selected settings have 100% confidence
                "impact_score": 0.8,
                "reason": f"Applied from profile: {profile.name}"
            })
            tuning_results.append(result)
        except Exception as e:
            tuning_results.append({
                "parameter": setting_key,
                "success": False,
                "error": str(e)
            })
    
    return {
        "profile_id": profile_id,
        "profile_name": profile.name,
        "applied_settings": tuning_results
    }


@router.post("/recommendations/apply")
async def apply_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Apply a specific optimization recommendation.
    
    Takes a recommendation ID and applies that specific tuning action.
    """
    tuner = AutoTuner()
    
    # Get current recommendations
    recommendations = await tuner.get_tuning_recommendations()
    
    if recommendation_id < 0 or recommendation_id >= len(recommendations):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    # Apply the selected recommendation
    selected_recommendation = recommendations[recommendation_id]
    result = await tuner.apply_tuning(selected_recommendation)
    
    return {
        "success": True if result and result.get("success") else False,
        "recommendation": {
            "parameter": selected_recommendation.parameter.value,
            "old_value": selected_recommendation.current_value,
            "new_value": selected_recommendation.new_value,
            "reason": selected_recommendation.reason
        },
        "result": result
    }


@router.get("/patterns")
async def get_system_patterns(
    current_user: User = Depends(get_current_user)
):
    """
    Get detected system usage patterns.
    
    Analyzes historical metrics to identify patterns in system usage.
    """
    analyzer = PatternAnalyzer()
    
    # For demo purposes, we'll create some mock metrics
    mock_metrics = {
        "cpu_usage": 85,
        "memory_usage": 70,
        "disk_usage": 65,
        "network_usage": 40,
        "process_count": 120,
        "additional": {
            "active_python_processes": 8,
            "load_average": [1.2, 1.0, 0.8]
        }
    }
    
    patterns = await analyzer.analyze(mock_metrics)
    summary = await analyzer.get_pattern_summary()
    
    return {
        "detected_patterns": patterns,
        "pattern_summary": summary
    }


@router.get("/history")
async def get_optimization_history(
    current_user: User = Depends(get_current_user)
):
    """
    Get history of applied optimizations.
    
    Returns a list of previously applied tuning actions and their results.
    """
    tuner = AutoTuner()
    
    # In a real implementation, this would fetch from a database
    # For now, we'll return the in-memory history
    return {
        "history": tuner.tuning_history,
        "active_tunings": tuner.active_tunings
    }
