// 출시 전 헤드리스 QA. docs/app/을 로컬로 띄워 실제 크롬에서 끝까지 돌린다
// 실행: NODE_PATH=$(npm root -g) node web/qa.mjs   (playwright 필요)
// 확인: 스크립트 오류 0, 음성 팩 전 조각 디코드, 실내 데모 완주, 구운 음성 재생(브라우저 TTS 미사용), 관제 음성 기본 끔,
//       실제 동물 녹음(가짜 파일로 경로 확인), 입체 음향 실측(좌우 귀 차이, 거리별 크기와 잔향),
//       지도 끌기·복귀, 결과 화면, 음성 팩이 없을 때 브라우저 TTS로 대체,
//       아이폰 에뮬레이션(무음 스위치 대응, 나침반 권한·방위, 캔버스 filter 없는 사파리에서 지도 어둡게)
import { createRequire } from 'node:module';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const ROOT = path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'docs', 'app');
const SHOTS = process.env.QA_SHOTS || '';

const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.png': 'image/png', '.bin': 'application/octet-stream', '.webmanifest': 'application/manifest+json' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (p.endsWith('/')) p += 'index.html';
  const f = path.join(ROOT, p);
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const BASE = `http://127.0.0.1:${server.address().port}/`;

/** 흰색 256×256 PNG. 지도 타일 대역. 흰 타일이 어둡게 그려지면 다크 지도 처리가 동작한 것이다 */
function whitePng() {
  const chunk = (t, d) => { const b = Buffer.alloc(12 + d.length); b.writeUInt32BE(d.length, 0); b.write(t, 4, 'ascii'); d.copy(b, 8); b.writeUInt32BE(zlib.crc32(Buffer.concat([Buffer.from(t, 'ascii'), d])) >>> 0, 8 + d.length); return b; };
  const ih = Buffer.alloc(13); ih.writeUInt32BE(256, 0); ih.writeUInt32BE(256, 4); ih[8] = 8; ih[9] = 2;
  const raw = Buffer.alloc(256 * (1 + 256 * 3), 255); for (let y = 0; y < 256; y++) raw[y * (1 + 256 * 3)] = 0;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ih), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
}
const WHITE = whitePng();
const tiles = (page) => page.route('**/tile.openstreetmap.org/**', r => r.fulfill({ status: 200, contentType: 'image/png', headers: { 'Access-Control-Allow-Origin': '*' }, body: WHITE }));
/** 레이더 캔버스 평균 밝기 0~255 */
const radarLum = (page) => page.evaluate(() => { const c = document.querySelector('#radar'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let s = 0, n = 0; for (let i = 0; i < d.length; i += 28) { s += (d[i] + d[i + 1] + d[i + 2]) / 3; n++; } return s / n; });

let fails = 0;
const check = (ok, msg) => { console.log((ok ? 'OK   ' : 'FAIL ') + msg); if (!ok) fails++; };

const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });

/** 소리 계측: 디코드 수, 재생된 버퍼 길이, 브라우저 TTS 호출 */
const PROBE = () => {
  window.__qa = { decodes: 0, starts: [], tts: [] };
  const AC = window.AudioContext || window.webkitAudioContext;
  const dec = AC.prototype.decodeAudioData;
  AC.prototype.decodeAudioData = function (...a) { window.__qa.decodes++; return dec.apply(this, a); };
  const st = AudioBufferSourceNode.prototype.start;
  AudioBufferSourceNode.prototype.start = function (...a) { if (this.buffer) window.__qa.starts.push(+this.buffer.duration.toFixed(2)); return st.apply(this, a); };
  if (window.speechSynthesis) { const sp = speechSynthesis.speak.bind(speechSynthesis); speechSynthesis.speak = (u) => { window.__qa.tts.push(u.text); return sp(u); }; }
};

