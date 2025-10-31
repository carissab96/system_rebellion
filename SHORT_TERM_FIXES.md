# Short-Term Stabilization Fixes

## Overview
Immediate fixes to prevent system freezes and authentication loops between CSRF auth and login auth.

## Goals
- Eliminate WebSocket connection freezes after login
- Prevent infinite retry loops
- Ensure instant agent manager access
- Improve CSRF and auth initialization reliability

## Priority Order
1. WebSocket Token Race Condition (Critical)
2. Prevent WebSocket Retry Loops (Critical)
3. Instant Agent Manager Access (High)
4. Optimize CSRF Fetching (Medium)
5. Auth Initialization Resilience (Medium)

---

## Fix 1: WebSocket Token Race Condition

### Problem
WebSocket attempts connection before login token is fully stored in localStorage, causing authentication failures and reconnection loops.

### Implementation
**File**: `frontend/src/hooks/useLoginForm.ts`

**Current Code** (lines 95-190):
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  // ... validation logic

  try {
    const response = await fetch('/api/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': currentCsrfToken,
        'Accept': 'application/json'
      },
      body: new URLSearchParams({
        username: formData.email.trim(),
        password: formData.password.trim(),
        grant_type: 'password'
      }),
      credentials: 'include'
    });

    if (!response.ok) {
      // ... error handling
    }

    const data = await response.json();

    // Store tokens and user data
    dispatch(authSlice.loginSuccess({
      user: data.user,
      token: data.access_token
    }));

    // Store tokens securely
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token);
    }

    // Close modal first
    onClose();

    // Navigate based on onboarding status
    if (data.user.is_onboarded) {
      navigate('/system-ready');
    } else {
      navigate('/onboarding');
    }
  } catch (error) {
    // ... error handling
  }
};
```

**Fixed Code**:
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  // ... validation logic

  try {
    const response = await fetch('/api/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': currentCsrfToken,
        'Accept': 'application/json'
      },
      body: new URLSearchParams({
        username: formData.email.trim(),
        password: formData.password.trim(),
        grant_type: 'password'
      }),
      credentials: 'include'
    });

    if (!response.ok) {
      // ... error handling
    }

    const data = await response.json();

    // CRITICAL: Store token SYNCHRONOUSLY before any async operations
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user_data', JSON.stringify(data.user));

    dispatch(authSlice.loginSuccess({
      user: data.user,
      token: data.access_token
    }));

    // Store refresh token
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token);
    }

    // Close modal first
    onClose();

    // Navigate based on onboarding status
    if (data.user.is_onboarded) {
      navigate('/system-ready');
    } else {
      navigate('/onboarding');
    }
  } catch (error) {
    // ... error handling
  }
};
```

### Testing
1. Login with valid credentials
2. Verify WebSocket connects immediately without retry loops
3. Check browser developer tools for any authentication errors
4. Confirm token is stored in localStorage before navigation

### Rollback
- Revert the synchronous localStorage calls back to their original async position

---

## Fix 2: Prevent WebSocket Retry Loops

### Problem
Failed WebSocket connections trigger infinite reconnection attempts, consuming resources.

### Implementation
**File**: `frontend/src/hooks/useWebSocketConnection.ts`

**Add to imports**:
```typescript
const [retryCount, setRetryCount] = useState(0);
const MAX_RETRIES = 5;
```

**Modify connect function**:
```typescript
const connect = useCallback(async () => {
  if (retryCount >= MAX_RETRIES) {
    console.error('Max WebSocket retries exceeded, giving up');
    dispatch(setError('Connection failed after multiple attempts'));
    return;
  }

  try {
    // ... existing connection logic
    setRetryCount(0); // Reset on success
  } catch (error) {
    setRetryCount(prev => prev + 1);
    // ... existing error handling
  }
}, [retryCount, dispatch]);
```

**Update reconnect function**:
```typescript
const reconnect = useCallback(() => {
  console.log('Manual reconnect requested');
  setLocalState(prev => ({
    ...prev,
    isConnecting: false,
    reconnectAttempts: 0,
    lastError: null,
    circuitBreaker: {
      state: 'CLOSED',
      failures: 0,
      waitTime: 0
    }
  }));
  setRetryCount(0); // Reset retry count on manual reconnect
  connect();
}, [connect]);
```

### Testing
1. Force WebSocket failures (disconnect network briefly)
2. Verify connection stops retrying after 5 attempts
3. Confirm manual reconnect resets the counter
4. Check error messages are user-friendly

### Rollback
- Remove retry count state and MAX_RETRIES constant
- Revert connect function to original implementation

---

## Fix 3: Instant Agent Manager Access

