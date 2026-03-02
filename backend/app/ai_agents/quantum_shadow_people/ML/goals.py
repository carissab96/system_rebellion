#!/usr/bin/env python3
"""
QSP Goal Vocabulary and Cold-Start Hypotheses

Goals are PROBLEMS, not solutions. The planner figures out how to solve them.

QSP's domain: Network health monitoring with security-adjacent awareness.
"""

# =============================================================================
# Goal vocabulary — shared with action_selection.py
# These are PROBLEMS, not solutions.
# =============================================================================

QSP_GOALS = [
    # Connection issues
    'connection_saturation',           # Too many connections
    'connection_flood',                # Rapid new connection rate
    'connection_state_anomaly',        # TIME_WAIT/CLOSE_WAIT pileup

    # Bandwidth issues
    'bandwidth_exhaustion',            # Rates maxed out
    'ddos_pattern',                    # Bandwidth + connection flood combined

    # Interface issues
    'interface_degradation',           # Errors and drops spiking
    'network_anomaly',                 # General anomalous patterns

    # Security-adjacent (derived from network data)
    'brute_force_pattern',             # Auth failures + repeated connections
    'unauthorized_connection_pattern', # Connections to unexpected ports
    'port_scan_pattern',               # Many ports probed from few sources
    'suspicious_auth_pattern',         # Auth failures at warning level

    # Normal / unknown
    'normal_operations',               # Nothing abnormal — routine monitoring
    'preventive_scan',                 # Scheduled health check
    'quantum_fluctuation',             # QSP quantum state unstable
    'insufficient_data',               # Not enough signal to classify
]


# =============================================================================
# Cold-start hypotheses — domain-informed starting sequences.
# These are NOT answers. They're first guesses that ML improves upon.
#
# QSP's domain knowledge:
# - Investigate before blocking — understand what you're seeing first
# - Rate limit before full block — proportional response
# - Scan ports when pattern suggests probing
# - monitor_passive is always a valid first step for low-severity situations
# - Escalate when pattern is beyond network domain
# =============================================================================

COLD_START_HYPOTHESES = {
    # Connection issues
    'connection_saturation':           ['analyze_traffic', 'apply_rate_limit', 'close_connections'],
    'connection_flood':                ['analyze_traffic', 'apply_rate_limit', 'throttle_network'],
    'connection_state_anomaly':        ['investigate_connections', 'close_connections'],

    # Bandwidth issues
    'bandwidth_exhaustion':            ['analyze_traffic', 'throttle_network', 'apply_rate_limit'],
    'ddos_pattern':                    ['apply_rate_limit', 'block_ips', 'throttle_network', 'escalate_to_vic20'],

    # Interface issues
    'interface_degradation':           ['investigate_connections', 'analyze_traffic', 'monitor_passive'],
    'network_anomaly':                 ['investigate_connections', 'quantum_scan', 'monitor_passive'],

    # Security-adjacent
    'brute_force_pattern':             ['apply_rate_limit', 'block_ips', 'investigate_connections'],
    'unauthorized_connection_pattern': ['investigate_connections', 'block_ips', 'update_firewall'],
    'port_scan_pattern':               ['scan_ports', 'block_ips', 'update_firewall'],
    'suspicious_auth_pattern':         ['investigate_connections', 'apply_rate_limit', 'monitor_passive'],

    # Normal / unknown
    'normal_operations':               ['monitor_passive'],
    'preventive_scan':                 ['scan_ports', 'quantum_scan', 'analyze_traffic'],
    'quantum_fluctuation':             ['quantum_scan', 'investigate_connections', 'monitor_passive'],
    'insufficient_data':               ['investigate_connections', 'analyze_traffic', 'monitor_passive'],
}


# Goals satisfied by completion of the sequence, not by a metric threshold.
COMPLETION_SATISFIED_GOALS = frozenset([
    'preventive_scan',
    'normal_operations',
])


# =============================================================================
# Goal → metric key mapping
# Maps goals to the metric used for goal satisfaction checks.
# =============================================================================

GOAL_TO_METRIC_KEY = {
    'connection_saturation':           'total_connections',
    'connection_flood':                'total_connections',
    'connection_state_anomaly':        'suspicious_connections',
    'bandwidth_exhaustion':            'recv_rate_bps',
    'ddos_pattern':                    'recv_rate_bps',
    'interface_degradation':           'network_anomalies',
    'network_anomaly':                 'network_anomalies',
    'brute_force_pattern':             'failed_auth_attempts',
    'unauthorized_connection_pattern': 'suspicious_connections',
    'port_scan_pattern':               'suspicious_connections',
    'suspicious_auth_pattern':         'failed_auth_attempts',
    'quantum_fluctuation':             'network_anomalies',
    'insufficient_data':               'network_anomalies',
}
