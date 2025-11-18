import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        // When running inside Docker Compose the backend is reachable
        // by the service name `backend` on port 8000.
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
})
