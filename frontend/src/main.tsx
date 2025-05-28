import React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import store from './store/store.ts';
import App from './App';
import './index.css';
import { initWebSocket } from './services/websocket/WebSocketService';

// Initialize WebSocket connection when the app loads
initWebSocket(store.dispatch);

const root = createRoot(document.getElementById('root')!);

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);