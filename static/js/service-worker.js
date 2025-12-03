/**
 * AgriBot Service Worker
 * Handles offline caching and PWA functionality
 */

const CACHE_VERSION = 'agribot-v1';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const KNOWLEDGE_CACHE = `${CACHE_VERSION}-knowledge`;

// Static assets to cache on install
const STATIC_ASSETS = [
    '/',
    '/chatbot',
    '/static/css/chatbot.css',
    '/static/js/chatbot-enhanced.js',
    '/static/css/auth.css',
    '/static/images/logo.png',
    '/static/images/bot-avatar.png',
    '/static/images/user-avatar.png',
    '/offline.html'
];

// Knowledge base endpoints to cache
const KNOWLEDGE_ENDPOINTS = [
    '/api/crops',
    '/api/diseases',
    '/api/best-practices'
];

// Maximum cache sizes
const MAX_DYNAMIC_CACHE_SIZE = 50;
const MAX_KNOWLEDGE_CACHE_SIZE = 100;

/**
 * Install event - cache static assets
 */
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing...');

    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('[Service Worker] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('[Service Worker] Skip waiting');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('[Service Worker] Installation failed:', error);
            })
    );
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating...');

    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames
                        .filter(cacheName => {
                            return cacheName.startsWith('agribot-') &&
                                   cacheName !== STATIC_CACHE &&
                                   cacheName !== DYNAMIC_CACHE &&
                                   cacheName !== KNOWLEDGE_CACHE;
                        })
                        .map(cacheName => {
                            console.log('[Service Worker] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        })
                );
            })
            .then(() => {
                console.log('[Service Worker] Claiming clients');
                return self.clients.claim();
            })
    );
});

/**
 * Fetch event - implement caching strategies
 */
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Handle different types of requests with appropriate strategies
    if (isStaticAsset(url)) {
        // Cache-first strategy for static assets
        event.respondWith(cacheFirst(request, STATIC_CACHE));
    } else if (isKnowledgeEndpoint(url)) {
        // Network-first with long cache fallback for knowledge base
        event.respondWith(networkFirstLongCache(request, KNOWLEDGE_CACHE));
    } else if (isAPIRequest(url)) {
        // Network-first with short cache fallback for API requests
        event.respondWith(networkFirst(request, DYNAMIC_CACHE));
    } else {
        // Network-first for everything else
        event.respondWith(networkFirst(request, DYNAMIC_CACHE));
    }
});

/**
 * Message event - handle commands from clients
 */
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }

    if (event.data && event.data.type === 'CACHE_KNOWLEDGE') {
        event.waitUntil(cacheKnowledgeBase());
    }

    if (event.data && event.data.type === 'CLEAR_CACHE') {
        event.waitUntil(clearAllCaches());
    }
});

/**
 * Cache-first strategy: Check cache, fallback to network
 */
async function cacheFirst(request, cacheName) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.error('[Service Worker] Cache-first strategy failed:', error);
        return await caches.match('/offline.html') || new Response('Offline');
    }
}

/**
 * Network-first strategy: Try network, fallback to cache
 */
async function networkFirst(request, cacheName) {
    try {
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
            trimCache(cacheName, MAX_DYNAMIC_CACHE_SIZE);
        }

        return networkResponse;
    } catch (error) {
        console.log('[Service Worker] Network failed, checking cache:', request.url);
        const cachedResponse = await caches.match(request);

        if (cachedResponse) {
            return cachedResponse;
        }

        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return await caches.match('/offline.html') || new Response('Offline');
        }

        return new Response('Offline', { status: 503 });
    }
}

/**
 * Network-first with long cache: For knowledge base data
 */
async function networkFirstLongCache(request, cacheName) {
    try {
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
            trimCache(cacheName, MAX_KNOWLEDGE_CACHE_SIZE);
        }

        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);

        if (cachedResponse) {
            console.log('[Service Worker] Using cached knowledge:', request.url);
            return cachedResponse;
        }

        return new Response(JSON.stringify({
            offline: true,
            message: 'This data is not available offline'
        }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Check if request is for a static asset
 */
function isStaticAsset(url) {
    return url.pathname.startsWith('/static/') ||
           url.pathname.endsWith('.css') ||
           url.pathname.endsWith('.js') ||
           url.pathname.endsWith('.png') ||
           url.pathname.endsWith('.jpg') ||
           url.pathname.endsWith('.svg') ||
           url.pathname.endsWith('.woff') ||
           url.pathname.endsWith('.woff2');
}

/**
 * Check if request is for knowledge base endpoint
 */
function isKnowledgeEndpoint(url) {
    return KNOWLEDGE_ENDPOINTS.some(endpoint => url.pathname.startsWith(endpoint));
}

/**
 * Check if request is an API request
 */
function isAPIRequest(url) {
    return url.pathname.startsWith('/api/');
}

/**
 * Trim cache to maximum size
 */
async function trimCache(cacheName, maxItems) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();

    if (keys.length > maxItems) {
        const keysToDelete = keys.slice(0, keys.length - maxItems);
        await Promise.all(keysToDelete.map(key => cache.delete(key)));
    }
}

/**
 * Cache knowledge base data proactively
 */
async function cacheKnowledgeBase() {
    const cache = await caches.open(KNOWLEDGE_CACHE);

    try {
        await Promise.all(
            KNOWLEDGE_ENDPOINTS.map(endpoint => {
                return fetch(endpoint)
                    .then(response => {
                        if (response.ok) {
                            return cache.put(endpoint, response);
                        }
                    })
                    .catch(error => {
                        console.warn('[Service Worker] Failed to cache:', endpoint, error);
                    });
            })
        );
        console.log('[Service Worker] Knowledge base cached');
    } catch (error) {
        console.error('[Service Worker] Failed to cache knowledge base:', error);
    }
}

/**
 * Clear all caches
 */
async function clearAllCaches() {
    const cacheNames = await caches.keys();
    await Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
    );
    console.log('[Service Worker] All caches cleared');
}

/**
 * Sync event - handle background sync
 */
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-messages') {
        event.waitUntil(syncQueuedMessages());
    }
});

/**
 * Sync queued messages when connection restored
 */
async function syncQueuedMessages() {
    try {
        // This will be implemented with IndexedDB
        console.log('[Service Worker] Syncing queued messages...');

        // Get queued messages from IndexedDB
        const db = await openIndexedDB();
        const messages = await getQueuedMessages(db);

        // Send each message
        for (const message of messages) {
            try {
                const response = await fetch('/api/chatbot/message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(message)
                });

                if (response.ok) {
                    await removeQueuedMessage(db, message.id);
                }
            } catch (error) {
                console.error('[Service Worker] Failed to sync message:', error);
            }
        }

        console.log('[Service Worker] Message sync complete');
    } catch (error) {
        console.error('[Service Worker] Sync failed:', error);
    }
}

/**
 * IndexedDB helpers (placeholders for now)
 */
async function openIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('AgribotDB', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            if (!db.objectStoreNames.contains('messageQueue')) {
                db.createObjectStore('messageQueue', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

async function getQueuedMessages(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['messageQueue'], 'readonly');
        const store = transaction.objectStore('messageQueue');
        const request = store.getAll();

        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function removeQueuedMessage(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['messageQueue'], 'readwrite');
        const store = transaction.objectStore('messageQueue');
        const request = store.delete(id);

        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}
