// components/AgentTheater/shared/Chart3D.tsx
import React, { useEffect, useRef } from 'react';

import * as THREE from 'three';

interface Chart3DProps {
  data: Array<{
    label: string;
    value: number; // 0-1 range
  }>;
  color: string;
  height: number;
  glowIntensity?: number;
}

export const Chart3D: React.FC<Chart3DProps> = ({ 
  data, 
  color, 
  height, 
  glowIntensity = 0.3 
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    if (!mountRef.current || !data.length) return;

    const width = mountRef.current.clientWidth;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true, 
      alpha: true,
      powerPreference: 'high-performance'
    });

    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
    mountRef.current.appendChild(renderer.domElement);

    // Create bars for each data point
    const barWidth = 0.8;
    const barSpacing = 1.5;
    const maxBarHeight = 3;
    
    data.forEach((item, index) => {
      const barHeight = item.value * maxBarHeight;
      const geometry = new THREE.BoxGeometry(barWidth, barHeight, barWidth);
      
      // Create material with glow effect
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color(color),
        emissive: new THREE.Color(color),
        emissiveIntensity: glowIntensity,
        shininess: 100
      });
      
      const bar = new THREE.Mesh(geometry, material);
      bar.position.x = (index - (data.length - 1) / 2) * barSpacing;
      bar.position.y = barHeight / 2;
      bar.castShadow = true;
      bar.receiveShadow = true;
      
      scene.add(bar);
    });

    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    // Add directional light for shadows
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);

    // Add subtle glow light matching the agent color
    const glowLight = new THREE.PointLight(new THREE.Color(color), 0.5, 20);
    glowLight.position.set(0, 5, 5);
    scene.add(glowLight);

    // Position camera
    camera.position.set(0, 3, 6);
    camera.lookAt(0, 1, 0);

    // Add ground plane for shadows
    const groundGeometry = new THREE.PlaneGeometry(20, 20);
    const groundMaterial = new THREE.MeshPhongMaterial({ 
      color: 0x1a1d29, 
      transparent: true, 
      opacity: 0.8 
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.1;
    ground.receiveShadow = true;
    scene.add(ground);

    // Store references
    sceneRef.current = scene;
    rendererRef.current = renderer;

    // Animation loop
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      
      // Subtle rotation for visual interest
      scene.rotation.y += 0.005;
      
      // Subtle glow pulsing
      if (glowLight) {
        glowLight.intensity = 0.5 + Math.sin(Date.now() * 0.001) * 0.1;
      }
      
      renderer.render(scene, camera);
    };

    animate();

    // Cleanup function
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
      scene.clear();
    };
  }, [data, color, height, glowIntensity]);

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      if (mountRef.current && rendererRef.current) {
        const width = mountRef.current.clientWidth;
        rendererRef.current.setSize(width, height);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [height]);

  // Show message if no data
  if (!data.length) {
    return (
      <div className="chart-3d-placeholder" style={{ height: `${height}px` }}>
        <div className="chart-placeholder-message">
          <span>No chart data available</span>
          <small>Agent not streaming metrics</small>
        </div>
      </div>
    );
  }

  return (
    <div className="chart-3d-container">
      <div 
        ref={mountRef} 
        className="chart-3d-mount"
        style={{ height: `${height}px`, width: '100%' }}
      />
      <div className="chart-3d-labels">
        {data.map((item, index) => (
          <div 
            key={index}
            className="chart-label"
            style={{ 
              left: `${((index + 0.5) / data.length) * 100}%`,
              color 
            }}
          >
            <span className="label-text">{item.label}</span>
            <span className="label-value">{Math.round(item.value * 100)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};
export default Chart3D;
