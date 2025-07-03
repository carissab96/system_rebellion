import './app.css';

import React from 'react';

import { Provider as ReduxProvider } from 'react-redux';
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
} from 'react-router-dom';

import { AutoTuner } from './components/auto-tuners/AutoTuner';
import SystemAlerts from './components/alerts/SystemAlerts';
import Login, { LoginProps } from './components/auth/login/Login';
import PersistenceWrapper from './components/auth/PersistenceWrapper';
import Layout from './components/common/Layout';
import { ToastProvider } from './components/common/Toast';
import SystemConfiguration
  from './components/configuration/SystemConfiguration';
import DashboardNew from './components/dashboard/dashboard/DashboardNew';
import SystemMetrics from './components/metrics/SystemMetrics';
import OptimizationProfiles
  from './components/optimization/OptimizationProfiles';
import { DesignSystemShowcase } from './design-system/docs';
import LandingPage from './pages/LandingPage/LandingPage';
import OnboardingPage from './pages/OnboardingPage';
import {
  useMetricsWebSocket,
} from './services/websocket/useMetricsWebSocket'; // FIXED PATH AND NAME
import { store } from './store/store';
import ProtectedRoute from './utils/ProtectedRoute';

type ErrorBoundaryState = {
  hasError: boolean;
  error: Error | null;
};

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, ErrorBoundaryState> {
  state: ErrorBoundaryState = {
    hasError: false,
    error: null
  };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error("Error Boundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message || 'An unknown error occurred'}</p>
          <button onClick={() => window.location.reload()}>Reload Application</button>
        </div>
      );
    }
    return this.props.children;
  }
}

const AppContent: React.FC = () => {
  // USE THE HOOK PROPERLY HERE!
  useMetricsWebSocket();

  // Default login props
  const loginProps: LoginProps = {
    isOpen: true,
    onClose: () => console.log('Login closed')
  };

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login {...loginProps} />} />

          <Route element={
            <ProtectedRoute>
              <Outlet />
            </ProtectedRoute>
          }>
            <Route path="/dashboard" element={<DashboardNew />} />
            <Route path="/optimization" element={<OptimizationProfiles />} />
            <Route path="/alerts" element={<SystemAlerts />} />
            <Route path="/configuration" element={<SystemConfiguration />} />
            <Route path="/metrics" element={<SystemMetrics />} />
            <Route path="/auto-tuner" element={<AutoTuner />} />
            <Route path="/onboarding" element={<OnboardingPage />} />
            <Route path="/design-system" element={<DesignSystemShowcase />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};

const App: React.FC = () => {
  return (
    <ReduxProvider store={store}>
      <ToastProvider>
        <ErrorBoundary>
          <PersistenceWrapper>
            <AppContent />
          </PersistenceWrapper>
        </ErrorBoundary>
      </ToastProvider>
    </ReduxProvider>
  );
};

export default App;