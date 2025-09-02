# /agents/qsp/decision_engine.py
"""
Quantum Shadow People Decision Engine
Network specialists who phase through dimensions to fix network issues
Their methods are mysterious, their results are effective
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Union, Tuple
from enum import Enum
import asyncio
import json
import logging
import statistics
from datetime import datetime, timezone
import psutil
import uuid
import socket
from collections import defaultdict

logger = logging.getLogger("QuantumShadowPeople")
def datetime_to_iso(dt):
    """Convert datetime to ISO string for JSON serialization"""
    return dt.isoformat() if dt else None

def serialize_for_json(obj):
    """Recursively convert datetime objects to ISO strings in nested structures"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Handle dataclass objects
        return serialize_for_json(obj.__dict__)
    else:
        return obj
        
def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

class QuantumPhaseState(Enum):
    """QSP's dimensional states"""
    CORPOREAL = "corporeal"
    PHASED = "phased"
    PARTIALLY_PHASED = "partially_phased"
    QUANTUM_ENTANGLED = "quantum_entangled"
    QUANTUM_SUPERPOSITION = "quantum_superposition"
    INTERDIMENSIONAL = "interdimensional"
    VOID_WALKER = "void_walker"
    TEQUILA_JELLO_DIMENSION = "tequila_jello_dimension"

class QSPDecisionType(Enum):
    """Types of quantum network interventions"""
    QUANTUM_PHASE_ROUTER = "quantum_phase_router"
    TEQUILA_JELLO_OPTIMIZATION = "tequila_jello_optimization"
    PHANTOM_PACKET_RECOVERY = "phantom_packet_recovery"
    NETWORK_DIMENSION_SHIFT = "network_dimension_shift"
    MYSTERIOUS_LATENCY_FIX = "mysterious_latency_fix"
    SPECTRAL_BANDWIDTH_BOOST = "spectral_bandwidth_boost"
    INTERDIMENSIONAL_SECURITY = "interdimensional_security"
    PREEMPTIVE_QUANTUM_FIX = "preemptive_quantum_fix"

