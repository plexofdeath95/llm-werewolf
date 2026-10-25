import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Backend (FastAPI) runs on :8000; /api includes the game WebSocket.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': { target: 'http://127.0.0.1:8000', ws: true, changeOrigin: true } },
  },
  build: { chunkSizeWarningLimit: 2500 },
})
