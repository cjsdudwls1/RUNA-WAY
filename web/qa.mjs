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

/** 소리 계측: 합성 노드 시작 수, 버퍼 재생 수, 녹음 재생 수(디코드한 파일), 브라우저 TTS 호출 */
const PROBE = () => {
  window.__qa = { osc: 0, buf: 0, rec: 0, tts: [] }; window.__dec = new WeakSet();
  const dd = BaseAudioContext.prototype.decodeAudioData; BaseAudioContext.prototype.decodeAudioData = function (...a) { return dd.apply(this, a).then(b => { window.__dec.add(b); return b; }); };
  const os = OscillatorNode.prototype.start; OscillatorNode.prototype.start = function (...a) { window.__qa.osc++; return os.apply(this, a); };
  const bs = AudioBufferSourceNode.prototype.start; AudioBufferSourceNode.prototype.start = function (...a) { window.__qa.buf++; if (this.buffer && window.__dec.has(this.buffer)) window.__qa.rec++; return bs.apply(this, a); };
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
  check((await page.textContent('#kindDesc')).includes('전력 질주'), '인터벌 설명');
  const before = await page.inputValue('#v_ipace');
  await page.locator('#params .stp').first().locator('button[data-d="1"]').dispatchEvent('pointerdown');
  await page.locator('#params .stp').first().locator('button[data-d="1"]').dispatchEvent('pointerup');
  const after = await page.inputValue('#v_ipace');
  check(before === '4:30' && after === '4:35', `페이스 조절 ${before} → ${after}`);
  check(JSON.parse(await page.evaluate(() => localStorage.getItem('rw.cfg'))).ipace === 275, '설정 저장');
  check((await page.textContent('#planSum')).includes('추격자'), '출발 간격 안내');
  // 숫자를 눌러 직접 입력
  for (const [key, typed, want] of [['ipace', '5.3', '5:30'], ['ipace', '447', '4:47'], ['setM', '1.2', '1200 m'], ['sets', '8', '8세트'], ['restS', '75', '1:15'], ['restS', '엉뚱', '1:15']]) {
    await page.click('#v_' + key); await page.fill('#v_' + key, typed); await page.press('#v_' + key, 'Enter');
    const got = await page.inputValue('#v_' + key);
    check(got === want, `직접 입력 ${key} "${typed}" → ${got}`);
  }
  check(await page.evaluate(() => window.__qa.buf) >= 3, '버튼 딸깍 ' + await page.evaluate(() => window.__qa.buf) + '번');
  await page.click('#kind button[data-v="build"]');
  check((await page.textContent('#planSum')).includes('6:30에서 5:00까지'), '빌드업 요약');
  check(JSON.parse(await page.evaluate(() => localStorage.getItem('rw.cfg'))).type === 'build', '운동 종류도 저장(다음에 열면 그대로)');
  await page.click('#kind button[data-v="normal"]');
  await page.click('#v_distM'); await page.fill('#v_distM', '7.25'); await page.press('#v_distM', 'Enter');
  check(await page.inputValue('#v_distM') === '7.25 km', '거리 직접 입력 7.25 km');
  check(errors.length === 0, '첫 화면 오류 없음 ' + errors.join(' | '));
  await ctx.close();
}