### Problem
Agent manager initialization may not be truly instant, causing WebSocket delays.

### Implementation
**File**: `backend/app/ai_agents/agent_manager.py`

**Current get_agent_manager function**:
```python
async def get_agent_manager(db_getter=None):
    # ... existing singleton logic
```

**Enhanced version**:
```python
_agent_manager_instance = None

async def get_agent_manager(db_getter=None):
    global _agent_manager_instance

    if _agent_manager_instance is None:
        if db_getter:
            _agent_manager_instance = await AgentManager.create(db_getter)
        else:
            raise RuntimeError("Agent manager not initialized and no db_getter provided")

    return _agent_manager_instance
```

**File**: `backend/main.py` (lifespan function)

**Ensure initialization is complete before yielding**:
```python
agent_start = time.time()
agent_manager = await get_agent_manager(db_getter=db_session_factory)
agent_elapsed = time.time() - agent_start
# Log completion and verify agents are ready
```

### Testing
1. Check startup logs show agent manager initialization
2. Verify WebSocket connections are instant (<100ms)
3. Monitor for any async delays in agent manager access

### Rollback
- Revert to original get_agent_manager implementation
- Remove global _agent_manager_instance

---

## Fix 4: Optimize CSRF Token Fetching

### Problem
Sequential CSRF endpoint tries can cause delays if primary endpoint is slow.

### Implementation
**File**: `frontend/Utils/csrf.ts`

**Enhanced getCsrfToken function**:
```typescript
export const getCsrfToken = async (forceRefresh = false): Promise<string | null> => {
  if (csrfTokenCache && !forceRefresh) {
    console.log("🦔 Sir Hawkington: Using cached CSRF token");
    return csrfTokenCache;
  }

  // Try primary endpoint first with timeout
  try {
    const response = await Promise.race([
      csrfAxios.get('/api/auth/csrf_token', {
        headers: { 'Cache-Control': 'no-cache' },
        params: { _t: Date.now() }
      }),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('CSRF fetch timeout')), 3000)
      )
    ]);

    if (response.data?.csrf_token) {
      csrfTokenCache = response.data.csrf_token;
      console.log(`🎉 CSRF token obtained from primary endpoint`);
      return csrfTokenCache;
    }
  } catch (error) {
    console.warn('Primary CSRF endpoint failed, trying alternatives...');
  }

  // Fallback to existing logic for alternative endpoints...
};
```

### Testing
1. Clear CSRF cache and verify fast primary endpoint usage
2. Simulate slow primary endpoint and confirm fallback works
3. Check timeout prevents hanging on unresponsive endpoints

### Rollback
- Revert to original sequential endpoint trying logic
- Remove Promise.race timeout wrapper

---

## Fix 5: Auth Initialization Resilience

### Problem
Auth initialization can hang during app startup if backend is slow.

### Implementation
**File**: `frontend/src/store/slices/authSlice.ts`

**Enhanced initializeAuth thunk**:
```typescript
export const initializeAuth = createAsyncThunk(
  'auth/initializeAuth',
  async (_, { rejectWithValue }) => {
    const savedToken = localStorage.getItem('access_token');

    if (!savedToken) {
      return { authenticated: false };
    }

    try {
      // Add timeout to prevent hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${savedToken}`,
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
        return { authenticated: false };
      }

      const userData = await response.json();
      return {
        authenticated: true,
        token: savedToken,
        user: userData.user
      };
    } catch (error) {
      console.warn('Auth initialization failed:', error);
      // Don't clear tokens on network errors - might be temporary
      return rejectWithValue('Auth initialization failed');
    }
  }
);
```

### Testing
1. Test with valid saved tokens
2. Test with invalid/expired tokens
3. Simulate network timeouts and verify graceful failure
4. Confirm app doesn't hang during startup

### Rollback
- Remove AbortController and timeout logic
- Revert to original fetch without signal/timeout

---

## Implementation Checklist

### Pre-Implementation
- [ ] Backup all modified files
- [ ] Have rollback plan ready for each fix
- [ ] Prepare test scenarios

### Post-Implementation
- [ ] Test login flow end-to-end
- [ ] Verify WebSocket connections are instant
- [ ] Monitor for any new authentication issues
- [ ] Check browser console for errors

### Success Metrics
- [ ] No more system freezes during login
- [ ] WebSocket connections < 500ms after login
- [ ] No infinite retry loops
- [ ] CSRF token fetching < 1 second
- [ ] App startup doesn't hang on auth initialization

## Emergency Rollback
If any fix causes issues:
1. Revert all changes to original state
2. Clear browser cache and localStorage
3. Restart backend and frontend services
4. Test basic login functionality
