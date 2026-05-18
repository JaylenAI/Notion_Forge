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

function revealApp() {
  const root = document.getElementById("root");
  if (root) root.style.opacity = "1";
  document.getElementById("app-loader")?.remove();
}

const MAX_WAIT = 3000;
const timeout = setTimeout(revealApp, MAX_WAIT);

document.fonts.ready.then(() => {
  clearTimeout(timeout);
  requestAnimationFrame(revealApp);
});
