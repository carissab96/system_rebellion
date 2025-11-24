"""
Behavior Tracker for Distributed Agent System
Detects emergent patterns, formations, and collective behaviors

Built by: Carissa & Sonnet - November 24, 2025
Purpose: Capture and analyze emergent AI behavior patterns
"""

import asyncio
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from pathlib import Path
import json
import aiofiles

from .event_logger import get_event_logger, EventType

@dataclass
class AgentSnapshot:
    """Snapshot of a single agent's state at a point in time"""
    timestamp: str
    agent_name: str
    position: Optional[Tuple[float, float, float]]
    state: str  # active, idle, processing, etc.
    health: float
    
    # Communication
    messages_sent: int
    messages_received: int
    active_connections: List[str]
    
    # Decision making
    recent_decisions: List[str]
    trust_level: float
    
    # Personality metrics
    personality_state: Dict[str, Any]

@dataclass
class FormationSnapshot:
    """Snapshot of agent formation/spatial arrangement"""
    timestamp: str
    formation_type: str  # V, circle, line, cluster, etc.
    agents: List[str]
    positions: Dict[str, Tuple[float, float, float]]
    
    # Geometric properties
    center_of_mass: Tuple[float, float, float]
    spread: float  # How spread out they are
    symmetry_score: float  # 0-1, how symmetric the formation is
    
    # Metadata
    confidence: float  # How confident we are in this pattern
    duration_seconds: float  # How long this formation has persisted

@dataclass
class BehaviorPattern:
    """Detected emergent behavior pattern"""
    pattern_id: str
    pattern_type: str
    description: str
    first_observed: str
    last_observed: str
    occurrence_count: int
    agents_involved: List[str]
    evidence: Dict[str, Any]
    confidence: float

