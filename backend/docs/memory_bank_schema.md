# Memory Bank Schema Documentation

## Overview
The Memory Bank system is designed to provide persistent, structured storage for AI agent memories and learnings. It enables agents to store, retrieve, and share knowledge across different parts of the system.

## Core Components

### 1. Memory Banks
Each agent has its own memory bank for storing agent-specific memories:
- `SirHawkingtonMemoryBank`: For data quality and monitoring insights
- `MethSnailMemoryBank`: For optimization patterns and performance data
- `HamstersMemoryBank`: For infrastructure and system insights
- `QuantumShadowPeopleMemoryBank`: For security and anomaly detection
- `VIC20MemoryBank`: For coordination and mediation patterns
- `CentralMemoryBank`: Shared memory for cross-agent learning

### 2. Schema Types

#### Base Models
- `AgentMemoryBase`: Base class for all memory entries
- `MemoryBankBase`: Base class for memory banks
- `CentralMemoryBase`: Base class for central/shared memories

#### CRUD Operations
- `*Create`: Schemas for creating new entries
- `*Update`: Schemas for updating existing entries
- `*InDB`: Schemas for database representation
- `*Response`: Schemas for API responses

### 3. Memory Categories
Memories are categorized for better organization:
- `OBSERVATION`: Raw system/agent observations
- `DECISION`: Agent decisions and their rationales
- `PATTERN`: Recognized patterns in system behavior
- `PREFERENCE`: User/agent preferences
- `INCIDENT`: System/security incidents
- `LEARNING`: Learned behaviors and optimizations
- `COORDINATION`: Inter-agent coordination data
- `PERFORMANCE`: Performance metrics and optimizations

## Database Schema

### AgentMemoryBank Table
```sql
CREATE TABLE agent_memory_bank (
    id SERIAL PRIMARY KEY,
    memory_id UUID NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    memory_type VARCHAR(50) NOT NULL,
    content JSONBCompat NOT NULL,
    importance INTEGER DEFAULT 2,
    context JSONBCompat,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    is_shared BOOLEAN DEFAULT FALSE,
    shared_with_central BOOLEAN DEFAULT FALSE,
    central_memory_id UUID
);

-- Indexes
CREATE INDEX idx_agent_memory_user ON agent_memory_bank(user_id);
CREATE INDEX idx_agent_memory_agent ON agent_memory_bank(agent_name);
CREATE INDEX idx_agent_memory_type ON agent_memory_bank(memory_type);
CREATE INDEX idx_agent_memory_shared ON agent_memory_bank(shared_with_central, central_memory_id);
```

### CentralMemoryBank Table
```sql
CREATE TABLE central_memory_bank (
    id SERIAL PRIMARY KEY,
    memory_id UUID NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
    source_agent VARCHAR(100) NOT NULL,
    source_memory_id UUID,
    memory_type VARCHAR(50) NOT NULL,
    content JSONBCompat NOT NULL,
    importance INTEGER DEFAULT 2,
    context JSONBCompat,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    relevance_score FLOAT DEFAULT 1.0
);

-- Indexes
CREATE INDEX idx_central_memory_user ON central_memory_bank(user_id);
CREATE INDEX idx_central_memory_agent ON central_memory_bank(source_agent);
CREATE INDEX idx_central_memory_type ON central_memory_bank(memory_type);
CREATE INDEX idx_central_memory_relevance ON central_memory_bank(relevance_score);
```

## API Endpoints

### Agent Memory Endpoints
- `POST /api/memories/agent` - Create a new agent memory
- `GET /api/memories/agent/{memory_id}` - Get a specific agent memory
- `PUT /api/memories/agent/{memory_id}` - Update an agent memory
- `DELETE /api/memories/agent/{memory_id}` - Delete an agent memory
- `GET /api/memories/agent` - List/filter agent memories

### Central Memory Endpoints
- `POST /api/memories/central` - Share a memory to central bank
- `GET /api/memories/central/{memory_id}` - Get a central memory
- `PUT /api/memories/central/{memory_id}` - Update a central memory
- `DELETE /api/memories/central/{memory_id}` - Delete a central memory
- `GET /api/memories/central` - List/filter central memories

