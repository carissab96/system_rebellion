import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import CPUMetric from '../../../../components/metrics/CPU/CPUMetric';

const mockStore = configureStore([]);

describe('CPUMetric Component', () => {
  let store: any;

  beforeEach(() => {
    store = mockStore({
      cpu: {
        metrics: {
          overall_usage: 45.5,
          physical_cores: 4,
          logical_cores: 8,
          model_name: 'Intel(R) Core(TM) i7-1165G7',
          frequency_mhz: 2800,
          temperature: {
            current: 65,
            min: 0,
            max: 100,
            critical: 90,
            throttle_threshold: 80,
            unit: 'C'
          },
          top_processes: [
            {
              pid: 1234,
              name: 'chrome',
              cpu_percent: 15.5,
              memory_percent: 8.2,
              user: 'user'
            }
          ],
          cores: [
            { id: 0, usage_percent: 45 },
            { id: 1, usage_percent: 35 },
            { id: 2, usage_percent: 55 },
            { id: 3, usage_percent: 25 }
          ],
          process_count: 150,
          thread_count: 200
        },
        loading: false,
        error: null
      }
    });
  });

  test('renders without crashing', () => {
    render(
      <Provider store={store}>
        <CPUMetric />
      </Provider>
    );
    expect(screen.getByText('CPU Activity')).toBeInTheDocument();
  });

  test('shows loading state', () => {
    store = mockStore({
      cpu: {
        metrics: null,
        loading: true,
        error: null
      }
    });

    render(
      <Provider store={store}>
        <CPUMetric />
      </Provider>
    );
    expect(screen.getByText('Loading CPU metrics...')).toBeInTheDocument();
  });

  test('shows error state', () => {
    store = mockStore({
      cpu: {
        metrics: null,
        loading: false,
        error: 'Failed to load CPU metrics'
      }
    });

    render(
      <Provider store={store}>
        <CPUMetric />
      </Provider>
    );
    expect(screen.getByText('Failed to load CPU metrics')).toBeInTheDocument();
  });

  test('switches between tabs', () => {
    render(
      <Provider store={store}>
        <CPUMetric />
      </Provider>
    );

    // Check Overview tab is visible by default
    expect(screen.getByText('CPU Usage')).toBeInTheDocument();

    // Switch to Processes tab
    fireEvent.click(screen.getByText('Processes'));
    expect(screen.getByText('chrome')).toBeInTheDocument();

    // Switch to Cores tab
    fireEvent.click(screen.getByText('Cores'));
    expect(screen.getByText('Core 0')).toBeInTheDocument();

    // Switch to Thermal tab
    fireEvent.click(screen.getByText('Thermal'));
    expect(screen.getByText('65°C')).toBeInTheDocument();
  });

  test('shows temperature alerts', () => {
    store = mockStore({
      cpu: {
        metrics: {
          ...store.getState().cpu.metrics,
          temperature: {
            current: 85,
            min: 0,
            max: 100,
            critical: 90,
            throttle_threshold: 80,
            unit: 'C'
          }
        },
        loading: false,
        error: null
      }
    });

    render(
      <Provider store={store}>
        <CPUMetric />
      </Provider>
    );

    expect(screen.getByText(/WARNING: CPU temperature has reached throttling threshold/i)).toBeInTheDocument();
  });

  test('respects compact mode', () => {
    render(
      <Provider store={store}>
        <CPUMetric compact={true} />
      </Provider>
    );

    const container = screen.getByTestId('cpu-metric-container');
    expect(container).toHaveClass('compact');
  });
});
