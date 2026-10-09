// 출시 전 헤드리스 QA. docs/app/을 로컬로 띄워 실제 크롬에서 끝까지 돌린다
// 실행: python3 web/build.py && NODE_PATH=$(npm root -g) node web/qa.mjs   (playwright 필요)
// 확인: 스크립트 오류 0, 첫 화면에서 바로 설정 → 출발, 일반런·빌드업·인터벌 실내 데모 완주,
//       말은 없다, 녹음(발소리·숨소리·으르렁·포효)이 실제로 울린다, 검수 화면 전 항목 재생,
//       GPS 모드(위치 에뮬레이션)에서 출발까지, 아이폰 에뮬레이션(무음 스위치 대응 설정)
import { createRequire } from 'node:module';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const require = createRequire(import.meta.url);
const { chromium, devices } = require('playwright');
const ROOT = path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'docs', 'app');
const SHOTS = process.env.QA_SHOTS || '';

const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.png': 'image/png', '.webmanifest': 'application/manifest+json', '.mp3': 'audio/mpeg' };
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

/** 소리 계측: 합성 노드 시작 수, 버퍼 재생 수, 녹음 재생 수(길이 0.3초 넘는 버퍼), 브라우저 TTS 호출 */
const PROBE = () => {
  window.__qa = { osc: 0, buf: 0, rec: 0, tts: [] };
  const os = OscillatorNode.prototype.start; OscillatorNode.prototype.start = function (...a) { window.__qa.osc++; return os.apply(this, a); };
  const bs = AudioBufferSourceNode.prototype.start; AudioBufferSourceNode.prototype.start = function (...a) { window.__qa.buf++; if (this.buffer && this.buffer.numberOfChannels === 1 && this.buffer.duration < 2.5 && this.buffer.duration > 0.3 && !this.loop) window.__qa.rec++; return bs.apply(this, a); };
  if (window.speechSynthesis) { const sp = speechSynthesis.speak.bind(speechSynthesis); speechSynthesis.speak = (u) => { if (u.text.trim()) window.__qa.tts.push(u.text); return sp(u); }; }
};

async function open(cfg, opts = {}) {
  const ctx = await browser.newContext({ viewport: { width: 400, height: 860 }, deviceScaleFactor: 2, ...(opts.device || {}), ...(opts.ctx || {}) });
  const page = await ctx.newPage(), errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error' && !/favicon|fonts\.g/.test(m.text() + ' ' + ((m.location() || {}).url || ''))) errors.push(m.text()); });
  await page.route('**/fonts.googleapis.com/**', r => r.abort());
  await page.addInitScript(PROBE);
  await page.addInitScript((c) => { localStorage.setItem('rw.cfg', JSON.stringify(c)); if (c.safe) localStorage.setItem('safetyOk', '1'); }, cfg || {});
  await page.goto(BASE + (opts.query || ''), { waitUntil: 'load' });
  return { ctx, page, errors };
}

/** 실내 데모 한 판. 10ms 틱(100배속) */
async function demo(cfg, label) {
  const { ctx, page, errors } = await open(cfg, { query: '?src=demo&demoMs=10' });
  check(await page.isVisible('#start'), `${label}: 첫 화면에 출발 버튼`);
  await page.click(`#kind button[data-v="${cfg.type}"]`);
  await page.waitForTimeout(1500);   // 녹음 받기(첫 화면 0.8초 뒤 시작)
  await page.click('#start');
  await page.waitForSelector('#result.on', { timeout: 120000 }).catch(() => { });
  check(await page.isVisible('#result'), `${label}: 끝까지 완주`);
  const r = await page.evaluate(() => ({ label: document.querySelector('#rLabel').textContent, hero: document.querySelector('#rHero').textContent, log: document.querySelector('#rLog').textContent, sets: document.querySelectorAll('#rSets tr').length, qa: window.__qa }));
  check(errors.length === 0, `${label}: 오류 없음 ${errors.slice(0, 3).join(' | ')}`);
  check(r.qa.tts.length === 0, `${label}: 말 없음 (${r.qa.tts.length})`);
  if (SHOTS) await page.screenshot({ path: path.join(SHOTS, `result_${cfg.type}.png`) });
  await ctx.close();
  return r;
}

// 1) 첫 화면 = 설정. 고르고 바로 출발
{
  const { ctx, page, errors } = await open({});
  check(await page.isVisible('#home') && await page.isVisible('#kind') && await page.isVisible('#start'), '첫 화면: 운동 종류, 값, 출발이 한 화면');
  check(!(await page.textContent('body')).includes('경주'), '경주 모드 없음');
  if (SHOTS) await page.screenshot({ path: path.join(SHOTS, 'home.png') });
  for (const k of ['normal', 'build', 'interval']) {
    await page.click(`#kind button[data-v="${k}"]`);
    const n = await page.locator('#params .stp').count();
    check(n === { normal: 2, build: 3, interval: 4 }[k], `${k}: 설정 항목 ${n}개`);
    if (SHOTS) await page.screenshot({ path: path.join(SHOTS, `home_${k}.png`) });
  }
  // 인터벌 페이스 +5초 → 4:35, 저장
  const before = await page.textContent('#v_ipace');
  await page.locator('#params .stp').first().locator('button[data-d="1"]').dispatchEvent('pointerdown');
  await page.locator('#params .stp').first().locator('button[data-d="1"]').dispatchEvent('pointerup');
  const after = await page.textContent('#v_ipace');
  check(before === '4:30' && after === '4:35', `페이스 조절 ${before} → ${after}`);
  check(JSON.parse(await page.evaluate(() => localStorage.getItem('rw.cfg'))).ipace === 275, '설정 저장');
  check((await page.textContent('#planSum')).includes('아무개씨'), '출발 간격 안내');
  await page.click('#kind button[data-v="build"]');
  check((await page.textContent('#planSum')).includes('6:30에서 5:00까지'), '빌드업 요약');
  check(JSON.parse(await page.evaluate(() => localStorage.getItem('rw.cfg'))).type === 'build', '운동 종류도 저장(다음에 열면 그대로)');
  check(errors.length === 0, '첫 화면 오류 없음 ' + errors.join(' | '));
  await ctx.close();
}

