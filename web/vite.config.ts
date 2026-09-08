import path from 'node:path'

import tailwindcss from '@tailwindcss/vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [
    tanstackRouter({
      target: 'react',
      autoCodeSplitting: true,
    }),
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_DEV_PROXY_TARGET ?? 'http://localhost:11112',
        changeOrigin: true,
      },
      '/health': {
        target: process.env.VITE_DEV_PROXY_TARGET ?? 'http://localhost:11112',
        changeOrigin: true,
      },
    },
  },
})
