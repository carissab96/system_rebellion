#!/usr/bin/env python3
"""
Situation Fingerprinting - Hierarchical Matching System

Generates 3-level fingerprints for situation matching:
- Level 1: resource_severity (broad)
- Level 2: resource_severity_rootcause (medium)
- Level 3: resource_severity_rootcause_process (specific)

Allows Terry to match exact situations OR fall back to broader patterns.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger('SituationFingerprint')


class SituationFingerprint:
    """
    Generate hierarchical fingerprints for situation matching.
    
    🐌🔍 "Now I can remember 'Python memory leaks' specifically,
           but also fall back to 'memory thrashing' in general!"
    """
    
    # Process category mapping
    PROCESS_CATEGORIES = {
        'python': ['python', 'python3', 'python3.11', 'python3.10', 'python3.9'],
        'database': ['postgres', 'postgresql', 'mysql', 'redis', 'mongodb', 'mariadb'],
        'web_server': ['nginx', 'apache', 'apache2', 'node', 'npm', 'gunicorn', 'uvicorn'],
        'system': ['systemd', 'kworker', 'ksoftirqd', 'migration', 'rcu_sched'],
    }
    
    @staticmethod
    def generate(
        resource_type: str,
        severity: str,
        root_cause: str,
        full_metrics: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate 3-level hierarchical fingerprint.
        
        Args:
            resource_type: 'cpu', 'memory', 'disk', 'network'
            severity: 'low', 'medium', 'high', 'critical'
            root_cause: 'cpu_bound', 'memory_thrashing', 'io_wait', etc.
            full_metrics: Full system metrics for process categorization
            
        Returns:
            Dictionary with level_1, level_2, level_3, and process_category
            
        Example:
            {
                'level_1': 'cpu_high',
                'level_2': 'cpu_high_memory_thrashing',
                'level_3': 'cpu_high_memory_thrashing_python',
                'process_category': 'python'
            }
        """
        # Level 1: Broad (resource + severity)
        l1 = f"{resource_type}_{severity}"
        
        # Level 2: Add root cause
        l2 = f"{resource_type}_{severity}_{root_cause}"
        
        # Level 3: Add process category
        process_category = SituationFingerprint._categorize_process(full_metrics)
        l3 = f"{resource_type}_{severity}_{root_cause}_{process_category}"
        
        logger.debug(f"🔍 Generated fingerprints: L1={l1}, L2={l2}, L3={l3}")
        
        return {
            'level_1': l1,
            'level_2': l2,
            'level_3': l3,
            'process_category': process_category
        }
    
    @staticmethod
    def _categorize_process(metrics: Dict[str, Any]) -> str:
        """
        Categorize the top process causing issues.
        
        Looks at the top CPU-consuming process and categorizes it.
        
        Args:
            metrics: Full system metrics
            
        Returns:
            Process category: 'python', 'database', 'web_server', 'system', 'other'
        """
        # Try to get top processes from CPU metrics
        top_processes = metrics.get('cpu', {}).get('top_processes', [])
        
        if not top_processes:
            logger.debug("   No top processes found - categorizing as 'other'")
            return 'other'
        
        # Get the top process name
        top_process = top_processes[0]
        top_process_name = top_process.get('name', '').lower()
        
        if not top_process_name:
            logger.debug("   Top process has no name - categorizing as 'other'")
            return 'other'
        
        # Match against known categories
        for category, process_names in SituationFingerprint.PROCESS_CATEGORIES.items():
            if any(pname in top_process_name for pname in process_names):
                logger.debug(f"   Categorized '{top_process_name}' as '{category}'")
                return category
        
        # No match - it's something else
        logger.debug(f"   Process '{top_process_name}' doesn't match known categories - using 'other'")
        return 'other'
    
    @staticmethod
    def explain_fingerprint(fingerprint: Dict[str, str]) -> str:
        """
        Generate human-readable explanation of a fingerprint.
        
        Args:
            fingerprint: Fingerprint dictionary from generate()
            
        Returns:
            Natural language explanation
        """
        parts = []
        
        parts.append(f"📍 SITUATION FINGERPRINT:")
        parts.append(f"")
        parts.append(f"  Level 1 (Broad):    {fingerprint['level_1']}")
        parts.append(f"  Level 2 (Medium):   {fingerprint['level_2']}")
        parts.append(f"  Level 3 (Specific): {fingerprint['level_3']}")
        parts.append(f"")
        parts.append(f"  Process Category: {fingerprint['process_category']}")
        parts.append(f"")
        parts.append(f"MATCHING STRATEGY:")
        parts.append(f"  1. Try exact match (Level 3)")
        parts.append(f"  2. Fall back to Level 2 if needed")
        parts.append(f"  3. Fall back to Level 1 if still needed")
        
        return "\n".join(parts)


