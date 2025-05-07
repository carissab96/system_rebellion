import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area, AreaChart, BarChart, Bar, Cell, Legend } from 'recharts';
import { useAppSelector } from '../../../../store/hooks';
import { RootState } from '../../../../store/store';
import './CPUMetric.css';
import { SystemMetric } from '../../../../types/metrics';

export const CPUMetric: React.FC = () => {
    // Explicitly type the selectors with SystemMetric
    const currentMetric = useAppSelector((state: RootState) => state.metrics.current) as SystemMetric | null;
    const historicalMetrics = useAppSelector((state: RootState) => state.metrics.historical) as SystemMetric[];
    const isLoading = useAppSelector((state: RootState) => state.metrics.loading);
    
    // Tab state
    const [activeTab, setActiveTab] = useState('overview');
    
    // CPU metrics state
    const [cpuUsage, setCpuUsage] = useState<number>(0);
    const [coreUsage, setCoreUsage] = useState<number[]>([]);
    const [cpuTemp, setCpuTemp] = useState<number | null>(null);
    const [cpuFreq, setCpuFreq] = useState<{current: number | null, min: number | null, max: number | null}>({current: null, min: null, max: null});
    const [topProcesses, setTopProcesses] = useState<any[]>([]);
    
    // Type your chart data
    const chartData: SystemMetric[] = historicalMetrics;
    
    // Extract CPU metrics from current metric
    useEffect(() => {
        if (currentMetric) {
            // Log CPU details to console for debugging
            console.log('CPU details:', currentMetric.cpu);
            
            // Set basic CPU usage
            setCpuUsage(currentMetric.cpu_usage || 0);
            
            // Set per-core usage if available
            if (currentMetric.cpu?.per_core_percent) {
                setCoreUsage(currentMetric.cpu.per_core_percent);
            }
            
            // Set CPU temperature if available
            if (currentMetric.cpu?.temperature) {
                setCpuTemp(currentMetric.cpu.temperature);
            }
            
            // Set CPU frequency if available
            if (currentMetric.cpu?.frequency) {
                setCpuFreq({
                    current: currentMetric.cpu.frequency.current,
                    min: currentMetric.cpu.frequency.min,
                    max: currentMetric.cpu.frequency.max
                });
            }
            
            // Set top CPU processes if available
            if (currentMetric.cpu?.top_processes) {
                setTopProcesses(currentMetric.cpu.top_processes);
            }
        }
    }, [currentMetric]);
    
    // Generate core usage data for bar chart
    const coreData = coreUsage.map((usage, index) => ({
        name: `Core ${index}`,
        usage: usage
    }));

    if (isLoading) {
        return <div className="metric-card">The Meth Snail is calculating CPU cycles...</div>;
    }

    return (
        <div className="metric-card">
            <h3>CPU Usage</h3>
            
            {/* Tab Navigation */}
            <div className="metric-tabs">
                <button 
                    className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                >
                    Overview
                </button>
                <button 
                    className={`tab-button ${activeTab === 'cores' ? 'active' : ''}`}
                    onClick={() => setActiveTab('cores')}
                >
                    Cores
                </button>
                <button 
                    className={`tab-button ${activeTab === 'processes' ? 'active' : ''}`}
                    onClick={() => setActiveTab('processes')}
                >
                    Processes
                </button>
                <button 
                    className={`tab-button ${activeTab === 'details' ? 'active' : ''}`}
                    onClick={() => setActiveTab('details')}
                >
                    Details
                </button>
            </div>
            
            {/* Overview Tab */}
            {activeTab === 'overview' && (
                <div className="tab-content">
                    <div className="metric-value">
                        {cpuUsage.toFixed(1)}%
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={200}>
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3a86ff" stopOpacity={0.8}/>
                                        <stop offset="95%" stopColor="#3a86ff" stopOpacity={0.2}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
                                <XAxis 
                                    dataKey="timestamp"
                                    tickFormatter={(time: string) => new Date(time).toLocaleTimeString()}
                                    stroke="rgba(255, 255, 255, 0.7)"
                                />
                                <YAxis 
                                    domain={[0, 100]}
                                    tickFormatter={(value: number) => `${value}%`}
                                    stroke="rgba(255, 255, 255, 0.7)"
                                />
                                <Tooltip 
                                    formatter={(value: number) => [`${Number(value).toFixed(1)}%`, 'CPU Usage']}
                                    labelFormatter={(label: string) => new Date(label).toLocaleString()}
                                    contentStyle={{ background: 'rgba(0, 0, 0, 0.8)', border: 'none', borderRadius: '8px' }}
                                    itemStyle={{ color: '#3a86ff' }}
                                    labelStyle={{ color: 'white' }}
                                />
                                <Area 
                                    type="monotone" 
                                    dataKey="cpu_usage" 
                                    stroke="#3a86ff" 
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#cpuGradient)"
                                    activeDot={{ r: 6, strokeWidth: 0, fill: '#3a86ff' }}
                                    isAnimationActive={true}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                    
                    {/* Temperature and Frequency */}
                    <div className="cpu-stats">
                        {cpuTemp !== null && (
                            <div className="cpu-stat-item">
                                <div className="stat-label">Temperature</div>
                                <div className="stat-value">{cpuTemp.toFixed(1)}°C</div>
                            </div>
                        )}
                        {cpuFreq.current !== null && (
                            <div className="cpu-stat-item">
                                <div className="stat-label">Frequency</div>
                                <div className="stat-value">{(cpuFreq.current / 1000).toFixed(2)} GHz</div>
                            </div>
                        )}
                    </div>
                </div>
            )}
            
            {/* Cores Tab */}
            {activeTab === 'cores' && (
                <div className="tab-content">
                    <div className="cores-header">
                        <div className="cores-title">Per-Core Usage</div>
                        <div className="cores-count">Cores: {coreUsage.length}</div>
                    </div>
                    
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={coreData} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
                                <XAxis 
                                    type="number" 
                                    domain={[0, 100]}
                                    tickFormatter={(value: number) => `${value}%`}
                                    stroke="rgba(255, 255, 255, 0.7)"
                                />
                                <YAxis 
                                    dataKey="name" 
                                    type="category" 
                                    width={60}
                                    stroke="rgba(255, 255, 255, 0.7)"
                                />
                                <Tooltip 
                                    formatter={(value: number) => [`${Number(value).toFixed(1)}%`, 'Usage']}
                                    contentStyle={{ background: 'rgba(0, 0, 0, 0.8)', border: 'none', borderRadius: '8px' }}
                                    itemStyle={{ color: '#3a86ff' }}
                                    labelStyle={{ color: 'white' }}
                                />
                                <Bar 
                                    dataKey="usage" 
                                    fill="#3a86ff" 
                                    radius={[0, 4, 4, 0]}
                                    barSize={20}
                                >
                                    {coreData.map((entry, index) => (
                                        <Cell 
                                            key={`cell-${index}`} 
                                            fill={entry.usage > 80 ? '#ff3838' : entry.usage > 50 ? '#ffbe0b' : '#3a86ff'} 
                                        />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
            
            {/* Processes Tab */}
            {activeTab === 'processes' && (
                <div className="tab-content">
                    <div className="processes-header">
                        <div className="processes-title">Top CPU Processes</div>
                    </div>
                    
                    <div className="processes-list">
                        {topProcesses.length > 0 ? (
                            topProcesses.map((process, index) => (
                                <div className="process-item" key={index}>
                                    <div className="process-name">{process.name}</div>
                                    <div className="process-usage">
                                        <div className="process-bar-container">
                                            <div 
                                                className="process-bar" 
                                                style={{ 
                                                    width: `${Math.min(process.cpu_percent, 100)}%`,
                                                    backgroundColor: process.cpu_percent > 80 ? '#ff3838' : process.cpu_percent > 50 ? '#ffbe0b' : '#3a86ff'
                                                }}
                                            ></div>
                                        </div>
                                        <div className="process-percent">{process.cpu_percent.toFixed(1)}%</div>
                                    </div>
                                    <div className="process-details">
                                        <span>PID: {process.pid}</span>
                                        <span>Mem: {process.memory_percent.toFixed(1)}%</span>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="no-data">No process data available</div>
                        )}
                    </div>
                </div>
            )}
            
            {/* Details Tab */}
            {activeTab === 'details' && (
                <div className="tab-content">
                    <div className="cpu-details">
                        <div className="detail-section">
                            <h4>CPU Information</h4>
                            <div className="detail-item">
                                <div className="detail-label">Logical Cores</div>
                                <div className="detail-value">{currentMetric?.cpu?.cores?.logical || 'N/A'}</div>
                            </div>
                            <div className="detail-item">
                                <div className="detail-label">Physical Cores</div>
                                <div className="detail-value">{currentMetric?.cpu?.cores?.physical || 'N/A'}</div>
                            </div>
                            <div className="detail-item">
                                <div className="detail-label">Current Frequency</div>
                                <div className="detail-value">
                                    {cpuFreq.current ? `${(cpuFreq.current / 1000).toFixed(2)} GHz` : 'N/A'}
                                </div>
                            </div>
                            <div className="detail-item">
                                <div className="detail-label">Min Frequency</div>
                                <div className="detail-value">
                                    {cpuFreq.min ? `${(cpuFreq.min / 1000).toFixed(2)} GHz` : 'N/A'}
                                </div>
                            </div>
                            <div className="detail-item">
                                <div className="detail-label">Max Frequency</div>
                                <div className="detail-value">
                                    {cpuFreq.max ? `${(cpuFreq.max / 1000).toFixed(2)} GHz` : 'N/A'}
                                </div>
                            </div>
                            <div className="detail-item">
                                <div className="detail-label">Temperature</div>
                                <div className="detail-value">
                                    {cpuTemp !== null ? `${cpuTemp.toFixed(1)}°C` : 'N/A'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CPUMetric;