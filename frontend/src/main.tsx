import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

/* Clean up stale panel data from previous library */
try {
  Object.keys(localStorage).forEach((key) => {
    if (key.startsWith("react-resizable-panels:")) {
      localStorage.removeItem(key);
    }
  });
} catch { /* ignore */ }

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
