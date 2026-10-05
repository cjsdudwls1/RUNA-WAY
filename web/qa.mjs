// 출시 전 헤드리스 QA. docs/app/을 로컬로 띄워 실제 크롬에서 끝까지 돌린다
// 실행: python3 web/build.py && NODE_PATH=$(npm root -g) node web/qa.mjs   (playwright 필요)
// 확인: 스크립트 오류 0, 모드 고르기 → 설정 → 출발, 경주·공포 × 일반런·빌드업·인터벌 실내 데모 완주,
//       경주는 대사를 말하고 공포는 말하지 않는다, 공포 소리가 실제로 울린다, 검수 화면 전 항목 재생,
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

/** 소리·말 계측: 합성 노드 시작 수, 버퍼 재생 수, 브라우저 TTS 호출 */
const PROBE = () => {
  window.__qa = { osc: 0, buf: 0, tts: [] };
  const os = OscillatorNode.prototype.start; OscillatorNode.prototype.start = function (...a) { window.__qa.osc++; return os.apply(this, a); };
  const bs = AudioBufferSourceNode.prototype.start; AudioBufferSourceNode.prototype.start = function (...a) { window.__qa.buf++; return bs.apply(this, a); };
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
  await page.click(`.mode.${cfg.mode}`);
  check(await page.isVisible('#setup'), `${label}: 설정 화면`);
  await page.click(`#kind button[data-v="${cfg.type}"]`);
  await page.click('#start');
  await page.waitForSelector('#result.on', { timeout: 120000 }).catch(() => { });
  const done = await page.isVisible('#result');
  check(done, `${label}: 끝까지 완주`);
  const r = await page.evaluate(() => ({ label: document.querySelector('#rLabel').textContent, hero: document.querySelector('#rHero').textContent, log: document.querySelector('#rLog').textContent, sets: document.querySelectorAll('#rSets tr').length, qa: window.__qa }));
  check(errors.length === 0, `${label}: 오류 없음 ${errors.slice(0, 3).join(' | ')}`);
  if (SHOTS) await page.screenshot({ path: path.join(SHOTS, `result_${cfg.mode}_${cfg.type}.png`) });
  await ctx.close();
  return r;
}

// 1) 첫 화면과 설정
{
  const { ctx, page, errors } = await open({});
  check(await page.isVisible('.mode.race') && await page.isVisible('.mode.horror'), '첫 화면: 경주·공포 모드 카드');
  const txt = await page.textContent('#pickMode');
  check(txt.includes('당신을 긁는 짜증나는 상대와 경주해 보세요') && txt.includes('당신을 쫓아오는 아무개씨를 피해 도망가세요'), '모드 설명 문구');
  if (SHOTS) await page.screenshot({ path: path.join(SHOTS, 'home.png') });
  await page.click('.mode.horror');
  check(await page.evaluate(() => document.body.classList.contains('horror')), '공포 모드면 붉은 테마');
  for (const k of ['normal', 'build', 'interval']) {
    await page.click(`#kind button[data-v="${k}"]`);
    const n = await page.locator('#params .stp').count();
    check(n === { normal: 2, build: 3, interval: 4 }[k], `${k}: 설정 항목 ${n}개`);
    if (SHOTS) await page.screenshot({ path: path.join(SHOTS, `setup_horror_${k}.png`) });
  }
  // 인터벌 페이스 +5초 → 4:35, 저장
  const before = await page.textContent('#v_ipace');
  await page.locator('#params .stp').first().locator('button[data-d="1"]').dispatchEvent('pointerdown');
  await page.locator('#params .stp').first().locator('button[data-d="1"]').dispatchEvent('pointerup');
  const after = await page.textContent('#v_ipace');
  check(before === '4:30' && after === '4:35', `페이스 조절 ${before} → ${after}`);
  check(JSON.parse(await page.evaluate(() => localStorage.getItem('rw.cfg'))).ipace === 275, '설정 저장');
  check((await page.textContent('#planSum')).includes('아무개씨는 약'), '공포: 출발 간격 안내');
  await page.click('#kind button[data-v="build"]');
  check((await page.textContent('#planSum')).includes('6:30에서 5:00까지'), '빌드업 요약');
  check(errors.length === 0, '설정 화면 오류 없음 ' + errors.join(' | '));
  await ctx.close();
}

