# Schema Layer Guide

This directory contains **Pydantic schemas** for all database models.
Schemas define how data moves between:

- The database (SQLAlchemy models)
- API endpoints (FastAPI request/response models)
- Services & repositories (internal validation)

---

## 🔑 Naming Convention

For each SQLAlchemy model in `app/models/`, create a matching schema file in `app/schemas/`:

- `models/agent_memory_banks.py` → `schemas/agent_memory.py`
- `models/agent_decision_models.py` → `schemas/agent_decision.py`
- `models/agent_tracking.py` → `schemas/agent_tracking.py`
- etc.

---

## 🧩 Schema Structure

Each schema file should include **3 main classes**:

1. **Base** – shared fields across all operations
2. **Create** – used for inserts (inherits from Base)
3. **Read** – used for reading from DB or API responses

Always include:
```python
class Config:
    from_attributes = True
