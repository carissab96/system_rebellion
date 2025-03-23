// vite.config.ts - Now with 100% more distinguished chaos!
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Sir Hawkington's Distinguished Proxy Configuration
export default defineConfig({
  plugins: [react()],
  server: {
    // The Meth Snail insists on port 5173 for optimal performance
    port: 5173,
    proxy: {
      // All /api requests will be proxied to the backend with aristocratic elegance
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('🧐 Sir Hawkington observes a proxy error:', err);
          });
          proxy.on('proxyReq', (_proxyReq, req, _res) => {
            console.log(`🎩 Distinguished request to ${req.url} being proxied with elegance`);
          });
        }
      },
      // WebSocket proxy for metrics - The Hamsters' domain
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err) => {
            console.log('🐌 The Meth Snail reports a WebSocket error:', err);
            console.log('🐌 Attempting to fix with quantum-grade duct tape...');
          });
        }
      }
    }
  },
  // The Stick's anxiety management settings
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // The VIC-20 suggests optimal chunking strategies
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        }
      }
    }
  }
});