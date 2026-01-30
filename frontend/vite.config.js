import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // Em dev: base '/' para abrir em http://localhost:5173/ e ver o app
  // Em build: base '/demos/' para Flask servir em /demos
  base: process.env.NODE_ENV === 'production' ? '/demos/' : '/',
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:5004', changeOrigin: true },
    },
  },
})
