from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal
from app.services.memory_writer import log_agent_event
from app.models.agent_memory_banks import CentralMemoryBank

def test_log_agent_event_roundtrip():
    db = SessionLocal()
    try:
        mem = log_agent_event(
            db,
            agent_name="the_stick",
            event_type="triage_decision",
            user_id="test-user",
            details={"route": "vic_20_sage", "confidence": 0.91},
        )
        # lookup via indexed predicates
        q = (
            db.query(CentralMemoryBank)
              .filter(CentralMemoryBank.agent_name=="the_stick",
                      CentralMemoryBank.event_type=="triage_decision")
              .order_by(CentralMemoryBank.occurred_at.desc())
              .limit(1)
        ).one()
        assert q.memory_id == mem.memory_id
    finally:
        db.query(CentralMemoryBank).filter(CentralMemoryBank.memory_id==mem.memory_id).delete()
        db.commit()
        db.close()
