// Service Worker (static copy) for Chingola Mining Monitor PWA
// This file is served from /static/service-worker.js

const CACHE_NAME = 'chingola-mining-v2.0-static';
const RUNTIME = 'runtime-cache-v2.0-static';

const PRECACHE = [
  '/static/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.map((key) => { if (key !== CACHE_NAME && key !== RUNTIME) return caches.delete(key); })
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  if (!event.request.url.startsWith(self.location.origin)) return;

  event.respondWith(
    caches.match(event.request).then((cached) => {
      const networkFetch = fetch(event.request).then((response) => {
        if (response && response.status === 200) {
          caches.open(RUNTIME).then((cache) => cache.put(event.request, response.clone()));
        }
        return response;
      }).catch(() => cached);

      return cached || networkFetch;
    })
  );
});

self.addEventListener('push', (event) => {
  const payload = event.data ? event.data.text() : 'New mining activity detected!';
  const options = {
    body: payload,
    icon: '/static/icon-192.png',
    badge: '/static/icon-192.png'
  };
  event.waitUntil(self.registration.showNotification('Chingola Mining Monitor', options));
});
