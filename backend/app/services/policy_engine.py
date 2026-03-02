#!/usr/bin/env python3
"""
Policy Engine for DecisionEnvelope

Environment-aware action classification and approval requirements.
One place to define: "in prod, backups are Class 3, not Class 2."

Key Features:
- Environment-aware classification overrides
- Service-specific rules (stateful services = higher risk)
- Policy composition (base + environment + service-specific)
- Audit trail of policy decisions
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Policy version for audit trail
POLICY_VERSION = "v1.0"


class Environment(Enum):
    """Deployment environment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ApprovalDecision(Enum):
    """Policy decision on action approval"""
    ALLOWED = "allowed"  # Execute without approval
    NEEDS_APPROVAL = "needs_approval"  # Requires user approval
    BLOCKED = "blocked"  # Not allowed in this environment


@dataclass
class PolicyDecision:
    """
    Result of policy evaluation.
    
    Tells the executor what gates are required for this action.
    """
    decision: ApprovalDecision
    intent_class: int  # 0-3 (may be overridden from base classification)
    required_gates: List[str]  # ['dry_run', 'restore_test', 'delay_60s', 'two_person']
    forced_delay_seconds: int
    reason: str  # Why this decision was made
    policy_rules_applied: List[str]  # Which policies contributed
    policy_version: str  # Policy version at evaluation time