class FingerprintMatcher:
    """
    Query historical learning records using hierarchical fingerprints.
    
    🐌🎯 "Try specific first, fall back to general if needed!"
    """
    
    def __init__(self, db_session):
        """
        Initialize fingerprint matcher.
        
        Args:
            db_session: AsyncSession for database queries
        """
        self.db = db_session
        self.logger = logger
    
    async def find_similar_situations(
        self,
        fingerprints: Dict[str, str],
        agent_name: str = 'meth_snail',
        min_records: int = 3
    ) -> Dict[str, Any]:
        """
        Query historical learning with fallback hierarchy.
        
        Strategy:
        1. Try Level 3 (most specific) - e.g., 'cpu_high_memory_thrashing_python'
        2. If < min_records, add Level 2 - e.g., 'cpu_high_memory_thrashing'
        3. If still < min_records, add Level 1 - e.g., 'cpu_high'
        
        Args:
            fingerprints: Fingerprint dictionary from SituationFingerprint.generate()
            agent_name: Which agent's learning to query
            min_records: Minimum records needed before falling back
            
        Returns:
            Dictionary with:
                - records: List of matching learning records
                - match_level: Which level matched (1, 2, or 3)
                - total_found: Total number of records found
        """
        try:
            from sqlalchemy import select
            from app.models.agent_learning import AgentLearningRecord
            
            records = []
            match_level = None
            
            # Try Level 3 (most specific)
            self.logger.debug(f"🔍 Trying Level 3: {fingerprints['level_3']}")
            query = select(AgentLearningRecord).where(
                AgentLearningRecord.agent_name == agent_name,
                AgentLearningRecord.fingerprint_l3 == fingerprints['level_3']
            ).order_by(AgentLearningRecord.created_at.desc())
            
            result = await self.db.execute(query)
            level_3_records = result.scalars().all()
            records.extend(level_3_records)
            
            if len(records) >= min_records:
                match_level = 3
                self.logger.info(f"   ✓ Found {len(records)} records at Level 3 (specific match)")
            else:
                # Fall back to Level 2
                self.logger.debug(f"   Only {len(records)} at Level 3, trying Level 2: {fingerprints['level_2']}")
                query = select(AgentLearningRecord).where(
                    AgentLearningRecord.agent_name == agent_name,
                    AgentLearningRecord.fingerprint_l2 == fingerprints['level_2']
                ).order_by(AgentLearningRecord.created_at.desc())
                
                result = await self.db.execute(query)
                level_2_records = result.scalars().all()
                
                # Add records not already in list
                existing_ids = {r.id for r in records}
                for record in level_2_records:
                    if record.id not in existing_ids:
                        records.append(record)
                
                if len(records) >= min_records:
                    match_level = 2
                    self.logger.info(f"   ✓ Found {len(records)} records at Level 2 (medium match)")
                else:
                    # Fall back to Level 1
                    self.logger.debug(f"   Only {len(records)} at Level 2, trying Level 1: {fingerprints['level_1']}")
                    query = select(AgentLearningRecord).where(
                        AgentLearningRecord.agent_name == agent_name,
                        AgentLearningRecord.fingerprint_l1 == fingerprints['level_1']
                    ).order_by(AgentLearningRecord.created_at.desc())
                    
                    result = await self.db.execute(query)
                    level_1_records = result.scalars().all()
                    
                    # Add records not already in list
                    for record in level_1_records:
                        if record.id not in existing_ids:
                            records.append(record)
                    
                    match_level = 1
                    self.logger.info(f"   ✓ Found {len(records)} records at Level 1 (broad match)")
            
            # Convert to dictionaries
            record_dicts = []
            for record in records:
                record_dicts.append({
                    'id': record.id,
                    'fingerprint_l1': record.fingerprint_l1,
                    'fingerprint_l2': record.fingerprint_l2,
                    'fingerprint_l3': record.fingerprint_l3,
                    'root_cause': record.root_cause,
                    'process_category': record.process_category,
                    'action': record.action,
                    'parameters': record.parameters,
                    'confidence': record.confidence,
                    'followed_vic20': record.followed_vic20,
                    'success': record.success,
                    'improvement': record.improvement,
                    'created_at': record.created_at.isoformat()
                })
            
            return {
                'records': record_dicts,
                'match_level': match_level,
                'total_found': len(record_dicts)
            }
            
        except ImportError:
            # Model doesn't exist yet
            self.logger.debug("   ⚠️ AgentLearningRecord model not yet available")
            return {'records': [], 'match_level': None, 'total_found': 0}
        except Exception as e:
            self.logger.error(f"   💥 Failed to query similar situations: {str(e)}")
            return {'records': [], 'match_level': None, 'total_found': 0}
