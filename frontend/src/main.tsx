import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import { store } from "./store/store";
import App from "./App";

const container = document.getElementById("root");
if (!container) {
  // eslint-disable-next-line no-console
  console.error("No #root element found in index.html");
  throw new Error("Missing #root");
}

ReactDOM.createRoot(container).render(
  <React.StrictMode>
    <Provider store={store}>
          <App />
    </Provider>
  </React.StrictMode>
);