class PolicyEngine:
    """
    Evaluates action requests against environment-aware policies.
    
    Usage:
        engine = PolicyEngine(environment=Environment.PRODUCTION)
        decision = engine.evaluate(envelope, context)
        
        if decision.decision == ApprovalDecision.BLOCKED:
            raise ActionBlockedError(decision.reason)
        elif decision.decision == ApprovalDecision.NEEDS_APPROVAL:
            await request_user_approval(envelope, decision)
    """
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self.logger = logging.getLogger(f"PolicyEngine.{environment.value}")
        
        # Base action classifications (can be overridden by environment)
        self.base_classifications = self._load_base_classifications()
        
        # Environment-specific overrides
        self.environment_overrides = self._load_environment_overrides()
        
        # Service-specific rules
        self.service_rules = self._load_service_rules()
    
    def evaluate(
        self,
        agent_name: str,
        action: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> PolicyDecision:
        """
        Evaluate action against policies.
        
        Args:
            agent_name: Name of agent requesting action
            action: Action to execute
            parameters: Action parameters
            context: Execution context (metrics, state, etc.)
            
        Returns:
            PolicyDecision with approval requirements
        """
        rules_applied = []
        
        # Step 1: Get base classification
        base_class = self._get_base_classification(action)
        intent_class = base_class
        rules_applied.append(f"base_class_{base_class}")
        
        # Step 2: Apply environment overrides
        env_override = self._apply_environment_override(action, parameters)
        if env_override is not None:
            intent_class = env_override
            rules_applied.append(f"env_override_{self.environment.value}_class_{env_override}")
        
        # Step 3: Apply service-specific rules
        service_override = self._apply_service_rules(action, parameters, context)
        if service_override is not None:
            intent_class = service_override
            rules_applied.append(f"service_override_class_{service_override}")
        
        # Step 4: Determine required gates
        required_gates = self._determine_required_gates(intent_class, action, parameters, context)
        
        # Step 5: Determine approval decision
        if intent_class == 0:
            decision = ApprovalDecision.ALLOWED
            reason = "Read-only action, no approval needed"
        elif intent_class == 1:
            decision = ApprovalDecision.ALLOWED
            reason = "Reversible action, no approval needed"
        elif intent_class >= 2:
            decision = ApprovalDecision.NEEDS_APPROVAL
            reason = f"Class {intent_class} action requires approval"
        else:
            decision = ApprovalDecision.BLOCKED
            reason = "Unknown classification"
        
        # Step 6: Check for environment-specific blocks
        if self._is_blocked_in_environment(action, parameters):
            decision = ApprovalDecision.BLOCKED
            reason = f"Action blocked in {self.environment.value} environment"
            rules_applied.append(f"blocked_in_{self.environment.value}")
        
        # Step 7: Calculate forced delay
        forced_delay = 0
        if intent_class == 3:
            forced_delay = 60  # 60 seconds for Class 3
            rules_applied.append("forced_delay_60s")
        elif intent_class == 2 and self.environment == Environment.PRODUCTION:
            forced_delay = 30  # 30 seconds for Class 2 in prod
            rules_applied.append("forced_delay_30s_prod")
        
        policy_decision = PolicyDecision(
            decision=decision,
            intent_class=intent_class,
            required_gates=required_gates,
            forced_delay_seconds=forced_delay,
            reason=reason,
            policy_rules_applied=rules_applied,
            policy_version=POLICY_VERSION
        )
        
        self.logger.info(
            f"Policy evaluation: {agent_name}.{action} -> {decision.value} "
            f"(class {intent_class}, gates: {required_gates})"
        )
        
        return policy_decision
    
    def _load_base_classifications(self) -> Dict[str, int]:
        """
        Load base action classifications (Class 0-3).
        
        These are the default classifications before environment overrides.
        """
        return {
            # Class 0: Read-only
            'monitor': 0,
            'investigate': 0,
            'scan_ports': 0,
            'analyze_traffic': 0,
            'quantum_scan': 0,
            'triage_alert': 0,
            'assess_confidence': 0,
            'route_to_specialist': 0,
            'log_decision': 0,
            'track_anxiety': 0,
            'detect_bob': 0,
            
            # Class 1: Reversible
            'emergency_cache_clear': 1,
            'clear_cache': 1,
            'optimize_memory_allocation': 1,
            'reduce_memory_footprint': 1,
            'throttle_cpu_intensive_tasks': 1,
            'adjust_process_priority': 1,
            'throttle_network': 1,
            'rate_limit': 1,
            'close_suspicious_connections': 1,
            'throttle_cpu': 1,
            'rotate_logs': 1,
            'compress_old_files': 1,
            'consume_paper_bag': 1,
            
            # Class 2: Conditionally Destructive
            'kill_memory_hog': 2,
            'restart_service': 2,
            'emergency_disk_cleanup': 2,
            'hamster-fstrim': 2,
            'hamster-cleanup-tmp': 2,
            'hamster-package-cache-clean': 2,
            'hamster-logrotate': 2,
            'archive_data': 2,
            'block': 2,
            'update_firewall_rules': 2,
            
            # Class 3: Irreversible
            'hamster-defrag': 3,
            'hamster-defrag-supervised': 3,
        }
    
    def _load_environment_overrides(self) -> Dict[str, Dict[str, int]]:
        """
        Load environment-specific classification overrides.
        
        Example: backup pruning is Class 2 in dev, Class 3 in prod.
        """
        return {
            Environment.PRODUCTION.value: {
                # Anything touching backups is Class 3 in production
                'prune_backups': 3,
                'delete_backup': 3,
                'rotate_backups': 3,
                
                # Service restarts are more dangerous in prod
                'restart_service': 3,  # Override from Class 2 to Class 3
                
                # Disk operations are more dangerous in prod
                'emergency_disk_cleanup': 3,  # Override from Class 2 to Class 3
            },
            Environment.STAGING.value: {
                # Staging is more permissive
                'hamster-defrag': 2,  # Override from Class 3 to Class 2
            },
            Environment.DEVELOPMENT.value: {
                # Dev is most permissive
                'hamster-defrag': 1,  # Override from Class 3 to Class 1
                'restart_service': 1,  # Override from Class 2 to Class 1
            }
        }
    
    def _load_service_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Load service-specific rules.
        
        Example: restarting postgres is Class 3, restarting nginx is Class 2.
        """
        return {
            'postgres': {
                'stateful': True,
                'restart_class': 3,
                'reason': 'Database restart can cause data loss'
            },
            'redis': {
                'stateful': True,
                'restart_class': 3,
                'reason': 'Redis restart loses in-memory data'
            },
            'rabbitmq': {
                'stateful': True,
                'restart_class': 3,
                'reason': 'Queue restart can lose unprocessed messages'
            },
            'nginx': {
                'stateful': False,
                'restart_class': 2,
                'reason': 'Web server restart causes brief downtime'
            },
            'uvicorn': {
                'stateful': False,
                'restart_class': 2,
                'reason': 'App server restart causes brief downtime'
            }
        }
    
    def _get_base_classification(self, action: str) -> int:
        """Get base classification for action"""
        return self.base_classifications.get(action, 2)  # Default to Class 2 if unknown
    
    def _apply_environment_override(
        self,
        action: str,
        parameters: Dict[str, Any]
    ) -> Optional[int]:
        """
        Apply environment-specific classification override.
        
        Returns:
            Overridden class, or None if no override
        """
        env_overrides = self.environment_overrides.get(self.environment.value, {})
        return env_overrides.get(action)
    
    def _apply_service_rules(
        self,
        action: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[int]:
        """
        Apply service-specific rules.
        
        Example: restart_service with service_name='postgres' -> Class 3
        
        Returns:
            Overridden class, or None if no override
        """
        if action != 'restart_service':
            return None
        
        service_name = parameters.get('service_name', '').lower()
        service_rule = self.service_rules.get(service_name)
        
        if service_rule and service_rule.get('stateful'):
            return service_rule.get('restart_class')
        
        return None
    
    def _determine_required_gates(
        self,
        intent_class: int,
        action: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Determine which gates are required for this action.
        
        Returns:
            List of required gates: ['dry_run', 'restore_test', 'delay_60s', 'two_person']
        """
        gates = []
        
        # Class 2+ requires dry-run
        if intent_class >= 2:
            gates.append('dry_run')
        
        # Class 3 requires restore test
        if intent_class >= 3:
            gates.append('restore_test')
        
        # Class 3 requires forced delay
        if intent_class >= 3:
            gates.append('delay_60s')
        
        # Production + Class 3 requires two-person approval
        if self.environment == Environment.PRODUCTION and intent_class >= 3:
            gates.append('two_person')
        
        # Backup operations require restore test
        if 'backup' in action.lower() or 'prune' in action.lower():
            if 'restore_test' not in gates:
                gates.append('restore_test')
        
        # Defrag operations require state validation
        if 'defrag' in action.lower():
            gates.append('state_validation')
        
        return gates
    
    def _is_blocked_in_environment(
        self,
        action: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """
        Check if action is blocked in current environment.
        
        Example: defrag on /boot is always blocked, regardless of environment.
        """
        # Block defrag on critical paths in all environments
        if 'defrag' in action.lower():
            mount_point = parameters.get('mount_point', '')
            critical_paths = ['/boot', '/boot/efi', '/sys', '/proc', '/dev']
            if any(mount_point.startswith(path) for path in critical_paths):
                return True
        
        # Block backup deletion in production
        if self.environment == Environment.PRODUCTION:
            if 'delete' in action.lower() and 'backup' in action.lower():
                return True
        
        return False


# Singleton instance (can be overridden for testing)
_policy_engine: Optional[PolicyEngine] = None


def get_policy_engine(environment: Optional[Environment] = None) -> PolicyEngine:
    """
    Get singleton PolicyEngine instance.
    
    Args:
        environment: Override environment (for testing)
        
    Returns:
        PolicyEngine instance
    """
    global _policy_engine
    
    if _policy_engine is None or environment is not None:
        # Detect environment from config or env var
        if environment is None:
            import os
            env_name = os.getenv('ENVIRONMENT', 'development').lower()
            environment = Environment(env_name)
        
        _policy_engine = PolicyEngine(environment=environment)
    
    return _policy_engine
