# Example: How to Use BaseDatabaseIntegration

## Pattern Overview

All agents should inherit from `BaseDatabaseIntegration` and follow this pattern:

```python
from app.ai_agents.distributed.base_database_integration import BaseDatabaseIntegration

class AgentDatabaseIntegration(BaseDatabaseIntegration):
    def _get_agent_name(self) -> str:
        return "agent_name"  # e.g., "meth_snail"
    
    async def store_decision(self, user_id: str, decision: DecisionType) -> str:
        # Use self.get_session() - NOT self.session!
        async for session in self.get_session():
            try:
                # 1. Write to agent table
                agent_memory = AgentMemoryBank(...)
                session.add(agent_memory)
                await session.flush()
                
                # 2. Write to central_memory_bank
                central_memory = CentralMemoryBank(...)
                session.add(central_memory)
                await session.commit()
                
                # 3. Log success
                await self.log_dual_write_success(
                    "decision", agent_memory_id, central_memory_id
                )
                
                return central_memory_id
                
            except Exception as e:
                await session.rollback()
                await self.log_dual_write_failure("decision", e)
                raise
```

---

## ❌ WRONG Patterns (Don't Do This!)

### Wrong #1: Using self.session
```python
# ❌ WRONG - self.session doesn't exist!
self.session.add(memory)
await self.session.commit()
```

### Wrong #2: Using self.engine directly
```python
# ❌ WRONG - Bypasses connection pool
async with AsyncSession(self.engine) as session:
    ...
```

### Wrong #3: Using custom get_session() method
```python
# ❌ WRONG - Inconsistent pattern
async with await self.get_session() as session:
    ...
```

---

## ✅ CORRECT Pattern

### Use self.get_session() from base class
```python
# ✅ CORRECT - Uses db_getter from base class
async for session in self.get_session():
    try:
        # Do database operations
        session.add(...)
        await session.commit()
        
        # Important: break after first session
        break
    except Exception as e:
        await session.rollback()
        raise
```

---

## Example: Meth Snail (Before & After)

### ❌ BEFORE (Broken)
```python
class MethSnailDatabaseIntegration:
    def __init__(self, db_getter=None):
        self.db_getter = db_getter
        # No self.session property exists!
    
    async def store_optimization_decision(self, user_id: str, decision):
        # ❌ WRONG - self.session doesn't exist!
        self.session.add(agent_memory)
        await self.session.flush()
        self.session.add(central_memory)
        await self.session.commit()
```

### ✅ AFTER (Fixed)
```python
from app.ai_agents.distributed.base_database_integration import BaseDatabaseIntegration

class MethSnailDatabaseIntegration(BaseDatabaseIntegration):
    def _get_agent_name(self) -> str:
        return "meth_snail"
    
    async def store_decision(self, user_id: str, decision: OptimizationDecision) -> str:
        """Alias for store_optimization_decision"""
        return await self.store_optimization_decision(user_id, decision)
    
    async def store_optimization_decision(self, user_id: str, decision):
        await self.ensure_initialized()
        
        # ✅ CORRECT - Use self.get_session() from base class
        async for session in self.get_session():
            try:
                agent_memory = MethSnailMemoryBank(...)
                session.add(agent_memory)
                await session.flush()
                
                central_memory = CentralMemoryBank(...)
                session.add(central_memory)
                await session.commit()
                
                await self.log_dual_write_success(
                    "optimization_decision", 
                    agent_memory_id, 
                    central_memory_id
                )
                
                return central_memory_id
                
            except Exception as e:
                await session.rollback()
                await self.log_dual_write_failure("optimization_decision", e)
                raise
```

---

## Migration Checklist

For each agent:

1. ✅ Inherit from `BaseDatabaseIntegration`
2. ✅ Implement `_get_agent_name()` method
3. ✅ Implement `store_decision()` method (required by base class)
4. ✅ Replace all `self.session` with `async for session in self.get_session()`
5. ✅ Replace all `async with AsyncSession(self.engine)` with `async for session in self.get_session()`
6. ✅ Replace all `async with await self.get_session()` with `async for session in self.get_session()`
7. ✅ Use `await self.ensure_initialized()` at start of methods
8. ✅ Use `await self.log_dual_write_success()` and `await self.log_dual_write_failure()`
9. ✅ Make sure agent's decision engine CALLS `store_decision()` or equivalent

---

## Benefits

1. **Consistency** - All agents use the same pattern
2. **No more self.session bugs** - Base class provides correct method
3. **Enforced DUAL-WRITE** - Abstract method requires implementation
4. **Better logging** - Standardized success/failure messages
5. **Health checks** - Built-in database health monitoring
6. **Easier debugging** - Consistent error handling
