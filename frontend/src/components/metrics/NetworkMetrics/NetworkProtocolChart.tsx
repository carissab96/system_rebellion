import React, { useEffect, useRef } from 'react';
import './NetworkMetrics.css';

// We'll use a simple chart library or create our own visualization
// For now, we'll create a custom visualization

interface ProtocolData {
  tcp?: number;
  udp?: number;
  icmp?: number;
  http?: number;
  https?: number;
  dns?: number;
  [key: string]: number | undefined;
}

interface NetworkProtocolChartProps {
  protocolData: ProtocolData;
}

const NetworkProtocolChart: React.FC<NetworkProtocolChartProps> = ({ protocolData }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Protocol colors with cyberpunk theme
  const protocolColors: Record<string, string> = {
    tcp: '#3a86ff',    // Blue
    udp: '#ff006e',    // Pink
    icmp: '#8338ec',   // Purple
    http: '#fb5607',   // Orange
    https: '#38b000',  // Green
    dns: '#ffbe0b',    // Yellow
    other: '#5e60ce',  // Indigo
  };
  
  useEffect(() => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calculate total
    const total = Object.values(protocolData).reduce((sum: number, value) => sum + (value || 0), 0);
    
    if (total === 0) {
      // Draw empty state
      ctx.font = '14px "Courier New", monospace';
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'center';
      ctx.fillText('No protocol data available', canvas.width / 2, canvas.height / 2);
      ctx.fillText('The Meth Snail suggests checking your network connection', canvas.width / 2, canvas.height / 2 + 20);
      return;
    }
    
    // Draw pie chart
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 10;
    
    let startAngle = 0;
    
    // Sort protocols by value for better visualization
    const sortedProtocols = Object.entries(protocolData)
      .filter(([_, value]) => value && value > 0)
      .sort(([_, a], [__, b]) => (b || 0) - (a || 0));
    
    // Draw slices
    sortedProtocols.forEach(([protocol, value]) => {
      if (!value || value === 0) return;
      
      const sliceAngle = total > 0 ? (value / total) * 2 * Math.PI : 0;
      const endAngle = startAngle + sliceAngle;
      
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, startAngle, endAngle);
      ctx.closePath();
      
      // Use protocol color or default to 'other'
      ctx.fillStyle = protocolColors[protocol.toLowerCase()] || protocolColors.other;
      ctx.fill();
      
      // Add cyberpunk-style glow effect
      ctx.shadowColor = ctx.fillStyle;
      ctx.shadowBlur = 10;
      ctx.stroke();
      ctx.shadowBlur = 0;
      
      // Calculate label position
      const labelAngle = startAngle + sliceAngle / 2;
      const labelRadius = radius * 0.7;
      const labelX = centerX + Math.cos(labelAngle) * labelRadius;
      const labelY = centerY + Math.sin(labelAngle) * labelRadius;
      
      // Draw label if slice is big enough
      if (sliceAngle > 0.2) {
        ctx.font = 'bold 12px "Courier New", monospace';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(protocol.toUpperCase(), labelX, labelY);
      }
      
      startAngle = endAngle;
    });
    
    // Draw center circle for cyberpunk effect
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius * 0.3, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fill();
    ctx.strokeStyle = '#00f5d4';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Draw title in center
    ctx.font = 'bold 14px "Courier New", monospace';
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('PROTOCOL', centerX, centerY - 7);
    ctx.fillText('ANALYSIS', centerX, centerY + 7);
    
  }, [protocolData]);
  
  // Create legend items
  const legendItems = Object.entries(protocolData)
    .filter(([_, value]) => value && value > 0)
    .sort(([_, a], [__, b]) => (b || 0) - (a || 0))
    .map(([protocol, value]) => {
      const totalValue = Object.values(protocolData).reduce((sum: number, v) => sum + (v || 0), 0);
      const percentage = value && value > 0 ? ((value / totalValue) * 100).toFixed(1) : '0.0';
      return (
        <div key={protocol} className="protocol-legend-item">
          <div 
            className="protocol-color-box" 
            style={{ backgroundColor: protocolColors[protocol.toLowerCase()] || protocolColors.other }}
          />
          <div className="protocol-name">{protocol.toUpperCase()}</div>
          <div className="protocol-percentage">{percentage}%</div>
        </div>
      );
    });
  
  return (
    <div className="network-protocol-chart">
      <div className="chart-container">
        <canvas 
          ref={canvasRef} 
          width={300} 
          height={300} 
          className="protocol-canvas"
        />
      </div>
      <div className="protocol-legend">
        {legendItems.length > 0 ? legendItems : (
          <div className="no-data-message">
            No protocol data available. Sir Hawkington suggests checking your aristocratic network configuration.
          </div>
        )}
      </div>
    </div>
  );
};

export default NetworkProtocolChart;
