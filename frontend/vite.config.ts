// vite.config.ts
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
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