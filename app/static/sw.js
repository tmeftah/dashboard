// the cache version gets updated every time there is a new deployment
const CACHE_VERSION = 12;
const CURRENT_CACHE = `main-${CACHE_VERSION}`;

var cacheFiles = [
  "/static/manifest.json",
  "/static/style.css",
  "/static/login.css",
  "/static/icon-512x512.png",
  "/static/particles-7193862_960_720.webp",
  "/static/offline.jpeg",
  "/static/wellcome.png",
  "/offline",
];

// on activation we clean up the previously registered service workers
self.addEventListener("activate", (evt) =>
  evt.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CURRENT_CACHE) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  )
);

// on install we download the routes we want to cache for offline
self.addEventListener("install", (evt) =>
  evt.waitUntil(
    caches.open(CURRENT_CACHE).then((cache) => {
      return cache.addAll(cacheFiles);
    })
  )
);

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches
      .match(event.request)
      .then((response) => response || fetch(event.request))
      .catch(() => {
        if (event.request.mode == "navigate") {
          console.log("hhh");
          return caches.match("/offline");
        }
      })
  );
});
