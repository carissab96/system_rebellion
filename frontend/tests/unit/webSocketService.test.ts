// src/__tests__/webSocketService.test.ts
describe('WebSocketService', () => {
  it('can be imported without errors', () => {
    // Just test that the module can be imported
    expect(() => {
      require('../services/websocket');
    }).not.toThrow();
  });

  it('has expected public methods', () => {
    const WebSocketService = require('../services/websocket').WebSocketService;

    // Test that the class has the expected static methods
    expect(typeof WebSocketService.getInstance).toBe('function');
  });
});
