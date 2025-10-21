// vite.config.ts
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  console.log('Current working directory:', process.cwd());
  console.log('Mode:', mode);

  
  const env = loadEnv(mode, process.cwd(), '')
  console.log('Loaded env vars:', Object.keys(env).filter(k => k.startsWith('VITE_')));
  console.log('VITE_WS_URL:', env.VITE_WS_URL);
  
  return {
    plugins: [
      react(),
    ],
    preview: {
      host: true,
      port: process.env.PORT ? parseInt(process.env.PORT) : 5173,
      allowedHosts: ['system-rebellion-frontend.onrender.com', 'system-rebellion-api.onrender.com'],
    },
    server: {
      port: process.env.PORT ? parseInt(process.env.PORT) : 5173,
      host: true, // Allow external connections
      hmr: {
        clientPort: 5173,
      },
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          // NO REWRITE RULE - let the full path pass through
        },
        '/ws': {
          target: env.VITE_WS_URL || 'ws://localhost:8000',
          ws: true,
          changeOrigin: true,
        },
      },
    },
  }
})