## Usage Examples

### Creating a New Memory
```python
from datetime import datetime
from app.schemas.agent_memory import AgentMemoryCreate

memory = AgentMemoryCreate(
    user_id="user_123",
    agent_name="sir_hawkington",
    memory_type="PATTERN",
    content={
        "pattern_name": "high_cpu_usage",
        "threshold": 90.0,
        "conditions": ["cpu_usage > 90%", "duration > 5m"],
        "severity": "high"
    },
    importance=3,  # HIGH
    context={
        "detected_at": "2023-05-15T14:30:00Z",
        "system_load": 4.2,
        "process_count": 187
    },
    tags=["performance", "alert", "cpu"]
)
```

### Querying Memories
```python
# Get all high-importance memories for an agent
high_importance_memories = db.query(AgentMemoryBank).filter(
    AgentMemoryBank.user_id == current_user.id,
    AgentMemoryBank.agent_name == "sir_hawkington",
    AgentMemoryBank.importance >= 3  # HIGH or CRITICAL
).all()

# Find memories by tag
cpu_memories = db.query(AgentMemoryBank).filter(
    AgentMemoryBank.user_id == current_user.id,
    AgentMemoryBank.tags.contains(["cpu"])
).all()
```

## Best Practices

1. **Memory Organization**
   - Use consistent naming for memory types and tags
   - Keep memory content structured and well-documented
   - Set appropriate importance levels for better filtering

2. **Performance**
   - Use indexes on frequently queried fields
   - Limit the size of memory content
   - Use pagination for listing endpoints

3. **Security**
   - Always validate memory content
   - Implement proper access controls
   - Sanitize user-provided data

4. **Maintenance**
   - Regularly archive old memories
   - Clean up unused or redundant memories
   - Monitor memory bank growth

## Integration with Agents

Each agent should implement methods to interact with its memory bank:

```python
class Agent:
    def __init__(self, agent_name: str, db: Session):
        self.agent_name = agent_name
        self.db = db
    
    def remember(self, memory_data: Dict[str, Any], memory_type: str, **kwargs):
        """Store a new memory"""
        memory = AgentMemoryCreate(
            user_id=current_user.id,
            agent_name=self.agent_name,
            memory_type=memory_type,
            content=memory_data,
            **kwargs
        )
        return create_agent_memory(db=self.db, memory=memory)
    
    def recall(self, memory_id: str) -> Optional[AgentMemoryInDB]:
        """Retrieve a specific memory"""
        return get_agent_memory(db=self.db, memory_id=memory_id)
    
    def find_related_memories(self, query: str, limit: int = 10) -> List[AgentMemoryInDB]:
        """Find memories related to a query"""
        return search_agent_memories(
            db=self.db,
            user_id=current_user.id,
            agent_name=self.agent_name,
            query=query,
            limit=limit
        )
```

## Testing

Test cases should cover:
- Memory creation and retrieval
- Memory updates and deletion
- Access controls and permissions
- Memory search and filtering
- Performance with large datasets
- Error conditions and edge cases

## Monitoring and Metrics

Track the following metrics:
- Memory creation rate
- Memory access patterns
- Storage usage
- Query performance
- Error rates

## Future Enhancements

1. **Memory Versioning**
   - Track changes to memories over time
   - Support for memory rollback

2. **Advanced Search**
   - Full-text search
   - Semantic search capabilities
   - Similarity-based retrieval

3. **Memory Compression**
   - Automatic summarization of similar memories
   - Pruning of redundant information

4. **Temporal Reasoning**
   - Time-based memory relevance
   - Memory decay mechanisms

## Troubleshooting

Common issues and solutions:

1. **Memory Not Found**
   - Verify the memory ID and user permissions
   - Check if the memory was deleted or archived

2. **Performance Issues**
   - Add appropriate database indexes
   - Optimize query patterns
   - Consider pagination for large result sets

3. **Data Consistency**
   - Implement transactions for multi-operation updates
   - Use database constraints for data integrity

## Related Documentation

- [Database Schema](./database-schema.md)
- [API Reference](./api-reference.md)
- [Agent Integration Guide](./agent-integration.md)
