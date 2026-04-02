// Service Worker — Winvite PWA
const CACHE = 'winvite-v3';
const PRECACHE = [
    '/',
    '/static/manifest.json',
    '/static/invite.css',
    '/static/icon.svg',
    '/static/icon-192.png',
    '/static/icon-512.png',
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

// Fetch strategy:
//   /static/*      → cache-first, update in background
//   /invite/*      → network-first, cache on success for offline fallback
//   everything else → network-first, fallback to cache
self.addEventListener('fetch', function(e) {
    if (e.request.method !== 'GET') return;
    var url = new URL(e.request.url);

    // Static assets — cache first, revalidate in background (stale-while-revalidate)
    if (url.pathname.startsWith('/static/')) {
        e.respondWith(
            caches.open(CACHE).then(function(cache) {
                return cache.match(e.request).then(function(cached) {
                    var fetchPromise = fetch(e.request).then(function(res) {
                        if (res.ok) cache.put(e.request, res.clone());
                        return res;
                    });
                    return cached || fetchPromise;
                });
            })
        );
        return;
    }

    // Invite pages — network first, cache on success so guests can view offline
    if (url.pathname.startsWith('/invite/')) {
        e.respondWith(
            fetch(e.request).then(function(res) {
                if (res.ok) {
                    var clone = res.clone();
                    caches.open(CACHE).then(function(c) { c.put(e.request, clone); });
                }
                return res;
            }).catch(function() {
                return caches.match(e.request).then(function(cached) {
                    return cached || caches.match('/');
                });
            })
        );
        return;
    }

    // Everything else — network first, fallback to cache
    e.respondWith(
        fetch(e.request).then(function(res) {
            if (res.ok) {
                var clone = res.clone();
                caches.open(CACHE).then(function(c) { c.put(e.request, clone); });
            }
            return res;
        }).catch(function() {
            return caches.match(e.request);
        })
    );
});
