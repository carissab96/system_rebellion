#!/usr/bin/env python3
"""
QSP Heuristic Configuration — Cold Start Values

THESE ARE NOT ANSWERS. They are domain-informed starting hypotheses.
As QSP accumulates learning data, these values are progressively replaced
by learned scores and thresholds.

If you find yourself adding to these configs instead of improving the ML
pipeline, you are going in the wrong direction.

Imported by:
  - action_effectiveness.py  (ACTION_HEURISTIC_CONFIG)
  - learned_thresholds.py    (DEFAULT_THRESHOLDS, THRESHOLD_ADJUSTMENT_CONFIG)
"""

# =============================================================================
# Action heuristic bootstrap — cold start scoring before historical data exists.
# Groups actions by behavior category and provides severity-correlated scores.
# ML replaces these as ActionOutcomeRecord data accumulates.
# =============================================================================

ACTION_HEURISTIC_CONFIG = {
    # Action category membership
    'aggressive_actions':    ['block_ips', 'update_firewall', 'close_connections'],
    'defensive_actions':     ['apply_rate_limit', 'throttle_network'],
    'investigative_actions': ['investigate_connections', 'scan_ports', 'analyze_traffic', 'quantum_scan'],
    'passive_actions':       ['monitor_passive'],
    'escalation_actions':    ['escalate_to_vic20'],

    # Aggressive: high score at high severity, low score at low severity
    'aggressive_high_severity': 0.8,
    'aggressive_mid_severity':  0.5,
    'aggressive_low_severity':  0.2,

    # Defensive: best at mid severity
    'defensive_high_severity': 0.6,
    'defensive_mid_severity':  0.7,
    'defensive_low_severity':  0.4,

    # Investigative: best at low-mid severity (gather info before acting)
    'investigative_high_severity': 0.3,
    'investigative_mid_severity':  0.6,
    'investigative_low_severity':  0.7,

    # Passive: only useful at low severity
    'passive_high_severity': 0.1,
    'passive_mid_severity':  0.3,
    'passive_low_severity':  0.8,

    # Escalation: high for out-of-domain threats (CPU/memory/disk → not QSP's job)
    'escalate_out_of_domain': 0.8,
    'escalate_in_domain':     0.2,

    'default_score': 0.5,
}

# QSP's domain metrics — anything NOT in this set is out-of-domain → escalate
QSP_DOMAIN_METRICS = frozenset([
    'total_connections',
    'established_connections',
    'suspicious_connections',
    'network_anomalies',
    'listening_ports',
    'tcp_connections',
    'udp_connections',
    'sent_rate_bps',
    'recv_rate_bps',
    'failed_auth_attempts',
    'anomalous_states',
    'existential_dread',
])

# =============================================================================
# Default thresholds — cold-start values only.
# Used ONLY when no learning history exists for a metric.
# As data accumulates, learned values replace these entirely.
# These are hypotheses, not answers.
# =============================================================================

DEFAULT_THRESHOLDS = {
    # Network connection metrics
    'total_connections': {
        'warning':  500.0,
        'critical': 1000.0,
    },
    'established_connections': {
        'warning':  300.0,
        'critical': 700.0,
    },
    'suspicious_connections': {
        'warning':  10.0,
        'critical': 50.0,
    },
    'network_anomalies': {
        'warning':  5.0,
        'critical': 20.0,
    },
    # Bandwidth metrics (bytes per second)
    'sent_rate_bps': {
        'warning':  50_000_000.0,    # 50 MB/s
        'critical': 100_000_000.0,   # 100 MB/s
    },
    'recv_rate_bps': {
        'warning':  50_000_000.0,
        'critical': 100_000_000.0,
    },
    # Auth failures (from AuthFailureMonitor)
    'failed_auth_attempts': {
        'warning':  5.0,
        'critical': 15.0,
    },
}

# =============================================================================
# Threshold adjustment config — controls how fast thresholds move.
# Asymmetric by design: false negatives (missed threats) are catastrophic
# in security, so the system reacts more aggressively to them.
# =============================================================================

THRESHOLD_ADJUSTMENT_CONFIG = {
    'false_negative_adjustment':      0.10,  # 10% decrease per FN trigger — missed threats are catastrophic
    'false_positive_adjustment':      0.05,  # 5% increase per FP trigger — less aggressive
    'false_negative_trigger_rate':    0.2,   # Lower threshold if FN rate exceeds this
    'false_positive_trigger_rate':    0.3,   # Raise threshold if FP rate exceeds this
    'min_threshold_floor':            1.0,   # Never go below 1 (always detect something)
    'confidence_fn_penalty':          0.5,   # FN reduces confidence by this factor
    'confidence_fp_penalty':          0.2,   # FP reduces confidence by this factor
    'full_confidence_sample_size':    20.0,  # Sample size for full confidence
}
