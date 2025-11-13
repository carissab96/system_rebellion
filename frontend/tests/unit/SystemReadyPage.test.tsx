// src/__tests__/SystemReadyPage.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import { SystemReadyPage } from '../pages/SystemReadyPage';
import authReducer from '../store/slices/authSlice';
import agentsReducer from '../store/slices/agentsSlice';
import metricsReducer from '../store/slices/metricSlice';

// Mock constants to avoid import.meta issues in Jest
jest.mock('../config/constants', () => ({
  API_BASE_URL: 'http://localhost:8000',
  WS_BASE_URL: 'ws://localhost:8000',
  API_ENDPOINTS: {
    AUTH: { LOGIN: '/api/auth/token' },
    WEBSOCKET: { SYSTEM_METRICS: '/api/ws/system-metrics' }
  }
}));

// Mock the WebSocket hook
jest.mock('../hooks/useWebSocketConnection', () => ({
  useWebSocketConnection: jest.fn(() => ({
    connectionStatus: 'connected',
    isConnected: true,
    lastError: null,
    reconnect: jest.fn(),
    reconnectAttempts: 0,
    isConnecting: false,
    resilienceStats: {},
    getResilienceStats: jest.fn()
  }))
}));

// Mock navigation
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

describe('SystemReadyPage', () => {
  const createMockStore = (authState: any, agentsState: any) => {
    return configureStore({
      reducer: {
        auth: authReducer,
        agents: agentsReducer,
        metrics: metricsReducer
      },
      preloadedState: {
        auth: {
          isAuthenticated: true,
          user: { id: '1', email: 'test@test.com', is_onboarded: true },
          token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QHRlc3QuY29tIiwiZXhwIjoyMDAwMDAwMDAwfQ.test',
          isLoading: false,
          isInitializing: false,
          error: null,
          csrfToken: null,
          ...authState
        },
        agents: {
          sir_hawkington: { recent_memories: [], display_data: null },
          the_stick: { recent_memories: [], display_data: null },
          meth_snail: { recent_memories: [], display_data: null },
          hamsters: { recent_memories: [], display_data: null },
          quantum_shadow_people: { recent_memories: [], display_data: null },
          vic20_sage: { recent_memories: [], display_data: null },
          last_update: null,
          active_agents: [],
          ...agentsState
        },
        metrics: {
          timestamp: null,
          cpu_usage: 0,
          memory_usage: 0,
          disk_usage: 0,
          network_recv_rate: 0,
          network_sent_rate: 0,
          process_count: 0,
          cpu: null,
          memory: null,
          disk: null,
          network: null,
          system_info: null,
          connectionStatus: 'connected' as const,
          lastError: null,
          lastUpdate: null
        }
      }
    });
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
  });

  describe('JWT Authentication Check', () => {
    it('should show JWT as ready when token is valid', () => {
      const store = createMockStore({}, {});
      
      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      expect(screen.getByText('Authentication Token')).toBeInTheDocument();
      expect(screen.getByText(/JWT valid/)).toBeInTheDocument();
    });

    it('should redirect to login when JWT is invalid', async () => {
      const store = createMockStore({
        isAuthenticated: false,
        token: null
      }, {});

      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/', { replace: true });
      });
    });

    it('should redirect when token is expired', async () => {
      // Token with exp in the past
      const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QHRlc3QuY29tIiwiZXhwIjoxMDAwMDAwfQ.test';
      
      const store = createMockStore({
        token: expiredToken
      }, {});

      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/', { replace: true });
      });
    });
  });

  describe('Agent Readiness Check', () => {
    it('should show agents as NOT ready when none are active', () => {
      const store = createMockStore({}, {
        active_agents: []
      });

      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      expect(screen.getByText('Agent Roster')).toBeInTheDocument();
      expect(screen.getByText(/0\/6/)).toBeInTheDocument();
      expect(screen.getByText(/Waiting for Systems/)).toBeInTheDocument();
    });

    it('should show which agents are missing', () => {
      const store = createMockStore({}, {
        active_agents: ['sir_hawkington', 'the_stick']
      });

      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      expect(screen.getByText(/2\/6/)).toBeInTheDocument();
      expect(screen.getByText(/Missing agents:/)).toBeInTheDocument();
      expect(screen.getByText(/hamsters/)).toBeInTheDocument();
      expect(screen.getByText(/meth_snail/)).toBeInTheDocument();
    });

    it('should show agents as ready when all 6 are active', () => {
      const store = createMockStore({}, {
        active_agents: [
          'sir_hawkington',
          'the_stick',
          'hamsters',
          'meth_snail',
          'quantum_shadow_people',
          'vic20_sage'
        ]
      });

      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      expect(screen.getByText(/All six agents active/)).toBeInTheDocument();
      expect(screen.getByText(/6\/6/)).toBeInTheDocument();
    });
  });

  describe('System Connection Check', () => {
    it('should show system as connected', () => {
      const store = createMockStore({}, {});

      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      const systemChannelElements = screen.getAllByText('Unified System Channel');
      expect(systemChannelElements.length).toBeGreaterThan(0);
      expect(screen.getByText(/Live telemetry, agent insights, and events streaming/)).toBeInTheDocument();
    });
  });

  describe('All Systems Ready', () => {
    it('should enable proceed button when all systems ready', () => {
      const store = createMockStore({}, {
        active_agents: [
          'sir_hawkington',
          'the_stick',
          'hamsters',
          'meth_snail',
          'quantum_shadow_people',
          'vic20_sage'
        ]
      });

      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      const proceedButton = screen.getByText('Enter the Theater');
      expect(proceedButton).not.toBeDisabled();
    });

    it('should disable proceed button when agents not ready', () => {
      const store = createMockStore({}, {
        active_agents: ['sir_hawkington'] // Only 1 of 6
      });

      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      const proceedButton = screen.getByText('Waiting for Systems');
      expect(proceedButton).toBeDisabled();
    });

    it('should show countdown when all ready', async () => {
      const store = createMockStore({}, {
        active_agents: [
          'sir_hawkington',
          'the_stick',
          'hamsters',
          'meth_snail',
          'quantum_shadow_people',
          'vic20_sage'
        ]
      });

      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      await waitFor(() => {
        expect(screen.getByText(/Auto-redirecting in/)).toBeInTheDocument();
      });
    });
  });

  describe('Real Telemetry - No Fake Data', () => {
    it('should NOT show agents ready if active_agents is empty', () => {
      const store = createMockStore({}, {
        active_agents: [] // Empty array
      });

      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      // Should show pending, not ready
      const badges = screen.getAllByText('Pending');
      expect(badges.length).toBeGreaterThan(0);
      
      // Should NOT show "All six agents active"
      expect(screen.queryByText(/All six agents active/)).not.toBeInTheDocument();
    });

    it('should accurately report partial agent readiness', () => {
      const store = createMockStore({}, {
        active_agents: ['sir_hawkington', 'the_stick', 'hamsters'] // 3 of 6
      });

      render(
        <Provider store={store}>
          <BrowserRouter>
            <SystemReadyPage />
          </BrowserRouter>
        </Provider>
      );

      // Should show 3/6
      expect(screen.getByText(/3\/6/)).toBeInTheDocument();
      
      // Should list missing agents
      expect(screen.getByText(/meth_snail/)).toBeInTheDocument();
      expect(screen.getByText(/quantum_shadow_people/)).toBeInTheDocument();
      expect(screen.getByText(/vic20_sage/)).toBeInTheDocument();
    });
  });
});