// 2) 실내 데모. 데모 주행은 시속 10km(6:00/km)
const base = { safe: true, distM: 500, pace: 345, p0: 420, p1: 300, ipace: 330, setM: 100, sets: 2, restS: 15 };
{
  const r = await demo({ ...base, type: 'normal' }, '일반런');
  check(r.qa.osc + r.qa.rec > 30, `소리 ${r.qa.osc + r.qa.rec}번 울림(합성 ${r.qa.osc}, 녹음 ${r.qa.rec})`);
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

// 3) 검수 화면: 소리마다 후보 목록, 후보 미리듣기, 고르기
{
  const { ctx, page, errors } = await open({});
  await page.click('#setBox summary'); await page.click('#openReview');
  const n = await page.locator('#rvList .rvg').count(), want = await page.evaluate(() => SND.LIST.length);
  check(n === want, `검수: 소리 ${n}개`);
  const cands = await page.evaluate(() => Object.fromEntries(Object.entries(SOUND_INDEX).map(([k, v]) => [k, Object.keys(v).length])));
  check(Object.keys(cands).length >= 15, `검수: 녹음 후보가 있는 소리 ${Object.keys(cands).length}개 ` + JSON.stringify(cands));
  // 으르렁: 후보 하나 미리듣기 → 녹음이 울린다
  const g = page.locator('.rvg[data-id=growl]');
  await g.locator('summary').click();
  const rows = await g.locator('.cand:not(.head)').count();
  check(rows === cands.growl, `으르렁 후보 ${rows}개`);
  const r0 = await page.evaluate(() => window.__qa.rec);
  await g.locator('.cand:not(.head) .pl').nth(2).click(); await page.waitForTimeout(1500);
  check(await page.evaluate(() => window.__qa.rec) > r0, '후보 미리듣기: 녹음 재생');
  // 이것만 → 하나만 사용, 끄기 → 끔, 전부 → 다시 전부
  await g.locator('.cand:not(.head) .only').nth(1).click();
  let sel = JSON.parse(await page.evaluate(() => localStorage.getItem('rw.snd')));
  check(sel.growl.length === 1 && (await g.locator('summary code').textContent()).includes(`1/${rows}`), '이것만: ' + JSON.stringify(sel.growl));
  await g.locator('.cand.head .none').click();
  check((await g.locator('summary code').textContent()).includes('끔'), '끄기');
  await g.locator('.cand.head .all').click();
  sel = JSON.parse(await page.evaluate(() => localStorage.getItem('rw.snd')));
  check(sel.growl.length === rows, '전부');
  // 합성음 후보가 있는 소리: 발소리. 합성음만 고르면 녹음 없이 합성음
  const st = page.locator('.rvg[data-id=step]');
  await st.locator('summary').click();
  check((await st.textContent()).includes('합성음'), '발소리: 합성음도 후보');
  // 전체 장면: 고른 소리로
  const o0 = await page.evaluate(() => window.__qa.buf);
  const sc = page.locator('.rvg[data-id=scene]'); await sc.locator('summary').click(); await sc.locator('.pl').click(); await page.waitForTimeout(2500);
  check(await page.evaluate(() => window.__qa.buf) > o0, '전체 장면 재생');
  if (SHOTS) await page.screenshot({ path: path.join(SHOTS, 'review.png'), fullPage: true });
  await page.click('#reviewStop'); await page.click('#reviewBack');
  check(await page.isVisible('#home') && errors.length === 0, '검수 닫기, 오류 없음 ' + errors.join(' | '));
  await ctx.close();
}
// 3-1) 고른 대로 주행: 발소리를 합성음만 고르면 발소리 녹음이 안 나온다
{
  const { ctx, page, errors } = await open({ ...{ safe: true, distM: 300, pace: 345 }, type: 'normal' }, { query: '?src=demo&demoMs=10' });
  await page.evaluate(() => { const s = {}; for (const it of SND.LIST) s[it.id] = []; s.step = ['synth']; localStorage.setItem('rw.snd', JSON.stringify(s)); });
  await page.reload({ waitUntil: 'load' }); await page.waitForTimeout(500);
  await page.click('#start'); await page.waitForSelector('#result.on', { timeout: 120000 }).catch(() => { });
  const qa = await page.evaluate(() => window.__qa);
  check(qa.rec === 0 && qa.osc >= 2, `고른 대로: 발소리 합성음만(녹음 ${qa.rec}, 합성 ${qa.osc})`);
  check(errors.length === 0, '고른 대로 주행 오류 없음 ' + errors.join(' | '));
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
  check(/m$/.test(s.big) && s.sub.includes('추격자'), `GPS: 달리는 중 표시 ${s.big} ${s.sub}`);
  const qa = await page.evaluate(() => window.__qa);
  check(qa.osc + qa.rec > 50 && qa.rec > 5 && qa.tts.length === 0, `GPS 실시간(준비 4초·카운트 3초 뒤 약 9초 주행): 합성음 ${qa.osc}개, 녹음 ${qa.rec}번(발소리), 말 ${qa.tts.length}`);
  if (SHOTS) await page.screenshot({ path: path.join(SHOTS, 'run.png') });
  await page.click('#pause');
  check(await page.textContent('#pause') === '재개', '일시정지 버튼');
  await page.click('#stop');
  check(await page.isVisible('#result') && (await page.textContent('#rLabel')).includes('중단'), 'GPS: 종료 → 중단 결과');
  await page.click('#again');
  check(await page.isVisible('#home'), '다시 → 첫 화면');
  check(/지난 기록/.test(await page.textContent('#last')) && await page.isVisible('#last'), '첫 화면에 지난 기록: ' + (await page.textContent('#last')));
  const p2 = await ctx.newPage(); await p2.goto(BASE, { waitUntil: 'load' });
  check(await p2.isVisible('#last') && (await p2.textContent('#planSum')).includes('지난번 설정') && await p2.inputValue('#v_distM') === '1 km', '앱을 다시 켜면 지난 기록과 지난번 설정 그대로');
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
