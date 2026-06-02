import { defineConfig } from 'vite'

// Detectar se está em Docker ou localhost
const API_TARGET = process.env.VITE_API_URL 
  ? process.env.VITE_API_URL.replace('http://', 'http://').replace('https://', 'https://')
  : 'http://localhost:8000'

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