// 2) 실내 데모 6판. 데모 주행은 시속 10km(6:00/km)
const base = { safe: true, distM: 500, pace: 345, p0: 420, p1: 300, ipace: 330, setM: 100, sets: 2, restS: 15 };
{
  const r = await demo({ ...base, mode: 'race', type: 'normal' }, '경주 일반런');
  check(/승리|패배/.test(r.label), '경주 일반런 결과: ' + r.label + ' ' + r.hero);
  check(r.qa.tts.length >= 3, `경주: 대사 ${r.qa.tts.length}번 말함 (${r.qa.tts.slice(0, 3).join(' / ')})`);
  check(r.log.includes('말(ready)') && r.log.includes('말(go)'), '경주: 준비·출발 대사');
  check(/말\((win|lose|win_close|lose_close)\)/.test(r.log), '경주: 결과 대사');
}
{
  const r = await demo({ ...base, mode: 'race', type: 'build' }, '경주 빌드업');
  check(r.log.includes('go'), '빌드업 로그');
}
{
  const r = await demo({ ...base, mode: 'race', type: 'interval' }, '경주 인터벌');
  check(r.sets === 3, `경주 인터벌: 세트 표 ${r.sets - 1}줄`);
  check(r.log.includes('rest') && r.log.includes('말(rest)'), '경주 인터벌: 회복 대사');
  check(/\d승 \d패/.test(r.hero), '경주 인터벌 전적 ' + r.hero);
}
{
  const r = await demo({ ...base, mode: 'horror', type: 'normal' }, '공포 일반런');
  check(r.qa.tts.length === 0, `공포: 대사 없음 (${r.qa.tts.length})`);
  check(r.qa.osc > 30, `공포: 합성음 ${r.qa.osc}개 울림(100배속이라 적다. 실시간은 4번에서)`);
  check(/탈출 성공|잡혔다/.test(r.label), '공포 결과: ' + r.label + ' ' + r.hero);
}
{
  const r = await demo({ ...base, mode: 'horror', type: 'build', p0: 330, p1: 240 }, '공포 빌드업(빨라서 잡힘)');
  check(r.label === '잡혔다' && r.log.includes('caught'), '느린 러너는 잡힌다: ' + r.hero);
}
{
  const r = await demo({ ...base, mode: 'horror', type: 'interval' }, '공포 인터벌');
  check(r.sets === 3 && r.log.includes('rest'), '공포 인터벌 세트 표와 회복');
}

// 3) 검수 화면: 모든 소리 재생, 대사 듣기
{
  const { ctx, page, errors } = await open({});
  await page.click('#setBox summary'); await page.click('#openReview');
  const n = await page.locator('#rvHorror .rv').count(), m = await page.locator('#rvRace .rv').count(), l = await page.locator('#rvLines .rv').count();
  check(n === 15 && m === 5, `검수: 공포 소리 ${n}개, 경주 소리 ${m}개`);
  check(l >= 30, `검수: 대사 상황 ${l}개`);
  for (const b of await page.locator('#rvHorror button, #rvRace button').all()) await b.click();
  await page.locator('#rvLines button').first().click();
  await page.waitForTimeout(500);
  const qa = await page.evaluate(() => window.__qa);
  check(qa.osc > 100 && qa.tts.length === 1, `검수 재생: 합성음 ${qa.osc}, 대사 ${qa.tts.length}`);
  if (SHOTS) await page.screenshot({ path: path.join(SHOTS, 'review.png'), fullPage: true });
  await page.click('#reviewStop'); await page.click('#reviewBack');
  check(await page.isVisible('#pickMode') && errors.length === 0, '검수 닫기, 오류 없음 ' + errors.join(' | '));
  await ctx.close();
}

// 4) GPS 모드: 위치 에뮬레이션으로 위치 잡기 → 준비 → 카운트다운 → 달리기
{
  const { ctx, page, errors } = await open({ mode: 'horror', type: 'normal', distM: 1000, pace: 360 }, { ctx: { permissions: ['geolocation'], geolocation: { latitude: 37.894, longitude: 127.2, accuracy: 6 } } });
  await page.click('.mode.horror'); await page.click('#start');
  check(await page.isVisible('#safety'), 'GPS 첫 출발: 안전 고지');
  await page.click('#safetyOk'); await page.click('#start');
  let lat = 37.894;
  for (let i = 0; i < 16; i++) { lat += 0.000025; await ctx.setGeolocation({ latitude: lat, longitude: 127.2, accuracy: 6 }); await page.waitForTimeout(1000); }   // 초속 약 2.8m
  const s = await page.evaluate(() => ({ big: document.querySelector('#gapBig').textContent, sub: document.querySelector('#gapSub').textContent, log: document.querySelector('#run').classList.contains('on') }));
  check(/m$/.test(s.big) && s.sub.includes('아무개씨'), `GPS: 달리는 중 표시 ${s.big} ${s.sub}`);
  const qa = await page.evaluate(() => window.__qa);
  check(qa.osc > 80 && qa.tts.length === 0, `GPS 공포 실시간(준비 4초·카운트 3초 뒤 약 9초 주행): 합성음 ${qa.osc}개(발소리·심장·종), 대사 ${qa.tts.length}`);
  if (SHOTS) await page.screenshot({ path: path.join(SHOTS, 'run_horror.png') });
  await page.click('#stop');
  check(await page.isVisible('#result') && (await page.textContent('#rLabel')).includes('중단'), 'GPS: 종료 → 중단 결과');
  check(errors.length === 0, 'GPS 모드 오류 없음 ' + errors.join(' | '));
  await ctx.close();
}

// 5) 경주 달리는 화면 스크린샷용 + 일시정지
{
  const { ctx, page, errors } = await open({ ...base, distM: 3000, mode: 'race', type: 'normal' }, { query: '?src=demo&demoMs=40' });
  await page.click('.mode.race'); await page.click('#start');
  await page.waitForFunction(() => /m$/.test(document.querySelector('#gapBig').textContent), null, { timeout: 30000 });
  await page.waitForTimeout(1500);
  await page.click('#pause');
  check(await page.textContent('#pause') === '재개', '일시정지 버튼');

  if (SHOTS) await page.screenshot({ path: path.join(SHOTS, 'run_race.png') });
  await page.click('#stop');
  check(errors.length === 0, '경주 화면 오류 없음 ' + errors.join(' | '));
  await ctx.close();
}

// 6) 아이폰
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
