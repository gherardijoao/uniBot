import { defineConfig } from 'vite'

// Proxy /api requests to the backend running on port 8000 during development
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
