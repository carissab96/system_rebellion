// import { AppDispatch } from '../../../store/store';
// import { updateMetrics, setError, setLoading } from '../../../store/slices/metrics/CPUSlice';
// import { CPUMetric } from '../../../store/slices/metrics/CPUSlice';

// export const handleCPUMetrics = (message: WebSocketMessage, dispatch: AppDispatch) => {
//   try {
//     const { type, data } = message;
    
//     if (type === 'cpu') {
//       // Validate CPU data
//       if (!data || typeof data.usage !== 'number' || !Array.isArray(data.cores)) {
//         throw new Error('Invalid CPU metrics data format');
//       }
      
//       // Transform data if needed
//       const cpuMetrics: CPUMetric = {
//         usage: data.usage,
//         cores: data.cores.map((core: any, index: number) => ({
//           id: index,
//           usage: typeof core === 'number' ? core : core.usage
//         })),
//         physical_cores: data.physical_cores || data.cores.length,
//         logical_cores: data.logical_cores || data.cores.length,
//         temperature: data.temperature,
//         frequency: data.frequency,
//         top_processes: Array.isArray(data.top_processes) ? data.top_processes.map((proc: any) => ({
//           pid: proc.pid,
//           name: proc.name,
//           cpu_percent: proc.cpu_percent,
//           memory_percent: proc.memory_percent
//         })) : []
//       };
      
//       // Update the CPU slice
//       dispatch(updateMetrics(cpuMetrics));
//     }
//   } catch (error) {
//     console.error('Error handling CPU metrics:', error);
//     dispatch(setError(error instanceof Error ? error.message : 'Unknown error processing CPU metrics'));
//   }
// };

// export const initializeCPUMetrics = (dispatch: AppDispatch) => {
//   dispatch(setLoading(true));
// };
