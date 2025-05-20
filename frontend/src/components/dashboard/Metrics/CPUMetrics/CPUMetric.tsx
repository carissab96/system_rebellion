import React, { useState } from 'react';
import { XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area, AreaChart, BarChart, Bar } from 'recharts';
import { useAppSelector } from '../../../../store/hooks';
import { RootState } from '../../../../store/store';
import { SystemMetric } from '../../../../types/metrics';
import { MetricsCard, MetricStatus } from '../../../../design-system/components/MetricsCard';
import { Tabs, Tab } from '../../../../design-system/components/Tabs/Tabs';
import { Card } from '../../../../design-system/components/Card/Card';

 // Interface for CPU process
interface CPUProcess {
  name: string;
  pid: number;
  cpu_percent: number;
  memory_percent: number;
}

 // Interface for CPU details
interface CPUDetails {
  cores: {
    logical: number;
    physical: number;
  };
  frequency: {
    current: number;
    min: number;
    max: number;
  };
  temperature: number;
  per_core_usage: number[];
}

export const CPUMetric: React.FC = () => {
     // Redux state
    const currentMetric = useAppSelector((state: RootState) => state.metrics.current) as SystemMetric | null;
    const historicalMetrics = useAppSelector((state: RootState) => state.metrics.historical || []) as SystemMetric[];
    const isLoading = useAppSelector((state: RootState) => state.metrics.loading);
    
     // Tab state
    const [activeTab, setActiveTab] = useState<string>('overview');
    
     // CPU metrics state
    const cpuUsage = currentMetric?.cpu_usage ?? 0;
    const cpuDetails = currentMetric?.cpu_usage as CPUDetails | undefined;
    const topProcesses = currentMetric?.cpu_usage as unknown as CPUProcess[] ?? [];
    const cpuTemp = cpuDetails?.temperature ?? null;
    const cpuFreq = {
        current: cpuDetails?.frequency?.current ?? null,
        min: cpuDetails?.frequency?.min ?? null,
        max: cpuDetails?.frequency?.max ?? null
    };
    
     // Chart data
    const chartData = (historicalMetrics || []).map(metric => ({
        timestamp: metric.timestamp,
        usage: metric.cpu_usage ?? 0
    }));
    
     // Generate core usage data for bar chart
    const coreData = cpuDetails?.per_core_usage?.map((usage: number, index: number) => ({
        name: `Core ${index + 1}`,
         usage
    })) ?? [];

    

     // Calculate CPU status
    const getStatus = (usage: number): MetricStatus => {
        if (usage >= 90) return 'critical';
        if (usage >= 70) return 'warning';
        return 'normal';
    };

     // Calculate trend
    const getTrend = (current: number, previous: number): 'up' | 'down' | 'stable' => {
        if (current > previous + 5) return 'up';
        if (current < previous - 5) return 'down';
        return 'stable';
    };

     // Get previous value from historical metrics
    const previousValue = historicalMetrics.length > 1 ? 
        historicalMetrics[historicalMetrics.length - 2].cpu_usage ?? cpuUsage : 
        cpuUsage;

     // Calculate change percentage (avoid division by zero)
    const changePercentage = previousValue !== 0 ? 
        ((cpuUsage - previousValue) / previousValue) * 100 : 
        0;

    if (isLoading) {
        return <MetricsCard title="CPU Usage" value="--" unit="%" updating={true} />;
    }

     //      Render the overview tab
    const renderOverviewTab = () => (
        <div className="overview-content">
            <div className="chart-container">
                <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={chartData}>
                        <defs>
                            <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3a86ff" stopOpacity={0.8}/>
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                        <XAxis 
                            dataKey="timestamp"
                            tickFormatter={(time: string) => new Date(time).toLocaleTimeString()}
                            stroke="var(--text-secondary)"
                        />
                        <YAxis 
                            domain={[0, 100]}
                            tickFormatter={(value: number) => `${value}%`}
                            stroke="var(--text-secondary)"
                        />
                        <Tooltip 
                            formatter={(value: number) => [`${Number(value).toFixed(1)}%`, 'CPU Usage']}
                            labelFormatter={(label: string) => new Date(label).toLocaleString()}
                            contentStyle={{ background: 'var(--background)', border: 'none', borderRadius: '8px' }}
                            itemStyle={{ color: 'var(--primary)' }}
                            labelStyle={{ color: 'var(--text-primary)' }}
                        />
                        <Area 
                            type="monotone" 
                            dataKey="usage" 
                            stroke="var(--primary)" 
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#cpuGradient)"
                            activeDot={{ r: 6, strokeWidth: 0, fill: 'var(--primary)' }}
                            isAnimationActive={true}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );



    function renderCoresTab(): React.ReactNode {
        return (
            <div className="cores-content">
                <h3>Core Usage</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={coreData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                        <XAxis dataKey="name" stroke="var(--text-secondary)" />
                        <YAxis domain={[0, 100]} tickFormatter={(value: number) => `${value}%`} stroke="var(--text-secondary)" />
                        <Tooltip />
                        <Bar dataKey="usage" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        );
    }

    function renderProcessesTab(): React.ReactNode {
        return (
            <div className="processes-content">
                <h3>Top CPU Processes</h3>
                <div className="process-list">
                    {topProcesses.length > 0 ? (
                        topProcesses.map((process: CPUProcess, index: number) => (
                            <Card key={index} className="process-card">
                                <div className="process-name">{process.name}</div>
                                <div className="process-usage">{process.cpu_percent.toFixed(1)}%</div>
                                <div className="process-details">
                                    <span>PID: {process.pid}</span>
                                    <span>Memory: {process.memory_percent.toFixed(1)}%</span>
                                </div>
                            </Card>
                        ))
                    ) : (
                        <div className="no-data">No process data available</div>
                    )}
                </div>
            </div>
        );
    }

    function renderDetailsTab(): React.ReactNode {
        return (
            <div className="details-content">
                <h3>CPU Details</h3>
                <div>
                    <div>Temperature: {cpuTemp !== null ? `${cpuTemp.toFixed(1)}°C` : 'N/A'}</div>
                    <div>Frequency: {cpuFreq.current ? `${(cpuFreq.current / 1000).toFixed(2)} GHz` : 'N/A'}</div>
                </div>
            </div>
        );
    }

    return (
        <div className="cpu-metric">
            <MetricsCard
                title="CPU Usage"
                value={`${cpuUsage.toFixed(1)}`}
                unit="%"
                status={getStatus(cpuUsage)}
                trend={getTrend(cpuUsage, previousValue)}
                changePercentage={changePercentage}
                showSparkline={true}
                sparklineData={(chartData || []).map(d => d.usage)}
            >
                <Tabs activeTab={activeTab} onChange={setActiveTab}>
                    <Tab id="overview" label="Overview">{renderOverviewTab()}</Tab>
                    <Tab id="cores" label="Cores">{renderCoresTab()}</Tab>
                    <Tab id="processes" label="Processes">{renderProcessesTab()}</Tab>
                    <Tab id="details" label="Details">{renderDetailsTab()}</Tab>
                </Tabs>
            </MetricsCard>
        </div>
    );
};

export default CPUMetric;