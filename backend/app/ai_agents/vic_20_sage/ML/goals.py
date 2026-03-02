"""
VIC-20 Goals and Cold-Start Hypotheses.

Cold-start values are used until enough historical data exists to replace them.
Min 3 successful samples required before learned recommendations override cold-start.
"""

from app.ai_agents.distributed.agent_registry import TERRY, HAMSTERS, QSP

VIC20_GOALS = [
    'route_to_correct_specialist',
    'minimize_resolution_time',
    'maximize_specialist_success_rate',
    'reduce_repeat_escalations',
    'maintain_system_stability',
]

COLD_START_RECOMMENDATIONS = {
    'cpu':     TERRY,
    'memory':  TERRY,
    'swap':    TERRY,
    'disk':    HAMSTERS,
    'network': QSP,
}

COLD_START_HYPOTHESES = {
    'cpu': {
        'specialist': TERRY,
        'action': 'adjust_process_priority',
        'confidence': 0.65,
        'basis': 'cold_start',
    },
    'memory': {
        'specialist': TERRY,
        'action': 'clear_cache',
        'confidence': 0.65,
        'basis': 'cold_start',
    },
    'swap': {
        'specialist': TERRY,
        'action': 'clear_cache',
        'confidence': 0.60,
        'basis': 'cold_start',
    },
    'disk': {
        'specialist': HAMSTERS,
        'action': 'rm_temp',
        'confidence': 0.65,
        'basis': 'cold_start',
    },
    'network': {
        'specialist': QSP,
        'action': 'analyze_traffic',
        'confidence': 0.60,
        'basis': 'cold_start',
    },
}

COMPLETION_SATISFIED_GOALS = {
    'route_to_correct_specialist': lambda outcome: outcome.routing_was_correct,
    'minimize_resolution_time': lambda outcome: outcome.specialist_improvement > 0,
    'maximize_specialist_success_rate': lambda outcome: outcome.specialist_success,
    'reduce_repeat_escalations': lambda outcome: outcome.specialist_success,
    'maintain_system_stability': lambda outcome: outcome.specialist_improvement >= 5.0,
}

GOAL_TO_METRIC_KEY = {
    'route_to_correct_specialist': 'routing_was_correct',
    'minimize_resolution_time': 'duration_seconds',
    'maximize_specialist_success_rate': 'specialist_success',
    'reduce_repeat_escalations': 'specialist_success',
    'maintain_system_stability': 'specialist_improvement',
}
