// frontend/src/components/metrics/charts/MetricsCharts.tsx
import React from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import './MetricsCharts.css';

// Common chart colors based on the design system
const CHART_COLORS = {
  cpu: {
    primary: '#3a86ff',
    secondary: '#8338ec',
    gradient: ['#3a86ff', '#8338ec'],
  },
  memory: {
    primary: '#8338ec',
    secondary: '#ff006e',
    gradient: ['#8338ec', '#ff006e'],
  },
  disk: {
    primary: '#ff006e',
    secondary: '#3a86ff',
    gradient: ['#ff006e', '#3a86ff'],
  },
  network: {
    primary: '#00f5d4',
    secondary: '#3a86ff',
    gradient: ['#00f5d4', '#3a86ff'],
  },
  temperature: {
    primary: '#ffbe0b',
    secondary: '#ff006e',
    gradient: ['#ffbe0b', '#ff006e'],
  }
};

// Common chart props
interface BaseChartProps {
  height?: number;
  width?: number;
  className?: string;
  showGrid?: boolean;
  showTooltip?: boolean;
  showXAxis?: boolean;
  showYAxis?: boolean;
  chartType: 'cpu' | 'memory' | 'disk' | 'network' | 'temperature';
}

// Time series data point interface
interface TimeSeriesDataPoint {
  timestamp: number | string;
  value: number;
  [key: string]: any;
}

// Props for line and area charts
interface TimeSeriesChartProps extends BaseChartProps {
  data: TimeSeriesDataPoint[];
  dataKey: string;
  xAxisDataKey?: string;
  yAxisUnit?: string;
  yAxisDomain?: [number, number];
  additionalLines?: {
    dataKey: string;
    color: string;
    strokeDasharray?: string;
  }[];
}

// Usage chart props
interface UsageChartProps extends BaseChartProps {
  usagePercent: number;
  showLabel?: boolean;
  label?: string;
}

// Bar chart props
interface BarChartProps extends BaseChartProps {
  data: any[];
  dataKey: string;
  nameKey: string;
  barSize?: number;
}

// Pie chart props
interface PieChartProps extends BaseChartProps {
  data: any[];
  dataKey: string;
  nameKey: string;
  colors?: string[];
}

/**
 * TimeSeriesLineChart - A line chart for time series data
 */
