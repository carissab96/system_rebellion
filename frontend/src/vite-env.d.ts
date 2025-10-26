/// <reference types="vite/client" />

interface ImportMetaEnv {
  VITE_API_URL: string;
  VITE_WS_URL: string;
  VITE_WS_RECONNECT_INTERVAL: number;
  VITE_WS_MAX_RECONNECT_ATTEMPTS: number;
}

interface ImportMeta {
  env: ImportMetaEnv;
}

declare global {
  var __DEV__: boolean;
}
