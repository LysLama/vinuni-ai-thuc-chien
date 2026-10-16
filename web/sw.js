const CACHE_NAME = "vinuni-ai-exam-v2.5";
const PRECACHE_ASSETS = [
  "./",
  "./index.html",
  "./styles.css",
  "./app_v3.js",
  "./app.js",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./data/questions-data.js",
  "./docs/docs-data.js",
  "./data/module_a_toan_dinh_luong.json",
  "./data/module_b_lap_trinh_du_lieu.json",
  "./data/module_c_kien_thuc_san_pham_ai.json",
  "./data/module_d_logic_dao_duc_hanh_vi.json",
  "./vendor/katex/katex.min.css",
  "./vendor/katex/katex.min.js",
  "./vendor/katex/auto-render.min.js",
  "./vendor/katex/fonts/KaTeX_Main-Regular.woff2",
  "./vendor/katex/fonts/KaTeX_Math-Italic.woff2",
  "./vendor/katex/fonts/KaTeX_Size1-Regular.woff2",
  "./vendor/katex/fonts/KaTeX_Size2-Regular.woff2",
  "./vendor/prism/prism-tomorrow.min.css",
  "./vendor/prism/prism.min.js",
  "./vendor/prism/prism-python.min.js",
  "./vendor/prism/prism-sql.min.js",
  "./vendor/marked/marked.min.js",
  "./vendor/marked/marked-katex-extension.umd.js",
  "./vendor/lucide/lucide.min.js"
];

// Install Event - Precache core static assets
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(PRECACHE_ASSETS).catch(err => {
        console.warn("Pre-cache asset warning:", err);
      });
    }).then(() => self.skipWaiting())
  );
});

// Activate Event - Clean up stale old caches
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event - Stale-While-Revalidate & Cache-First with Network Fallback
self.addEventListener("fetch", event => {
  // Only handle GET requests
  if (event.request.method !== "GET") return;

  const url = new URL(event.request.url);

  // For data and static assets, use Cache First with Background Update
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const fetchPromise = fetch(event.request)
        .then(networkResponse => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          // If network offline and not in cache, fallback
          return cachedResponse;
        });

      return cachedResponse || fetchPromise;
    })
  );
});
