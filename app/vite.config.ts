import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/hit': 'http://localhost:5000',
      '/stand': 'http://localhost:5000',
      '/bet': 'http://localhost:5000',
      '/start': 'http://localhost:5000',
      '/next_round': 'http://localhost:5000',
    },
  },
});