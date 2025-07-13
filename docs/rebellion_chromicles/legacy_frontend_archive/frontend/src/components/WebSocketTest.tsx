import React, { useState, useEffect } from 'react';
import { getWebSocketInstance, initWebSocket } from '../services/websocket/webSocketService';

const WebSocketTest: React.FC = () => {
  const [connectionStatus, setConnectionStatus] = useState<string>('disconnected');
  const [messages, setMessages] = useState<string[]>([]);
  const [wsInstance, setWsInstance] = useState<any>(null);

  useEffect(() => {
    // Initialize WebSocket
    const ws = initWebSocket(null);
    setWsInstance(ws);

    // Set up connection status listener
    ws.onConnectionStatusChange = (status: string) => {
      setConnectionStatus(status);
      addMessage(`Connection status changed to: ${status}`);
    };

    // Set up message listener
    ws.onMessage = (message: any) => {
      addMessage(`Received: ${JSON.stringify(message)}`);
    };

    return () => {
      ws.disconnect();
    };
  }, []);

  const addMessage = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setMessages(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const handleConnect = async () => {
    if (wsInstance) {
      try {
        addMessage('Attempting to connect...');
        await wsInstance.connect();
        addMessage('Connect method completed');
      } catch (error) {
        addMessage(`Connect error: ${error}`);
      }
    }
  };

  const handleDisconnect = () => {
    if (wsInstance) {
      wsInstance.disconnect();
      addMessage('Disconnect requested');
    }
  };

  const handleResetCircuitBreaker = () => {
    if (wsInstance) {
      wsInstance.resetCircuitBreaker();
      addMessage('Circuit breaker reset');
    }
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h2>WebSocket Connection Test</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <strong>Status: </strong>
        <span style={{ 
          color: connectionStatus === 'connected' ? 'green' : 
                connectionStatus === 'connecting' ? 'orange' : 'red' 
        }}>
          {connectionStatus}
        </span>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <button onClick={handleConnect} style={{ marginRight: '10px' }}>
          Connect
        </button>
        <button onClick={handleDisconnect} style={{ marginRight: '10px' }}>
          Disconnect
        </button>
        <button onClick={handleResetCircuitBreaker} style={{ marginRight: '10px' }}>
          Reset Circuit Breaker
        </button>
        <button onClick={clearMessages}>
          Clear Messages
        </button>
      </div>

      <div style={{ 
        border: '1px solid #ccc', 
        padding: '10px', 
        height: '400px', 
        overflowY: 'scroll',
        backgroundColor: '#f9f9f9'
      }}>
        <h3>Messages:</h3>
        {messages.map((message, index) => (
          <div key={index} style={{ marginBottom: '5px', fontSize: '12px' }}>
            {message}
          </div>
        ))}
      </div>
    </div>
  );
};

export default WebSocketTest;
