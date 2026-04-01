import { Toaster } from "react-hot-toast";

function ToastProvider() {
  return (
    <Toaster
      position="bottom-center"
      toastOptions={{
        duration: 3000,
        style: {
          background: "var(--toast-bg, #2a2a2a)",
          color: "var(--toast-color, #e5e2e1)",
          borderRadius: "12px",
          fontSize: "13px",
          fontFamily: "'Inter', sans-serif",
          border: "1px solid var(--toast-border, #424656)",
          padding: "12px 16px",
          boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
        },
        success: {
          iconTheme: { primary: "#4edea3", secondary: "#003824" },
        },
        error: {
          iconTheme: { primary: "#ffb4ab", secondary: "#690005" },
        },
      }}
    />
  );
}

export default ToastProvider;
