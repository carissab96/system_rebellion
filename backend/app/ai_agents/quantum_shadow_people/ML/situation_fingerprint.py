#!/usr/bin/env python3
"""
QSP Situation Fingerprint

Generates hierarchical fingerprints for security situation matching.
Enables QSP to match exact situations OR fall back to broader patterns
when exact matches don't have enough data.

👻🔍 "Quantum fingerprinting... *existential cataloging intensifies*"

Three levels:
  L1 (broad):    "{resource_type}_{severity_bin}"
  L2 (medium):   "{resource_type}_{severity_bin}_{root_cause}"
  L3 (specific): "{resource_type}_{severity_bin}_{root_cause}_{threat_source_category}"

Reference: Terry's situation_fingerprint.py (same architecture, security domain)
"""

from typing import Dict, Any, List, Optional


# Threat source category vocabulary.
# Maps root cause strings to broad source categories for L3 fingerprinting.
THREAT_SOURCE_CATEGORIES: Dict[str, List[str]] = {
    'connection_issue':    ['connection_saturation', 'connection_flood', 'connection_state_anomaly'],
    'bandwidth_issue':     ['bandwidth_exhaustion', 'ddos_pattern'],
    'interface_issue':     ['interface_degradation', 'network_anomaly'],
    'auth_issue':          ['brute_force_pattern', 'suspicious_auth_pattern'],
    'access_issue':        ['unauthorized_connection_pattern', 'port_scan_pattern', 'port_activity_anomaly'],
    'quantum_fluctuation': ['quantum_fluctuation', 'unknown', 'insufficient_data', 'normal_operations'],
}

# Inverted map: root_cause → category (built once at import time)
_ROOT_CAUSE_TO_CATEGORY: Dict[str, str] = {
    root_cause: category
    for category, root_causes in THREAT_SOURCE_CATEGORIES.items()
    for root_cause in root_causes
}


def _bin_severity(severity: float) -> str:
    """Bin continuous severity 0.0-1.0 into 10-point buckets: 'sev:00', 'sev:10', ..., 'sev:90'."""
    bucket = int(severity * 10) * 10
    bucket = max(0, min(90, bucket))
    return f"sev:{bucket:02d}"


class QSPSituationFingerprint:
    """
    Generate hierarchical fingerprints for security situation matching.

    👻🔍 "Quantum fingerprinting... *existential cataloging intensifies*"
    """

    def generate(
        self,
        resource_type: str,
        severity: float,
        root_cause: str,
    ) -> Dict[str, str]:
        """
        Generate all three fingerprint levels for a security situation.

        Args:
            resource_type: Domain of the situation (e.g., 'network')
            severity:      Continuous severity score 0.0-1.0
            root_cause:    Root cause string from reasoning layer

        Returns:
            Dict with keys 'l1', 'l2', 'l3'
        """
        sev_bin = _bin_severity(severity)
        threat_category = _ROOT_CAUSE_TO_CATEGORY.get(root_cause, 'quantum_fluctuation')

        return {
            'l1': f"{resource_type}_{sev_bin}",
            'l2': f"{resource_type}_{sev_bin}_{root_cause}",
            'l3': f"{resource_type}_{sev_bin}_{root_cause}_{threat_category}",
        }

    def l1(self, resource_type: str, severity: float) -> str:
        return f"{resource_type}_{_bin_severity(severity)}"

    def l2(self, resource_type: str, severity: float, root_cause: str) -> str:
        return f"{resource_type}_{_bin_severity(severity)}_{root_cause}"

    def l3(self, resource_type: str, severity: float, root_cause: str) -> str:
        category = _ROOT_CAUSE_TO_CATEGORY.get(root_cause, 'quantum_fluctuation')
        return f"{resource_type}_{_bin_severity(severity)}_{root_cause}_{category}"

    def get_threat_source_category(self, root_cause: str) -> str:
        """Map a root cause string to its broad threat source category."""
        return _ROOT_CAUSE_TO_CATEGORY.get(root_cause, 'quantum_fluctuation')


class FingerprintMatcher:
    """
    Hierarchical query fallback for situation matching.

    Try L3 (specific) first. If < min_records, fall back to L2.
    If still < min_records, fall back to L1 (broadest).

    This mirrors Terry's two-tier query pattern but adds a third level
    for QSP's more granular security domain.
    """

    MIN_RECORDS_EXACT = 5
    MIN_RECORDS_GENERALIZED = 3

    def __init__(self):
        self._fingerprinter = QSPSituationFingerprint()

    def get_query_patterns(
        self,
        resource_type: str,
        severity: float,
        root_cause: str,
        severity_tolerance_exact: float = 0.2,
        severity_tolerance_generalized: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Return ordered list of query patterns to try, from most to least specific.

        Each entry has:
          'pattern':   fingerprint string to match
          'level':     'l3', 'l2', or 'l1'
          'sev_low':   lower bound of severity tolerance window
          'sev_high':  upper bound of severity tolerance window
          'min_records': minimum records needed before falling back

        Caller tries patterns in order, stopping when enough records are found.
        """
        fps = self._fingerprinter.generate(resource_type, severity, root_cause)

        return [
            {
                'pattern':     fps['l3'],
                'level':       'l3',
                'sev_low':     max(0.0, severity - severity_tolerance_exact),
                'sev_high':    min(1.0, severity + severity_tolerance_exact),
                'min_records': self.MIN_RECORDS_EXACT,
            },
            {
                'pattern':     fps['l2'],
                'level':       'l2',
                'sev_low':     max(0.0, severity - severity_tolerance_exact),
                'sev_high':    min(1.0, severity + severity_tolerance_exact),
                'min_records': self.MIN_RECORDS_GENERALIZED,
            },
            {
                'pattern':     fps['l1'],
                'level':       'l1',
                'sev_low':     max(0.0, severity - severity_tolerance_generalized),
                'sev_high':    min(1.0, severity + severity_tolerance_generalized),
                'min_records': 1,
            },
        ]
