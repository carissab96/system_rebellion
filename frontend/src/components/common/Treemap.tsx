import React, { useRef, useEffect } from 'react';

interface TreemapNode {
  name: string;
  path?: string;
  value: number;
  children?: TreemapNode[];
  color?: string;
}

interface TreemapProps {
  data: TreemapNode;
  width?: number;
  height?: number;
  onNodeClick?: (node: TreemapNode) => void;
  colorScale?: string[];
}

export const Treemap: React.FC<TreemapProps> = ({
  data,
  width = 800,
  height = 500,
  onNodeClick,
  colorScale = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#34495e']
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !data) return;

    // In a real implementation, this would use D3.js or a similar library
    // to render the treemap visualization. For this placeholder, we'll just
    // create a simple div-based representation.
    
    const container = containerRef.current;
    container.innerHTML = '';
    container.style.width = `${width}px`;
    container.style.height = `${height}px`;
    container.style.position = 'relative';
    
    // Simple recursive function to render nodes
    const renderNode = (node: TreemapNode, x: number, y: number, w: number, h: number, depth: number) => {
      const div = document.createElement('div');
      div.style.position = 'absolute';
      div.style.left = `${x}px`;
      div.style.top = `${y}px`;
      div.style.width = `${w}px`;
      div.style.height = `${h}px`;
      div.style.backgroundColor = node.color || colorScale[depth % colorScale.length];
      div.style.border = '1px solid white';
      div.style.overflow = 'hidden';
      div.style.padding = '4px';
      div.style.boxSizing = 'border-box';
      div.style.fontSize = '12px';
      div.style.color = 'white';
      div.style.textShadow = '1px 1px 1px rgba(0,0,0,0.5)';
      div.style.cursor = 'pointer';
      
      // Add text if there's enough space
      if (w > 60 && h > 30) {
        div.innerHTML = `
          <div style="font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
            ${node.name}
          </div>
          ${node.value ? `<div>${formatBytes(node.value)}</div>` : ''}
        `;
      }
      
      // Add click handler
      if (onNodeClick) {
        div.onclick = () => onNodeClick(node);
      }
      
      container.appendChild(div);
      
      // Render children if they exist
      if (node.children && node.children.length > 0) {
        // Simple algorithm to layout children
        // In a real implementation, this would use a more sophisticated algorithm
        const totalValue = node.children.reduce((sum, child) => sum + child.value, 0);
        
        let currentX = x;
        let currentY = y;
        const isHorizontal = w > h;
        
        node.children.forEach(child => {
          const ratio = child.value / totalValue;
          let childW, childH;
          
          if (isHorizontal) {
            childW = w * ratio;
            childH = h;
            renderNode(child, currentX, currentY, childW, childH, depth + 1);
            currentX += childW;
          } else {
            childW = w;
            childH = h * ratio;
            renderNode(child, currentX, currentY, childW, childH, depth + 1);
            currentY += childH;
          }
        });
      }
    };
    
    // Start rendering from the root
    renderNode(data, 0, 0, width, height, 0);
    
  }, [data, width, height, colorScale, onNodeClick]);
  
  return <div ref={containerRef} className="treemap-container"></div>;
};

// Helper function to format bytes
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};