async function run(opts) {
  const ctx = await browser.newContext({ viewport: { width: 400, height: 860 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error' && !/tile\.openstreetmap|fonts\.g|ERR_|Failed to load resource/.test(m.text())) errors.push(m.text()); });
  const reqs = [];
  page.on('request', r => reqs.push(r.url()));
  await page.addInitScript(PROBE);
  if (opts.blockVoice) await page.route('**/voice/**', r => r.abort());
  await page.route('**/tile.openstreetmap.org/**', r => r.abort());   // 외부 타일은 QA 대상 아님
  await page.goto(BASE);
  return { ctx, page, errors, reqs };
}

// 1. 음성 팩 무결성: 모든 조각이 크롬에서 디코드되는가
{
  const { ctx, page, errors } = await run({});
  const r = await page.evaluate(async () => {
    const P = VOICE_PACK, ac = new OfflineAudioContext(1, 48000, 48000);
    const out = { op: 0, opBad: [], an: 0, anBad: [], opSec: 0, anSec: 0 };
    const load = async (f) => new Uint8Array(await (await fetch('voice/' + f + '?v=' + P.ver)).arrayBuffer());
    const op = await load('op.bin');
    for (const [k, [o, l]] of Object.entries(P.op)) {
      try { const b = await ac.decodeAudioData(op.slice(o, o + l).buffer); out.op++; out.opSec += b.duration; if (b.duration < 0.15) out.opBad.push(k); } catch (e) { out.opBad.push(k); }
    }
    return out;
  });
  // 실제 동물 녹음: 목록의 모든 파일이 크롬에서 디코드되는가
  const sr = await page.evaluate(async () => {
    const ac = new OfflineAudioContext(1, 48000, 48000), bad = []; let n = 0;
    for (const fs of Object.values(SOUND_INDEX)) for (const f of fs) {
      try { const b = await (await fetch('sounds/' + f + '?v=' + SOUND_VER)).arrayBuffer(); const a = await ac.decodeAudioData(b); if (a.duration < 0.2) bad.push(f); n++; } catch (e) { bad.push(f); }
    }
    return { n, bad };
  });
  check(sr.bad.length === 0 && sr.n > 0, `동물 녹음 ${sr.n}개 디코드, 불량 ${sr.bad.join(',') || 0}`);
  check(r.opBad.length === 0 && r.op >= 400, `관제 음성 ${r.op}조각 디코드 (${r.opSec.toFixed(0)}초) 불량 ${r.opBad.join(',') || 0}`);
  // 대사에서 쓰는 키가 전부 팩에 있는가 (조각 누락 = 그 문장만 기계음으로 빠진다)
  const miss = await page.evaluate(() => {
    const need = ['intro_head', 'intro_hide', 'intro_top', 'intro_kmh', 'intro_tail', 'intro_now', 'warn60', 'warn15', 'spotted', 'sisok', 'hold', 'again', 'stick', 'meter',
      'hit1', 'hit2', 'hit3', 'tired1', 'tired2', 'tired3', 'tired4', 'tired5', 'recover1', 'recover2', 'lost', 'half1', 'half2', 'cool', 'end_fail', 'end_arrive',
      'end_hits0', 'end_hits1', 'end_hits2', 'end_final', 'unit_min', 'unit_sec', 'end_stop', 'wait', 'wait_coarse', 'pocket', 'test_tail', 'zero', 'cnt1', 'cnt2', 'cnt3', 'cnt5'];
    for (const d of ['front', 'back', 'lf', 'rf', 'l', 'r', 'lb', 'rb']) need.push('dc_' + d, 'dx_' + d, 'dr_' + d);
    for (let n = 1; n < 100; n++) need.push('n' + n); for (let h = 1; h < 10; h++) need.push('n' + h * 100);
    for (let n = 1; n <= 120; n++) need.push('kmh' + n);
    for (let n = 1; n < 50; n++) need.push('m' + n); for (let n = 50; n <= 300; n += 10) need.push('m' + n);
    need.push('intro_max');
    for (const a of ANIMALS) need.push('name_' + a.id);
    const m = need.filter(k => !VOICE_PACK.op[k]);
    return m;
  });
  check(miss.length === 0, `대사 키 누락 ${miss.length ? miss.join(',') : '없음'}`);
  check(errors.length === 0, `로드 오류 ${errors.join(' | ') || '없음'}`);
  await page.click('#openSet');
  check(!(await page.locator('#iosAudioBox').isVisible()), '아이폰 아닌 기기: 아이폰 소리 설정 숨김');
  await ctx.close();
}

// 1b. 기본값: 관제 음성 끔. 음성 팩(2.8MB)도 안 받고, 말도 안 한다
{
  const { ctx, page, errors, reqs } = await run({});
  await page.waitForTimeout(1500);
  await page.click('#openSet');
  const on = await page.evaluate(() => document.querySelector('#voice button.on').dataset.v);
  await page.click('#mode button[data-v="replay"]');
  await page.click('#warmup button[data-v="0"]');
  await page.click('#start');
  await page.waitForTimeout(6000);
  await page.click('#stop'); await page.waitForSelector('#result.on');
  const log = await page.locator('#rLog').textContent(), q = await page.evaluate(() => window.__qa);
  check(on === 'off', `관제 음성 기본값 ${on}`);
  check(!reqs.some(u => u.includes('voice/op.bin')), '관제 음성 끔: 음성 팩 안 받음');
  check(!log.includes('말: ') && q.tts.length === 0, `관제 음성 끔: 말 없음 (로그 ${log.split('\n').filter(l => l.includes('말: ')).length}, 기계음 ${q.tts.length})`);
  check(errors.length === 0, `기본값 주행 오류 ${errors.join(' | ') || '없음'}`);
  await ctx.close();
}

// 2. 실내 데모 완주 + 구운 음성 + 지도 끌기
{
  const { ctx, page, errors, reqs } = await run({});
  await page.click('#openSet');
  await page.click('#voice button[data-v="normal"]');   // 관제 음성은 기본 끔. 음성 경로를 보려면 켠다
  await page.click('#mode button[data-v="replay"]');
  await page.click('#warmup button[data-v="0"]');     // 워밍업 없이 바로 쫓기게. 스프린트·피격 대사를 빨리 본다
  await page.click('#start');
  await page.waitForTimeout(2500);
  if (SHOTS) await page.screenshot({ path: SHOTS + '/run.png' });
  // 지도 끌기
  const box = await page.locator('#radar').boundingBox();
  const px = async () => page.evaluate(() => { const c = document.querySelector('#radar'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let h = 0; for (let i = 0; i < d.length; i += 97) h = (h * 31 + d[i]) >>> 0; return h; });
  const before = await page.locator('#recenter').isVisible();
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.down();
  for (let i = 1; i <= 10; i++) await page.mouse.move(box.x + box.width / 2 + i * 12, box.y + box.height / 2 + i * 8);
  await page.mouse.up();
  await page.waitForTimeout(150);
  const after = await page.locator('#recenter').isVisible();
  check(!before && after, `지도 끌기 → '내 위치로' 버튼 표시 (${before} → ${after})`);
  // 끌린 상태에서 내 위치 화살표가 중심을 벗어났는가 (중심 픽셀이 초록 화살표가 아니어야 한다)
  const centerGreen = async () => page.evaluate(() => { const c = document.querySelector('#radar'); const d = c.getContext('2d').getImageData(c.width / 2, c.height / 2 - 4, 1, 1).data; return d[1] > d[0] + 30 && d[1] > d[2] + 30; });
  check(!(await centerGreen()), '끈 뒤 화면 중심에 내 위치가 없다 (지도가 따라 움직였다)');
  if (SHOTS) await page.screenshot({ path: SHOTS + '/dragged.png' });
  await page.mouse.wheel(0, -300); await page.waitForTimeout(100);
  await page.click('#recenter'); await page.waitForTimeout(200);
  check(!(await page.locator('#recenter').isVisible()), `'내 위치로' 누르면 복귀`);
  check(await centerGreen(), '복귀 후 화면 중심에 내 위치');
  const nums = await page.evaluate(() => ['#nGap', '#nPace', '#nTime', '#nDist', '#eName', '#eState'].map(s => document.querySelector(s).textContent).join(' | '));
  check(!/NaN|undefined/.test(nums), '주행 화면 숫자 정상: ' + nums);
  const h1 = await px(); await page.waitForTimeout(300); const h2 = await px();
  check(h1 !== h2, '레이더 계속 갱신 중');
  // 완주 대기
  await page.waitForSelector('#result.on', { timeout: 240000 });
  await page.waitForTimeout(3500);
  const q = await page.evaluate(() => window.__qa);
  const log = await page.locator('#rLog').textContent();
  const said = log.split('\n').filter(l => l.includes('말: '));
  console.log('     발화 ' + said.length + '회. 처음 6개:\n       ' + said.slice(0, 6).join('\n       '));
  check(reqs.some(u => u.includes('voice/op.bin')), '음성 팩 요청');
  check(said.length >= 4, `대사 발화 ${said.length}회`);
  check(q.tts.length === 0, `브라우저 기계음 TTS 호출 0회 (실제 ${q.tts.length})`);
  check(q.decodes >= 10, `구운 음성 디코드 ${q.decodes}회`);
  check(!/오류/.test(log), '세션 로그에 오류 없음');
  const title = await page.locator('#rLabel').textContent();
  check(/탈출|중단/.test(title), '결과 화면: ' + title);
  if (SHOTS) await page.screenshot({ path: SHOTS + '/result.png', fullPage: true });
  check(errors.length === 0, `실행 중 스크립트 오류 ${errors.join(' | ') || '없음'}`);
  await ctx.close();
}

// 3. 음성 팩을 못 받는 환경: 기존 브라우저 TTS로 대체되고 멈추지 않는다
{
  const { ctx, page, errors } = await run({ blockVoice: true });
  await page.click('#openSet');
  await page.click('#voice button[data-v="normal"]');   // 관제 음성은 기본 끔. 음성 경로를 보려면 켠다
  await page.click('#mode button[data-v="replay"]');
  await page.click('#warmup button[data-v="0"]');
  await page.click('#start');
  await page.waitForTimeout(6000);
  const q = await page.evaluate(() => window.__qa);
  check(q.tts.length >= 1, `팩 차단 시 브라우저 TTS 대체 ${q.tts.length}회: ${q.tts[0] || ''}`);
  await page.click('#stop');
  await page.waitForSelector('#result.on');
  check(errors.length === 0, `대체 경로 오류 ${errors.join(' | ') || '없음'}`);
  await ctx.close();
}

// 3b. 느린 망: 음성 팩이 2.5초 늦게 온다. 출발 직후 첫 말도 기계음으로 새지 않아야 한다
{
  const ctx = await browser.newContext({ viewport: { width: 400, height: 860 } });
  const page = await ctx.newPage();
  const errors = []; page.on('pageerror', e => errors.push(e.message));
  await page.addInitScript(PROBE);
  await page.route('**/tile.openstreetmap.org/**', r => r.abort());
  await page.route('**/voice/**', async r => { await new Promise(x => setTimeout(x, 2500)); await r.continue(); });
  await page.goto(BASE);
  await page.click('#openSet');
  await page.click('#voice button[data-v="normal"]');   // 관제 음성은 기본 끔. 음성 경로를 보려면 켠다
  await page.click('#mode button[data-v="replay"]');
  await page.click('#warmup button[data-v="0"]');
  await page.click('#start');
  await page.waitForTimeout(9000);
  const q = await page.evaluate(() => window.__qa);
  check(q.tts.length === 0 && q.decodes >= 3, `느린 망에서도 첫 말부터 구운 음성 (디코드 ${q.decodes}, 기계음 ${q.tts.length}: ${q.tts[0] || ''})`);
  await page.click('#stop');
  check(errors.length === 0, `느린 망 오류 ${errors.join(' | ') || '없음'}`);
  await ctx.close();
}

// 4. 소리 테스트 버튼: 관제 문장
{
  const { ctx, page, errors } = await run({});
  await page.click('#openSet');
  await page.click('#voice button[data-v="normal"]');   // 관제 음성은 기본 끔. 음성 경로를 보려면 켠다
  await page.click('#audioTest');
  await page.waitForTimeout(7000);
  const q = await page.evaluate(() => window.__qa);
  check(q.tts.length === 0 && q.decodes >= 2, `소리 테스트: 구운 음성 사용 (디코드 ${q.decodes}, 기계음 ${q.tts.length})`);
  check(errors.length === 0, `소리 테스트 오류 ${errors.join(' | ') || '없음'}`);
  await ctx.close();
}

// 5. 실주행 GPS 모드: 안전 고지 → 출발 → 위치가 1초에 3m씩 북쪽으로 움직인다(약 11 km/h)
{
  const ctx = await browser.newContext({ viewport: { width: 400, height: 860 }, permissions: ['geolocation'], geolocation: { latitude: 37.8949, longitude: 127.2003, accuracy: 6 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.addInitScript(PROBE);
  await tiles(page);
  await page.goto(BASE);
  await page.click('#modeTabs [data-m="monster"]');   // 어두운 지도는 괴물 모드
  await page.click('#openSet');
  await page.click('#voice button[data-v="normal"]');   // 관제 음성은 기본 끔. 음성 경로를 보려면 켠다
  await page.click('#warmup button[data-v="0"]');
  await page.click('#start');
  check(await page.locator('#safety').isVisible(), '첫 실주행에 안전 고지 표시');
  await page.click('#safetyOk');
  await page.click('#start');
  let lat = 37.8949;
  for (let i = 0; i < 45; i++) { lat += 3 / 111320; await ctx.setGeolocation({ latitude: lat, longitude: 127.2003, accuracy: 6 }); await page.waitForTimeout(1000); }
  const nums = await page.evaluate(() => ({ dist: +document.querySelector('#nDist').textContent, pace: document.querySelector('#nPace').textContent, time: document.querySelector('#nTime').textContent }));
  check(nums.dist >= 0.08 && nums.dist <= 0.16, `GPS 45초 이동 거리 ${nums.dist} km (실제 0.135)`);
  check(!/NaN/.test(nums.pace), `GPS 페이스 표시 ${nums.pace} km/h`);
  const lum5 = await radarLum(page), dbg5 = await page.locator('#dbg').textContent();
  check(/지도 OK/.test(dbg5) && lum5 < 60, `괴물 모드 어두운 지도 (크롬 filter 경로) 평균 밝기 ${lum5.toFixed(0)}/255 · ${dbg5}`);
  await page.click('#stop');
  await page.waitForSelector('#result.on');
  const log = await page.locator('#rLog').textContent();
  const q = await page.evaluate(() => window.__qa);
  check(log.includes('말: ') && q.tts.length === 0, `GPS 모드 구운 음성 발화 (기계음 ${q.tts.length})`);
  // 'GPS 오류 신호 없음 (2)'는 플레이라이트 위치 에뮬레이션이 갱신마다 내는 것이다(앱 없는 빈 페이지에서도 똑같이 난다). 제외한다
  const bad = log.split('\n').filter(l => /오류/.test(l) && !/GPS 오류 신호 없음 \(2\)/.test(l));
  check(errors.length === 0 && bad.length === 0, `GPS 모드 오류 ${errors.join(' | ') || '없음'} ${bad.join(' / ')}`);
  await ctx.close();
}

// 6. 아이폰 에뮬레이션. 사파리에 있고 크롬에 없는 것(오디오 세션, 나침반 권한, webkitCompassHeading)을 흉내 내고
//    사파리에 없고 크롬에 있는 것(캔버스 filter)을 지운다
const IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1';
const IOS_SHIM = (withSession) => {
  window.__ios = { perm: 0, plays: 0 };
  if (withSession) Object.defineProperty(navigator, 'audioSession', { value: { type: 'auto' }, configurable: true });
  window.DeviceOrientationEvent.requestPermission = () => { window.__ios.perm++; return Promise.resolve('granted'); };
  delete CanvasRenderingContext2D.prototype.filter;
  const pl = HTMLMediaElement.prototype.play; HTMLMediaElement.prototype.play = function () { window.__ios.plays++; return pl.call(this); };
};
const compass = (page, deg) => page.evaluate((deg) => {
  const e = new Event('deviceorientation');
  Object.assign(e, { alpha: 200, beta: 40, gamma: 0, absolute: false, webkitCompassHeading: deg, webkitCompassAccuracy: 10 });
  window.dispatchEvent(e);
}, deg);
{
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, userAgent: IPHONE, isMobile: true, hasTouch: true, deviceScaleFactor: 3, permissions: ['geolocation'], geolocation: { latitude: 37.8949, longitude: 127.2003, accuracy: 6 } });
  const page = await ctx.newPage();
  const errors = []; page.on('pageerror', e => errors.push(e.message));
  await page.addInitScript(PROBE); await page.addInitScript(IOS_SHIM, true);
  await tiles(page);
  await page.goto(BASE);
  await page.click('#modeTabs [data-m="monster"]');   // 어두운 지도는 괴물 모드
  await page.click('#openSet');
  await page.click('#voice button[data-v="normal"]');   // 관제 음성은 기본 끔. 음성 경로를 보려면 켠다
  check(await page.locator('#iosAudioBox').isVisible(), '아이폰: 소리 모드 설정 표시');
  await page.click('#iosAudio button[data-v="ambient"]');
  const t1 = await page.evaluate(() => navigator.audioSession.type);
  await page.click('#iosAudio button[data-v="playback"]');
  const t2 = await page.evaluate(() => navigator.audioSession.type);
  check(t1 === 'ambient' && t2 === 'playback', `아이폰: 소리 모드 전환 → 오디오 세션 ${t1} → ${t2}`);
  await page.click('#warmup button[data-v="0"]');
  await page.click('#start'); await page.click('#safetyOk'); await page.click('#start');
  let lat = 37.8949;
  for (let i = 0; i < 12; i++) { lat += 3 / 111320; await ctx.setGeolocation({ latitude: lat, longitude: 127.2003, accuracy: 6 }); await page.waitForTimeout(1000); }
  for (let i = 0; i < 8; i++) { await compass(page, 90); await page.waitForTimeout(80); }
  await page.waitForTimeout(400);
  const ios = await page.evaluate(() => ({ ...window.__ios, type: navigator.audioSession.type }));
  const dbg = await page.locator('#dbg').textContent();
  check(ios.perm === 1, `아이폰: 출발 버튼에서 나침반 권한 요청 ${ios.perm}회`);
  check(/나침반 90°/.test(dbg), `아이폰: webkitCompassHeading으로 방위 인식 · ${dbg}`);
  check(ios.type === 'playback', `아이폰: 출발 시 오디오 세션 ${ios.type} (무음 스위치 무시)`);
  const lum = await radarLum(page);
  check(/지도 OK/.test(dbg) && lum < 60, `아이폰: 캔버스 filter 없이 다크 지도 평균 밝기 ${lum.toFixed(0)}/255`);
  // 실제 아이폰처럼 나침반 값을 계속 흘려보내면 지도가 그 방향으로 돈다. 동쪽(90°)을 보면 북쪽 표시(빨간 삼각형)가 화면 왼쪽에 있어야 한다
  await page.evaluate(() => { window.__cmp = setInterval(() => { const e = new Event('deviceorientation'); Object.assign(e, { alpha: 200, beta: 40, gamma: 0, absolute: false, webkitCompassHeading: 90, webkitCompassAccuracy: 10 }); window.dispatchEvent(e); }, 50); });
  await page.waitForTimeout(1500);
  // 떨림 방지 데드밴드(약 3°) 때문에 정확히 90°에서 멈추지 않는다. 한 점이 아니라 가장자리 영역에서 빨간 삼각형을 센다
  const north = await page.evaluate(() => {
    const c = document.querySelector('#radar'), g = c.getContext('2d'), W = c.width;
    const count = (x0, y0, w, h) => { const d = g.getImageData(x0, y0, w, h).data; let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i] > 180 && d[i + 1] < 130 && d[i + 2] < 130) n++; return n; };
    return { left: count(8, W / 2 - 80, 40, 160), top: count(W / 2 - 80, 8, 160, 40) };
  });
  await page.evaluate(() => clearInterval(window.__cmp));
  check(north.left > 40 && north.top < 5, `아이폰: 나침반 90°로 지도 회전 (북쪽 표시 빨간 픽셀 왼쪽 ${north.left}, 위 ${north.top})`);
  if (SHOTS) await page.screenshot({ path: SHOTS + '/ios.png' });
  const q = await page.evaluate(() => window.__qa);
  check(q.tts.length === 0 && q.decodes >= 3, `아이폰: 구운 음성 재생 (디코드 ${q.decodes}, 기계음 ${q.tts.length})`);
  await page.click('#stop'); await page.waitForSelector('#result.on');
  check(errors.length === 0, `아이폰 에뮬레이션 오류 ${errors.join(' | ') || '없음'}`);
  await ctx.close();
}
// 6b. 오디오 세션 API가 없는 옛 아이폰(16.4 미만): 소리 없는 <audio>로 우회
{
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, userAgent: IPHONE, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  const errors = []; page.on('pageerror', e => errors.push(e.message));
  await page.addInitScript(PROBE); await page.addInitScript(IOS_SHIM, false);
  await page.route('**/tile.openstreetmap.org/**', r => r.abort());
  await page.goto(BASE);
  await page.click('#openSet');
  await page.click('#mode button[data-v="replay"]');
  await page.click('#start');
  await page.waitForTimeout(1500);
  const ios = await page.evaluate(() => window.__ios);
  check(ios.plays >= 1 && ios.perm === 0, `옛 아이폰: 무음 <audio> 우회 재생 ${ios.plays}회, 실내 데모는 나침반 권한 안 물음`);
  await page.click('#stop'); await page.waitForSelector('#result.on');
  check(errors.length === 0, `옛 아이폰 오류 ${errors.join(' | ') || '없음'}`);
  await ctx.close();
}

// 9. 치타 추격 (2026-09-25 피드백): 처음부터 보이는가, 순간이동 없이 다가오는가, 관제 음성을 꺼도 잡히면 알려주는가
{
  const { ctx, page, errors, reqs } = await run({});
  await page.click('#openSet');
  await page.click('#animals .row[data-id="cheetah"]');
  await page.click('#mode button[data-v="replay"]');
  await page.click('#warmup button[data-v="0"]');
  const pack = await page.evaluate(() => document.querySelector('#npack button.on').dataset.v);
  await page.waitForTimeout(1000);
  await page.click('#start');
  await page.waitForTimeout(700);
  if (SHOTS) await page.screenshot({ path: SHOTS + '/edge.png' });
  // 레이더 밖이면 가장자리 노란 화살표
  const arrow = await page.evaluate(() => { const c = document.querySelector('#radar'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i] > 200 && d[i + 1] > 160 && d[i + 1] < 235 && d[i + 2] < 100) n++; return n; });
  const gaps = []; let caught = false;
  for (let i = 0; i < 400 && !caught; i++) {
    const v = await page.evaluate(() => ({ g: +document.querySelector('#nGap').textContent, h: document.querySelector('#hitsDots').textContent }));
    if (!isNaN(v.g)) gaps.push(v.g); caught = v.h.includes('●');
    await page.waitForTimeout(60);
  }
  await page.waitForTimeout(2500);
  const q = await page.evaluate(() => window.__qa);
  await page.click('#stop'); await page.waitForSelector('#result.on');
  const log = await page.locator('#rLog').textContent();
  let maxDrop = 0; for (let i = 1; i < gaps.length; i++) maxDrop = Math.max(maxDrop, gaps[i - 1] - gaps[i]);
  check(pack === '1', `기본 무리 수 ${pack}마리`);
  check(gaps[0] >= 200, `치타 시작 거리 ${gaps[0]}m (예전의 2배, 200m 이상)`);
  check(arrow > 30, `레이더 밖 적을 가장자리 화살표로 표시 (노란 픽셀 ${arrow})`);
  check(maxDrop < 60, `순간이동 없음: 한 번에 줄어든 거리 최대 ${maxDrop}m (돌진 시속 114km = 틱당 32m)`);
  check(caught && /말: 한 번 잡혔다/.test(log) && q.tts.length === 0, `관제 음성 끔 상태에서도 잡히면 "한 번 잡혔다" (잡힘 ${caught}, 기계음 ${q.tts.length})`);
  check(reqs.some(u => u.includes('voice/hit.bin')) && !reqs.some(u => u.includes('voice/op.bin')), '잡힘 알림 팩만 받고 큰 음성 팩(2.8MB)은 안 받음');
  check(errors.length === 0, `치타 추격 오류 ${errors.join(' | ') || '없음'}`);
  await ctx.close();
}

// 7. 실제 동물 녹음. 아직 녹음이 없으니 가짜 파일(길이로 구별되는 톤)을 끼워 경로를 본다
//    고른 동물 것만 받는가, 변형을 번갈아 쓰는가, 녹음이 없는 동물은 동물군 파일로 대체하는가, 방향이 맞게 배치되는가
function wav(sec, freq) {
  const sr = 22050, n = Math.round(sr * sec), b = Buffer.alloc(44 + n * 2);
  b.write('RIFF', 0); b.writeUInt32LE(36 + n * 2, 4); b.write('WAVE', 8); b.write('fmt ', 12); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22);
  b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(n * 2, 40);
  for (let i = 0; i < n; i++) b.writeInt16LE(Math.round(Math.sin(2 * Math.PI * freq * i / sr) * 12000 * Math.min(1, i / 200, (n - i) / 200)), 44 + i * 2);
  return b;
}
{
  const FIX = { 'elephant_roam_1.wav': wav(0.61, 220), 'elephant_roam_2.wav': wav(0.73, 247), 'elephant_sprint_1.wav': wav(0.43, 330), 'elephant_tired_1.wav': wav(0.97, 180), 'hoof_roam_1.wav': wav(0.55, 300) };
  const index = { elephant_roam: ['elephant_roam_1.wav', 'elephant_roam_2.wav'], elephant_sprint: ['elephant_sprint_1.wav'], elephant_tired: ['elephant_tired_1.wav'], hoof_roam: ['hoof_roam_1.wav'] };
  const ctx = await browser.newContext({ viewport: { width: 400, height: 860 } });
  const page = await ctx.newPage();
  const errors = [], reqs = [];
  page.on('pageerror', e => errors.push(e.message)); page.on('request', r => reqs.push(r.url()));
  await page.addInitScript(PROBE);
  await page.addInitScript(() => { window.__pan = []; const cp = BaseAudioContext.prototype.createPanner; BaseAudioContext.prototype.createPanner = function () { const p = cp.call(this); window.__pan.push(p); return p; }; });
  await page.route('**/tile.openstreetmap.org/**', r => r.abort());
  await page.route(u => u.pathname === '/' || u.pathname === '/index.html', async r => {
    const res = await r.fetch(); const body = (await res.text()).replace(/const SOUND_INDEX = \{[^;]*\}, SOUND_VER = "[^"]*";/, 'const SOUND_INDEX = ' + JSON.stringify(index) + ', SOUND_VER = "qa";');
    await r.fulfill({ response: res, body });
  });
  await page.route('**/sounds/**', r => { const f = new URL(r.request().url()).pathname.split('/').pop(); return FIX[f] ? r.fulfill({ status: 200, contentType: 'audio/wav', body: FIX[f] }) : r.fulfill({ status: 404 }); });
  await page.goto(BASE);
  await page.waitForTimeout(1200);
  check(!reqs.some(u => /sounds\/elephant/.test(u)), '녹음: 고르기 전에는 코끼리 파일 안 받음 (기본 닭은 녹음 없음)');
  await page.click('#openSet');
  await page.click('#animals .row[data-id="elephant"]');
  await page.waitForTimeout(800);
  const got = reqs.filter(u => /sounds\/elephant_/.test(u)).length;
  check(got === 4, `녹음: 코끼리를 고르면 코끼리 파일 ${got}/4개 받음`);
  await page.evaluate(() => { window.__pan = []; window.__qa.starts = []; });
  await page.click('#audioTest');
  await page.waitForTimeout(9500);
  const t = await page.evaluate(() => ({ starts: window.__qa.starts, pan: window.__pan.filter(p => p.panningModel === 'HRTF' && !(p.positionX.value === 0 && p.positionZ.value === 0)).map(p => [+p.positionX.value.toFixed(2), +p.positionZ.value.toFixed(2)]) }));
  const cnt = (d) => t.starts.filter(x => x === d).length;
  check(cnt(0.61) + cnt(0.73) === 5 && cnt(0.61) >= 2 && cnt(0.73) >= 2, `녹음: 소리 테스트 평상시 울음 5번, 변형 번갈아 (0.61초 ${cnt(0.61)}번, 0.73초 ${cnt(0.73)}번)`);
  check(cnt(0.43) === 4, `녹음: 다가오는 돌진 소리 4번 (${cnt(0.43)})`);
  const xs = t.pan.slice(0, 5).map(p => p[0]), back = t.pan.slice(5, 9);
  check(t.pan.length === 9 && xs[0] < -0.5 && xs[1] < -0.5 && Math.abs(xs[2]) < 0.05 && xs[3] > 0.5 && xs[4] > 0.5, `녹음: 입체 음향 위치 왼쪽→정면→오른쪽 x=${xs.join(',')}`);
  check(back.length === 4 && back.every(p => p[1] > 0.9 && Math.abs(p[0]) < 0.05), `녹음: 뒤에서 다가오는 소리는 뒤(z>0) ${JSON.stringify(back)}`);
  // 녹음이 없는 동물(낙타)은 동물군(발굽) 파일로
  await page.click('#animals .row[data-id="camel"]');
  await page.waitForTimeout(800);
  check(reqs.some(u => /sounds\/hoof_roam_1\.wav/.test(u)), '녹음: 낙타는 자기 녹음이 없어 발굽 동물군 파일로 대체');
  // 코끼리로 주행: 녹음이 실제로 쓰이는가
  await page.click('#animals .row[data-id="elephant"]');
  await page.click('#mode button[data-v="replay"]');
  await page.click('#warmup button[data-v="0"]');
  await page.evaluate(() => { window.__qa.starts = []; });
  await page.click('#start');
  await page.waitForTimeout(8000);
  const s2 = await page.evaluate(() => window.__qa.starts);
  const rec = s2.filter(x => [0.61, 0.73, 0.43, 0.97].includes(x)).length;
  await page.click('#stop'); await page.waitForSelector('#result.on');
  const log = await page.locator('#rLog').textContent();
  check(rec >= 3, `녹음: 코끼리 주행 중 녹음 재생 ${rec}번`);
  check(errors.length === 0 && !/소리 (파일|디코드) 실패/.test(log), `녹음 경로 오류 ${errors.join(' | ') || '없음'}`);
  await ctx.close();
}

// 10. 모드와 괴물 (2026-09-25): 사파리/괴물 테마, 적응형 속도, 괴물 대사, 배경음악
{
  const FX = { 'dokkaebi_roam_1.wav': wav(0.81, 70), 'dokkaebi_sprint_1.wav': wav(0.66, 90), 'dokkaebi_line_spot_1.wav': wav(1.11, 150), 'dokkaebi_line_sprint_1.wav': wav(0.91, 160), 'dokkaebi_line_hit_1.wav': wav(1.21, 170) };
  const index = { dokkaebi_roam: ['dokkaebi_roam_1.wav'], dokkaebi_sprint: ['dokkaebi_sprint_1.wav'], dokkaebi_line_spot: ['dokkaebi_line_spot_1.wav'], dokkaebi_line_sprint: ['dokkaebi_line_sprint_1.wav'], dokkaebi_line_hit: ['dokkaebi_line_hit_1.wav'] };
  const MUS = { 'monster_home.wav': wav(3.03, 110), 'monster_run.wav': wav(2.97, 130) };
  const music = { monster_home: 'monster_home.wav', monster_run: 'monster_run.wav' };
  const ctx = await browser.newContext({ viewport: { width: 400, height: 860 } });
  const page = await ctx.newPage();
  const errors = [], reqs = [];
  page.on('pageerror', e => errors.push(e.message)); page.on('request', r => reqs.push(r.url()));
  await page.addInitScript(PROBE);
  await page.addInitScript(() => { window.__loops = []; const st = AudioBufferSourceNode.prototype.start; AudioBufferSourceNode.prototype.start = function (...a) { if (this.loop && this.buffer && this.buffer.duration > 2.5) window.__loops.push(+this.buffer.duration.toFixed(2)); return st.apply(this, a); }; });
  await tiles(page);
  await page.route(u => u.pathname === '/' || u.pathname === '/index.html', async r => {
    const res = await r.fetch();
    const body = (await res.text()).replace(/const SOUND_INDEX = \{[^;]*\}, SOUND_VER = "[^"]*";/, 'const SOUND_INDEX = ' + JSON.stringify(index) + ', SOUND_VER = "qa";')
      .replace(/const MUSIC_INDEX = \{[^;]*\}, MUSIC_VER = "[^"]*";/, 'const MUSIC_INDEX = ' + JSON.stringify(music) + ', MUSIC_VER = "qa";');
    await r.fulfill({ response: res, body });
  });
  await page.route('**/sounds/**', r => { const f = new URL(r.request().url()).pathname.split('/').pop(); return FX[f] ? r.fulfill({ status: 200, contentType: 'audio/wav', body: FX[f] }) : r.fulfill({ status: 404 }); });
  await page.route('**/music/**', r => { const f = new URL(r.request().url()).pathname.split('/').pop(); return MUS[f] ? r.fulfill({ status: 200, contentType: 'audio/wav', body: MUS[f] }) : r.fulfill({ status: 404 }); });
  await page.goto(BASE);
  const t0 = await page.evaluate(() => ({ mode: document.body.dataset.mode, title: document.querySelector('#title').textContent, rows: document.querySelectorAll('#animals .row').length, pick: document.querySelector('#pickName').textContent }));
  check(t0.mode === 'animal' && t0.title === '사바나 추격' && t0.rows === 25 && t0.pick === '닭', `기본 모드 동물 사파리 (${t0.mode}, "${t0.title}", 도감 ${t0.rows}종, 기본 ${t0.pick})`);
  await page.click('#modeTabs [data-m="monster"]');
  const t1 = await page.evaluate(() => ({ mode: document.body.dataset.mode, title: document.querySelector('#title').textContent, rows: [...document.querySelectorAll('#animals .row')].map(r => r.dataset.id).join(','), pick: document.querySelector('#pickName').textContent, art: !!document.querySelector('#art svg') }));
  check(t1.mode === 'monster' && t1.rows === 'jeoseung,dokkaebi' && t1.pick === '도깨비' && t1.art, `괴물 모드 전환 (${t1.mode}, 목록 ${t1.rows}, 기본 ${t1.pick}, 일러스트 ${t1.art})`);
  await page.reload();
  check(await page.evaluate(() => document.body.dataset.mode) === 'monster', '고른 모드는 다시 열어도 유지');
  // 첫 터치에 홈 배경음악
  await page.mouse.click(200, 30); await page.waitForTimeout(1200);
  const homeLoop = await page.evaluate(() => window.__loops.slice());
  check(homeLoop.includes(3.03), `괴물 홈 배경음악 반복 재생 (${homeLoop.join(',') || '없음'})`);
  await page.click('#openSet');
  await page.click('#mode button[data-v="replay"]');
  await page.click('#warmup button[data-v="0"]');
  await page.click('#start');
  await page.waitForFunction(() => { const t = document.querySelector('#nTime').textContent.split(':'); return +t[0] * 60 + +t[1] >= 125; }, null, { timeout: 60000 }).catch(() => { });   // 페이스 측정(60초)과 첫 돌진까지
  const loops = await page.evaluate(() => window.__loops.slice());
  await page.click('#stop'); await page.waitForSelector('#result.on');
  const log = await page.locator('#rLog').textContent();
  check(loops.includes(2.97), `괴물 주행 배경음악으로 바뀜 (${loops.join(',')})`);
  const m = log.match(/페이스 ([\d.]+) km\/h → 도깨비 돌진 (\d+) km\/h/);
  check(m && Math.abs(+m[2] - 1.6 * +m[1]) <= 1.2, `적응형 속도: ${m ? `내 페이스 ${m[1]} km/h → 도깨비 돌진 ${m[2]} km/h (×1.6)` : '측정 로그 없음'}`);
  check(/괴물: spot/.test(log) && /괴물: sprint/.test(log), `도깨비 대사 재생 (발견 ${/괴물: spot/.test(log)}, 돌진 ${/괴물: sprint/.test(log)})`);
  check(reqs.some(u => /sounds\/dokkaebi_line_sprint_1/.test(u)), '괴물 대사 파일은 고른 괴물 것만 받음');
  // 저승사자: 지속주. 등속 = 내 페이스
  await page.click('#again');
  await page.click('#openSet');
  await page.click('#animals .row[data-id="jeoseung"]');
  await page.click('#start');
  await page.waitForFunction(() => { const t = document.querySelector('#nTime').textContent.split(':'); return +t[0] * 60 + +t[1] >= 75; }, null, { timeout: 60000 }).catch(() => { });
  await page.click('#stop'); await page.waitForSelector('#result.on');
  const log2 = await page.locator('#rLog').textContent();
  const m2 = log2.match(/페이스 ([\d.]+) km\/h → 저승사자 등속 ([\d.]+) km\/h/);
  check(m2 && Math.abs(+m2[2] - +m2[1]) <= 0.2, `적응형 속도: ${m2 ? `내 페이스 ${m2[1]} km/h → 저승사자 등속 ${m2[2]} km/h (×1.0)` : '측정 로그 없음'}`);
  // 배경음악 끄기
  await page.click('#again'); await page.click('#openSet');
  await page.click('#bgm button[data-v="off"]');
  check(await page.evaluate(() => localStorage.getItem('bgm')) === 'off', '배경음악 끄기 저장');
  check(errors.length === 0 && !/오류/.test(log + log2), `모드·괴물 오류 ${errors.join(' | ') || '없음'}`);
  await ctx.close();
}
// 10b. 사파리 지도는 밝은 탐험 지도(흰 타일이 어둡게 뒤집히지 않는다)
{
  const ctx = await browser.newContext({ viewport: { width: 400, height: 860 }, permissions: ['geolocation'], geolocation: { latitude: 37.8949, longitude: 127.2003, accuracy: 6 } });
  const page = await ctx.newPage(); await tiles(page); await page.goto(BASE);
  await page.evaluate(() => localStorage.setItem('safetyOk', '1')); await page.reload();
  await page.click('#start');
  let lat = 37.8949; for (let i = 0; i < 8; i++) { lat += 3 / 111320; await ctx.setGeolocation({ latitude: lat, longitude: 127.2003, accuracy: 6 }); await page.waitForTimeout(1000); }
  const lum = await radarLum(page);
  check(lum > 150, `사파리 지도 밝은 톤 평균 밝기 ${lum.toFixed(0)}/255`);
  await ctx.close();
}

// 8. 입체 음향 실측. 앱의 출력 체인(out, makeVerb)을 그대로 꺼내 오프라인으로 렌더링하고 귀별 에너지를 잰다
{
  const src = fs.readFileSync(path.join(path.dirname(new URL(import.meta.url).pathname), 'app.html'), 'utf8');
  const outSrc = src.match(/function out\(near, rel, dest, intensity\) \{[\s\S]*?\n\}/)[0], verbSrc = src.match(/function makeVerb\(ctx, dest\) \{[\s\S]*?\n\}/)[0]
    + '\n' + src.match(/function nearOf\(m\) \{.*\}/)[0].replace('function nearOf', 'window.nearOf = function') + '\n' + src.match(/function distOf\(near\) \{.*\}/)[0].replace('function distOf', 'window.distOf = function');
  const page = await browser.newPage();
  const r = await page.evaluate(async ([outSrc, verbSrc]) => {
    eval(verbSrc.replace('function makeVerb', 'window.makeVerb = function')); eval(outSrc.replace('function out', 'window.out = function'));
    async function render(near, rel, verbOnly) {
      const sr = 48000, ctx = new OfflineAudioContext(2, sr * 2.2, sr), sfx = ctx.createGain(); sfx.connect(ctx.destination);
      const verb = makeVerb(ctx, sfx);
      window.A = { ctx, hrtf: true, sfx: verbOnly ? ctx.createGain() : sfx, master: sfx, verb: verbOnly ? verb : null };   // 직접음과 잔향을 따로 잰다
      const nb = ctx.createBuffer(1, sr * 0.3, sr), d = nb.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * 0.5;
      const s = ctx.createBufferSource(); s.buffer = nb; const o = out(near, rel); s.connect(o.node); s.start(0.1);
      const buf = await ctx.startRendering(), L = buf.getChannelData(0), R = buf.getChannelData(1);
      let eL = 0, eR = 0; for (let i = 0; i < L.length; i++) { eL += L[i] * L[i]; eR += R[i] * R[i]; }
      const db = (x) => 10 * Math.log10(x + 1e-12);
      return { lr: db(eR) - db(eL), e: db(eL + eR) };
    }
    const m = {};
    for (const [k, near, rel] of [['right', 0.8, Math.PI / 2], ['left', 0.8, -Math.PI / 2], ['front', 0.8, 0], ['near', 0.9, Math.PI], ['mid', 0.5, Math.PI], ['far', 0.15, Math.PI], ['d16', 5 / 6, Math.PI], ['d32', 4 / 6, Math.PI], ['d64', 3 / 6, Math.PI], ['d128', 2 / 6, Math.PI], ['d256', 1 / 6, Math.PI]]) {
      m[k] = await render(near, rel, false); m[k].verb = (await render(near, rel, true)).e;
    }
    return m;
  }, [outSrc, verbSrc]);
  const f = (x) => x.toFixed(1);
  check(r.right.lr > 3 && r.left.lr < -3 && Math.abs(r.front.lr) < 1.5, `입체 음향: 오른쪽 소리는 오른쪽 귀 +${f(r.right.lr)}dB, 왼쪽 소리는 ${f(r.left.lr)}dB, 정면 ${f(r.front.lr)}dB`);
  check(r.near.e - r.mid.e > 6 && r.mid.e - r.far.e > 10, `입체 음향: 거리별 직접음 가까이 ${f(r.near.e)} · 중간 ${f(r.mid.e)} · 멀리 ${f(r.far.e)} dB`);
  const steps = ['d16', 'd32', 'd64', 'd128', 'd256'].map((k, i, a) => i ? r[a[i - 1]].e - r[k].e : null).slice(1);
  check(steps.every(x => x > 3), `입체 음향: 거리가 두 배가 될 때마다 작아짐 16→32→64→128→256m: ${steps.map(f).join(' / ')} dB`);
  const drr = (k) => r[k].e - r[k].verb;
  check(drr('near') > 12 && drr('far') < 0 && drr('near') > drr('mid') && drr('mid') > drr('far'), `입체 음향: 직접음/잔향 비 가까이 ${f(drr('near'))} · 중간 ${f(drr('mid'))} · 멀리 ${f(drr('far'))} dB (멀수록 울림)`);
  await page.close();
}

await browser.close(); server.close();
console.log(fails ? `\n실패 ${fails}건` : '\n전부 통과');
process.exit(fails ? 1 : 0);
