"""
Enhanced auto_tuner_db_helpers.py with Hamsters engineering support
Complete version with all pattern analysis functions
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from collections import Counter
from app.models.tuning_history import TuningHistory
from app.core.database import SessionLocal, AsyncSessionLocal

logger = logging.getLogger('Hamsters.Database')

async def save_hamsters_engineering_to_db(
    engineering_data: Dict, 
    user_id: str,
    hamsters_decision: Optional[Dict] = None
) -> None:
    """
    Save Hamsters engineering solution to database with full tracking
    
    Args:
        engineering_data: Dictionary containing engineering solution data
        user_id: ID of the user applying the engineering
        hamsters_decision: Optional HamstersOptimizationDecision data
    """
    try:
        from app.core.database import AsyncSessionLocal
        
        # Convert user_id to int if it's a string
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid user_id format: {user_id}, using default user_id=1")
            user_id_int = 1
        
        async with AsyncSessionLocal() as db:
            # Extract Hamsters-specific data
            hamsters_data = hamsters_decision or {}
            
            db_engineering = TuningHistory(
                user_id=user_id_int,
                parameter=engineering_data['parameter'],
                old_value=str(engineering_data.get('current_value', '')),
                new_value=str(engineering_data['new_value']),
                success=bool(engineering_data.get('success', False)),
                error=str(engineering_data.get('error', '')) if engineering_data.get('error') else None,
                metrics_before=engineering_data.get('metrics_before'),
                metrics_after=engineering_data.get('metrics_after'),
                
                # Hamsters engineering tracking
                beer_consumed=engineering_data.get('beer_consumed', 0),
                duct_tape_used=engineering_data.get('duct_tape_used', False),
                supply_closet_raids=engineering_data.get('supply_closet_raids', 0),
                redneck_ingenuity_level=engineering_data.get('redneck_ingenuity_level', 0.0),
                engineering_solution=engineering_data.get('redneck_solution', ''),
                beer_level_before=engineering_data.get('beer_level_before', 'FULL'),
                beer_level_after=engineering_data.get('beer_level_after', 'FULL'),
                duct_tape_inventory_used=engineering_data.get('duct_tape_inventory_used', 0),
                supply_closet_items=engineering_data.get('supply_closet_items', []),
                
                # Engineering quality metrics
                confidence_score=engineering_data.get('confidence', 0.0),
                impact_score=engineering_data.get('impact_score', 0.0),
                urgency_level=engineering_data.get('urgency', 'LOW'),
                priority_level=hamsters_data.get('priority', 'BEER_BREAK'),
                
                # Pattern learning data
                pattern_confidence=engineering_data.get('pattern_confidence', 0.0),
                learned_from_patterns=engineering_data.get('learned_from_patterns', False),
                historical_data_points=engineering_data.get('historical_data_points', 0)
            )
            
            db.add(db_engineering)
            await db.commit()
            await db.refresh(db_engineering)
            
            logger.info(f"🐹🍺 Saved Hamsters engineering solution to database: {engineering_data['parameter']}")
            
    except Exception as e:
        logger.error(f"🐹❌ Error saving Hamsters engineering to database: {str(e)}")

async def get_hamsters_engineering_history(
    user_id: Optional[str] = None, 
    limit: int = 100,
    include_patterns: bool = True,
    include_user_data: bool = True
) -> List[Dict]:
    """
    Get Hamsters engineering history with full tracking data and proper user relationships
    
    Args:
        user_id: Optional user ID to filter by
        limit: Maximum number of records to return
        include_patterns: Whether to include pattern learning data
        include_user_data: Whether to include user relationship data
        
    Returns:
        List of Hamsters engineering history records
    """
    try:
        from app.core.database import AsyncSessionLocal
        
        # Convert user_id to int if it's a string and not None
        user_id_int = None
        if user_id is not None:
            try:
                user_id_int = int(user_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id format: {user_id}, not filtering by user_id")
        
        async with AsyncSessionLocal() as db:
            # Build query with proper relationship loading
            query = select(TuningHistory)
            
            if include_user_data:
                query = query.options(selectinload(TuningHistory.user))
            
            if user_id_int is not None:
                query = query.where(TuningHistory.user_id == user_id_int)
                
            query = query.order_by(TuningHistory.timestamp.desc()).limit(limit)
            result = await db.execute(query)
            engineering_history = result.scalars().all()
            
            history_dicts = []
            for record in engineering_history:
                try:
                    # Create enhanced dictionary with Hamsters data
                    if include_user_data:
                        history_dict = await record.to_dict_async(db)
                    else:
                        history_dict = record.to_dict()
                    
                    # Add computed fields
                    history_dict['engineering_quality'] = _calculate_engineering_quality(record)
                    history_dict['beer_efficiency'] = _calculate_beer_efficiency(record)
                    history_dict['supply_closet_effectiveness'] = _calculate_supply_closet_effectiveness(record)
                    
                    if include_patterns:
                        history_dict['pattern_learning_score'] = _calculate_pattern_learning_score(record)
                    
                    history_dicts.append(history_dict)
                    
                except Exception as e:
                    logger.error(f"🐹❌ Error converting Hamsters record to dict: {str(e)}")
            
            return history_dicts
            
    except Exception as e:
        logger.error(f"🐹❌ Error getting Hamsters engineering history: {str(e)}")
        return []

async def get_hamsters_pattern_data(
    user_id: Optional[str] = None, 
    days_back: int = 30
) -> Dict[str, Any]:
    """
    Get pattern data for Hamsters learning algorithms
    
    Args:
        user_id: Optional user ID to filter by
        days_back: Number of days of history to analyze
        
    Returns:
        Dictionary containing pattern analysis data
    """
    try:
        from app.core.database import AsyncSessionLocal
        
        user_id_int = None
        if user_id is not None:
            try:
                user_id_int = int(user_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id format: {user_id}")
        
        async with AsyncSessionLocal() as db:
            # Get records from the last N days
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            query = select(TuningHistory).where(TuningHistory.timestamp >= cutoff_date)
            
            if user_id_int is not None:
                query = query.where(TuningHistory.user_id == user_id_int)
            
            result = await db.execute(query)
            records = result.scalars().all()
            
            # Analyze patterns
            pattern_data = {
                'total_engineering_solutions': len(records),
                'successful_solutions': len([r for r in records if r.success]),
                'success_rate': len([r for r in records if r.success]) / len(records) if records else 0,
                'beer_consumption_patterns': _analyze_beer_patterns(records),
                'duct_tape_usage_patterns': _analyze_duct_tape_patterns(records),
                'supply_closet_patterns': _analyze_supply_closet_patterns(records),
                'parameter_success_rates': _analyze_parameter_success_rates(records),
                'ingenuity_trends': _analyze_ingenuity_trends(records),
                'time_based_patterns': _analyze_time_patterns(records),
                'pattern_learning_effectiveness': _analyze_pattern_learning_effectiveness(records),
                'urgency_distribution': _analyze_urgency_distribution(records),
                'engineering_solution_effectiveness': _analyze_engineering_solution_effectiveness(records)
            }
            
            return pattern_data
            
    except Exception as e:
        logger.error(f"🐹❌ Error getting Hamsters pattern data: {str(e)}")
        return {}

async def get_hamsters_learning_recommendations(
    user_id: Optional[str] = None,
    days_back: int = 30
) -> List[Dict[str, Any]]:
    """
    Get learning-based recommendations from Hamsters engineering history
    
    Args:
        user_id: Optional user ID to filter by
        days_back: Number of days of history to analyze
        
    Returns:
        List of learning-based recommendations
    """
    try:
        pattern_data = await get_hamsters_pattern_data(user_id, days_back)
        recommendations = []
        
        # Beer consumption optimization
        beer_patterns = pattern_data.get('beer_consumption_patterns', {})
        if beer_patterns.get('average_beer_consumption', 0) > 2:
            recommendations.append({
                'type': 'beer_optimization',
                'recommendation': 'Consider pre-loading beer inventory for high-consumption scenarios',
                'confidence': 0.8,
                'based_on': f"Average beer consumption: {beer_patterns.get('average_beer_consumption', 0):.1f}"
            })
        
        # Duct tape usage optimization
        duct_tape_patterns = pattern_data.get('duct_tape_usage_patterns', {})
        if duct_tape_patterns.get('duct_tape_success_rate', 0) > 0.8:
            recommendations.append({
                'type': 'duct_tape_optimization',
                'recommendation': 'Quantum-grade duct tape solutions show high success rate - prioritize for complex problems',
                'confidence': 0.9,
                'based_on': f"Duct tape success rate: {duct_tape_patterns.get('duct_tape_success_rate', 0):.1%}"
            })
        
        # Supply closet optimization
        supply_closet_patterns = pattern_data.get('supply_closet_patterns', {})
        if supply_closet_patterns.get('raid_frequency', 0) > 0.3:
            recommendations.append({
                'type': 'supply_closet_optimization',
                'recommendation': 'High raid frequency detected - consider pre-stocking commonly used items',
                'confidence': 0.75,
                'based_on': f"Raid frequency: {supply_closet_patterns.get('raid_frequency', 0):.1%}"
            })
        
        # Parameter-specific recommendations
        param_success = pattern_data.get('parameter_success_rates', {})
        for param, success_rate in param_success.items():
            if success_rate < 0.6:
                recommendations.append({
                    'type': 'parameter_optimization',
                    'recommendation': f'Parameter {param} shows low success rate - consider alternative engineering approaches',
                    'confidence': 0.7,
                    'based_on': f"{param} success rate: {success_rate:.1%}"
                })
        
        return recommendations
        
    except Exception as e:
        logger.error(f"🐹❌ Error getting Hamsters learning recommendations: {str(e)}")
        return []

# Helper functions for pattern analysis

def _calculate_engineering_quality(record: TuningHistory) -> float:
    """Calculate overall engineering quality score"""
    quality_score = 0.0
    
    # Success contributes 40%
    if record.success:
        quality_score += 0.4
    
    # Confidence contributes 30%
    quality_score += (record.confidence_score or 0.0) * 0.3
    
    # Redneck ingenuity contributes 20%
    quality_score += (record.redneck_ingenuity_level or 0.0) * 0.2
    
    # Pattern learning contributes 10%
    if record.learned_from_patterns:
        quality_score += 0.1
    
    return min(1.0, quality_score)

def _calculate_beer_efficiency(record: TuningHistory) -> float:
    """Calculate beer consumption efficiency"""
    if not record.beer_consumed:
        return 1.0  # No beer needed = maximum efficiency
    
    # Lower beer consumption with higher success = better efficiency
    success_factor = 1.0 if record.success else 0.5
    beer_factor = 1.0 / (record.beer_consumed or 1)
    
    return min(1.0, success_factor * beer_factor)

def _calculate_supply_closet_effectiveness(record: TuningHistory) -> float:
    """Calculate supply closet raid effectiveness"""
    if not record.supply_closet_raids:
        return 1.0  # No raids needed = maximum effectiveness
    
    # Factor in success rate and ingenuity level
    success_factor = 1.0 if record.success else 0.3
    ingenuity_factor = record.redneck_ingenuity_level or 0.5
    raid_efficiency = 1.0 / (record.supply_closet_raids or 1)
    
    return min(1.0, success_factor * ingenuity_factor * raid_efficiency)

def _calculate_pattern_learning_score(record: TuningHistory) -> float:
    """Calculate pattern learning effectiveness score"""
    if not record.learned_from_patterns:
        return 0.0
    
    # Factor in pattern confidence and data points
    pattern_conf = record.pattern_confidence or 0.0
    data_points_factor = min(1.0, (record.historical_data_points or 0) / 100)
    
    return pattern_conf * data_points_factor

def _analyze_beer_patterns(records: List[TuningHistory]) -> Dict[str, Any]:
    """Analyze beer consumption patterns"""
    if not records:
        return {}
    
    beer_records = [r for r in records if r.beer_consumed]
    
    return {
        'total_beer_consumed': sum(r.beer_consumed for r in beer_records),
        'average_beer_consumption': sum(r.beer_consumed for r in beer_records) / len(beer_records) if beer_records else 0,
        'max_beer_consumption': max(r.beer_consumed for r in beer_records) if beer_records else 0,
        'beer_success_correlation': len([r for r in beer_records if r.success]) / len(beer_records) if beer_records else 0,
        'high_beer_solutions': len([r for r in beer_records if r.beer_consumed >= 3]),
        'beer_level_transitions': _analyze_beer_level_transitions(beer_records),
        'beer_consumption_by_parameter': _analyze_beer_by_parameter(beer_records),
        'beer_efficiency_trend': _calculate_beer_efficiency_trend(beer_records)
    }

def _analyze_duct_tape_patterns(records: List[TuningHistory]) -> Dict[str, Any]:
    """Analyze duct tape usage patterns"""
    if not records:
        return {}
    
    duct_tape_records = [r for r in records if r.duct_tape_used]
    
    return {
        'duct_tape_usage_rate': len(duct_tape_records) / len(records),
        'duct_tape_success_rate': len([r for r in duct_tape_records if r.success]) / len(duct_tape_records) if duct_tape_records else 0,
        'average_inventory_used': sum(r.duct_tape_inventory_used or 0 for r in duct_tape_records) / len(duct_tape_records) if duct_tape_records else 0,
        'total_inventory_used': sum(r.duct_tape_inventory_used or 0 for r in duct_tape_records),
        'duct_tape_by_urgency': _analyze_duct_tape_by_urgency(duct_tape_records),
        'quantum_grade_effectiveness': _analyze_quantum_grade_effectiveness(duct_tape_records)
    }

def _analyze_supply_closet_patterns(records: List[TuningHistory]) -> Dict[str, Any]:
    """Analyze supply closet raid patterns"""
    if not records:
        return {}
    
    raid_records = [r for r in records if r.supply_closet_raids]
    
    return {
        'raid_frequency': len(raid_records) / len(records),
        'average_raids_per_solution': sum(r.supply_closet_raids for r in raid_records) / len(raid_records) if raid_records else 0,
        'total_raids': sum(r.supply_closet_raids for r in raid_records),
        'raid_success_rate': len([r for r in raid_records if r.success]) / len(raid_records) if raid_records else 0,
        'most_used_items': _analyze_most_used_supply_items(raid_records),
        'raid_effectiveness_by_priority': _analyze_raid_effectiveness_by_priority(raid_records),
        'supply_closet_depletion_rate': _calculate_supply_closet_depletion_rate(raid_records)
    }

def _analyze_parameter_success_rates(records: List[TuningHistory]) -> Dict[str, float]:
    """Analyze success rates by parameter type"""
    if not records:
        return {}
    
    parameter_stats = {}
    for record in records:
        param = record.parameter
        if param not in parameter_stats:
            parameter_stats[param] = {'total': 0, 'successful': 0}
        
        parameter_stats[param]['total'] += 1
        if record.success:
            parameter_stats[param]['successful'] += 1
    
    return {
        param: stats['successful'] / stats['total'] 
        for param, stats in parameter_stats.items()
    }

def _analyze_ingenuity_trends(records: List[TuningHistory]) -> Dict[str, Any]:
    """Analyze redneck ingenuity trends over time"""
    if not records:
        return {}
    
    # Sort by timestamp
    sorted_records = sorted(records, key=lambda r: r.timestamp or datetime.min)
    
    ingenuity_levels = [r.redneck_ingenuity_level or 0.0 for r in sorted_records]
    
    return {
        'average_ingenuity': sum(ingenuity_levels) / len(ingenuity_levels) if ingenuity_levels else 0,
        'max_ingenuity': max(ingenuity_levels) if ingenuity_levels else 0,
        'ingenuity_trend': _calculate_trend(ingenuity_levels),
        'high_ingenuity_solutions': len([r for r in sorted_records if (r.redneck_ingenuity_level or 0) > 0.8]),
        'ingenuity_success_correlation': _calculate_ingenuity_success_correlation(sorted_records)
    }

def _analyze_time_patterns(records: List[TuningHistory]) -> Dict[str, Any]:
    """Analyze time-based patterns in engineering solutions"""
    if not records:
        return {}
    
    # Group by hour of day
    hour_stats = {}
    for record in records:
        if record.timestamp:
            hour = record.timestamp.hour
            if hour not in hour_stats:
                hour_stats[hour] = {'total': 0, 'successful': 0, 'beer_consumed': 0}
            
            hour_stats[hour]['total'] += 1
            if record.success:
                hour_stats[hour]['successful'] += 1
            hour_stats[hour]['beer_consumed'] += record.beer_consumed or 0
    
    # Find 3am patterns (The Hamsters' prime time)
    three_am_stats = hour_stats.get(3, {'total': 0, 'successful': 0, 'beer_consumed': 0})
    
    return {
        'three_am_solutions': three_am_stats['total'],
        'three_am_success_rate': three_am_stats['successful'] / three_am_stats['total'] if three_am_stats['total'] > 0 else 0,
        'three_am_beer_consumption': three_am_stats['beer_consumed'],
        'peak_engineering_hours': _find_peak_engineering_hours(hour_stats),
        'late_night_effectiveness': _calculate_late_night_effectiveness(hour_stats)
    }

def _analyze_pattern_learning_effectiveness(records: List[TuningHistory]) -> Dict[str, Any]:
    """Analyze how effective pattern learning has been"""
    if not records:
        return {}
    
    pattern_records = [r for r in records if r.learned_from_patterns]
    non_pattern_records = [r for r in records if not r.learned_from_patterns]
    
    return {
        'pattern_learning_usage_rate': len(pattern_records) / len(records),
        'pattern_learning_success_rate': len([r for r in pattern_records if r.success]) / len(pattern_records) if pattern_records else 0,
        'non_pattern_success_rate': len([r for r in non_pattern_records if r.success]) / len(non_pattern_records) if non_pattern_records else 0,
        'pattern_learning_improvement': _calculate_pattern_learning_improvement(pattern_records, non_pattern_records),
        'average_pattern_confidence': sum(r.pattern_confidence or 0 for r in pattern_records) / len(pattern_records) if pattern_records else 0,
        'pattern_data_points_average': sum(r.historical_data_points or 0 for r in pattern_records) / len(pattern_records) if pattern_records else 0
    }

def _analyze_urgency_distribution(records: List[TuningHistory]) -> Dict[str, Any]:
    """Analyze distribution of urgency levels"""
    if not records:
        return {}
    
    urgency_counts = Counter(r.urgency_level or 'UNKNOWN' for r in records)
    total_records = len(records)
    
    return {
        'urgency_distribution': {
            urgency: count / total_records 
            for urgency, count in urgency_counts.items()
        },
        'high_urgency_solutions': len([r for r in records if r.urgency_level in ['HIGH', 'CRITICAL']]),
        'urgency_success_rates': _calculate_urgency_success_rates(records)
    }

def _analyze_engineering_solution_effectiveness(records: List[TuningHistory]) -> Dict[str, Any]:
    """Analyze effectiveness of different engineering solutions"""
    if not records:
        return {}
    
    solution_stats = {}
    for record in records:
        solution = record.engineering_solution or 'UNKNOWN'
        # Group similar solutions
        solution_type = _categorize_engineering_solution(solution)
        
        if solution_type not in solution_stats:
            solution_stats[solution_type] = {'total': 0, 'successful': 0, 'beer_consumed': 0}
        
        solution_stats[solution_type]['total'] += 1
        if record.success:
            solution_stats[solution_type]['successful'] += 1
        solution_stats[solution_type]['beer_consumed'] += record.beer_consumed or 0
    
    return {
        'solution_effectiveness': {
            solution: stats['successful'] / stats['total'] 
            for solution, stats in solution_stats.items()
        },
        'most_effective_solutions': _find_most_effective_solutions(solution_stats),
        'beer_intensive_solutions': _find_beer_intensive_solutions(solution_stats)
    }

# Additional helper functions

def _analyze_beer_level_transitions(records: List[TuningHistory]) -> Dict[str, int]:
    """Analyze beer level transitions"""
    transitions = {}
    for record in records:
        before = record.beer_level_before or 'UNKNOWN'
        after = record.beer_level_after or 'UNKNOWN'
        transition = f"{before} → {after}"
        transitions[transition] = transitions.get(transition, 0) + 1
    
    return transitions

def _analyze_beer_by_parameter(records: List[TuningHistory]) -> Dict[str, float]:
    """Analyze beer consumption by parameter type"""
    param_beer = {}
    for record in records:
        param = record.parameter
        if param not in param_beer:
            param_beer[param] = {'total_beer': 0, 'count': 0}
        
        param_beer[param]['total_beer'] += record.beer_consumed or 0
        param_beer[param]['count'] += 1
    
    return {
        param: stats['total_beer'] / stats['count']
        for param, stats in param_beer.items()
    }

def _calculate_beer_efficiency_trend(records: List[TuningHistory]) -> str:
    """Calculate beer efficiency trend over time"""
    if len(records) < 2:
        return "INSUFFICIENT_DATA"
    
    # Sort by timestamp
    sorted_records = sorted(records, key=lambda r: r.timestamp or datetime.min)
    
    # Calculate efficiency for first and last half
    mid_point = len(sorted_records) // 2
    first_half = sorted_records[:mid_point]
    second_half = sorted_records[mid_point:]
    
    first_efficiency = sum(_calculate_beer_efficiency(r) for r in first_half) / len(first_half)
    second_efficiency = sum(_calculate_beer_efficiency(r) for r in second_half) / len(second_half)
    
    if second_efficiency > first_efficiency * 1.1:
        return "IMPROVING"
    elif second_efficiency < first_efficiency * 0.9:
        return "DECLINING"
    else:
        return "STABLE"

def _analyze_duct_tape_by_urgency(records: List[TuningHistory]) -> Dict[str, float]:
    """Analyze duct tape usage by urgency level"""
    urgency_duct_tape = {}
    for record in records:
        urgency = record.urgency_level or 'UNKNOWN'
        if urgency not in urgency_duct_tape:
            urgency_duct_tape[urgency] = {'with_tape': 0, 'total': 0}
        
        urgency_duct_tape[urgency]['total'] += 1
        if record.duct_tape_used:
            urgency_duct_tape[urgency]['with_tape'] += 1
    
    return {
        urgency: stats['with_tape'] / stats['total']
        for urgency, stats in urgency_duct_tape.items()
    }

def _analyze_quantum_grade_effectiveness(records: List[TuningHistory]) -> float:
    """Analyze quantum-grade duct tape effectiveness"""
    quantum_records = [r for r in records if r.engineering_solution and 'quantum' in r.engineering_solution.lower()]
    
    if not quantum_records:
        return 0.0
    
    return len([r for r in quantum_records if r.success]) / len(quantum_records)

def _analyze_most_used_supply_items(records: List[TuningHistory]) -> Dict[str, int]:
    """Analyze most frequently used supply closet items"""
    item_counts = Counter()
    
    for record in records:
        if record.supply_closet_items:
            items = record.supply_closet_items if isinstance(record.supply_closet_items, list) else []
            for item in items:
                item_counts[item] += 1
    
    return dict(item_counts.most_common(10))

def _analyze_raid_effectiveness_by_priority(records: List[TuningHistory]) -> Dict[str, float]:
    """Analyze raid effectiveness by priority level"""
    priority_stats = {}
    for record in records:
        priority = record.priority_level or 'UNKNOWN'
        if priority not in priority_stats:
            priority_stats[priority] = {'total': 0, 'successful': 0}
        
        priority_stats[priority]['total'] += 1
        if record.success:
            priority_stats[priority]['successful'] += 1
    
    return {
        priority: stats['successful'] / stats['total']
        for priority, stats in priority_stats.items()
    }

def _calculate_supply_closet_depletion_rate(records: List[TuningHistory]) -> float:
    """Calculate how quickly supply closet gets depleted"""
    if not records:
        return 0.0
    
    # Sort by timestamp
    sorted_records = sorted(records, key=lambda r: r.timestamp or datetime.min)
    
    # Calculate raids per day
    if len(sorted_records) < 2:
        return 0.0
    
    first_date = sorted_records[0].timestamp
    last_date = sorted_records[-1].timestamp
    
    if not first_date or not last_date:
        return 0.0
    
    days_span = (last_date - first_date).days or 1
    total_raids = sum(r.supply_closet_raids for r in sorted_records)
    
    return total_raids / days_span

def _calculate_trend(values: List[float]) -> str:
    """Calculate trend from list of values"""
    if len(values) < 2:
        return "INSUFFICIENT_DATA"
    
    # Simple linear trend calculation
    n = len(values)
    x_avg = (n - 1) / 2
    y_avg = sum(values) / n
    
    numerator = sum((i - x_avg) * (values[i] - y_avg) for i in range(n))
    denominator = sum((i - x_avg) ** 2 for i in range(n))
    
    if denominator == 0:
        return "STABLE"
    
    slope = numerator / denominator
    
    if slope > 0.05:
        return "IMPROVING"
    elif slope < -0.05:
        return "DECLINING"
    else:
        return "STABLE"

def _calculate_ingenuity_success_correlation(records: List[TuningHistory]) -> float:
    """Calculate correlation between ingenuity level and success"""
    if not records:
        return 0.0
    
    ingenuity_success_pairs = [
        (r.redneck_ingenuity_level or 0, 1 if r.success else 0)
        for r in records
    ]
    
    if len(ingenuity_success_pairs) < 2:
        return 0.0
    
    # Simple correlation calculation
    n = len(ingenuity_success_pairs)
    sum_x = sum(pair[0] for pair in ingenuity_success_pairs)
    sum_y = sum(pair[1] for pair in ingenuity_success_pairs)
    sum_xy = sum(pair[0] * pair[1] for pair in ingenuity_success_pairs)
    sum_x2 = sum(pair[0] ** 2 for pair in ingenuity_success_pairs)
    sum_y2 = sum(pair[1] ** 2 for pair in ingenuity_success_pairs)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator

def _find_peak_engineering_hours(hour_stats: Dict[int, Dict[str, int]]) -> List[int]:
    """Find peak engineering hours"""
    if not hour_stats:
        return []
    
    # Sort hours by total engineering solutions
    sorted_hours = sorted(hour_stats.items(), key=lambda x: x[1]['total'], reverse=True)
    
    # Return top 3 hours
    return [hour for hour, stats in sorted_hours[:3]]

def _calculate_late_night_effectiveness(hour_stats: Dict[int, Dict[str, int]]) -> float:
    """Calculate effectiveness during late night hours (10 PM - 4 AM)"""
    late_night_hours = [22, 23, 0, 1, 2, 3, 4]  # 10 PM - 4 AM
    
    late_night_total = 0
    late_night_successful = 0
    
    for hour in late_night_hours:
        if hour in hour_stats:
            late_night_total += hour_stats[hour]['total']
            late_night_successful += hour_stats[hour]['successful']
    
    if late_night_total == 0:
        return 0.0
    
    return late_night_successful / late_night_total

def _calculate_pattern_learning_improvement(pattern_records: List[TuningHistory], non_pattern_records: List[TuningHistory]) -> float:
    """Calculate improvement from pattern learning"""
    if not pattern_records or not non_pattern_records:
        return 0.0
    
    pattern_success_rate = len([r for r in pattern_records if r.success]) / len(pattern_records)
    non_pattern_success_rate = len([r for r in non_pattern_records if r.success]) / len(non_pattern_records)
    
    return pattern_success_rate - non_pattern_success_rate

def _calculate_urgency_success_rates(records: List[TuningHistory]) -> Dict[str, float]:
    """Calculate success rates by urgency level"""
    urgency_stats = {}
    for record in records:
        urgency = record.urgency_level or 'UNKNOWN'
        if urgency not in urgency_stats:
            urgency_stats[urgency] = {'total': 0, 'successful': 0}
        
        urgency_stats[urgency]['total'] += 1
        if record.success:
            urgency_stats[urgency]['successful'] += 1
    
    return {
        urgency: stats['successful'] / stats['total']
        for urgency, stats in urgency_stats.items()
    }

def _categorize_engineering_solution(solution: str) -> str:
    """Categorize engineering solutions into types"""
    solution_lower = solution.lower()
    
    if 'quantum' in solution_lower and 'duct tape' in solution_lower:
        return 'QUANTUM_DUCT_TAPE'
    elif 'duct tape' in solution_lower:
        return 'DUCT_TAPE'
    elif 'beer' in solution_lower:
        return 'BEER_POWERED'
    elif 'supply closet' in solution_lower:
        return 'SUPPLY_CLOSET'
    elif 'redneck' in solution_lower:
        return 'REDNECK_ENGINEERING'
    else:
        return 'STANDARD'

def _find_most_effective_solutions(solution_stats: Dict[str, Dict[str, int]]) -> List[str]:
    """Find most effective engineering solutions"""
    effectiveness_list = []
    
    for solution, stats in solution_stats.items():
        if stats['total'] > 0:
            effectiveness = stats['successful'] / stats['total']
            effectiveness_list.append((solution, effectiveness))
    
    # Sort by effectiveness and return top 3
    effectiveness_list.sort(key=lambda x: x[1], reverse=True)
    return [solution for solution, _ in effectiveness_list[:3]]

def _find_beer_intensive_solutions(solution_stats: Dict[str, Dict[str, int]]) -> List[str]:
    """Find solutions that require the most beer"""
    beer_intensive_list = []
    
    for solution, stats in solution_stats.items():
        if stats['total'] > 0:
            avg_beer = stats['beer_consumed'] / stats['total']
            beer_intensive_list.append((solution, avg_beer))
    
    # Sort by beer consumption and return top 3
    beer_intensive_list.sort(key=lambda x: x[1], reverse=True)
    return [solution for solution, _ in beer_intensive_list[:3]]

# Legacy support function to maintain backward compatibility
async def save_tuning_history_to_db(tuning_data: Dict, user_id: str) -> None:
    """
    Legacy function - redirects to new Hamsters engineering function
    
    Args:
        tuning_data: Dictionary containing tuning data
        user_id: ID of the user applying the tuning
    """
    logger.info("🐹 Redirecting legacy tuning save to Hamsters engineering")
    await save_hamsters_engineering_to_db(tuning_data, user_id)

async def get_tuning_history_from_db(user_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """
    Legacy function - redirects to new Hamsters engineering function
    
    Args:
        user_id: Optional user ID to filter by
        limit: Maximum number of records to return
        
    Returns:
        List of tuning history records
    """
    logger.info("🐹 Redirecting legacy tuning history to Hamsters engineering")
    return await get_hamsters_engineering_history(user_id, limit, include_patterns=False, include_user_data=False)