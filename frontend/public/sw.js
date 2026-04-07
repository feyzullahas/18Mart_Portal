const CACHE_VERSION = "v2";
const STATIC_CACHE = `portal-static-${CACHE_VERSION}`;
const RUNTIME_CACHE = `portal-runtime-${CACHE_VERSION}`;
const OFFLINE_URL = "/offline.html";

const PRECACHE_URLS = [
  "/",
  "/index.html",
  "/manifest.json",
  "/icon-192.png",
  "/icon-512.png",
  "/favicon.png",
  "/logo.png",
  OFFLINE_URL,
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter(
              (key) => key !== STATIC_CACHE && key !== RUNTIME_CACHE
            )
            .map((key) => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;

  if (request.method !== "GET") {
    return;
  }

  const requestUrl = new URL(request.url);
  const isSameOrigin = requestUrl.origin === self.location.origin;
  const isNavigation = request.mode === "navigate";

  if (isNavigation) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(RUNTIME_CACHE).then((cache) => cache.put(request, copy));
          return response;
        })
        .catch(async () => {
          const cachedPage = await caches.match(request);
          if (cachedPage) return cachedPage;
          return caches.match(OFFLINE_URL);
        })
    );
    return;
  }

  if (isSameOrigin) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        const networkFetch = fetch(request)
          .then((response) => {
            const copy = response.clone();
            caches.open(RUNTIME_CACHE).then((cache) => cache.put(request, copy));
            return response;
          })
          .catch(() => cachedResponse);

        return cachedResponse || networkFetch;
      })
    );
    return;
  }

  event.respondWith(fetch(request).catch(() => caches.match(request)));
});