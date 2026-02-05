#!/usr/bin/env python3
"""
Evidence Export Service

Minimal evidence bundle export for court defense.
Thin slice implementation - just the essentials for Phase 1.

Provides:
- Single envelope export (JSON)
- Linked learning record
- Related learning events
- One-click "evidence bundle" for any decision
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import logging


class EvidenceExportService:
    """
    Export evidence bundles for legal defense.
    
    Usage:
        service = EvidenceExportService(db)
        bundle = await service.export_envelope_bundle(envelope_id)
        
        # Save to file
        with open(f"evidence_{envelope_id}.json", 'w') as f:
            json.dump(bundle, f, indent=2)
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger("EvidenceExport")
    
    async def export_envelope_bundle(
        self,
        envelope_id: str,
        include_learning_events: bool = True,
        max_events: int = 50
    ) -> Dict[str, Any]:
        """
        Export complete evidence bundle for a decision envelope.
        
        Args:
            envelope_id: UUID of envelope to export
            include_learning_events: Include related learning events
            max_events: Maximum number of learning events to include
            
        Returns:
            Evidence bundle with envelope, learning record, and events
        """
        from app.models.decision_envelope import DecisionEnvelope, LearningEventLog
        from app.models.agent_learning import AgentLearningRecord
        
        # Fetch envelope
        result = await self.db.execute(
            select(DecisionEnvelope).where(DecisionEnvelope.envelope_id == envelope_id)
        )
        envelope = result.scalar_one_or_none()
        
        if not envelope:
            raise ValueError(f"Envelope not found: {envelope_id}")
        
        bundle = {
            'envelope': envelope.to_dict(),
            'learning_record': None,
            'learning_events': [],
            'human_readable_summary': self._generate_summary(envelope),
            'metadata': {
                'exported_at': self._now_iso(),
                'export_version': '1.0',
                'evidence_type': 'decision_envelope_bundle'
            }
        }
        
        # Fetch linked learning record
        if envelope.learning_record_id:
            result = await self.db.execute(
                select(AgentLearningRecord).where(
                    AgentLearningRecord.id == envelope.learning_record_id
                )
            )
            learning_record = result.scalar_one_or_none()
            if learning_record:
                bundle['learning_record'] = learning_record.to_dict()
        
        # Fetch related learning events
        if include_learning_events:
            result = await self.db.execute(
                select(LearningEventLog)
                .where(LearningEventLog.source_envelope_id == envelope_id)
                .order_by(LearningEventLog.created_at.desc())
                .limit(max_events)
            )
            events = result.scalars().all()
            bundle['learning_events'] = [event.to_dict() for event in events]
        
        self.logger.info(
            f"Exported evidence bundle: {envelope_id} "
            f"({len(bundle['learning_events'])} events)"
        )
        
        return bundle
    
    async def export_agent_timeline(
        self,
        agent_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        max_envelopes: int = 100
    ) -> Dict[str, Any]:
        """
        Export timeline of all decisions by an agent.
        
        Args:
            agent_name: Name of agent
            start_time: ISO-8601 start time (optional)
            end_time: ISO-8601 end time (optional)
            max_envelopes: Maximum number of envelopes to include
            
        Returns:
            Timeline bundle with all agent decisions
        """
        from app.models.decision_envelope import DecisionEnvelope
        from datetime import datetime
        
        query = select(DecisionEnvelope).where(
            DecisionEnvelope.agent_name == agent_name
        )
        
        if start_time:
            query = query.where(DecisionEnvelope.created_at >= datetime.fromisoformat(start_time))
        
        if end_time:
            query = query.where(DecisionEnvelope.created_at <= datetime.fromisoformat(end_time))
        
        query = query.order_by(DecisionEnvelope.created_at.desc()).limit(max_envelopes)
        
        result = await self.db.execute(query)
        envelopes = result.scalars().all()
        
        timeline = {
            'agent_name': agent_name,
            'start_time': start_time,
            'end_time': end_time,
            'envelope_count': len(envelopes),
            'envelopes': [envelope.to_dict() for envelope in envelopes],
            'metadata': {
                'exported_at': self._now_iso(),
                'export_version': '1.0',
                'evidence_type': 'agent_timeline'
            }
        }
        
        self.logger.info(
            f"Exported agent timeline: {agent_name} "
            f"({len(envelopes)} envelopes)"
        )
        
        return timeline
    
    async def export_propagation_chain(
        self,
        envelope_id: str,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Export learning propagation chain ("who taught who what").
        
        Args:
            envelope_id: Starting envelope ID
            max_depth: Maximum chain depth to follow
            
        Returns:
            Propagation chain showing how learning spread
        """
        from app.models.decision_envelope import LearningEventLog
        
        chain = []
        visited = set()
        queue = [(envelope_id, 0)]
        
        while queue and len(chain) < max_depth:
            current_id, depth = queue.pop(0)
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            # Find all events that reference this envelope
            result = await self.db.execute(
                select(LearningEventLog)
                .where(LearningEventLog.source_envelope_id == current_id)
                .order_by(LearningEventLog.created_at.asc())
            )
            events = result.scalars().all()
            
            for event in events:
                chain.append({
                    'depth': depth,
                    'event': event.to_dict(),
                    'propagation_chain': event.propagation_chain
                })
                
                # Queue target agent's envelopes for next level
                if event.target_agent and depth < max_depth - 1:
                    # Find next envelope in chain (simplified - would need more logic)
                    pass
        
        propagation = {
            'root_envelope_id': envelope_id,
            'chain_length': len(chain),
            'chain': chain,
            'metadata': {
                'exported_at': self._now_iso(),
                'export_version': '1.0',
                'evidence_type': 'propagation_chain'
            }
        }
        
        self.logger.info(
            f"Exported propagation chain: {envelope_id} "
            f"({len(chain)} events)"
        )
        
        return propagation
    
    async def verify_hash_chain(
        self,
        envelope_id: str
    ) -> Dict[str, Any]:
        """
        Verify tamper-evident hash chain for an envelope.
        
        Args:
            envelope_id: Envelope to verify
            
        Returns:
            Verification result with any broken links
        """
        from app.models.decision_envelope import DecisionEnvelope
        
        result = await self.db.execute(
            select(DecisionEnvelope).where(DecisionEnvelope.envelope_id == envelope_id)
        )
        envelope = result.scalar_one_or_none()
        
        if not envelope:
            raise ValueError(f"Envelope not found: {envelope_id}")
        
        # Verify payload hash
        computed_hash = envelope.compute_payload_hash()
        payload_valid = (computed_hash == envelope.payload_hash)
        
        # Verify chain link (if prev_envelope_hash exists)
        chain_valid = True
        if envelope.prev_envelope_hash:
            # Fetch previous envelope
            result = await self.db.execute(
                select(DecisionEnvelope)
                .where(DecisionEnvelope.payload_hash == envelope.prev_envelope_hash)
                .order_by(DecisionEnvelope.created_at.desc())
                .limit(1)
            )
            prev_envelope = result.scalar_one_or_none()
            
            if not prev_envelope:
                chain_valid = False
        
        verification = {
            'envelope_id': envelope_id,
            'payload_hash_valid': payload_valid,
            'chain_link_valid': chain_valid,
            'computed_hash': computed_hash,
            'stored_hash': envelope.payload_hash,
            'prev_envelope_hash': envelope.prev_envelope_hash,
            'verified_at': self._now_iso()
        }
        
        self.logger.info(
            f"Verified hash chain: {envelope_id} "
            f"(payload: {payload_valid}, chain: {chain_valid})"
        )
        
        return verification
    
    def _generate_summary(self, envelope) -> str:
        """
        Generate human-readable summary for 3am incident response.
        
        Not for court. For you, when adrenaline is high.
        """
        from datetime import datetime
        
        # Parse timestamp
        if isinstance(envelope.created_at, str):
            created_at = datetime.fromisoformat(envelope.created_at)
        else:
            created_at = envelope.created_at
        
        timestamp_str = created_at.strftime("%b %d at %H:%M UTC")
        
        # Build summary
        summary_parts = []
        
        # Basic action
        summary_parts.append(
            f"On {timestamp_str}, {envelope.agent_name} proposed {envelope.action}"
        )
        
        # Parameters (if significant)
        if envelope.parameters:
            param_str = ", ".join([f"{k}={v}" for k, v in envelope.parameters.items()])
            summary_parts.append(f"with parameters: {param_str}")
        
        # Classification
        class_names = {0: "read-only", 1: "reversible", 2: "conditionally destructive", 3: "irreversible"}
        class_name = class_names.get(envelope.intent_class, "unknown")
        summary_parts.append(f". The action was classified Class {envelope.intent_class} ({class_name})")
        
        # Approval flow
        if envelope.approval_required:
            if envelope.approval_granted:
                summary_parts.append(f", required approval, and was approved")
                if envelope.forced_delay_seconds > 0:
                    summary_parts.append(f" after a {envelope.forced_delay_seconds}s delay")
            else:
                summary_parts.append(f", required approval, but was DENIED")
        
        # Safeguards
        if envelope.backups_exist is not None:
            if envelope.backups_restorable:
                summary_parts.append(". Backups were verified as restorable")
            elif envelope.backups_exist:
                summary_parts.append(". Backups existed but were NOT verified as restorable")
            else:
                summary_parts.append(". WARNING: No backups existed")
        
        # State drift
        if envelope.state_drift_detected:
            summary_parts.append(f". State drift was detected: {envelope.state_drift_reason}")
        
        # Execution outcome
        if envelope.executed:
            if envelope.success:
                summary_parts.append(". Execution succeeded")
                if envelope.actual_impact:
                    impact_str = ", ".join([f"{k}: {v}" for k, v in envelope.actual_impact.items()])
                    summary_parts.append(f" with impact: {impact_str}")
            else:
                summary_parts.append(". Execution FAILED")
                if envelope.execution_result and 'error' in envelope.execution_result:
                    summary_parts.append(f": {envelope.execution_result['error']}")
        else:
            summary_parts.append(". Action was NOT executed")
        
        return "".join(summary_parts) + "."
    
    def _now_iso(self) -> str:
        """Get current time as ISO-8601 string"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


async def get_evidence_export_service(db: AsyncSession) -> EvidenceExportService:
    """
    Get EvidenceExportService instance.
    
    Args:
        db: Database session
        
    Returns:
        EvidenceExportService instance
    """
    return EvidenceExportService(db)
