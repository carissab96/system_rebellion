import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Provider as ReduxProvider } from 'react-redux';
import { store } from './store/store';
import { ToastProvider } from './components/common/Toast';
import './App.css';
import { useMetricsWebSocket } from './services/websocket/useMetricsWebSocket'; // FIXED PATH AND NAME

// Components
import Login, { LoginProps } from './components/Auth/login/Login';
import DashboardNew from './components/dashboard/Dashboard/DashboardNew';
import Layout from './components/common/Layout';
import OptimizationProfiles from './components/optimization/OptimizationProfiles';
import SystemAlerts from './components/alerts/SystemAlerts';
import SystemConfiguration from './components/configuration/SystemConfiguration';
import SystemMetrics from './components/metrics/SystemMetrics';
import AutoTunerComponent from './components/auto_tuners/auto_tuner';
import OnboardingPage from './pages/OnboardingPage';
import LandingPage from './pages/LandingPage';
import ProtectedRoute from './utils/ProtectedRoute';
import { DesignSystemShowcase } from './design-system/docs';
import PersistenceWrapper from './components/Auth/PersistenceWrapper';
import React from 'react';

// Error Boundary State
type ErrorBoundaryState = {
  hasError: boolean;
  error: Error | null;
};

// Error Boundary Component
class ErrorBoundary extends React.Component<{children: React.ReactNode}, ErrorBoundaryState> {
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

// Create a component that uses the WebSocket hook
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
            <Route path="/auto-tuner" element={<AutoTunerComponent />} />
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