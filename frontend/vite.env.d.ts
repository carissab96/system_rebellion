/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_URL: string
    readonly VITE_WS_URL: string
    readonly VITE_APP_NAME: string
    // add other VITE_ prefixed env vars as needed
  }
  
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }