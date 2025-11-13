# System Rebellion - Frontend Test Suite

All tests for the System Rebellion frontend.

## Directory Structure

- **`unit/`** - Unit tests for components and utilities
- **`integration/`** - Integration tests for user flows

## Running Tests

```bash
# All tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage

# Specific test
npm test -- LiveAgentTheater
```

## Test Organization

- Unit tests should be fast and isolated
- Integration tests can use mock WebSocket and API
- Use React Testing Library for component tests

## Writing Tests

```typescript
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '../store/store';

test('component renders correctly', () => {
  render(
    <Provider store={store}>
      <YourComponent />
    </Provider>
  );
  
  expect(screen.getByText('Expected Text')).toBeInTheDocument();
});
```
