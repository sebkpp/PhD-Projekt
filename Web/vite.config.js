import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
      react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      '/players': 'http://localhost:5000',
      '/join': 'http://localhost:5000',
      '/leave': 'http://localhost:5000',
      '/heartbeat': 'http://localhost:5000',
      // weitere Endpunkte nach Bedarf
    }
  }
})
