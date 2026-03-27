import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 9501,
    host: true,
    proxy: {
      "/api": {
        target: "http://localhost:9500",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:9500",
        ws: true,
      },
    },
  },
});
