/// <reference lib="webworker" />
import { clientsClaim } from 'workbox-core'
import { cleanupOutdatedCaches, matchPrecache, precacheAndRoute } from 'workbox-precaching'

declare let self: ServiceWorkerGlobalScope & { __WB_MANIFEST: Array<{ url: string; revision: string | null }> }

cleanupOutdatedCaches()
precacheAndRoute(self.__WB_MANIFEST)
clientsClaim()

// A atualização depende de um clique explícito: não recarregar formulários ou a tela da chave.
self.addEventListener('message', event => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting()
})

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url)
  if (url.origin !== self.location.origin || event.request.mode !== 'navigate' || url.pathname.startsWith('/api')) return
  // Nenhuma navegação é persistida. Offline mostra somente uma página educativa estática.
  event.respondWith(fetch(event.request).catch(async () =>
    (await matchPrecache('/offline.html')) || new Response('CyberCare sem conexão. Conecte-se à internet para continuar.', {
      status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' }
    })
  ))
})
