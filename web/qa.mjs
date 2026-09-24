// 출시 전 헤드리스 QA. docs/app/을 로컬로 띄워 실제 크롬에서 끝까지 돌린다
// 실행: NODE_PATH=$(npm root -g) node web/qa.mjs   (playwright 필요)
// 확인: 스크립트 오류 0, 음성 팩 전 조각 디코드, 실내 데모 완주, 구운 음성 재생(브라우저 TTS 미사용),
//       지도 끌기·복귀, 결과 화면, 음성 팩이 없을 때 브라우저 TTS로 대체
import { createRequire } from 'node:module';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
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
  await ctx.close();
}

// 2. 실내 데모 완주 + 구운 음성 + 지도 끌기
{
  const { ctx, page, errors, reqs } = await run({});
  await page.click('#openSet');
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
  const centerGreen = async () => page.evaluate(() => { const c = document.querySelector('#radar'); const d = c.getContext('2d').getImageData(c.width / 2, c.height / 2 - 4, 1, 1).data; return d[1] > 200 && d[0] < 120; });
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
  await page.route('**/tile.openstreetmap.org/**', r => r.abort());
  await page.goto(BASE);
  await page.click('#openSet');
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

await browser.close(); server.close();
console.log(fails ? `\n실패 ${fails}건` : '\n전부 통과');
process.exit(fails ? 1 : 0);
