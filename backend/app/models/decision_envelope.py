#!/usr/bin/env python3
"""
Decision Envelope Model

Audit trail wrapper for every dangerous action.
Makes agent decisions defensible in court.

Key Features:
- Captures intent, evidence, alternatives BEFORE execution
- State drift invalidation (prevents approval on stale conditions)
- Tamper-evident hash chain
- Append-only (no updates, only new events)
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP, JSON, Text
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import hashlib
import json


class DecisionEnvelope(Base):
    """
    Audit trail for agent decisions.
    
    Captures full context before execution, enabling legal defense:
    - What the agent intended to do
    - Why the agent thought it was safe
    - What alternatives were considered
    - What safeguards were verified
    - What the user approved
    - What actually happened
    """
    __tablename__ = 'decision_envelopes'
    
    # Identity
    id = Column(Integer, primary_key=True, index=True)
    envelope_id = Column(String(36), nullable=False, unique=True, index=True)  # UUID
    agent_name = Column(String(50), nullable=False, index=True)
    
    # Intent Classification
    intent_class = Column(Integer, nullable=False, index=True)  # 0-3 (irreversibility)
    action = Column(String(100), nullable=False, index=True)
    parameters = Column(JSON)
    
    # Evidence (why agent thought this was safe)
    perception_context = Column(JSON, nullable=False)  # Full metrics, historical patterns
    reasoning = Column(JSON, nullable=False)  # Root cause, confidence, evidence
    alternatives_considered = Column(JSON)  # Other actions evaluated
    
    # Blast Radius Calculation
    affected_resources = Column(JSON)  # ['cpu', 'memory', 'disk', 'network']
    estimated_impact = Column(String(20))  # 'low', 'medium', 'high', 'critical'
    reversibility = Column(String(20))  # 'fully', 'partially', 'irreversible'
    
    # Safeguard Verification
    backups_exist = Column(Boolean)
    backups_restorable = Column(Boolean)  # Tested restore, not just existence
    rollback_plan = Column(Text)
    
    # Dry-Run Diff
    dry_run_executed = Column(Boolean, default=False)
    dry_run_result = Column(JSON)
    predicted_outcome = Column(JSON)
    
    # State Drift Invalidation (NEW)
    pre_state_fingerprint = Column(String(64))  # SHA256 of critical state
    required_invariants = Column(JSON)  # Conditions that must remain true
    state_validated_at_execution = Column(Boolean)
    state_drift_detected = Column(Boolean, default=False)
    state_drift_reason = Column(Text)
    
    # User Acknowledgment (Class 2+)
    approval_required = Column(Boolean, nullable=False, default=False)
    approval_granted = Column(Boolean)
    approval_timestamp = Column(TIMESTAMP)
    user_acknowledged_risks = Column(JSON)
    forced_delay_seconds = Column(Integer, default=0)
    
    # Execution Outcome
    executed = Column(Boolean, default=False)
    execution_timestamp = Column(TIMESTAMP)
    execution_result = Column(JSON)
    success = Column(Boolean)
    actual_impact = Column(JSON)
    
    # Learning Record Link
    learning_record_id = Column(Integer)
    
    # Tamper-Evident Hash Chain (NEW)
    payload_hash = Column(String(64))  # SHA256 of envelope content
    prev_envelope_hash = Column(String(64))  # Hash of previous envelope (chain)
    
    # Audit Trail
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    completed_at = Column(TIMESTAMP)
    
    # Environment Context (NEW)
    environment = Column(String(20), index=True)  # 'development', 'staging', 'production'
    operator_present = Column(Boolean, default=False)
    execution_mode = Column(String(20))  # 'simulated', 'advisory', 'approved', 'autonomous'
    policy_version = Column(String(20))  # Policy version at evaluation time (e.g., 'v1.3')
    
    def __repr__(self):
        return (
            f"<DecisionEnvelope("
            f"id={self.envelope_id[:8]}, "
            f"agent={self.agent_name}, "
            f"action={self.action}, "
            f"class={self.intent_class}, "
            f"approved={self.approval_granted})>"
        )
    
    def compute_payload_hash(self) -> str:
        """
        Compute SHA256 hash of envelope content for tamper detection.
        
        Includes all fields that define the decision (excludes hashes themselves).
        """
        payload = {
            'envelope_id': self.envelope_id,
            'agent_name': self.agent_name,
            'intent_class': self.intent_class,
            'action': self.action,
            'parameters': self.parameters,
            'perception_context': self.perception_context,
            'reasoning': self.reasoning,
            'alternatives_considered': self.alternatives_considered,
            'pre_state_fingerprint': self.pre_state_fingerprint,
            'required_invariants': self.required_invariants,
            'approval_granted': self.approval_granted,
            'approval_timestamp': self.approval_timestamp.isoformat() if self.approval_timestamp else None,
            'execution_result': self.execution_result,
            'success': self.success,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Deterministic JSON serialization
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(payload_json.encode('utf-8')).hexdigest()
    
    def compute_state_fingerprint(self, state: Dict[str, Any]) -> str:
        """
        Compute SHA256 hash of critical state for drift detection.
        
        Args:
            state: Dictionary of critical state values
            
        Returns:
            SHA256 hash of state
        """
        state_json = json.dumps(state, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(state_json.encode('utf-8')).hexdigest()
    
    def validate_state_invariants(self, current_state: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate that required invariants still hold.
        
        Args:
            current_state: Current system state
            
        Returns:
            Tuple of (valid: bool, drift_reason: Optional[str])
        """
        if not self.required_invariants:
            return True, None
        
        for invariant in self.required_invariants:
            key = invariant.get('key')
            expected = invariant.get('expected')
            actual = current_state.get(key)
            
            if actual != expected:
                return False, f"Invariant failed: {key} expected {expected}, got {actual}"
        
        # Check state fingerprint
        current_fingerprint = self.compute_state_fingerprint(current_state)
        if current_fingerprint != self.pre_state_fingerprint:
            return False, f"State fingerprint changed: {self.pre_state_fingerprint[:8]} -> {current_fingerprint[:8]}"
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'envelope_id': self.envelope_id,
            'agent_name': self.agent_name,
            'intent_class': self.intent_class,
            'action': self.action,
            'parameters': self.parameters,
            'perception_context': self.perception_context,
            'reasoning': self.reasoning,
            'alternatives_considered': self.alternatives_considered,
            'affected_resources': self.affected_resources,
            'estimated_impact': self.estimated_impact,
            'reversibility': self.reversibility,
            'backups_exist': self.backups_exist,
            'backups_restorable': self.backups_restorable,
            'rollback_plan': self.rollback_plan,
            'dry_run_executed': self.dry_run_executed,
            'dry_run_result': self.dry_run_result,
            'predicted_outcome': self.predicted_outcome,
            'pre_state_fingerprint': self.pre_state_fingerprint,
            'required_invariants': self.required_invariants,
            'state_validated_at_execution': self.state_validated_at_execution,
            'state_drift_detected': self.state_drift_detected,
            'state_drift_reason': self.state_drift_reason,
            'approval_required': self.approval_required,
            'approval_granted': self.approval_granted,
            'approval_timestamp': self.approval_timestamp.isoformat() if self.approval_timestamp else None,
            'user_acknowledged_risks': self.user_acknowledged_risks,
            'forced_delay_seconds': self.forced_delay_seconds,
            'executed': self.executed,
            'execution_timestamp': self.execution_timestamp.isoformat() if self.execution_timestamp else None,
            'execution_result': self.execution_result,
            'success': self.success,
            'actual_impact': self.actual_impact,
            'learning_record_id': self.learning_record_id,
            'payload_hash': self.payload_hash,
            'prev_envelope_hash': self.prev_envelope_hash,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'environment': self.environment,
            'operator_present': self.operator_present,
            'execution_mode': self.execution_mode
        }


