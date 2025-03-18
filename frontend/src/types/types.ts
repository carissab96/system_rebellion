



  export interface UserProfile {
    id: string;
    username: string;
    operating_system: 'linux' | 'windows' | 'macos';
    os_version: string;
    linux_distro?: string;
    linux_distro_version?: string;
    cpu_cores?: number;
    total_memory?: number;
  }
  
  export interface UserPreferences {
    theme: 'light' | 'dark' | 'system';
    language: string;
  }


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