import { configureStore } from '@reduxjs/toolkit';
import cpuReducer, {
  updateMetrics,
  setError,
  setLoading,
  selectCPUMetrics,
  selectCPULoading,
  selectCPUError
} from '../../../store/slices/metrics/CPUSlice';

describe('CPU Slice', () => {
  const initialState = {
    metrics: null,
    loading: false,
    error: null
  };

  const sampleMetrics = {
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
      { id: 1, usage_percent: 35 }
    ],
    process_count: 150,
    thread_count: 200
  };

  let store: any;

  beforeEach(() => {
    store = configureStore({
      reducer: {
        cpu: cpuReducer
      }
    });
  });

  test('should handle initial state', () => {
    expect(store.getState().cpu).toEqual(initialState);
  });

  test('should handle updateMetrics', () => {
    store.dispatch(updateMetrics(sampleMetrics));
    expect(selectCPUMetrics(store.getState())).toEqual(sampleMetrics);
  });

  test('should handle setLoading', () => {
    store.dispatch(setLoading(true));
    expect(selectCPULoading(store.getState())).toBe(true);
  });

  test('should handle setError', () => {
    const errorMessage = 'Test error message';
    store.dispatch(setError(errorMessage));
    expect(selectCPUError(store.getState())).toBe(errorMessage);
  });

  test('should clear error when updating metrics', () => {
    store.dispatch(setError('Test error'));
    store.dispatch(updateMetrics(sampleMetrics));
    expect(selectCPUError(store.getState())).toBe(null);
  });

  test('should clear loading when updating metrics', () => {
    store.dispatch(setLoading(true));
    store.dispatch(updateMetrics(sampleMetrics));
    expect(selectCPULoading(store.getState())).toBe(false);
  });

  test('should clear metrics when setting error', () => {
    store.dispatch(updateMetrics(sampleMetrics));
    store.dispatch(setError('Test error'));
    expect(selectCPUMetrics(store.getState())).toBe(null);
  });

  test('selectors should handle missing state', () => {
    const emptyState = { someOtherSlice: {} };
    expect(selectCPUMetrics(emptyState)).toBe(null);
    expect(selectCPULoading(emptyState)).toBe(false);
    expect(selectCPUError(emptyState)).toBe(null);
  });
});
