import '@testing-library/jest-dom';

// Mock WebSocket
class MockWebSocket {
  onopen: (() => void) | null = null;
  onmessage: ((event: any) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: ((error: any) => void) | null = null;
  
  constructor(_url: string) {
    setTimeout(() => this.onopen?.(), 0);
  }
  
  send(_data: string) {}
  close() {}
}

global.WebSocket = MockWebSocket as any;
