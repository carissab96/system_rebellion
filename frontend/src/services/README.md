# System Rebellion Frontend Services

This directory contains the API and WebSocket services for the System Rebellion frontend.

## API Service

The `api.ts` file provides an Axios-based HTTP client with the following features:

- Automatic JWT token handling
- Token refresh on 401 responses
- Consistent error handling
- TypeScript support

### Usage

```typescript
import apiService from '@/services/api';

// Make API requests
const response = await apiService.request({
  method: 'GET',
  url: '/some/endpoint',
});

// Or use convenience methods
const loginResponse = await apiService.login(email, password);
const metrics = await apiService.getSystemMetrics();
```

## WebSocket Service

The `websocket.ts` file provides a WebSocket client with the following features:

- Automatic reconnection
- Multiple subscribers support
- TypeScript support
- Error handling

### Usage

```typescript
import { useWebSocket, useSystemMetricsWebSocket } from '@/services/websocket';

// For custom WebSocket connections
const { send, close, connected } = useWebSocket('/ws/custom-endpoint', {
  onMessage: (data) => {
    console.log('Received:', data);
  },
  onOpen: () => console.log('Connected'),
  onClose: () => console.log('Disconnected'),
  onError: (error) => console.error('Error:', error),
});

// For system metrics
const { send: sendMetrics } = useSystemMetricsWebSocket({
  onMessage: (metrics) => {
    // Handle metrics updates
  },
});
```

## Configuration

Environment variables should be set in `.env.local` (not committed to version control):

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## Authentication

The API service automatically handles JWT tokens. To authenticate a user:

```typescript
try {
  const response = await apiService.login(email, password);
  // Tokens are automatically stored in localStorage
} catch (error) {
  // Handle error
}
```

## Error Handling

All API errors are instances of `AxiosError` with additional type information:

```typescript
try {
  await apiService.someRequest();
} catch (error) {
  if (axios.isAxiosError(error)) {
    console.error('API Error:', error.response?.data);
  }
}
```

## WebSocket Reconnection

The WebSocket service automatically handles reconnection with exponential backoff. You can configure the behavior in `config/constants.ts`.
