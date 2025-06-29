import './styles/index.css';

import React from 'react';

import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';

import App from './App.tsx';
import { initWebSocket } from './services/websocket/webSocketService';
import store from './store/store.ts';

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