import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
  optimizeDeps: {
    exclude: ['@mediapipe/pose', '@mediapipe/camera_utils', '@mediapipe/drawing_utils']
  },
  build: {
    commonjsOptions: {
      include: [/node_modules/],
      exclude: [/@mediapipe/]
    }
  }
}) 