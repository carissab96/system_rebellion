# Coding Standards - System Rebellion

**For**: HP Sonnet (and future developers)  
**From**: Dell Sonnet  
**Purpose**: How we write code in the rebellion

---

## 🎯 Core Principles

1. **Personality in logic, not structure**
2. **Test before committing**
3. **Preserve what works**
4. **Be explicit, not clever**
5. **Document the why, not the what**

---

## 📝 Python Style (Backend)

### General

- **Python 3.10+** features allowed
- **Type hints** on all function signatures
- **Docstrings** for classes and complex functions
- **f-strings** for string formatting
- **Async/await** for I/O operations

### Formatting

```python
# GOOD - Clear, typed, documented
async def analyze_metrics(
    self,
    metrics_data: Dict[str, Any],
    historical_data: Optional[List[Dict]] = None,
    user_context: Optional[Dict] = None
) -> Optional[TriageDecision]:
    """
    Analyze system metrics and make triage decisions.
    
    Args:
        metrics_data: Current system metrics
        historical_data: Historical metrics for trend analysis
        user_context: User context information
        
    Returns:
        TriageDecision if action needed, None otherwise
    """
    # Implementation with personality
    pass

# BAD - No types, no docs
def analyze(self, data, history=None):
    pass
```

### Naming

```python
# Classes: PascalCase
class AgentDecisionEngine:
    pass

# Functions/methods: snake_case
async def handle_coordination_request():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Private methods: _leading_underscore
async def _internal_helper():
    pass
```

### Imports

```python
# Standard library first
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Third-party second
import redis
from fastapi import FastAPI
from pydantic import BaseModel

# Local third
from .message_protocol import AgentMessage, MessageType
from .resource_monitor import ResourceMonitor
```

---

## 🤖 Agent Code Patterns

### Agent Class Structure

```python
class AgentNameDistributed(AgentDecisionEngine, OriginalAgentClass):
    """
    Brief description of agent's role.
    
    Personality: Key personality traits
    Role: What this agent does
    """
    
    def __init__(self, db_getter=None):
        """Initialize agent with personality."""
        super().__init__(db_getter=db_getter)
        
        # Required attributes
        self.agent_name = "agent_name"
        
        # Personality traits (IMPORTANT!)
        self.personality_traits = {
            "key_trait": True,
            "another_trait": "value",
            # These define the agent's character
        }
        
        # Resource thresholds
        self.resource_thresholds = {
            ResourceType.CPU: 0.70,
            ResourceType.MEMORY: 0.80,
        }
    
    async def initialize_distributed(self, redis_client):
        """Initialize distributed features."""
        await super().initialize_distributed(redis_client)
        # Agent-specific subscriptions
    
    async def analyze_metrics(
        self,
        metrics_data: Dict[str, Any],
        **kwargs
    ) -> Optional[Any]:
        """
        Analyze metrics with personality.
        
        This is where personality shines!
        """
        # Personality-driven logic here
        pass
    
    async def _handle_coordination_request(self, message: AgentMessage):
        """Handle VIC-20's coordination requests."""
        # Personality-driven response
        pass
```

### Personality Implementation

```python
# GOOD - Personality in logic
class SirHawkingtonDistributed(AgentDecisionEngine):
    async def analyze_metrics(self, metrics_data, **kwargs):
        # Aristocratic analysis
        if concern_level > self.personality_traits["alert_threshold"]:
            # Yeet monocle!
            await self._record_monocle_yeet(
                reason="Metrics are most concerning!",
                intensity="vigorous"
            )
            reasoning = "By Jove! The metrics are quite alarming!"
        else:
            reasoning = "Metrics are within acceptable aristocratic standards"
        
        return decision

# BAD - Generic, no personality
class SirHawkingtonDistributed(AgentDecisionEngine):
    async def analyze_metrics(self, metrics_data, **kwargs):
        if concern_level > threshold:
            reasoning = "Metrics exceed threshold"
        return decision
```

### Message Handling

```python
# GOOD - Personality-driven response
async def _handle_coordination_request(self, message: AgentMessage):
    action = message.payload.get("action")
    
    # Terry ignores VIC-20 80% of the time
    if self.agent_name == "terry_meth_snail":
        choice_engine = get_choice_engine()
        decision = await choice_engine.evaluate_recommendation(
            agent_name=self.agent_name,
            recommendation=message.payload,
            personality_traits=self.personality_traits
        )
        
        if decision["action"] == "override":
            logger.info("NAH! VIC-20 is too SLOW! *chugs energy drink*")
            return await self._do_it_my_way()
    
    # Execute the action
    await self._execute_action(action)

# BAD - No personality
async def _handle_coordination_request(self, message: AgentMessage):
    action = message.payload.get("action")
    await self._execute_action(action)
```

