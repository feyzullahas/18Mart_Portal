const CACHE_VERSION = "v4";
const STATIC_CACHE = `portal-static-${CACHE_VERSION}`;
const RUNTIME_CACHE = `portal-runtime-${CACHE_VERSION}`;
const API_CACHE = `portal-api-${CACHE_VERSION}`;
const OFFLINE_URL = "/offline.html";

const APP_SHELL = [
  "/",
  "/index.html",
  "/manifest.json",
  "/icon-192.png",
  "/icon-512.png",
  "/favicon.png",
  "/logo.png",
  OFFLINE_URL,
];

const isApiRequest = (requestUrl, request) => {
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
  if (!response || (!response.ok && response.type !== "opaque")) return;
  const cache = await caches.open(cacheName);
  await cache.put(request, response.clone());
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

  if (request.method !== "GET") return;

  const requestUrl = new URL(request.url);
  const isNavigation = request.mode === "navigate";

  if (isNavigation) {
    event.respondWith(
      caches.match("/index.html").then((cached) => {
        const fetchPromise = fetch(request)
          .then((response) => {
            cacheResponse(RUNTIME_CACHE, "/index.html", response);
            return response;
          })
          .catch(() => undefined);

        if (cached) {
          event.waitUntil(fetchPromise);
          return cached;
        }

        return fetchPromise.then((response) => response || caches.match(OFFLINE_URL));
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
      caches.match(request).then((cached) =>
        cached ||
        fetch(request).then((response) => {
          cacheResponse(RUNTIME_CACHE, request, response);
          return response;
        })
      )
    );
    return;
  }

  event.respondWith(
    fetch(request).catch(() => caches.match(request))
  );
});