// 2) 실내 데모. 데모 주행은 시속 10km(6:00/km)
const base = { safe: true, distM: 500, pace: 345, p0: 420, p1: 300, ipace: 330, setM: 100, sets: 2, restS: 15 };
{
  const r = await demo({ ...base, type: 'normal' }, '일반런');
  check(r.qa.osc > 30, `합성음 ${r.qa.osc}개 울림(100배속이라 적다. 실시간은 4번에서)`);
  check(r.qa.rec > 5, `녹음 ${r.qa.rec}번 울림(발소리 등)`);
  check(/탈출 성공|잡혔다/.test(r.label), '결과: ' + r.label + ' ' + r.hero);
  check(/소리 (scream|roar)/.test(r.log), '주행 중 먼 비명·포효: ' + (r.log.match(/소리 (scream|roar)/g) || []).join(', '));
}
{
  const r = await demo({ ...base, type: 'build', p0: 330, p1: 240 }, '빌드업(빨라서 잡힘)');
  check(r.label === '잡혔다' && r.log.includes('caught'), '느린 러너는 잡힌다: ' + r.hero);
}
{
  const r = await demo({ ...base, type: 'interval' }, '인터벌');
  check(r.sets === 3 && r.log.includes('rest'), '인터벌 세트 표와 회복');
}

// 3) 검수 화면: 모든 소리 재생
{
  const { ctx, page, errors } = await open({});
  await page.waitForTimeout(1500);
  await page.click('#setBox summary'); await page.click('#openReview');
  await page.waitForTimeout(800);
  const n = await page.locator('#rvList .rv').count(), want = await page.evaluate(() => SND.LIST.length);
  check(n === want, `검수: 소리 ${n}개`);
  const recs = await page.locator('#rvList code', { hasText: '녹음' }).count();
  check(recs >= 7, `검수: 녹음 있는 소리 ${recs}개`);
  for (const b of await page.locator('#rvList button').all()) await b.click();
  await page.waitForTimeout(500);
  const qa = await page.evaluate(() => window.__qa);
  check(qa.osc > 100 && qa.rec >= 7 && qa.tts.length === 0, `검수 재생: 합성음 ${qa.osc}, 녹음 ${qa.rec}`);
  if (SHOTS) await page.screenshot({ path: path.join(SHOTS, 'review.png'), fullPage: true });
  await page.click('#reviewStop'); await page.click('#reviewBack');
  check(await page.isVisible('#home') && errors.length === 0, '검수 닫기, 오류 없음 ' + errors.join(' | '));
  await ctx.close();
}

// 4) GPS 모드: 위치 에뮬레이션으로 위치 잡기 → 준비 → 카운트다운 → 달리기
{
  const { ctx, page, errors } = await open({ type: 'normal', distM: 1000, pace: 360 }, { ctx: { permissions: ['geolocation'], geolocation: { latitude: 37.894, longitude: 127.2, accuracy: 6 } } });
  await page.click('#start');
  check(await page.isVisible('#safety'), 'GPS 첫 출발: 안전 고지');
  await page.click('#safetyOk'); await page.click('#start');
  let lat = 37.894;
  for (let i = 0; i < 16; i++) { lat += 0.000025; await ctx.setGeolocation({ latitude: lat, longitude: 127.2, accuracy: 6 }); await page.waitForTimeout(1000); }   // 초속 약 2.8m
  const s = await page.evaluate(() => ({ big: document.querySelector('#gapBig').textContent, sub: document.querySelector('#gapSub').textContent }));
  check(/m$/.test(s.big) && s.sub.includes('아무개씨'), `GPS: 달리는 중 표시 ${s.big} ${s.sub}`);
  const qa = await page.evaluate(() => window.__qa);
  check(qa.osc > 50 && qa.rec > 5 && qa.tts.length === 0, `GPS 실시간(준비 4초·카운트 3초 뒤 약 9초 주행): 합성음 ${qa.osc}개, 녹음 ${qa.rec}번(발소리), 말 ${qa.tts.length}`);
  if (SHOTS) await page.screenshot({ path: path.join(SHOTS, 'run.png') });
  await page.click('#pause');
  check(await page.textContent('#pause') === '재개', '일시정지 버튼');
  await page.click('#stop');
  check(await page.isVisible('#result') && (await page.textContent('#rLabel')).includes('중단'), 'GPS: 종료 → 중단 결과');
  await page.click('#again');
  check(await page.isVisible('#home'), '다시 → 첫 화면');
  check(errors.length === 0, 'GPS 모드 오류 없음 ' + errors.join(' | '));
  await ctx.close();
}

// 5) 아이폰
{
  const { ctx, page, errors } = await open({}, { device: devices['iPhone 13'] });
  await page.click('#setBox summary');
  check(await page.isVisible('#iosAudioBox'), '아이폰: 무음 스위치 대응 설정 보임');
  check(errors.length === 0, '아이폰 오류 없음 ' + errors.join(' | '));
  await ctx.close();
}

await browser.close(); server.close();
console.log(fails ? `\n실패 ${fails}건` : '\n모두 통과');
process.exit(fails ? 1 : 0);
