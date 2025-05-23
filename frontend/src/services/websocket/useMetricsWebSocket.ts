import { useEffect, useRef } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { WebSocketService, CPUMetricsMessage } from './WebSocketService';
import { RootState } from '../../store/store';
import { updateMetrics as updateCPUMetrics, setError as setCPUError, setLoading as setCPULoading } from '../../store/slices/metrics/CPUSlice';

export const useMetricsWebSocket = () => {
  const dispatch = useAppDispatch();
  const { isAuthenticated } = useAppSelector((state: RootState) => state.auth);
  const wsRef = useRef<WebSocketService | null>(null);

  useEffect(() => {
    if (isAuthenticated && !wsRef.current) {
      wsRef.current = new WebSocketService(dispatch);

      wsRef.current.onMessage = (message: CPUMetricsMessage) => {
        dispatch(updateCPUMetrics({
          usage_percent: message.data.usage_percent,
          temperature: message.data.temperature,
          cores: message.data.cores.map((usage, index) => ({
            id: index,
            usage: usage
          })),
          physical_cores: message.data.physical_cores,
          logical_cores: message.data.logical_cores,
          frequency_mhz: message.data.frequency_mhz,
          top_processes: message.data.top_processes
        }));
      };

      wsRef.current.onError = (error: Error) => {
        console.error('WebSocket error:', error);
        dispatch(setCPUError(error.message));
      };

      dispatch(setCPULoading(true));
      wsRef.current.connect();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
        wsRef.current = null;
      }
    };
  }, [dispatch, isAuthenticated]);

  return {
    reconnect: () => {
      if (wsRef.current) {
        wsRef.current.connect();
      }
    },
    disconnect: () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
      }
    }
  };
};

export default useMetricsWebSocket;
