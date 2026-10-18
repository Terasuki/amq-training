import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Mostly Recharts; the bundle is only ever served from localhost.
    chunkSizeWarningLimit: 1000,
  },
  server: {
    // The API is served by Flask: run `python app.py` in the repo root.
    proxy: { '/api': 'http://127.0.0.1:8888' },
  },
})