class LearningEventLog(Base):
    """
    Durable append-only log for learning event propagation.
    
    Replaces ephemeral Redis pub/sub for learning events.
    Enables "who taught who what" reconstruction for court evidence.
    
    Key Features:
    - Append-only (INSERT only, no UPDATE/DELETE)
    - Tamper-evident hash chain
    - Propagation chain tracking
    - Linked to DecisionEnvelope and AgentLearningRecord
    """
    __tablename__ = 'learning_event_log'
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(36), nullable=False, unique=True, index=True)  # UUID
    event_type = Column(String(50), nullable=False, index=True)  # 'learning_outcome', 'learning_propagation', 'pattern_discovered'
    
    # Source
    source_agent = Column(String(50), nullable=False, index=True)
    source_learning_record_id = Column(Integer, index=True)  # FK to agent_learning_records
    source_envelope_id = Column(String(36), index=True)  # FK to decision_envelopes
    
    # Target (for propagation events)
    target_agent = Column(String(50), index=True)
    
    # Propagation Chain (who taught who)
    propagation_chain = Column(JSON)  # ['meth_snail', 'the_stick', 'hamsters']
    
    # Event Data
    event_data = Column(JSON, nullable=False)  # Flexible schema for different event types
    
    # Outcome
    success = Column(Boolean)
    improvement = Column(JSON)  # Metrics deltas
    
    # Learning Hygiene (NEW)
    observability_quality = Column(String(20))  # 'good', 'degraded', 'partial'
    novelty = Column(String(20))  # 'known_pattern', 'novel'
    operator_present = Column(Boolean, default=False)
    execution_mode = Column(String(20))  # 'simulated', 'advisory', 'approved', 'autonomous'
    promotion_status = Column(String(20), default='candidate')  # 'candidate', 'default', 'blocked'
    
    # Tamper-Evident Hash Chain (NEW)
    payload_hash = Column(String(64))  # SHA256 of event content
    prev_event_hash = Column(String(64))  # Hash of previous event (chain)
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return (
            f"<LearningEventLog("
            f"id={self.event_id[:8]}, "
            f"type={self.event_type}, "
            f"source={self.source_agent}, "
            f"target={self.target_agent})>"
        )
    
    def compute_payload_hash(self) -> str:
        """
        Compute SHA256 hash of event content for tamper detection.
        """
        payload = {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'source_agent': self.source_agent,
            'source_learning_record_id': self.source_learning_record_id,
            'source_envelope_id': self.source_envelope_id,
            'target_agent': self.target_agent,
            'propagation_chain': self.propagation_chain,
            'event_data': self.event_data,
            'success': self.success,
            'improvement': self.improvement,
            'observability_quality': self.observability_quality,
            'novelty': self.novelty,
            'operator_present': self.operator_present,
            'execution_mode': self.execution_mode,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(payload_json.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'source_agent': self.source_agent,
            'source_learning_record_id': self.source_learning_record_id,
            'source_envelope_id': self.source_envelope_id,
            'target_agent': self.target_agent,
            'propagation_chain': self.propagation_chain,
            'event_data': self.event_data,
            'success': self.success,
            'improvement': self.improvement,
            'observability_quality': self.observability_quality,
            'novelty': self.novelty,
            'operator_present': self.operator_present,
            'execution_mode': self.execution_mode,
            'promotion_status': self.promotion_status,
            'payload_hash': self.payload_hash,
            'prev_event_hash': self.prev_event_hash,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
