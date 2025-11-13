# System Rebellion - Test Suite

All tests for the System Rebellion backend.

## Directory Structure

- **`unit/`** - Unit tests for individual components
- **`integration/`** - Integration tests for multi-component flows
- **`distributed/`** - Tests for distributed agent consciousness system

## Running Tests

```bash
# All tests
pytest

# Specific directory
pytest tests/unit/
pytest tests/integration/
pytest tests/distributed/

# Specific test file
pytest tests/distributed/test_triage_broadcasting.py

# With coverage
pytest --cov=app tests/
```

## Test Organization

- Unit tests should be fast and isolated
- Integration tests can use database and external services
- Distributed tests verify agent coordination and Redis communication

## Current Status

**70/70 tests passing** ✅
- 45 unit tests
- 14 integration tests  
- 11 distributed tests
