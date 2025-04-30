





    export interface Options {
      method?: string;
      headers?: Record<string, string>;
      body?: any;
      credentials?: RequestCredentials;
    }
    import { PayloadAction } from '@reduxjs/toolkit';

export interface AuthAction extends PayloadAction{
    headers?: Record<string, string>;
    body?: any;
    credentials?: RequestCredentials;
}

// types/types.ts
export interface Options extends RequestInit {
  headers?: Record<string, string>;
  credentials?: RequestCredentials;
}