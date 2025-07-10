# /models/qsp_models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class QSPNetworkMetrics(Base):
    """Store network metrics for quantum analysis"""
    __tablename__ = 'qsp_network_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # Core network metrics
    latency = Column(Float, nullable=True)
    bandwidth_utilization = Column(Float, nullable=True)
    packet_loss = Column(Float, nullable=True)
    jitter = Column(Float, nullable=True)
    
    # Network details
    download_speed = Column(Float, nullable=True)
    upload_speed = Column(Float, nullable=True)
    connection_type = Column(String, nullable=True)
    
    # Raw metrics data
    raw_metrics = Column(JSON, nullable=True)

class QSPDecisionLog(Base):
    """Store QSP quantum decisions and optimizations"""
    __tablename__ = 'qsp_decision_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # Decision details
    decision_type = Column(String, nullable=False, index=True)
    quantum_state = Column(String, nullable=False)
    network_target = Column(String, nullable=False)
    
    # Optimization details
    optimization_parameters = Column(JSON, nullable=True)
    tequila_jello_shots_required = Column(Integer, default=0)
    mysterious_explanation = Column(Text, nullable=True)
    technical_details = Column(JSON, nullable=True)
    
    # Performance metrics
    expected_improvement = Column(Float, nullable=True)
    confidence_level = Column(Float, nullable=True)
    
    # Success tracking
    optimization_applied = Column(Boolean, default=False)
    actual_improvement = Column(Float, nullable=True)
    success_verified = Column(Boolean, default=False)

class QSPQuantumStats(Base):
    """Store QSP quantum performance statistics"""
    __tablename__ = 'qsp_quantum_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # Quantum performance
    quantum_fixes_applied = Column(Integer, default=0)
    tequila_jello_shots_consumed = Column(Integer, default=0)
    dimensional_shifts_performed = Column(Integer, default=0)
    
    # Network improvement metrics
    average_latency_improvement = Column(Float, nullable=True)
    average_bandwidth_improvement = Column(Float, nullable=True)
    packet_loss_reductions = Column(Integer, default=0)
    
    # Learning metrics
    network_patterns_learned = Column(Integer, default=0)
    optimization_success_rate = Column(Float, nullable=True)
    
    # Raw stats
    raw_stats = Column(JSON, nullable=True)

class QSPNetworkPatterns(Base):
    """Store learned network patterns for optimization"""
    __tablename__ = 'qsp_network_patterns'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    
    # Pattern identification
    pattern_type = Column(String, nullable=False, index=True)
    pattern_name = Column(String, nullable=True)
    
    # Pattern data
    pattern_data = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=True)
    
    # Pattern effectiveness
    optimization_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    
    # Last update
    last_updated = Column(DateTime, default=datetime.now, nullable=False)