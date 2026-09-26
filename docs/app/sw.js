// 러너웨이 서비스 워커. 빌드마다 캐시 이름이 바뀐다(build.py가 BUILD를 채운다)
// 페이지: 네트워크 우선(새 버전이 바로 반영), 끊기면 캐시
// 음성 팩·아이콘: 캐시 우선(주소에 버전이 붙어 있어 낡을 일이 없다)
// 지도 타일·폰트 같은 외부 요청은 건드리지 않는다
const CACHE = 'rw-5c35f7bc7f';
self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(['./', 'manifest.webmanifest', 'icon-512.png'])).catch(() => { }));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('rw-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin) return;
  if (r.mode === 'navigate') {
    e.respondWith(fetch(r).then(res => { const c = res.clone(); caches.open(CACHE).then(x => x.put('./', c)); return res; })
      .catch(() => caches.match('./')));
    return;
  }
  e.respondWith(caches.match(r).then(hit => hit || fetch(r).then(res => {
    if (res.ok) { const c = res.clone(); caches.open(CACHE).then(x => x.put(r, c)); }
    return res;
  })));
});
