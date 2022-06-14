var cacheName = "main_cache_v3";
var filesToCache = [
  "/",
  "./static/manifest.json",
  "./static/app.js",
  "./static/style.css",
  "./static/login.css",
  "./static/icon-512x512.png",
  "./static/particles-7193862_960_720.webp",
  "./static/meinAvatar.png",
];

/* Start the service worker and cache all of the app's content */
self.addEventListener("install", (e) => {
  console.log("[Service Worker] Install");
  e.waitUntil(
    (async () => {
      const cache = await caches.open(cacheName);
      console.log("[Service Worker] Caching all: app shell and content");
      await cache.addAll(filesToCache);
      console.log("[Service Worker] Caching terminated");
    })()
  );
}); //

/* Serve cached content when offline */
self.addEventListener("fetch", function (e) {
  e.respondWith(
    caches.match(e.request).then(function (response) {
      return response || fetch(e.request);
    })
  );
});

///

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys.map((key) => {
            if (!cacheName.includes(key)) {
              return caches.delete(key);
            }
          })
        )
      )
      .then(() => {
        console.log("New cache ready to handle fetches!");
      })
  );
});
