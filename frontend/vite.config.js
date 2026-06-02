import { defineConfig } from 'vite'

// Proxy /api requests to the backend running on port 8000 during development
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
