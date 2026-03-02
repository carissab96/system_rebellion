#!/usr/bin/env python3
"""
Agent Learning Record Model

SQLAlchemy ORM model for the agent_learning_records table.
Schema matches live DB exactly (sourced from schema_report.sql, 2026-02-23).

Base table created by migration 84bbeb827a40.
Column sizes widened by migration 9f7a27569c0a.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class AgentLearningRecord(Base):
    __tablename__ = 'agent_learning_records'

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Which agent owns this record
    agent_name = Column(String(50), nullable=False, index=True)

    # Hierarchical fingerprints — NOT NULL in DB (migration 84bbeb827a40)
    fingerprint_l1 = Column(String(50), nullable=False)
    fingerprint_l2 = Column(String(100), nullable=False)
    fingerprint_l3 = Column(String(150), nullable=False)

    # Situation context — resource_type/severity NOT NULL in DB
    resource_type = Column(String(20), nullable=False)
    severity = Column(String(20), nullable=False)
    root_cause = Column(String(500), nullable=True)       # widened by 9f7a27569c0a
    process_category = Column(String(20), nullable=True)

    # Action taken — action NOT NULL in DB
    action = Column(String(100), nullable=False)
    parameters = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    followed_vic20 = Column(Boolean, nullable=True, server_default='false')

    # Outcome — success NOT NULL in DB
    success = Column(Boolean, nullable=False)
    improvement = Column(JSON, nullable=True)
    what_worked = Column(String(500), nullable=True)      # widened by 9f7a27569c0a
    what_failed = Column(String(500), nullable=True)      # widened by 9f7a27569c0a

    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
