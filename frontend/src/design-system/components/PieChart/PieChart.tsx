import React from 'react';
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import './PieChart.css';

interface PieChartData {
  name: string;
  value: number;
  color?: string;
}

interface PieChartProps {
  data: PieChartData[];
  width?: number;
  height?: number;
  innerRadius?: number;
  outerRadius?: number;
  paddingAngle?: number;
  className?: string;
}

export const PieChart: React.FC<PieChartProps> = ({
  data,
  width = 400,
  height = 400,
  innerRadius = 0,
  outerRadius = 80,
  paddingAngle = 0,
  className = ''
}) => {
  // Generate colors if not provided
  const colors = [
    '#00B8D9',
    '#008CBA',
    '#005A87',
    '#003366',
    '#001A33'
  ];

  return (
    <div className={`pie-chart ${className}`}>
      <ResponsiveContainer width={width} height={height}>
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={innerRadius}
            outerRadius={outerRadius}
            paddingAngle={paddingAngle}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color || colors[index % colors.length]}
              />
            ))}
          </Pie>
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  );
};