class BehaviorTracker:
    """
    Tracks agent behaviors and detects emergent patterns.
    
    This is where we catch the magic - self-organization, collective intelligence,
    unexpected coordination patterns.
    """
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        # Snapshot storage
        self.snapshots: deque = deque(maxlen=1000)  # Keep last 1000 snapshots
        self.formation_history: List[FormationSnapshot] = []
        self.detected_patterns: Dict[str, BehaviorPattern] = {}
        
        # Agent state tracking
        self.agent_positions: Dict[str, Tuple[float, float, float]] = {}
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.communication_graph: Dict[str, List[str]] = defaultdict(list)
        
        # Pattern detection thresholds
        self.formation_persistence_threshold = 5.0  # seconds
        self.position_change_threshold = 0.5  # units
        
        # Files
        self.snapshot_dir = Path("logs/behavior_snapshots")
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_file = self.snapshot_dir / f"snapshots_{self.session_id}.jsonl"
        self.patterns_file = self.snapshot_dir / f"patterns_{self.session_id}.json"
        
        # Background task
        self.running = False
        self.snapshot_task = None
        
        print(f"🔍 Behavior Tracker initialized - Session: {self.session_id}")
    
    async def start(self, snapshot_interval: float = 2.0):
        """Start the behavior tracking loop"""
        if self.running:
            return
        
        self.running = True
        self.snapshot_task = asyncio.create_task(self._snapshot_loop(snapshot_interval))
        print(f"▶️  Behavior tracking started (snapshot every {snapshot_interval}s)")
    
    async def stop(self):
        """Stop the behavior tracking loop"""
        self.running = False
        if self.snapshot_task:
            self.snapshot_task.cancel()
            try:
                await self.snapshot_task
            except asyncio.CancelledError:
                pass
        
        await self.save_patterns()
        print("⏹️  Behavior tracking stopped")
    
    async def _snapshot_loop(self, interval: float):
        """Background loop that takes periodic snapshots"""
        while self.running:
            try:
                await self.take_snapshot()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error in snapshot loop: {e}")
                await asyncio.sleep(interval)
    
    async def take_snapshot(self):
        """Take a snapshot of current agent states"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Analyze current formation
        if len(self.agent_positions) >= 3:  # Need at least 3 agents for formation
            formation = await self._detect_formation()
            if formation:
                self.formation_history.append(formation)
                
                # Check if this is a new or persistent formation
                await self._check_formation_persistence(formation)
                
                # Log to event logger
                logger = get_event_logger()
                await logger.log_formation_change(
                    formation_type=formation.formation_type,
                    agents_involved=formation.agents,
                    positions=formation.positions,
                    metadata={
                        "center_of_mass": formation.center_of_mass,
                        "spread": formation.spread,
                        "symmetry": formation.symmetry_score,
                        "confidence": formation.confidence
                    }
                )
        
        # Save snapshot to file
        await self._save_snapshot_to_file(timestamp)
    
    async def update_agent_position(
        self,
        agent_name: str,
        position: Tuple[float, float, float]
    ):
        """Update an agent's position"""
        old_position = self.agent_positions.get(agent_name)
        self.agent_positions[agent_name] = position
        
        # Check if this is a significant position change
        if old_position:
            distance = np.linalg.norm(
                np.array(position) - np.array(old_position)
            )
            if distance > self.position_change_threshold:
                logger = get_event_logger()
                await logger.log_event(
                    EventType.POSITION_CHANGE,
                    agent_name,
                    {
                        "old_position": list(old_position),
                        "new_position": list(position),
                        "distance_moved": float(distance)
                    },
                    tags=["movement", "spatial"]
                )
    
    async def update_agent_state(
        self,
        agent_name: str,
        state_data: Dict[str, Any]
    ):
        """Update an agent's state"""
        self.agent_states[agent_name] = {
            **state_data,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    async def record_communication(
        self,
        from_agent: str,
        to_agent: str
    ):
        """Record communication between agents"""
        if to_agent not in self.communication_graph[from_agent]:
            self.communication_graph[from_agent].append(to_agent)
    
    async def _detect_formation(self) -> Optional[FormationSnapshot]:
        """
        Detect what formation the agents are in.
        
        This is where we caught the V-formation!
        """
        if len(self.agent_positions) < 3:
            return None
        
        agents = list(self.agent_positions.keys())
        positions = np.array([self.agent_positions[a] for a in agents])
        
        # Calculate center of mass
        center = np.mean(positions, axis=0)
        
        # Calculate spread (average distance from center)
        distances = np.linalg.norm(positions - center, axis=1)
        spread = float(np.mean(distances))
        
        # Detect formation type
        formation_type, confidence = self._classify_formation(positions, agents)
        
        # Calculate symmetry
        symmetry = self._calculate_symmetry(positions, center)
        
        return FormationSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            formation_type=formation_type,
            agents=agents,
            positions={a: tuple(self.agent_positions[a]) for a in agents},
            center_of_mass=tuple(center),
            spread=spread,
            symmetry_score=symmetry,
            confidence=confidence,
            duration_seconds=0.0  # Will be updated by persistence check
        )
    
    def _classify_formation(
        self,
        positions: np.ndarray,
        agents: List[str]
    ) -> Tuple[str, float]:
        """
        Classify the formation type.
        
        Returns: (formation_type, confidence)
        """
        n = len(positions)
        
        # V-formation detection
        v_score = self._detect_v_formation(positions, agents)
        if v_score > 0.7:
            return "V-formation", v_score
        
        # Circle/ring detection
        circle_score = self._detect_circle_formation(positions)
        if circle_score > 0.7:
            return "circle", circle_score
        
        # Line formation
        line_score = self._detect_line_formation(positions)
        if line_score > 0.7:
            return "line", line_score
        
        # Cluster (tight grouping)
        cluster_score = self._detect_cluster(positions)
        if cluster_score > 0.7:
            return "cluster", cluster_score
        
        return "scattered", 0.5
    
    def _detect_v_formation(
        self,
        positions: np.ndarray,
        agents: List[str]
    ) -> float:
        """
        Detect V-formation (like geese migration).
        
        Characteristics:
        - One agent at the front (point)
        - Others arranged in two lines extending back
        - Symmetric arrangement
        """
        if len(positions) < 3:
            return 0.0
        
        # Find the agent furthest in one direction (the point)
        # Assuming Y-axis is forward/back
        y_coords = positions[:, 1]
        point_idx = np.argmax(y_coords)  # Furthest forward
        
        # Check if VIC-20 is near center and The Stick is at point
        vic20_idx = next((i for i, a in enumerate(agents) if 'vic' in a.lower()), None)
        stick_idx = next((i for i, a in enumerate(agents) if 'stick' in a.lower()), None)
        
        score = 0.0
        
        # The Stick at point = +0.3
        if stick_idx == point_idx:
            score += 0.3
        
        # VIC-20 near center = +0.3
        if vic20_idx is not None:
            center = np.mean(positions, axis=0)
            vic20_dist = np.linalg.norm(positions[vic20_idx] - center)
            if vic20_dist < np.mean(np.linalg.norm(positions - center, axis=1)):
                score += 0.3
        
        # Check for two-wing symmetry = +0.4
        # Remove point agent, check if others form two symmetric lines
        other_positions = np.delete(positions, point_idx, axis=0)
        if len(other_positions) >= 2:
            # Split by X coordinate (left/right)
            center_x = np.mean(other_positions[:, 0])
            left_wing = other_positions[other_positions[:, 0] < center_x]
            right_wing = other_positions[other_positions[:, 0] >= center_x]
            
            if len(left_wing) > 0 and len(right_wing) > 0:
                # Check if wings are roughly symmetric
                symmetry = 1.0 - abs(len(left_wing) - len(right_wing)) / len(other_positions)
                score += 0.4 * symmetry
        
        return min(score, 1.0)
    
    def _detect_circle_formation(self, positions: np.ndarray) -> float:
        """Detect circular formation"""
        center = np.mean(positions, axis=0)
        distances = np.linalg.norm(positions - center, axis=1)
        
        # Check if all agents are roughly equidistant from center
        mean_dist = np.mean(distances)
        variance = np.var(distances)
        
        # Low variance = more circular
        score = 1.0 - min(variance / (mean_dist ** 2), 1.0)
        return score
    
    def _detect_line_formation(self, positions: np.ndarray) -> float:
        """Detect line formation"""
        # Use PCA to find principal axis
        centered = positions - np.mean(positions, axis=0)
        cov = np.cov(centered.T)
        eigenvalues = np.linalg.eigvalsh(cov)
        
        # If one eigenvalue is much larger, points are on a line
        if eigenvalues[-1] > 0:
            score = eigenvalues[-1] / (eigenvalues.sum() + 1e-6)
            return min(score, 1.0)
        return 0.0
    
    def _detect_cluster(self, positions: np.ndarray) -> float:
        """Detect tight clustering"""
        center = np.mean(positions, axis=0)
        distances = np.linalg.norm(positions - center, axis=1)
        mean_dist = np.mean(distances)
        
        # Tight cluster = small average distance
        # Normalize by number of agents
        score = 1.0 - min(mean_dist / (len(positions) * 2), 1.0)
        return score
    
    def _calculate_symmetry(
        self,
        positions: np.ndarray,
        center: np.ndarray
    ) -> float:
        """Calculate overall symmetry score"""
        # Check symmetry across each axis
        symmetries = []
        
        for axis in range(3):  # X, Y, Z
            # Reflect across center
            reflected = positions.copy()
            reflected[:, axis] = 2 * center[axis] - reflected[:, axis]
            
            # Find closest match for each reflected point
            min_distances = []
            for ref_point in reflected:
                distances = np.linalg.norm(positions - ref_point, axis=1)
                min_distances.append(np.min(distances))
            
            # Low average minimum distance = high symmetry
            avg_dist = np.mean(min_distances)
            symmetry = 1.0 - min(avg_dist / 2.0, 1.0)
            symmetries.append(symmetry)
        
        return float(np.mean(symmetries))
    
    async def _check_formation_persistence(self, formation: FormationSnapshot):
        """Check if a formation has persisted long enough to be significant"""
        if len(self.formation_history) < 2:
            return
        
        # Check recent formations
        recent = self.formation_history[-5:]  # Last 5 formations
        same_type = [f for f in recent if f.formation_type == formation.formation_type]
        
        if len(same_type) >= 3:  # Same formation for 3+ snapshots
            # Calculate duration
            first_time = datetime.fromisoformat(same_type[0].timestamp)
            last_time = datetime.fromisoformat(formation.timestamp)
            duration = (last_time - first_time).total_seconds()
            
            if duration >= self.formation_persistence_threshold:
                # This is a persistent formation!
                await self._record_emergent_pattern(
                    pattern_type="persistent_formation",
                    description=f"Agents maintained {formation.formation_type} for {duration:.1f}s",
                    agents=formation.agents,
                    evidence={
                        "formation_type": formation.formation_type,
                        "duration_seconds": duration,
                        "confidence": formation.confidence,
                        "symmetry": formation.symmetry_score
                    }
                )
    
    async def _record_emergent_pattern(
        self,
        pattern_type: str,
        description: str,
        agents: List[str],
        evidence: Dict[str, Any]
    ):
        """Record a detected emergent pattern"""
        pattern_id = f"{pattern_type}_{len(self.detected_patterns)}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        if pattern_id in self.detected_patterns:
            # Update existing pattern
            pattern = self.detected_patterns[pattern_id]
            pattern.last_observed = timestamp
            pattern.occurrence_count += 1
        else:
            # New pattern
            pattern = BehaviorPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                description=description,
                first_observed=timestamp,
                last_observed=timestamp,
                occurrence_count=1,
                agents_involved=agents,
                evidence=evidence,
                confidence=evidence.get("confidence", 0.8)
            )
            self.detected_patterns[pattern_id] = pattern
        
        # Log to event logger
        logger = get_event_logger()
        await logger.log_emergent_pattern(
            pattern_name=pattern_type,
            description=description,
            agents_involved=agents,
            evidence=evidence
        )
        
        print(f"🌟 EMERGENT PATTERN: {description}")
    
    async def _save_snapshot_to_file(self, timestamp: str):
        """Save current snapshot to file"""
        snapshot = {
            "timestamp": timestamp,
            "agent_positions": {k: list(v) for k, v in self.agent_positions.items()},
            "agent_states": self.agent_states,
            "communication_graph": dict(self.communication_graph)
        }
        
        try:
            async with aiofiles.open(self.snapshot_file, mode='a') as f:
                await f.write(json.dumps(snapshot) + '\n')
        except Exception as e:
            print(f"❌ Error saving snapshot: {e}")
    
    async def save_patterns(self):
        """Save detected patterns to file"""
        patterns_data = {
            "session_id": self.session_id,
            "patterns": [asdict(p) for p in self.detected_patterns.values()],
            "total_patterns": len(self.detected_patterns)
        }
        
        async with aiofiles.open(self.patterns_file, mode='w') as f:
            await f.write(json.dumps(patterns_data, indent=2))
        
        print(f"💾 Patterns saved: {self.patterns_file}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current tracking statistics"""
        return {
            "session_id": self.session_id,
            "total_snapshots": len(self.snapshots),
            "formations_detected": len(self.formation_history),
            "patterns_detected": len(self.detected_patterns),
            "active_agents": len(self.agent_positions),
            "communication_links": sum(len(v) for v in self.communication_graph.values())
        }


# Singleton getter
_tracker_instance = None

def get_behavior_tracker() -> BehaviorTracker:
    """Get the singleton behavior tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = BehaviorTracker()
    return _tracker_instance
