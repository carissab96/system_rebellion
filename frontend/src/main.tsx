import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import { store } from "./store/store";
import App from "./App";
import { GlobalErrorBoundary } from "./components/GlobalErrorBoundary";
import "./index.css";
import { WebSocketService } from "./services/websocket";

// Initialize WebSocket services when a URL is provided
const websocketUrl = import.meta.env.VITE_WS_URL;
console.log('WS URL:', import.meta.env.VITE_WS_URL);
console.log('All env:', import.meta.env);
if (websocketUrl) {
  // Initialize metrics WebSocket
  WebSocketService.getInstance(websocketUrl);
  console.log('✅ Metrics WebSocket service initialized');
} else {
  // eslint-disable-next-line no-console
  console.warn("VITE_WS_URL is not defined; skipping WebSocket initialization.");
}

if (typeof window !== 'undefined') {
  (window as any).store = store;
}

const container = document.getElementById("root");
if (!container) {
  // eslint-disable-next-line no-console
  console.error("No #root element found in index.html");
  throw new Error("Missing #root");
}

ReactDOM.createRoot(container).render(
  <React.StrictMode>
    <GlobalErrorBoundary>
      <Provider store={store}>
        <App />
      </Provider>
    </GlobalErrorBoundary>
  </React.StrictMode>
);
