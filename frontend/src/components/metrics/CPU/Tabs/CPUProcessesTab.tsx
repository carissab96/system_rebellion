// frontend/src/components/metrics/CPU/tabs/CPUProcessesTab.tsx

import React, { useState } from 'react';
import { CPUProcess } from '../types';
import { killProcess } from '../Utils/processManager';
import './CPUTabs.css';

interface CPUProcessesTabProps {
  processes: CPUProcess[];
  compact?: boolean;
}

const CPUProcessesTab: React.FC<CPUProcessesTabProps> = ({ processes, compact = false }) => {
  const [isKilling, setIsKilling] = useState<{[key: number]: boolean}>({});
  const [killResult, setKillResult] = useState<{[key: number]: {success: boolean; message: string}}>({});
  
  // Handle kill process
  const handleKillProcess = async (pid: number) => {
    if (isKilling[pid]) return; // Prevent multiple clicks
    
    setIsKilling(prev => ({ ...prev, [pid]: true }));
    
    try {
      const result = await killProcess(pid);
      
      setKillResult(prev => ({ 
        ...prev, 
        [pid]: { 
          success: result.success, 
          message: result.message 
        } 
      }));
      
      // Clear result message after 3 seconds
      setTimeout(() => {
        setKillResult(prev => {
          const newState = { ...prev };
          delete newState[pid];
          return newState;
        });
      }, 3000);
    } catch (err) {
      setKillResult(prev => ({ 
        ...prev, 
        [pid]: { 
          success: false, 
          message: `Error: ${err instanceof Error ? err.message : 'Unknown error'}` 
        } 
      }));
    } finally {
      setIsKilling(prev => ({ ...prev, [pid]: false }));
    }
  };

  // If no process data available
  if (!processes || processes.length === 0) {
    return (
      <div className="cpu-section">
        <div className="cpu-section-title">Top CPU Processes</div>
        <div className="no-data-message">No process data available</div>
      </div>
    );
  }

  return (
    <div className="cpu-section">
      <div className="cpu-section-title">Top CPU Processes</div>
      <table className="process-table">
        <thead>
          <tr>
            <th>Process</th>
            <th>PID</th>
            <th>User</th>
            <th>CPU %</th>
            <th>Memory %</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {processes.map((process) => (
            <tr key={process.pid}>
              <td>
                <div className="process-name">{process.name}</div>
                {process.command && <div className="process-command">{process.command}</div>}
              </td>
              <td>{process.pid}</td>
              <td>{process.user}</td>
              <td>
                <div className="usage-bar-container">
                  <div 
                    className="usage-bar-fill" 
                    style={{ width: `${Math.min(process.cpu_percent, 100)}%` }}
                  />
                  <span className="usage-text">{process.cpu_percent.toFixed(1)}%</span>
                </div>
              </td>
              <td>
                {process.memory_percent !== undefined && (
                  <div className="usage-bar-container">
                    <div 
                      className="usage-bar-fill memory" 
                      style={{ width: `${Math.min(process.memory_percent, 100)}%` }}
                    />
                    <span className="usage-text">{process.memory_percent.toFixed(1)}%</span>
                  </div>
                )}
              </td>
              <td>
                <div className="process-actions">
                  <button 
                    className="kill-button" 
                    onClick={() => handleKillProcess(process.pid)}
                    disabled={isKilling[process.pid]}
                  >
                    {isKilling[process.pid] ? 'Killing...' : 'Kill'}
                  </button>
                  
                  {killResult[process.pid] && (
                    <div className={`kill-result ${killResult[process.pid].success ? 'success' : 'error'}`}>
                      {killResult[process.pid].message}
                    </div>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CPUProcessesTab;