export const TimeSeriesLineChart: React.FC<TimeSeriesChartProps> = ({
  data,
  dataKey,
  xAxisDataKey = 'timestamp',
  height = 300,
  width,
  className = '',
  showGrid = true,
  showTooltip = true,
  showXAxis = true,
  showYAxis = true,
  yAxisUnit = '',
  yAxisDomain,
  chartType = 'cpu',
  additionalLines = [],
}) => {
  const chartColors = CHART_COLORS[chartType];
  
  return (
    <div className={`metrics-chart line-chart ${className}`} style={{ height, width: width || '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          {showGrid && <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.1)" />}
          {showXAxis && <XAxis 
            dataKey={xAxisDataKey} 
            stroke="#adb5bd" 
            tick={{ fill: '#adb5bd', fontSize: 12 }} 
            tickLine={{ stroke: '#adb5bd' }}
            axisLine={{ stroke: '#adb5bd' }}
          />}
          {showYAxis && <YAxis 
            stroke="#adb5bd" 
            tick={{ fill: '#adb5bd', fontSize: 12 }} 
            tickLine={{ stroke: '#adb5bd' }}
            axisLine={{ stroke: '#adb5bd' }}
            unit={yAxisUnit}
            domain={yAxisDomain || ['dataMin', 'dataMax']}
          />}
          {showTooltip && <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(30, 30, 30, 0.9)',
              border: `1px solid ${chartColors.primary}`,
              borderRadius: '4px',
              color: '#f8f9fa'
            }} 
            itemStyle={{ color: '#f8f9fa' }}
            labelStyle={{ color: '#adb5bd' }}
          />}
          <Line 
            type="monotone" 
            dataKey={dataKey} 
            stroke={chartColors.primary}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 6, stroke: chartColors.primary, strokeWidth: 2, fill: '#fff' }}
          />
          {additionalLines.map((line, index) => (
            <Line
              key={`line-${index}`}
              type="monotone"
              dataKey={line.dataKey}
              stroke={line.color}
              strokeWidth={2}
              strokeDasharray={line.strokeDasharray}
              dot={false}
              activeDot={{ r: 6, stroke: line.color, strokeWidth: 2, fill: '#fff' }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * TimeSeriesAreaChart - An area chart for time series data
 */
export const TimeSeriesAreaChart: React.FC<TimeSeriesChartProps> = ({
  data,
  dataKey,
  xAxisDataKey = 'timestamp',
  height = 300,
  width,
  className = '',
  showGrid = true,
  showTooltip = true,
  showXAxis = true,
  showYAxis = true,
  yAxisUnit = '',
  yAxisDomain,
  chartType = 'cpu',
  additionalLines = [],
}) => {
  const chartColors = CHART_COLORS[chartType];
  
  return (
    <div className={`metrics-chart area-chart ${className}`} style={{ height, width: width || '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id={`colorGradient-${chartType}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={chartColors.primary} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={chartColors.primary} stopOpacity={0.2}/>
            </linearGradient>
          </defs>
          {showGrid && <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.1)" />}
          {showXAxis && <XAxis 
            dataKey={xAxisDataKey} 
            stroke="#adb5bd" 
            tick={{ fill: '#adb5bd', fontSize: 12 }} 
            tickLine={{ stroke: '#adb5bd' }}
            axisLine={{ stroke: '#adb5bd' }}
          />}
          {showYAxis && <YAxis 
            stroke="#adb5bd" 
            tick={{ fill: '#adb5bd', fontSize: 12 }} 
            tickLine={{ stroke: '#adb5bd' }}
            axisLine={{ stroke: '#adb5bd' }}
            unit={yAxisUnit}
            domain={yAxisDomain || ['dataMin', 'dataMax']}
          />}
          {showTooltip && <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(30, 30, 30, 0.9)',
              border: `1px solid ${chartColors.primary}`,
              borderRadius: '4px',
              color: '#f8f9fa'
            }} 
            itemStyle={{ color: '#f8f9fa' }}
            labelStyle={{ color: '#adb5bd' }}
          />}
          <Area 
            type="monotone" 
            dataKey={dataKey} 
            stroke={chartColors.primary}
            strokeWidth={2}
            fill={`url(#colorGradient-${chartType})`}
            activeDot={{ r: 6, stroke: chartColors.primary, strokeWidth: 2, fill: '#fff' }}
          />
          {additionalLines.map((line, index) => (
            <Area
              key={`area-${index}`}
              type="monotone"
              dataKey={line.dataKey}
              stroke={line.color}
              strokeWidth={2}
              fill="none"
              strokeDasharray={line.strokeDasharray}
              activeDot={{ r: 6, stroke: line.color, strokeWidth: 2, fill: '#fff' }}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * UsageGauge - A circular gauge for displaying usage percentages
 */
export const UsageGauge: React.FC<UsageChartProps> = ({
  usagePercent,
  height = 200,
  width,
  className = '',
  showLabel = true,
  label = 'Usage',
  chartType = 'cpu',
}) => {
  const chartColors = CHART_COLORS[chartType];
  
  // Calculate color based on usage percentage
  const getColor = (usage: number) => {
    if (usage > 90) return '#ff3838'; // Danger
    if (usage > 70) return '#ffbe0b'; // Warning
    return chartColors.primary; // Normal
  };
  
  const color = getColor(usagePercent);
  
  return (
    <div className={`metrics-chart gauge-chart ${className}`} style={{ height, width: width || height }}>
      <svg viewBox="0 0 200 200" width="100%" height="100%">
        {/* Background circle */}
        <circle
          cx="100"
          cy="100"
          r="80"
          fill="none"
          stroke="#333"
          strokeWidth="20"
        />
        
        {/* Usage arc */}
        <circle
          cx="100"
          cy="100"
          r="80"
          fill="none"
          stroke={color}
          strokeWidth="20"
          strokeDasharray={`${usagePercent * 5.02} 502`}
          strokeLinecap="round"
          transform="rotate(-90 100 100)"
          style={{
            filter: `drop-shadow(0 0 5px ${color})`,
          }}
        />
        
        {/* Percentage text */}
        <text
          x="100"
          y="100"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="36"
          fontWeight="bold"
          fill="#f8f9fa"
        >
          {usagePercent.toFixed(1)}%
        </text>
        
        {/* Label text */}
        {showLabel && (
          <text
            x="100"
            y="130"
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="14"
            fill="#adb5bd"
          >
            {label}
          </text>
        )}
      </svg>
    </div>
  );
};

/**
 * MetricsBarChart - A bar chart for comparing values
 */
export const MetricsBarChart: React.FC<BarChartProps> = ({
  data,
  dataKey,
  nameKey,
  height = 300,
  width,
  className = '',
  showGrid = true,
  showTooltip = true,
  showXAxis = true,
  showYAxis = true,
  chartType = 'cpu',
  barSize = 20,
}) => {
  const chartColors = CHART_COLORS[chartType];
  
  return (
    <div className={`metrics-chart bar-chart ${className}`} style={{ height, width: width || '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id={`barGradient-${chartType}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={chartColors.primary} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={chartColors.secondary} stopOpacity={0.8}/>
            </linearGradient>
          </defs>
          {showGrid && <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.1)" />}
          {showXAxis && <XAxis 
            dataKey={nameKey} 
            stroke="#adb5bd" 
            tick={{ fill: '#adb5bd', fontSize: 12 }} 
            tickLine={{ stroke: '#adb5bd' }}
            axisLine={{ stroke: '#adb5bd' }}
          />}
          {showYAxis && <YAxis 
            stroke="#adb5bd" 
            tick={{ fill: '#adb5bd', fontSize: 12 }} 
            tickLine={{ stroke: '#adb5bd' }}
            axisLine={{ stroke: '#adb5bd' }}
          />}
          {showTooltip && <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(30, 30, 30, 0.9)',
              border: `1px solid ${chartColors.primary}`,
              borderRadius: '4px',
              color: '#f8f9fa'
            }} 
            itemStyle={{ color: '#f8f9fa' }}
            labelStyle={{ color: '#adb5bd' }}
          />}
          <Bar 
            dataKey={dataKey} 
            fill={`url(#barGradient-${chartType})`}
            barSize={barSize}
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * MetricsPieChart - A pie chart for showing distribution
 */
export const MetricsPieChart: React.FC<PieChartProps> = ({
  data,
  dataKey,
  nameKey,
  height = 300,
  width,
  className = '',
  showTooltip = true,
  chartType = 'cpu',
  colors,
}) => {
  const chartColors = colors || [
    CHART_COLORS.cpu.primary,
    CHART_COLORS.memory.primary,
    CHART_COLORS.disk.primary,
    CHART_COLORS.network.primary,
    CHART_COLORS.temperature.primary,
    '#00f5d4',
    '#ffbe0b',
    '#ff3838',
  ];
  
  return (
    <div className={`metrics-chart pie-chart ${className}`} style={{ height, width: width || '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey={dataKey}
            nameKey={nameKey}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
            ))}
          </Pie>
          <Legend 
            layout="horizontal" 
            verticalAlign="bottom" 
            align="center"
            formatter={(value) => <span style={{ color: '#f8f9fa' }}>{value}</span>}
          />
          {showTooltip && <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(30, 30, 30, 0.9)',
              border: `1px solid ${CHART_COLORS[chartType].primary}`,
              borderRadius: '4px',
              color: '#f8f9fa'
            }} 
            itemStyle={{ color: '#f8f9fa' }}
            labelStyle={{ color: '#adb5bd' }}
          />}
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * MetricsSparkline - A small line chart for showing trends
 */
export const MetricsSparkline: React.FC<TimeSeriesChartProps> = ({
  data,
  dataKey,
  height = 50,
  width = 120,
  className = '',
  chartType = 'cpu',
}) => {
  const chartColors = CHART_COLORS[chartType];
  
  return (
    <div className={`metrics-chart sparkline-chart ${className}`} style={{ height, width }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <Line 
            type="monotone" 
            dataKey={dataKey} 
            stroke={chartColors.primary}
            strokeWidth={1.5}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default {
  TimeSeriesLineChart,
  TimeSeriesAreaChart,
  UsageGauge,
  MetricsBarChart,
  MetricsPieChart,
  MetricsSparkline,
};