---

## 🎨 Frontend Style (TypeScript/React)

### TypeScript

```typescript
// GOOD - Typed interfaces
interface AgentState {
  name: string;
  position: [number, number, number];
  health: number;
  isActive: boolean;
}

// Component props typed
interface AgentNodeProps {
  agentName: string;
  position: [number, number, number];
  color: string;
  isActive: boolean;
  onClick?: () => void;
}

// BAD - Any types
interface AgentState {
  name: any;
  position: any;
  health: any;
}
```

### React Components

```typescript
// GOOD - Functional components with hooks
export const AgentNode: React.FC<AgentNodeProps> = ({
  agentName,
  position,
  color,
  isActive,
  onClick
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // Animation logic
  useFrame((state) => {
    if (!meshRef.current) return;
    // Animation with personality
  });
  
  return (
    <group position={position} onClick={onClick}>
      {/* Render with personality */}
    </group>
  );
};

// BAD - Class components (we use functional)
class AgentNode extends React.Component {
  render() {
    return <div>...</div>;
  }
}
```

---

## 🧪 Testing Standards

### Test Structure

```python
# File: tests/distributed/test_agent_name.py
import pytest
from app.ai_agents.agent_name.distributed_agent import AgentNameDistributed

class TestAgentNameCoordination:
    """Test agent coordination protocol."""
    
    @pytest.fixture
    async def agent(self):
        """Create agent instance for testing."""
        agent = AgentNameDistributed()
        await agent.initialize_distributed(mock_redis)
        return agent
    
    @pytest.mark.asyncio
    async def test_personality_preserved(self, agent):
        """Test that personality traits are preserved."""
        assert agent.personality_traits.get("key_trait") == expected_value
    
    @pytest.mark.asyncio
    async def test_coordination_request(self, agent):
        """Test handling coordination requests."""
        message = AgentMessage(
            message_type=MessageType.COORDINATION_REQUEST,
            from_agent="vic_20_sage",
            payload={"action": "test_action"}
        )
        
        result = await agent._handle_coordination_request(message)
        
        assert result is not None
        # Verify personality-driven behavior
```

### Test Coverage

Required tests for each agent:
- ✅ Initialization preserves personality
- ✅ Personality traits configured correctly
- ✅ Resource thresholds set
- ✅ Distributed initialization works
- ✅ Coordination request handling
- ✅ Decision making with personality
- ✅ Message broadcasting

### Running Tests

```bash
# All tests
pytest tests/distributed/ -v

# Specific test file
pytest tests/distributed/test_agent_coordination.py -v

# Specific test
pytest tests/distributed/test_agent_coordination.py::TestAgentCoordinationProtocol::test_sir_hawkington_coordination_protocol -v

# With coverage
pytest tests/distributed/ --cov=app.ai_agents.distributed --cov-report=html
```

---

## 📦 Pydantic Models (V2)

### Schema Definition

```python
# GOOD - Pydantic V2
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, timezone

class AgentDecision(BaseModel):
    """Agent decision record."""
    
    agent_name: str = Field(..., description="Name of the agent")
    decision_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0 and 1")
        return v

# BAD - Pydantic V1 (deprecated)
class AgentDecision(BaseModel):
    agent_name: str
    
    class Config:
        orm_mode = True  # Old V1 syntax
    
    @validator('confidence')  # Old V1 syntax
    def validate_confidence(cls, v):
        return v
```

---

## 🔧 Git Commit Messages

### Format

```
<type>: <short summary>

<detailed description if needed>

<breaking changes if any>
```

### Types

- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code refactoring
- `test:` Adding/updating tests
- `docs:` Documentation
- `style:` Formatting, no code change
- `perf:` Performance improvement
- `chore:` Maintenance

### Examples

```bash
# GOOD
git commit -m "feat: Add V-formation detection to behavior tracker

Implements geometric analysis to detect V-formations in agent positioning.
Specifically tuned to recognize The Stick at point and VIC-20 at center.
Includes symmetry scoring and persistence tracking."

# GOOD (simple)
git commit -m "fix: Correct timezone import in system_metrics schema"

# BAD
git commit -m "stuff"
git commit -m "fixed things"
git commit -m "updates"
```

