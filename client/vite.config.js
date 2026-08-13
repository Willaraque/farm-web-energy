import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/auth": "http://127.0.0.1:8000",
      "/token": "http://127.0.0.1:8000",
      "/verify-token": "http://127.0.0.1:8000",
      "/delete-token": "http://127.0.0.1:8000",
      "/users": "http://127.0.0.1:8000",
      "/market-data": "http://127.0.0.1:8000",
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
});
