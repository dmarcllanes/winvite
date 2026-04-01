// Service Worker — Winvite PWA
const CACHE = 'winvite-v1';
const PRECACHE = [
    '/',
    '/static/manifest.json',
    '/static/icon.svg',
    '/static/icon-maskable.svg',
];

// Install: pre-cache shell assets
self.addEventListener('install', function(e) {
    e.waitUntil(
        caches.open(CACHE).then(function(cache) {
            return cache.addAll(PRECACHE);
        })
    );
    self.skipWaiting();
});

// Activate: clean up old caches
self.addEventListener('activate', function(e) {
    e.waitUntil(
        caches.keys().then(function(keys) {
            return Promise.all(
                keys.filter(function(k) { return k !== CACHE; })
                    .map(function(k) { return caches.delete(k); })
            );
        })
    );
    self.clients.claim();
});

// Fetch: network-first for HTML/API, cache-first for static assets
self.addEventListener('fetch', function(e) {
    var url = new URL(e.request.url);

    // Static assets → cache first, then network
    if (url.pathname.startsWith('/static/')) {
        e.respondWith(
            caches.match(e.request).then(function(cached) {
                return cached || fetch(e.request).then(function(res) {
                    var clone = res.clone();
                    caches.open(CACHE).then(function(c) { c.put(e.request, clone); });
                    return res;
                });
            })
        );
        return;
    }

    // HTML pages → network first, fallback to cache
    e.respondWith(
        fetch(e.request).then(function(res) {
            var clone = res.clone();
            caches.open(CACHE).then(function(c) { c.put(e.request, clone); });
            return res;
        }).catch(function() {
            return caches.match(e.request);
        })
    );
});
