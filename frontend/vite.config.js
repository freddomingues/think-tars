import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // Em dev: base '/' para abrir em http://localhost:5173/ e ver o app
  // Em build: base '/' para servir na raiz (Render)
  base: '/',
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:5004', changeOrigin: true },
    },
  },
})