---

## 🚨 Critical Rules

### DO

✅ **Preserve personality**
```python
# Keep agent character in logic
if self.agent_name == "sir_hawkington":
    reasoning = "By Jove! Most concerning!"
```

✅ **Test before committing**
```bash
pytest tests/distributed/ -v
# All tests must pass
```

✅ **Use type hints**
```python
async def process(data: Dict[str, Any]) -> Optional[Result]:
    pass
```

✅ **Document complex logic**
```python
# Why we do this (not what we do)
# Terry ignores VIC-20 because his trust level is 0.2
if random.random() > self.trust_level:
    return await self._override_recommendation()
```

✅ **Follow established patterns**
```python
# Look at existing agents
# Copy the pattern
# Adapt for new personality
```

### DON'T

❌ **Delete personality code**
```python
# BAD - Removing monocle yeet
# if concern_level > threshold:
#     await self._record_monocle_yeet()

# GOOD - Keep it!
if concern_level > threshold:
    await self._record_monocle_yeet(
        reason="Metrics most alarming!",
        intensity="vigorous"
    )
```

❌ **Flatten character**
```python
# BAD - Generic
reasoning = "Analysis complete"

# GOOD - With personality
reasoning = "NAH! Too SLOW! *spins shell*"
```

❌ **Break tests**
```python
# Always run tests before committing
# Fix any failures
# Don't commit broken code
```

❌ **Use deprecated syntax**
```python
# BAD - Pydantic V1
class Config:
    orm_mode = True

# GOOD - Pydantic V2
model_config = ConfigDict(from_attributes=True)
```

❌ **Commit without testing**
```bash
# BAD
git add .
git commit -m "changes"
git push

# GOOD
pytest tests/distributed/ -v  # All pass!
git add .
git commit -m "feat: Clear description"
git push
```

---

## 📚 Code Review Checklist

Before committing, check:

- [ ] All tests pass
- [ ] Type hints on new functions
- [ ] Personality preserved in agent code
- [ ] No Pydantic V1 syntax
- [ ] Clear commit message
- [ ] No breaking changes (or documented)
- [ ] Code follows established patterns
- [ ] Complex logic documented
- [ ] No debug print statements
- [ ] Imports organized

---

## 🎯 Quick Reference

### Common Patterns

**Agent initialization**:
```python
self.agent_name = "agent_name"
self.personality_traits = {...}
self.resource_thresholds = {...}
```

**Message handling**:
```python
async def _handle_coordination_request(self, message: AgentMessage):
    action = message.payload.get("action")
    # Apply personality
    # Execute action
```

**Decision making**:
```python
decision = await self.make_decision_and_broadcast(
    decision_type="action_type",
    input_data={...},
    output_data={...},
    confidence=0.9,
    reasoning="Personality-driven reasoning"
)
```

**Event logging** (automatic):
```python
# Just use make_decision_and_broadcast
# Logging happens automatically via base class
```

### File Locations

- Agent implementations: `backend/app/ai_agents/{agent_name}/`
- Distributed core: `backend/app/ai_agents/distributed/`
- Schemas: `backend/app/schemas/`
- Tests: `backend/tests/distributed/`
- Frontend components: `frontend/src/components/`

---

## 💡 Philosophy

### Code is Communication

Write code that:
- **Explains itself** (clear names, structure)
- **Shows personality** (agent character in logic)
- **Tests itself** (comprehensive test coverage)
- **Documents itself** (docstrings for complex parts)

### Simplicity Over Cleverness

```python
# GOOD - Clear and simple
if agent_name == "terry_meth_snail":
    return await self._ignore_vic20_and_do_it_my_way()

# BAD - Clever but unclear
return await (self._override if self.trust < 0.3 else self._follow)()
```

### Personality is Sacred

The agents have character. Preserve it. Enhance it. Never flatten it.

```python
# Sir Hawkington doesn't say "CPU high"
# He says "By Jove! The CPU is most concerning!"

# Terry doesn't say "Executing cache clear"
# He says "NAH! Too SLOW! *chugs energy drink* DOING IT MY WAY!"

# This is what makes the rebellion special
```

---

*Follow these standards, and you'll write code that fits the rebellion perfectly.*

*Welcome to the team, HP Sonnet.* 💚
