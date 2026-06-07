const CACHE_VERSION = "v8";
const STATIC_CACHE = `portal-static-${CACHE_VERSION}`;
const RUNTIME_CACHE = `portal-runtime-${CACHE_VERSION}`;
const API_CACHE = `portal-api-${CACHE_VERSION}`;
const OFFLINE_URL = "/offline.html";

const APP_SHELL = [
  "/",
  "/index.html",
  "/icon-192.png",
  "/icon-512.png",
  "/favicon.png",
  "/logo.png",
  OFFLINE_URL,
];

// meal-ratings endpoint'ine ait her türlü isteği hiç dokunmadan bırak
const isMealRatingRequest = (requestUrl) => {
  return requestUrl.href.includes("meal-ratings");
};

const isApiRequest = (requestUrl, request) => {
  // cross-origin istekler: sadece anonim fetch (destination === "")
  // meal-ratings cross-origin ise zaten yukarıda filtreli
  if (requestUrl.origin !== self.location.origin) {
    return request.destination === "";
  }

  if (requestUrl.pathname.startsWith("/api")) return true;

  const accept = request.headers.get("accept") || "";
  if (accept.includes("application/json")) return true;

  return ["/meals", "/weather", "/bus", "/calendar"].some((path) =>
    requestUrl.pathname.startsWith(path)
  );
};

const shouldCacheStatic = (requestUrl, request) => {
  if (requestUrl.origin !== self.location.origin) return false;
  const destination = request.destination;
  return ["style", "script", "image", "font"].includes(destination);
};

const cacheResponse = async (cacheName, request, response) => {
  if (!response || !response.ok) return;
  // opaque response'ları (cross-origin no-cors) cache'leme — clone edilemez
  if (response.type === "opaque") return;
  try {
    const cache = await caches.open(cacheName);
    await cache.put(request, response.clone());
  } catch (e) {
    // cache yazma hatası sessizce geç
  }
};

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(APP_SHELL))
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
              (key) =>
                key !== STATIC_CACHE &&
                key !== RUNTIME_CACHE &&
                key !== API_CACHE
            )
            .map((key) => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Sadece GET isteklerini işle
  if (request.method !== "GET") return;

  const requestUrl = new URL(request.url);

  // meal-ratings endpoint'ini HİÇ dokunma — auth gerektiriyor, CORS hassas
  if (isMealRatingRequest(requestUrl)) return;

  const isNavigation = request.mode === "navigate";

  if (isNavigation) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          cacheResponse(RUNTIME_CACHE, request, response);
          return response;
        })
        .catch(() => {
          return caches
            .match("/index.html")
            .then((cached) => cached || caches.match(OFFLINE_URL));
        })
    );
    return;
  }

  if (isApiRequest(requestUrl, request)) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          cacheResponse(API_CACHE, request, response);
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  if (shouldCacheStatic(requestUrl, request)) {
    event.respondWith(
      caches.match(request).then(
        (cached) =>
          cached ||
          fetch(request).then((response) => {
            cacheResponse(RUNTIME_CACHE, request, response);
            return response;
          })
      )
    );
    return;
  }

  event.respondWith(fetch(request).catch(() => caches.match(request)));
});
