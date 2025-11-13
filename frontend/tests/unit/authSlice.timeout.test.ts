// src/__tests__/authSlice.timeout.test.ts
// Testing the timeout fixes for hung login issue
import { configureStore } from '@reduxjs/toolkit';
import type { AppDispatch } from '../store/store';
import authReducer, { 
  fetchCsrfToken, 
  loginUser, 
  registerUser 
} from '../store/slices/authSlice';

// Mock the constants module
jest.mock('../config/constants', () => ({
  API_BASE_URL: 'http://localhost:8000',
  WS_BASE_URL: 'ws://localhost:8000',
}));

// Mock fetch globally
global.fetch = jest.fn();

describe('🔥 Auth Timeout & Error Handling Tests', () => {
  let store: ReturnType<typeof configureStore>;
  let dispatch: AppDispatch;

  beforeEach(() => {
    store = configureStore({
      reducer: {
        auth: authReducer,
      },
    });
    dispatch = store.dispatch as AppDispatch;
    jest.clearAllMocks();
  });

  describe('🔐 CSRF Token Fetch', () => {
    it('✅ should successfully fetch CSRF token with timeout protection', async () => {
      const mockCsrfToken = 'test-csrf-token-123';
      
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ csrf_token: mockCsrfToken }),
      });

      const result = await dispatch(fetchCsrfToken()).unwrap();

      expect(result).toBe(mockCsrfToken);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/csrf_token',
        expect.objectContaining({
          signal: expect.any(AbortSignal),
        })
      );
    });

    it('⏱️ should handle timeout gracefully', async () => {
      // Mock a hanging request that never resolves
      (global.fetch as jest.Mock).mockImplementationOnce(
        () => new Promise(() => {
          // Never resolve - simulates hanging request
        })
      );

      await expect(
        dispatch(fetchCsrfToken()).unwrap()
      ).rejects.toThrow();
    }, 10000); // 10 second Jest timeout

    it('❌ should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      await expect(
        dispatch(fetchCsrfToken()).unwrap()
      ).rejects.toThrow('Network error');
    });

    it('🚫 should handle 404 response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Not found' }),
      });

      await expect(
        dispatch(fetchCsrfToken()).unwrap()
      ).rejects.toThrow();
    });
  });

  describe('🔑 Login User', () => {
    const mockLoginData = {
      email: 'test@example.com',
      password: 'password123',
      csrfToken: 'test-csrf-token',
    };

    it('✅ should successfully login with timeout protection', async () => {
      const mockResponse = {
        access_token: 'test-token-123',
        user: {
          id: '1',
          email: 'test@example.com',
          username: 'testuser',
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await dispatch(loginUser(mockLoginData)).unwrap();

      expect(result.token).toBe('test-token-123');
      expect(result.user.email).toBe('test@example.com');
      
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/token',
        expect.objectContaining({
          method: 'POST',
          signal: expect.any(AbortSignal),
          headers: expect.objectContaining({
            'X-CSRFToken': 'test-csrf-token',
          }),
        })
      );
    });

    it('⏱️ should handle login timeout', async () => {
      (global.fetch as jest.Mock).mockImplementationOnce(
        () => new Promise(() => {
          // Never resolve
        })
      );

      await expect(
        dispatch(loginUser(mockLoginData)).unwrap()
      ).rejects.toThrow();
    });

    it('🔒 should handle invalid credentials', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid credentials' }),
      });

      await expect(
        dispatch(loginUser(mockLoginData)).unwrap()
      ).rejects.toThrow('Invalid credentials');
    });

    it('💥 should handle server errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal server error' }),
      });

      await expect(
        dispatch(loginUser(mockLoginData)).unwrap()
      ).rejects.toThrow('Internal server error');
    });
  });

  describe('📝 Register User', () => {
    const mockRegisterData = {
      email: 'newuser@example.com',
      username: 'newuser',
      password: 'password123',
      first_name: 'New',
      last_name: 'User',
      company_name: 'Test Co',
      job_title: 'Developer',
      csrfToken: 'test-csrf-token',
    };

    it('✅ should successfully register with timeout protection', async () => {
      const mockResponse = {
        access_token: 'new-token-123',
        user: {
          id: '2',
          email: 'newuser@example.com',
          username: 'newuser',
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await dispatch(registerUser(mockRegisterData)).unwrap();

      expect(result.token).toBe('new-token-123');
      expect(result.user.email).toBe('newuser@example.com');
      
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/register',
        expect.objectContaining({
          method: 'POST',
          signal: expect.any(AbortSignal),
        })
      );
    });

    it('⏱️ should handle registration timeout', async () => {
      (global.fetch as jest.Mock).mockImplementationOnce(
        () => new Promise(() => {
          // Never resolve
        })
      );

      await expect(
        dispatch(registerUser(mockRegisterData)).unwrap()
      ).rejects.toThrow();
    });

    it('⚠️ should handle duplicate email error', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Email already registered' }),
      });

      await expect(
        dispatch(registerUser(mockRegisterData)).unwrap()
      ).rejects.toThrow('Email already registered');
    });
  });

  describe('🔧 URL Configuration', () => {
    it('should use full API_BASE_URL for all requests', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ csrf_token: 'test' }),
      });

      await dispatch(fetchCsrfToken()).unwrap();

      const fetchCall = (global.fetch as jest.Mock).mock.calls[0];
      expect(fetchCall[0]).toBe('http://localhost:8000/api/auth/csrf_token');
    });

    it('should include AbortSignal in all requests', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ csrf_token: 'test' }),
      });

      await dispatch(fetchCsrfToken()).unwrap();

      const fetchCall = (global.fetch as jest.Mock).mock.calls[0];
      expect(fetchCall[1]).toHaveProperty('signal');
      expect(fetchCall[1].signal).toBeInstanceOf(AbortSignal);
    });
  });

  describe('📊 State Management', () => {
    it('should set loading state during login', () => {
      store.dispatch({ type: 'auth/login/pending' });

      const state = (store.getState() as any).auth;
      expect(state.isLoading).toBe(true);
      expect(state.error).toBeNull();
    });

    it('should clear error on new login attempt', () => {
      // Set an error first
      store.dispatch({
        type: 'auth/login/rejected',
        error: { message: 'Previous error' },
      });

      expect((store.getState() as any).auth.error).toBe('Previous error');

      // Start new login
      store.dispatch({ type: 'auth/login/pending' });

      expect((store.getState() as any).auth.error).toBeNull();
    });

    it('should store token and user on successful login', async () => {
      const mockResponse = {
        access_token: 'test-token',
        user: { id: '1', email: 'test@example.com', username: 'test' },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await dispatch(
        loginUser({
          email: 'test@example.com',
          password: 'password',
          csrfToken: 'csrf',
        })
      ).unwrap();

      const state = (store.getState() as any).auth;
      expect(state.token).toBe('test-token');
      expect(state.user?.email).toBe('test@example.com');
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });
  });
});