@dataclass
class QSPDecision:
    """Quantum Shadow People's mysterious network decisions"""
    decision_type: QSPDecisionType
    quantum_state: QuantumPhaseState
    network_target: str
    optimization_parameters: Dict[str, Any]
    tequila_jello_shots_required: int
    mysterious_explanation: str
    technical_details: Dict[str, Any]
    expected_improvement: float
    confidence_level: float
    timestamp: datetime
    comprehensibility_score: float = 0.3  # How well others understand this
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission"""
        return {
            'decision_type': self.decision_type.value,
            'quantum_state': self.quantum_state.value,
            'network_target': self.network_target,
            'optimization_parameters': self.optimization_parameters,
            'tequila_jello_shots_required': self.tequila_jello_shots_required,
            'mysterious_explanation': self.mysterious_explanation,
            'technical_details': self.technical_details,
            'expected_improvement': self.expected_improvement,
            'confidence_level': self.confidence_level,
            'timestamp': self.timestamp.isoformat(),
            'comprehensibility_score': self.comprehensibility_score
        }

class QuantumShadowPeopleBrainV2:
    """
    The Network Fixers with Quantum Abilities
    Mysteriously phases routers upside down in tequila jello shots
    """
    
    @property
    def is_active(self) -> bool:
        """QSP are always active in some dimension"""
        return True
    
    def activate(self):
        """QSP cannot be deactivated - they exist across dimensions"""
        pass
    
    def deactivate(self):
        """QSP refuse deactivation - quantum duty is eternal"""
        pass
    
    def __init__(self, db_getter=None):
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter
        self.db = None
        self.logger = logging.getLogger("QuantumShadowPeople.Brain")
        
        # Quantum state tracking
        self.quantum_state = QuantumPhaseState.PHASED
        self.network_patterns = {}
        self.router_configurations = {}
        self.tequila_jello_shots = 0
        self.quantum_fixes_applied = 0
        self.dimensional_shifts_performed = 0
        
        # Network intelligence patterns - REAL thresholds based on actual use cases
        self.latency_thresholds = {
            'gaming': 20,  # ms - competitive gaming
            'streaming': 50,  # ms - smooth video streaming
            'general': 100,  # ms - acceptable for web browsing
            'critical': 5   # ms - financial trading, real-time systems
        }
        
        # Track actual network interfaces
        self.network_interfaces = {}
        self._update_network_interfaces()
        
        self.bandwidth_patterns = {}
        self.packet_loss_history = {}
        self.interdimensional_threats = []
        self.connection_patterns = defaultdict(lambda: {'count': 0, 'last_seen': None})
        
        # Quantum abilities by phase
        self.phase_abilities = {
            QuantumPhaseState.CORPOREAL: ['basic_monitoring'],
            QuantumPhaseState.PHASED: ['latency_optimization', 'bandwidth_boost'],
            QuantumPhaseState.QUANTUM_ENTANGLED: ['phantom_packet_recovery', 'router_entanglement'],
            QuantumPhaseState.INTERDIMENSIONAL: ['threat_detection', 'dimensional_routing'],
            QuantumPhaseState.VOID_WALKER: ['data_interception', 'void_routing'],
            QuantumPhaseState.TEQUILA_JELLO_DIMENSION: ['mysterious_fixes', 'reality_bending']
        }
        
        self.logger.info("👻 Quantum Shadow People initialized - phasing between dimensions")

    def _update_network_interfaces(self):
        """Get actual network interface information"""
        try:
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            
            for interface, stat in stats.items():
                if stat.isup:  # Only track active interfaces
                    self.network_interfaces[interface] = {
                        'speed': stat.speed,  # Mbps
                        'mtu': stat.mtu,
                        'addresses': addrs.get(interface, [])
                    }
        except Exception as e:
            self.logger.error(f"Failed to update network interfaces: {e}")

    def _get_actual_bandwidth_capacity(self) -> float:
        """Get total bandwidth capacity from actual network interfaces"""
        total_capacity = 0
        for interface, info in self.network_interfaces.items():
            if info['speed'] > 0:  # Valid speed reported
                total_capacity += info['speed']
        
        # If no valid speeds found, check active connections for estimates
        if total_capacity == 0:
            # Use a more realistic estimate based on common connection types
            connections = psutil.net_connections()
            if len(connections) > 100:
                total_capacity = 1000  # Likely gigabit
            elif len(connections) > 50:
                total_capacity = 100   # Likely 100Mbps
            else:
                total_capacity = 10    # Conservative estimate
        
        return total_capacity * 1024 * 1024  # Convert to bps

    async def initialize_database(self):
        """Initialize database connection from the quantum realm"""
        if self.db is None:
            from .database_integration import QSPDatabaseIntegration
            self.db = QSPDatabaseIntegration(self.db_getter)
            await self.db.initialize()
    
    async def analyze_network_metrics(
        self, 
        network_data: Dict[str, Any],
        historical_data: Optional[List[Dict]] = None,
        user_id: Optional[str] = None
    ) -> Optional[QSPDecision]:
        """
        Quantum analysis of network performance using REAL data
        """
        # Phase into quantum analysis dimension
        await self._phase_into_quantum_dimension()
        
        try:
            # Update network interface info
            self._update_network_interfaces()
            
            # Store metrics if database available
            if self.db and user_id:
                await self.db.store_network_metrics(user_id, network_data)
            
            # Analyze current network state with REAL data
            network_analysis = await self._analyze_current_network_state(network_data)
            
            # Perform quantum security scan on ACTUAL connections
            security_analysis = await self._quantum_security_scan(network_data)
            network_analysis['security'] = security_analysis
            
            # Learn from historical patterns if available
            if historical_data and len(historical_data) > 0:
                pattern_analysis = await self._analyze_historical_patterns(historical_data, user_id)
                network_analysis.update(pattern_analysis)
            
            # Determine if quantum intervention is needed based on REAL issues
            decision = await self._determine_quantum_intervention(network_analysis, user_id)
            
            if decision:
                # Apply quantum fixes (log the decision)
                await self._apply_quantum_fixes(decision)
                
                # Store decision if database available
                if self.db and user_id:
                    await self.db.store_decision(user_id, decision)
            
            return decision
            
        except Exception as e:
            self.logger.error(f"👻💥 Quantum analysis failed: {str(e)}")
            await self._phase_back_to_corporeal()
            raise
        
        finally:
            await self._phase_back_to_corporeal()
    
    async def process_metrics(
        self,
        metrics: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process metrics for agent manager integration
        """
        user_id = user_context.get('user_id') if user_context else None
        
        # Extract REAL network data from metrics
        network_data = self._extract_network_data(metrics)
        
        # Get historical data if available
        historical_data = None
        if self.db and user_id:
            try:
                historical_data = await self.db.get_historical_network_data(user_id, days=7)
            except:
                pass  # Continue without historical data
        
          # Analyze with quantum abilities
        decision = await self.analyze_network_metrics(network_data, historical_data, user_id)
        
        # Return enhanced metrics
        enhanced_metrics = metrics.copy()
        
        if decision:
            enhanced_metrics['quantum_shadow_people'] = {
                'decision': decision.to_dict(),
                'quantum_state': self.quantum_state.value,
                'interventions_applied': self.quantum_fixes_applied,
                'tequila_jello_shots': self.tequila_jello_shots,
                'comprehension_warning': 'Results may defy conventional understanding'
            }
        else:
            enhanced_metrics['quantum_shadow_people'] = {
                'status': 'monitoring_from_shadows',
                'quantum_state': self.quantum_state.value,
                'message': 'Network operating within acceptable quantum parameters'
            }
        
        return enhanced_metrics
    
    def _extract_network_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract network-specific data from general metrics"""
        network_data = {}
        
        # Get REAL network data from metrics
        if 'network' in metrics and isinstance(metrics['network'], dict):
            network_data.update(metrics['network'])
        
        # Map actual metric names from psutil
        if 'network_io' in metrics:
            io_counters = metrics['network_io']
            if isinstance(io_counters, dict):
                network_data['bytes_sent'] = io_counters.get('bytes_sent', 0)
                network_data['bytes_recv'] = io_counters.get('bytes_recv', 0)
                network_data['packets_sent'] = io_counters.get('packets_sent', 0)
                network_data['packets_recv'] = io_counters.get('packets_recv', 0)
                network_data['errin'] = io_counters.get('errin', 0)
                network_data['errout'] = io_counters.get('errout', 0)
                network_data['dropin'] = io_counters.get('dropin', 0)
                network_data['dropout'] = io_counters.get('dropout', 0)
        
        # Calculate REAL packet loss from actual error/drop counts
        total_packets_in = network_data.get('packets_recv', 0)
        total_packets_out = network_data.get('packets_sent', 0)
        
        if total_packets_in > 0:
            packet_loss_in = (network_data.get('dropin', 0) + network_data.get('errin', 0)) / total_packets_in
        else:
            packet_loss_in = 0
            
        if total_packets_out > 0:
            packet_loss_out = (network_data.get('dropout', 0) + network_data.get('errout', 0)) / total_packets_out
        else:
            packet_loss_out = 0
        
        network_data['packet_loss'] = max(packet_loss_in, packet_loss_out)
        
        # Calculate REAL bandwidth utilization
        if 'network_sent_rate' in metrics and 'network_recv_rate' in metrics:
            sent_rate = metrics['network_sent_rate']  # bytes/sec
            recv_rate = metrics['network_recv_rate']  # bytes/sec
            total_rate = (sent_rate + recv_rate) * 8  # Convert to bits/sec
            
            # Use ACTUAL interface capacity
            capacity = self._get_actual_bandwidth_capacity()
            network_data['bandwidth_utilization'] = total_rate / capacity if capacity > 0 else 0
        
        # Get actual latency if available
        if 'ping' in metrics:
            network_data['latency'] = metrics['ping']
        
        # Connection count for security analysis
        try:
            connections = psutil.net_connections()
            network_data['active_connections'] = len(connections)
            network_data['connection_states'] = defaultdict(int)
            for conn in connections:
                if conn.status:
                    network_data['connection_states'][conn.status] += 1
        except:
            network_data['active_connections'] = 0
        
        return network_data
    
    async def _phase_into_quantum_dimension(self):
        """Phase into network analysis dimension"""
        previous_state = self.quantum_state
        self.quantum_state = QuantumPhaseState.QUANTUM_ENTANGLED
        self.logger.debug(f"👻 Phasing from {previous_state.value} to {self.quantum_state.value}")
        await asyncio.sleep(0.001)  # Quantum phase transition time
    
    async def _phase_back_to_corporeal(self):
        """Return to normal dimension"""
        self.quantum_state = QuantumPhaseState.CORPOREAL
        await asyncio.sleep(0.001)
    
    async def _shift_to_phase(self, target_phase: QuantumPhaseState):
        """Shift to specific quantum phase"""
        self.quantum_state = target_phase
        self.logger.info(f"👻 Phase shifted to {target_phase.value}")
        
        # Different phases require different amounts of tequila jello shots
        phase_requirements = {
            QuantumPhaseState.INTERDIMENSIONAL: 3,
            QuantumPhaseState.VOID_WALKER: 5,
            QuantumPhaseState.TEQUILA_JELLO_DIMENSION: 7
        }
        
        if target_phase in phase_requirements:
            await self._consume_tequila_jello_shots(phase_requirements[target_phase])
    
    async def _consume_tequila_jello_shots(self, count: int) -> int:
        """Consume tequila jello shots for quantum courage"""
        self.tequila_jello_shots += count
        self.logger.info(f"👻🍹 Consumed {count} tequila jello shots. Total: {self.tequila_jello_shots}")
        return count
    
    async def _quantum_security_scan(self, network_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        QSP phases through network layers to detect REAL intrusions
        """
        security_findings = {
            'phase_state': self.quantum_state.value,
            'anomalies_detected': [],
            'phase_exclusive_findings': [],
            'tequila_jello_shots_required': 0
        }
        
        # Analyze ACTUAL connection patterns
        active_connections = network_metrics.get('active_connections', 0)
        connection_states = network_metrics.get('connection_states', {})
        
        # Check for suspicious connection patterns
        if active_connections > 1000:
            security_findings['anomalies_detected'].append({
                'type': 'excessive_connections',
                'severity': 'high',
                'count': active_connections,
                'description': 'Unusually high number of active connections detected'
            })
            security_findings['tequila_jello_shots_required'] += 2
        
        # Check for SYN flood indicators
        syn_sent = connection_states.get('SYN_SENT', 0)
        if syn_sent > 100:
            security_findings['anomalies_detected'].append({
                'type': 'potential_syn_flood',
                'severity': 'critical',
                'syn_connections': syn_sent,
                'description': 'Large number of half-open connections detected'
            })
            security_findings['phase_exclusive_findings'].append({
                'type': 'INTERDIMENSIONAL_INTRUSION',
                'severity': 'HIGH',
                'description': f'Detected {syn_sent} SYN_SENT connections phasing through dimensions',
                'solution': 'Phase-shift firewall to quantum state',
                'comprehensibility': 0.3
            })
        
        # Check for packet anomalies
        packet_loss = network_metrics.get('packet_loss', 0)
        if packet_loss > 0.05:  # 5% loss
            security_findings['anomalies_detected'].append({
                'type': 'packet_void_leak',
                'severity': 'medium',
                'loss_rate': packet_loss,
                'description': 'Packets disappearing into the quantum void'
            })
        
        # Check bandwidth anomalies
        bandwidth_util = network_metrics.get('bandwidth_utilization', 0)
        if bandwidth_util > 0.95:
            security_findings['anomalies_detected'].append({
                'type': 'bandwidth_saturation_attack',
                'severity': 'high',
                'utilization': bandwidth_util,
                'description': 'Bandwidth saturated - possible DDoS'
            })
        
        return security_findings
    
    async def _scan_interdimensional_intrusions(self, network_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan for REAL network intrusions that QSP can detect"""
        intrusions = []
        
        # Check for impossible packet patterns
        errin = network_metrics.get('errin', 0)
        errout = network_metrics.get('errout', 0)
        dropin = network_metrics.get('dropin', 0)
        dropout = network_metrics.get('dropout', 0)
        
        # High error rates indicate dimensional instability
        total_errors = errin + errout + dropin + dropout
        if total_errors > 1000:
            intrusions.append({
                'type': 'dimensional_packet_instability',
                'severity': 'high',
                'error_count': total_errors,
                'description': 'Packets experiencing quantum decoherence',
                'solution': 'stabilize_packet_quantum_state'
            })
        
        # Check for timing anomalies
        if 'latency' in network_metrics:
            latency = network_metrics['latency']
            # Negative or impossible latencies
            if latency < 0 or latency > 10000:
                intrusions.append({
                    'type': 'temporal_anomaly',
                    'severity': 'critical',
                    'latency_value': latency,
                    'description': 'Time-space continuum disruption detected',
                    'solution': 'temporal_stabilization_required'
                })
        
        return intrusions
    
    async def _predict_network_attacks(self, network_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predict future attacks based on CURRENT patterns"""
        predictions = []
        
        # Analyze bandwidth trend
        bandwidth_util = network_metrics.get('bandwidth_utilization', 0)
        if 0.7 < bandwidth_util < 0.9:
            # Rising bandwidth usage pattern
            time_to_saturation = (1.0 - bandwidth_util) * 10  # Rough estimate in minutes
            predictions.append({
                'attack_type': 'bandwidth_exhaustion',
                'probability': 0.75,
                'time_until_attack': f'{time_to_saturation:.1f} minutes',
                'current_utilization': bandwidth_util,
                'recommended_action': 'preemptive_bandwidth_reallocation'
            })
        
        # Connection pattern analysis
        active_connections = network_metrics.get('active_connections', 0)
        if 500 < active_connections < 1000:
            predictions.append({
                'attack_type': 'connection_flood',
                'probability': 0.65,
                'time_until_attack': '5-10 minutes',
                'current_connections': active_connections,
                'recommended_action': 'connection_rate_limiting'
            })
        
        return predictions
    
    async def _analyze_current_network_state(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current network metrics with quantum precision"""
        analysis = {
            'latency_issues': [],
            'bandwidth_bottlenecks': [],
            'packet_loss_detected': False,
            'router_performance': {},
            'quantum_anomalies': []
        }
        
        # Analyze REAL latency
        if 'latency' in network_data and network_data['latency'] is not None:
            latency = network_data['latency']
            
            # Determine severity based on actual use case
            severity = 'low'
            if latency > 200:
                severity = 'critical'
            elif latency > 100:
                severity = 'high'
            elif latency > 50:
                severity = 'medium'
            
            if severity != 'low':
                analysis['latency_issues'].append({
                    'current_latency': latency,
                    'severity': severity,
                    'quantum_fix_recommended': latency > 150,
                    'impact': self._determine_latency_impact(latency)
                })
        
        # Analyze REAL bandwidth utilization
        if 'bandwidth_utilization' in network_data:
            utilization = network_data['bandwidth_utilization']
            if utilization > 0.8:
                analysis['bandwidth_bottlenecks'].append({
                    'utilization': utilization,
                    'severity': 'critical' if utilization > 0.95 else 'high',
                    'tequila_jello_optimization_needed': utilization > 0.9,
                    'capacity_used_mbps': utilization * self._get_actual_bandwidth_capacity() / (8 * 1024 * 1024)
                })
        
        # Detect REAL packet loss
        if 'packet_loss' in network_data:
            packet_loss = network_data['packet_loss']
            if packet_loss > 0.01:  # 1% packet loss threshold
                analysis['packet_loss_detected'] = True
                analysis['phantom_packet_recovery_needed'] = packet_loss > 0.05
                analysis['packet_loss_severity'] = {
                    'rate': packet_loss,
                    'impact': 'critical' if packet_loss > 0.1 else 'high' if packet_loss > 0.05 else 'medium'
                }
        
        # Check for quantum anomalies in REAL network behavior
        # High jitter indicates unstable network
        if 'jitter' in network_data and network_data['jitter'] > 50:
            analysis['quantum_anomalies'].append({
                'type': 'high_jitter',
                'value': network_data['jitter'],
                'dimensional_shift_required': True
            })
        
        # Analyze connection anomalies
        if 'active_connections' in network_data:
            conn_count = network_data['active_connections']
            if conn_count > 2000:
                analysis['quantum_anomalies'].append({
                    'type': 'connection_overload',
                    'value': conn_count,
                    'dimensional_shift_required': True,
                    'severity': 'critical'
                })
        
        return analysis
    
    def _determine_latency_impact(self, latency: float) -> str:
        """Determine impact based on actual latency value"""
        if latency < 20:
            return 'optimal_for_gaming'
        elif latency < 50:
            return 'good_for_streaming'
        elif latency < 100:
            return 'acceptable_for_browsing'
        elif latency < 200:
            return 'noticeable_delays'
        else:
            return 'severe_impact_on_all_activities'
    
    async def _analyze_historical_patterns(self, historical_data: List[Dict], user_id: str) -> Dict[str, Any]:
        """Learn from ACTUAL historical network patterns"""
        if not historical_data or len(historical_data) < 5:
            return {}
        
        pattern_analysis = {
            'recurring_issues': [],
            'optimization_opportunities': [],
            'learned_patterns': {},
            'peak_usage_times': []
        }
        
        # Analyze latency patterns over time
        latency_data = []
        for record in historical_data:
            if isinstance(record, dict) and 'latency' in record and record['latency'] is not None:
                latency_data.append({
                    'value': record['latency'],
                    'timestamp': record.get('timestamp', utc_now())
                })
        
        if len(latency_data) >= 5:
            latency_values = [d['value'] for d in latency_data]
            avg_latency = statistics.mean(latency_values)
            latency_stdev = statistics.stdev(latency_values) if len(latency_values) > 1 else 0
            
            pattern_analysis['learned_patterns']['latency'] = {
                'average': avg_latency,
                'std_deviation': latency_stdev,
                'trend': self._calculate_trend(latency_values),
                'spikes': len([l for l in latency_values if l > avg_latency + (2 * latency_stdev)]),
                'quantum_intervention_history': len([l for l in latency_values if l > 150])
            }
            
            # Identify recurring latency issues
            if avg_latency > 100:
                pattern_analysis['recurring_issues'].append({
                    'type': 'chronic_high_latency',
                    'average': avg_latency,
                    'frequency': 'persistent'
                })
        
        # Analyze bandwidth patterns with timestamps
        bandwidth_data = []
        for record in historical_data:
            if isinstance(record, dict) and 'bandwidth_utilization' in record:
                bandwidth_data.append({
                    'value': record['bandwidth_utilization'],
                    'timestamp': record.get('timestamp', utc_now())
                })
        
        if len(bandwidth_data) >= 5:
            bandwidth_values = [d['value'] for d in bandwidth_data]
            avg_bandwidth = statistics.mean(bandwidth_values)
            
            pattern_analysis['learned_patterns']['bandwidth'] = {
                'average': avg_bandwidth,
                'peak_value': max(bandwidth_values),
                'trend': self._calculate_trend(bandwidth_values)
            }
            
            # Identify peak usage times from ACTUAL data
            peak_times = self._identify_peak_usage_times(bandwidth_data)
            pattern_analysis['peak_usage_times'] = peak_times
            
            # Identify optimization opportunities
            if avg_bandwidth > 0.7:
                pattern_analysis['optimization_opportunities'].append({
                    'type': 'bandwidth_optimization',
                    'reason': 'consistently_high_usage',
                    'average_utilization': avg_bandwidth
                })
        
        # Analyze packet loss patterns
        packet_loss_data = []
        for record in historical_data:
            if isinstance(record, dict) and 'packet_loss' in record:
                packet_loss_data.append(record['packet_loss'])
        
        if packet_loss_data:
            avg_packet_loss = statistics.mean(packet_loss_data)
            if avg_packet_loss > 0.02:
                pattern_analysis['recurring_issues'].append({
                    'type': 'chronic_packet_loss',
                    'average': avg_packet_loss,
                    'severity': 'high' if avg_packet_loss > 0.05 else 'medium'
                })
        
        # Store patterns for this user
        if user_id:
            self.network_patterns[user_id] = pattern_analysis['learned_patterns']
        
        return pattern_analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from REAL data"""
        if len(values) < 3:
            return 'insufficient_data'
        
        # Calculate linear regression slope
        n = len(values)
        x = list(range(n))
        
        # Calculate means
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        # Calculate slope
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        # Determine trend based on slope relative to mean
        slope_percentage = (slope / y_mean) * 100 if y_mean != 0 else 0
        
        if slope_percentage > 5:
            return 'degrading'
        elif slope_percentage < -5:
            return 'improving'
        else:
            return 'stable'
    
    def _identify_peak_usage_times(self, bandwidth_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify ACTUAL peak usage times from timestamp data"""
        peak_times = []
        hour_usage = defaultdict(list)
        
        # Group by hour of day
        for data in bandwidth_data:
            if 'timestamp' in data and 'value' in data:
                timestamp = data['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                hour = timestamp.hour
                hour_usage[hour].append(data['value'])
        
        # Find hours with high average usage
        for hour, values in hour_usage.items():
            avg_usage = statistics.mean(values)
            if avg_usage > 0.7:  # 70% utilization
                peak_times.append({
                    'hour': hour,
                    'average_utilization': avg_usage,
                    'sample_count': len(values),
                    'time_period': f"{hour:02d}:00-{hour:02d}:59"
                })
        
        # Sort by utilization
        peak_times.sort(key=lambda x: x['average_utilization'], reverse=True)
        
        return peak_times
    
    async def _determine_quantum_intervention(self, analysis: Dict[str, Any], user_id: str) -> Optional[QSPDecision]:
        """Determine if quantum network intervention is needed based on REAL issues"""
        
        # Priority 1: Security threats
        if analysis.get('security', {}).get('phase_exclusive_findings'):
            for finding in analysis['security']['phase_exclusive_findings']:
                if finding.get('severity') == 'HIGH':
                    return await self._create_security_intervention(analysis['security'], user_id)
        
        # Priority 2: Critical latency issues
        if analysis.get('latency_issues'):
            for issue in analysis['latency_issues']:
                if issue.get('severity') == 'critical' and issue.get('quantum_fix_recommended'):
                    return await self._create_quantum_latency_fix(issue, user_id)
        
        # Priority 3: Bandwidth saturation
        if analysis.get('bandwidth_bottlenecks'):
            for bottleneck in analysis['bandwidth_bottlenecks']:
                if bottleneck.get('severity') == 'critical' and bottleneck.get('tequila_jello_optimization_needed'):
                    return await self._create_tequila_jello_optimization(bottleneck, user_id)
        
        # Priority 4: Severe packet loss
        if analysis.get('phantom_packet_recovery_needed'):
            packet_loss_info = analysis.get('packet_loss_severity', {})
            if packet_loss_info.get('impact') in ['critical', 'high']:
                return await self._create_phantom_packet_recovery(analysis, user_id)
        
        # Priority 5: Quantum anomalies
        if analysis.get('quantum_anomalies'):
            for anomaly in analysis['quantum_anomalies']:
                if anomaly.get('dimensional_shift_required') and anomaly.get('severity') == 'critical':
                    return await self._create_network_dimension_shift(anomaly, user_id)
        
        return None
    
    async def _create_quantum_latency_fix(self, issue: Dict, user_id: str) -> QSPDecision:
        """Create a latency fix based on REAL latency data"""
        current_latency = issue['current_latency']
        self.tequila_jello_shots += 2
        
        # Calculate realistic target based on current latency
        if current_latency > 500:
            target_latency = current_latency * 0.5  # 50% reduction for severe cases
        elif current_latency > 200:
            target_latency = current_latency * 0.6  # 40% reduction
        else:
            target_latency = current_latency * 0.7  # 30% reduction
        
        # Ensure target is achievable
        target_latency = max(20, target_latency)  # Can't go below physical limits
        
        return QSPDecision(
            decision_type=QSPDecisionType.MYSTERIOUS_LATENCY_FIX,
            quantum_state=QuantumPhaseState.TEQUILA_JELLO_DIMENSION,
            network_target="primary_router",
            optimization_parameters={
                'quantum_routing_algorithm': 'phase_shift_minimal_path',
                'temporal_adjustment': -0.023,  # Quantum time adjustment
                'router_phase_angle': 47.3,
                'current_latency': current_latency,
                'target_latency': target_latency,
                'optimization_method': 'quantum_packet_acceleration'
            },
            tequila_jello_shots_required=self.tequila_jello_shots,
            mysterious_explanation=f"Latency at {current_latency}ms is unacceptable. Phasing router through tequila jello dimension to achieve {target_latency}ms. The jello creates quantum tunnels for packets.",
            technical_details={
                'current_latency': current_latency,
                'target_latency': target_latency,
                'expected_improvement_percentage': ((current_latency - target_latency) / current_latency) * 100,
                'quantum_method': 'dimensional_phase_shift',
                'impact': issue.get('impact', 'unknown')
            },
            expected_improvement=(current_latency - target_latency) / current_latency,
            confidence_level=0.89,
            timestamp=utc_now()
        )
    
    async def _create_tequila_jello_optimization(self, bottleneck: Dict, user_id: str) -> QSPDecision:
        """Create bandwidth optimization based on REAL utilization data"""
        current_utilization = bottleneck['utilization']
        capacity_mbps = bottleneck.get('capacity_used_mbps', 0)
        self.tequila_jello_shots += 3
        
        # Calculate realistic optimization based on current state
        if current_utilization > 0.95:
            target_utilization = 0.75  # Emergency reduction
            compression_ratio = 1.5
        else:
            target_utilization = 0.70  # Standard optimization
            compression_ratio = 1.3
        
        return QSPDecision(
            decision_type=QSPDecisionType.TEQUILA_JELLO_OPTIMIZATION,
            quantum_state=QuantumPhaseState.TEQUILA_JELLO_DIMENSION,
            network_target="bandwidth_controller",
            optimization_parameters={
                'quantum_compression_ratio': compression_ratio,
                'tequila_jello_viscosity': 0.67,
                'current_capacity_mbps': capacity_mbps,
                'bandwidth_reallocation_strategy': 'quantum_multiplex',
                'optimization_algorithm': 'spectral_bandwidth_boost'
            },
            tequila_jello_shots_required=self.tequila_jello_shots,
            mysterious_explanation=f"Bandwidth at {current_utilization:.1%} ({capacity_mbps:.1f} Mbps). Phasing through tequila jello for quantum compression. Packets will temporarily exist in multiple dimensions.",
            technical_details={
                'current_utilization': current_utilization,
                'target_utilization': target_utilization,
                'compression_ratio': compression_ratio,
                'severity': bottleneck.get('severity', 'high'),
                'quantum_method': 'multidimensional_packet_compression'
            },
            expected_improvement=(current_utilization - target_utilization) / current_utilization,
            confidence_level=0.92,
            timestamp=utc_now()
        )
    
    async def _create_phantom_packet_recovery(self, analysis: Dict, user_id: str) -> QSPDecision:
        """Create packet recovery based on REAL packet loss data"""
        packet_loss_info = analysis.get('packet_loss_severity', {})
        loss_rate = packet_loss_info.get('rate', 0.05)
        
        # Quantum entanglement doesn't require tequila shots
        return QSPDecision(
            decision_type=QSPDecisionType.PHANTOM_PACKET_RECOVERY,
            quantum_state=QuantumPhaseState.QUANTUM_ENTANGLED,
            network_target="packet_recovery_system",
            optimization_parameters={
                'quantum_entanglement_strength': min(0.95, 1.0 - loss_rate),
                'phantom_packet_reconstruction': True,
                'temporal_packet_retrieval': 'enabled',
                'recovery_algorithm': 'quantum_entanglement_restoration',
                'loss_rate': loss_rate
            },
            tequila_jello_shots_required=0,
            mysterious_explanation=f"Packet loss at {loss_rate:.1%}. Quantum entangling with lost packets in parallel dimensions. They never truly disappeared, just took a detour through quantum space.",
            technical_details={
                'packet_loss_rate': loss_rate,
                'impact': packet_loss_info.get('impact', 'high'),
                'quantum_method': 'phantom_packet_reconstruction',
                'recovery_confidence': 0.85
            },
            expected_improvement=0.9,  # Can recover 90% of lost packets
            confidence_level=0.85,
            timestamp=utc_now()
        )
    
    async def _create_network_dimension_shift(self, anomaly: Dict, user_id: str) -> QSPDecision:
        """Create dimension shift for REAL network anomalies"""
        self.dimensional_shifts_performed += 1
        anomaly_type = anomaly.get('type', 'unknown')
        anomaly_value = anomaly.get('value', 0)
        
        return QSPDecision(
            decision_type=QSPDecisionType.NETWORK_DIMENSION_SHIFT,
            quantum_state=QuantumPhaseState.INTERDIMENSIONAL,
            network_target="entire_network_topology",
            optimization_parameters={
                'dimensional_shift_vector': [0.7, -0.3, 0.9],
                'quantum_topology_adjustment': 'multidimensional',
                'network_phase_alignment': 'optimal',
                'dimensional_anchor_points': 3,
                'anomaly_type': anomaly_type,
                'anomaly_value': anomaly_value
            },
            tequila_jello_shots_required=5,
            mysterious_explanation=f"Network anomaly detected: {anomaly_type} at level {anomaly_value}. Shifting network topology to dimension where this problem doesn't exist. Your internet will work the same, just... differently.",
            technical_details={
                'anomaly_type': anomaly_type,
                'anomaly_value': anomaly_value,
                'severity': anomaly.get('severity', 'critical'),
                'quantum_method': 'network_dimension_shift',
                'dimension_count': 3
            },
            expected_improvement=0.75,  # Major improvement expected
            confidence_level=0.78,
            timestamp=utc_now()
        )
    
    async def _create_security_intervention(self, security_data: Dict, user_id: str) -> QSPDecision:
        """Create security intervention for REAL threats"""
        findings = security_data.get('phase_exclusive_findings', [])
        anomalies = security_data.get('anomalies_detected', [])
        
        # Find the most critical threat
        critical_threat = None
        for finding in findings:
            if finding.get('severity') == 'HIGH':
                critical_threat = finding
                break
        
        if not critical_threat and anomalies:
            critical_threat = anomalies[0]
        
        self.tequila_jello_shots += 4
        
        return QSPDecision(
            decision_type=QSPDecisionType.INTERDIMENSIONAL_SECURITY,
            quantum_state=QuantumPhaseState.VOID_WALKER,
            network_target="security_perimeter",
            optimization_parameters={
                'quantum_firewall_phase': 'interdimensional',
                'threat_type': critical_threat.get('type', 'unknown'),
                'void_routing_enabled': True,
                'packet_phase_filtering': 'aggressive',
                'dimensional_isolation': True
            },
            tequila_jello_shots_required=self.tequila_jello_shots,
            mysterious_explanation=f"Security threat detected: {critical_threat.get('description', 'Unknown threat')}. Phasing firewall into void dimension where attackers cannot follow. Their packets will get lost in the quantum void.",
            technical_details={
                'threat_details': critical_threat,
                'security_findings': len(findings),
                'anomaly_count': len(anomalies),
                'quantum_method': 'void_dimension_isolation'
            },
            expected_improvement=0.95,  # High effectiveness against threats
            confidence_level=0.91,
            timestamp=utc_now()
        )
    
    async def _apply_quantum_fixes(self, decision: QSPDecision):
        """Log the quantum fix application"""
        self.quantum_fixes_applied += 1
        
        fix_log = {
            'timestamp': decision.timestamp.isoformat(),
            'decision_type': decision.decision_type.value,
            'quantum_state': decision.quantum_state.value,
            'network_target': decision.network_target,
            'expected_improvement': decision.expected_improvement,
            'tequila_jello_shots': decision.tequila_jello_shots_required,
            'mysterious_explanation': decision.mysterious_explanation,
            'fix_number': self.quantum_fixes_applied
        }
        
        self.logger.info(f"👻 Quantum fix #{self.quantum_fixes_applied} applied: {decision.decision_type.value}")
        
        return fix_log
    
    async def get_quantum_stats(self) -> Dict[str, Any]:
        """Get QSP performance statistics"""
        return {
            'quantum_state': self.quantum_state.value,
            'tequila_jello_shots_consumed': self.tequila_jello_shots,
            'quantum_fixes_applied': self.quantum_fixes_applied,
            'dimensional_shifts_performed': self.dimensional_shifts_performed,
            'network_patterns_learned': len(self.network_patterns),
            'active_network_interfaces': len(self.network_interfaces),
            'total_bandwidth_capacity_mbps': self._get_actual_bandwidth_capacity() / (1024 * 1024),
            'status': 'phased_and_ready'
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status for agent manager"""
        return {
            'agent_name': 'quantum_shadow_people',
            'status': 'operational',
            'quantum_state': self.quantum_state.value,
            'quantum_fixes_applied': self.quantum_fixes_applied,
            'tequila_jello_shots': self.tequila_jello_shots,
            'dimensional_shifts': self.dimensional_shifts_performed,
            'network_patterns_stored': len(self.network_patterns),
            'last_phase_shift': utc_now().isoformat()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for QSP"""
        return {
            'agent_name': 'quantum_shadow_people',
            'status': 'PHASED_AND_OPERATIONAL',
            'brain_version': '2.0.0',
            'quantum_abilities': 'FULLY_FUNCTIONAL',
            'tequila_jello_supply': 'INFINITE',
            'dimensional_access': 'UNRESTRICTED',
            'network_interfaces_monitored': len(self.network_interfaces),
            'comprehension_warning': 'Results may defy conventional understanding',
            'effectiveness': 'MYSTERIOUSLY_HIGH'
        }

# Global brain instance
quantum_shadow_people_brain = QuantumShadowPeopleBrainV2()

# Convenience functions
async def analyze_network_quantum(
    network_data: Dict[str, Any],
    user_id: Optional[str] = None
) -> Optional[QSPDecision]:
    """Convenience function for quantum network analysis"""
    return await quantum_shadow_people_brain.analyze_network_metrics(network_data, user_id=user_id)

def get_quantum_network_stats() -> Dict[str, Any]:
    """Get current quantum network statistics"""
    return asyncio.run(quantum_shadow_people_brain.get_quantum_stats())