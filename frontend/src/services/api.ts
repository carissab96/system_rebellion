// api.ts
import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type AxiosError,
} from 'axios';
import { API_BASE_URL, WS_BASE_URL } from '../config/constants';

/* ===== Types ===== */

export interface User {
  id: string;
  email: string;
  first_name?: string | null;
  last_name?: string | null;
  is_onboarded?: boolean;
  is_active?: boolean;
  created_at?: string | null;
  updated_at?: string | null;
  last_login?: string | null;
  failed_login_attempts?: number;
  lockout_until?: string | null;
}

export type LoginResponse = {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  user: User;
};

type RefreshResponse = {
  access_token: string;
  refresh_token?: string;
};

export interface ApiError {
  message: string;
  status?: number;
  data?: any;
}

/* ===== Small helpers ===== */

function setTokens(access?: string, refresh?: string) {
  if (access) localStorage.setItem('access_token', access);
  if (refresh) localStorage.setItem('refresh_token', refresh);
}
function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

async function tryWithFallback<T>(
  primary: () => Promise<T>,
  fallback: () => Promise<T>
): Promise<T> {
  try {
    return await primary();
  } catch (e) {
    const err = e as AxiosError;
    const code = err.response?.status ?? 0;
    // Route moved or missing? Try the alternate.
    if ([404, 405, 308, 307].includes(code)) return await fallback();
    throw e;
  }
}

function normalizeWsBase(urlLike: string | undefined): string {
  if (!urlLike) return '';
  if (urlLike.startsWith('ws://') || urlLike.startsWith('wss://')) return urlLike;
  if (urlLike.startsWith('http://')) return urlLike.replace(/^http:\/\//, 'ws://');
  if (urlLike.startsWith('https://')) return urlLike.replace(/^https:\/\//, 'wss://');
  return urlLike; // raw host or path, you do you
}

/* ===== Axios instance ===== */

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false, // bearer tokens, not cookies
  // Do NOT default Content-Type; per-request only (login is form-encoded)
});

// Attach bearer from storage on every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers = config.headers ?? {};
      (config.headers as any).Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Refresh-on-401 (single retry)
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest: any = error.config;
    const status = error.response?.status;

    if (status === 401 && !originalRequest?._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');

        // Use a plain axios call to avoid interceptor recursion
        const res = await tryWithFallback<AxiosResponse<RefreshResponse>>(
          () =>
            axios.post(
              `${API_BASE_URL}/api/auth/refresh-token`,
              { refresh_token: refreshToken },
              { withCredentials: false }
            ),
          () =>
            axios.post(
              `${API_BASE_URL}/refresh-token`,
              { refresh_token: refreshToken },
              { withCredentials: false }
            )
        );

        const { access_token, refresh_token } = res.data;
        setTokens(access_token, refresh_token);

        originalRequest.headers = originalRequest.headers ?? {};
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch {
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

/* ===== API surface ===== */

export const apiService = {
  // -------- Auth --------
  async login(email: string, password: string): Promise<LoginResponse> {
    // FastAPI OAuth2PasswordRequestForm expects x-www-form-urlencoded with "username"
    const body = new URLSearchParams({
      username: email.trim(),
      password,
      grant_type: 'password',
      scope: '',
    });

    const res = await tryWithFallback<AxiosResponse<LoginResponse>>(
      () =>
        api.post('/api/auth/token', body, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        }),
      () =>
        api.post('/token', body, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
    );

    setTokens(res.data.access_token, res.data.refresh_token);
    return res.data;
  },

  async me() {
    // Prefer a true "me" endpoint; fall back to a CSRF ping so UI can at least tell the API is alive
    const res = await tryWithFallback(
      () => api.get('/api/auth/me'),
      () => api.get('/api/auth/csrf_token')
    );
    return (res as any).data;
  },

  async register(email: string, password: string, username: string) {
    const res = await tryWithFallback(
      () => api.post('/api/auth/register', { email, password, username }),
      () => api.post('/auth/register', { email, password, username })
    );
    return res.data;
  },

  // If you don’t actually have this route yet, fail loudly instead of ghosting.
  async updateProfile(_profileData: object) {
    throw new Error('updateProfile: backend route not implemented');
    // Example when you add it:
    // const res = await api.put('/api/me', _profileData);
    // return res.data;
  },

  // -------- Onboarding --------
  async saveOnboardingProgress(progressData: object) {
    const res = await api.post('/api/onboarding/onboarding-progress', progressData);
    return res.data;
  },

  async completeOnboarding(onboardingData: object) {
    const res = await api.post('/api/auth/complete-onboarding', onboardingData);
    return res.data;
  },

  async getOnboardingProgress() {
    const res = await api.get('/api/onboarding/onboarding-progress');
    return res.data;
  },

  async clearOnboardingProgress() {
    const res = await api.delete('/api/onboarding/onboarding-progress');
    return res.data;
  },

  // -------- System / Agents --------
  async detectSystem() {
    const res = await tryWithFallback(
      () => api.get('/api/system/detect'),
      () => api.get('/system/detect')
    );
    return res.data;
  },

  // Single-shot metrics for fallback when WS is down
  async getSystemMetricsOnce() {
    const res = await tryWithFallback(
      () => api.get('/api/metrics/system'),
      () => api.get('/metrics/system')
    );
    return res.data;
  },

  async getAgentStatus() {
    const res = await tryWithFallback(
      () => api.get('/api/ai-agents/status'),
      () => api.get('/ai-agents/status')
    );
    return res.data;
  },

  // -------- WebSocket --------
  getWebSocketUrl(): string {
    const token = localStorage.getItem('access_token') ?? '';
    const base = normalizeWsBase(WS_BASE_URL) || normalizeWsBase(API_BASE_URL);
    // If someone gives you a bare host, be polite.
    const url =
      base.startsWith('ws://') || base.startsWith('wss://')
        ? `${base}`
        : `ws://${base.replace(/^\/+/, '')}`;
    return `${url.replace(/\/+$/, '')}/ws/system-metrics?token=${encodeURIComponent(token)}`;
  },

  // -------- Generic request escape hatch --------
  async request<T = any>(config: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return api.request<T>(config);
  },

  // Optional convenience
  logout() {
    clearTokens();
  },
};

export { api }; // raw instance if you need it
export default apiService;
