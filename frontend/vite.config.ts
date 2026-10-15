import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [react(), tailwindcss(), VitePWA({
    strategies: 'injectManifest', srcDir: 'src', filename: 'sw.ts',
    registerType: 'prompt', injectRegister: false,
    manifest: {
      id: '/', name: 'CyberCare — Respeito também é tecnologia', short_name: 'CyberCare',
      description: 'Educação, acolhimento e prevenção ao bullying. Ambiente demonstrativo com dados fictícios.',
      lang: 'pt-BR', start_url: '/', scope: '/', display: 'standalone',
      theme_color: '#073F39', background_color: '#FFF8EF',
      icons: [
        { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
        { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
        { src: '/icons/maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
      ]
    },
    // Somente recursos estáticos. Não incluir páginas HTML da aplicação nem respostas da API.
    injectManifest: { globPatterns: ['assets/*.{js,css}', 'icons/*.png', 'logo.svg', 'offline.html'], maximumFileSizeToCacheInBytes: 2 * 1024 * 1024 },
    devOptions: { enabled: false }
  })],
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
  preview: { host: '127.0.0.1', port: 4173, proxy: { '/api': 'http://127.0.0.1:8000' } }
})
