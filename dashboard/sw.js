// Kuro OS Service Worker (PWA)
const CACHE_NAME = "kuro-os-v6";

self.addEventListener("install", (e) => {
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(keys.map((k) => caches.delete(k)));
    })
  );
  self.clients.claim();
});

// Network-first: Luôn lấy từ máy chủ, chỉ fallback sang cache khi mất mạng hoàn toàn
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET" || e.request.url.includes("/api/") || e.request.url.includes("/ws")) {
    return;
  }
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        // Cập nhật ngầm vào cache
        if (res.status === 200) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(e.request, clone));
        }
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
