// src/__tests__/useLoginForm.test.tsx
import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../store/slices/authSlice';
import { useLoginForm } from '../hooks/useLoginForm';

// Mock the constants module before other imports
jest.mock('../config/constants', () => ({
  API_BASE_URL: 'http://localhost:8000',
  WS_BASE_URL: 'ws://localhost:8000',
}));

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
}));

// Mock fetch globally
global.fetch = jest.fn();

// Create a test store
const createTestStore = () => {
  return configureStore({
    reducer: {
      auth: authReducer,
    },
    preloadedState: {
      auth: {
        user: null,
        token: null,
        isLoading: false,
        error: null,
        csrfToken: 'test-csrf-token', // Pre-populate CSRF token
      },
    },
  });
};

describe('useLoginForm', () => {
  let store: ReturnType<typeof createTestStore>;

  beforeEach(() => {
    store = createTestStore();
    jest.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <Provider store={store}>{children}</Provider>
  );

  it('initializes with empty form data', () => {
    const { result } = renderHook(() => useLoginForm(true, jest.fn()), { wrapper });

    expect(result.current.formData.email).toBe('');
    expect(result.current.formData.password).toBe('');
    expect(result.current.formData.rememberMe).toBe(false);
  });

  it('validates form fields correctly', () => {
    const { result } = renderHook(() => useLoginForm(true, jest.fn()), { wrapper });

    // Test empty email - validation only happens on submit
    act(() => {
      result.current.handleInputChange('email', '');
      result.current.handleInputChange('password', 'password123');
    });

    // Trigger validation by attempting submit (but it will fail due to empty email)
    act(() => {
      try {
        result.current.handleSubmit({ preventDefault: jest.fn() } as any);
      } catch (e) {
        // Expected to fail validation
      }
    });

    expect(result.current.localErrors.email).toBe('Email is required');

    // Test invalid email
    act(() => {
      result.current.handleInputChange('email', 'invalid-email');
    });

    // Clear previous error and trigger validation again
    act(() => {
      try {
        result.current.handleSubmit({ preventDefault: jest.fn() } as any);
      } catch (e) {
        // Expected to fail validation
      }
    });

    expect(result.current.localErrors.email).toBe('Please enter a valid email');

    // Test empty password
    act(() => {
      result.current.handleInputChange('email', 'test@example.com');
      result.current.handleInputChange('password', '');
    });

    // Trigger validation again
    act(() => {
      try {
        result.current.handleSubmit({ preventDefault: jest.fn() } as any);
      } catch (e) {
        // Expected to fail validation
      }
    });

    expect(result.current.localErrors.password).toBe('Password is required');
  });

  it('clears field errors when user types', () => {
    const { result } = renderHook(() => useLoginForm(true, jest.fn()), { wrapper });

    // First set some errors by attempting validation
    act(() => {
      result.current.handleInputChange('email', '');
      result.current.handleInputChange('password', '');
    });

    // Trigger validation
    act(() => {
      try {
        result.current.handleSubmit({ preventDefault: jest.fn() } as any);
      } catch (e) {
        // Expected to fail validation
      }
    });

    expect(result.current.localErrors.email).toBe('Email is required');
    expect(result.current.localErrors.password).toBe('Password is required');

    // Now type in email field - should clear email error
    act(() => {
      result.current.handleInputChange('email', 't');
    });

    expect(result.current.localErrors.email).toBeUndefined();
    expect(result.current.localErrors.password).toBe('Password is required'); // Other errors remain
  });

  it('prevents form submission when loading', async () => {
    const { result } = renderHook(() => useLoginForm(true, jest.fn()), { wrapper });

    // Mock the store to be in loading state
    store.dispatch({ type: 'auth/loginUser/pending' });

    act(() => {
      result.current.handleInputChange('email', 'test@example.com');
      result.current.handleInputChange('password', 'password123');
    });

    let submitPrevented = false;
    await act(async () => {
      try {
        await result.current.handleSubmit({ preventDefault: () => { submitPrevented = true; } } as any);
      } catch (e) {
        // Expected to not submit
      }
    });

    expect(submitPrevented).toBe(true);
  });

  it('prevents form submission with validation errors', async () => {
    const { result } = renderHook(() => useLoginForm(true, jest.fn()), { wrapper });

    // Fill form with invalid data
    act(() => {
      result.current.handleInputChange('email', 'invalid-email');
      result.current.handleInputChange('password', '');
    });

    let submitPrevented = false;
    await act(async () => {
      try {
        await result.current.handleSubmit({ preventDefault: () => { submitPrevented = true; } } as any);
      } catch (e) {
        // Expected to not submit
      }
    });

    expect(submitPrevented).toBe(true);
  });

  it('updates form data correctly', () => {
    const { result } = renderHook(() => useLoginForm(true, jest.fn()), { wrapper });

    act(() => {
      result.current.handleInputChange('email', 'test@example.com');
      result.current.handleInputChange('password', 'password123');
      result.current.handleInputChange('rememberMe', true);
    });

    expect(result.current.formData.email).toBe('test@example.com');
    expect(result.current.formData.password).toBe('password123');
    expect(result.current.formData.rememberMe).toBe(true);
  });
});
