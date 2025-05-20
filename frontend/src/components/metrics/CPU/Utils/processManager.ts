// frontend/src/components/metrics/CPU/utils/processManager.ts

import { ProcessKillResult } from '../Tabs/types';
import api from '../../../../utils/api';

/**
 * Sends a request to kill a process by PID
 * @param pid Process ID to kill
 * @returns Promise with kill result
 */
export async function killProcess(pid: number): Promise<ProcessKillResult> {
  try {
    // Call your API endpoint
    const response = await api.post('/system/process/kill', { pid });
    
    // Return the result
    const data = await (response as Response).json();
    return {
      success: data.success,
      message: data.message || 'Process terminated successfully',
      pid
    };
  } catch (error) {
    console.error('Error killing process:', error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Failed to terminate process',
      pid
    };
  }
}

/**
 * Checks if the current user has permission to kill a process
 * This can be used to conditionally show/hide kill buttons
 */
export async function checkKillPermission(): Promise<boolean> {
  try {
    const response: any = await api.get('/system/permissions/check');
    return (response as any).data?.hasPermission;
  } catch (error) {
    console.error('Error checking kill permission:', error);
    return false;
  }
}