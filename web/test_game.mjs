// 규칙 시험. 실행: node web/test_game.mjs
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const G = require('./game.js');
let fails = 0;
const check = (ok, msg) => { console.log((ok ? 'OK   ' : 'FAIL ') + msg); if (!ok) fails++; };

/** speed(t) km/h로 달리는 가상 러너. 끝날 때까지 돌리고 사건과 해설 키를 모은다 */
function sim(cfg, speed, opt = {}) {
  const p = G.plan(cfg), g = new G.Game(p), talk = new G.Talk(p), ev = [], said = [];
  let d = 0, t = 0, snaps = [];
  const push = (e) => { ev.push(...e); said.push(...talk.feed(g.snap(false, false), e).map(x => x.key)); };
  push(g.ready());
  while (!g.done && t < (opt.maxT || 20000)) {
    const kmh = speed(t, g); t++;
    const ok = !(opt.lost && opt.lost(t));
    if (ok) d += kmh / 3.6;
    const r = g.tick({ distCm: Math.round(d * 100), speedCms: ok ? Math.round(kmh / 0.036) : 0, accM: 8, ok }, false);
    ev.push(...r.ev); said.push(...talk.feed(r.snap, r.ev).map(x => x.key)); snaps.push(r.snap);
  }
  return { g, ev, said, snaps, types: ev.map(e => e.type), fin: ev.find(e => e.type === 'finish') };
}

// 1) 경주 일반런 1km 6:00. 11km/h로 뛰면 약 33초 차로 이긴다
{
  const r = sim({ mode: 'race', type: 'normal', distM: 1000, pace: 360 }, () => 11);
  const m = r.fin.margin;
  check(r.fin && !r.fin.quit && m > 30 && m < 36, `경주 일반 승리 차이 ${m.toFixed(1)}초 (기대 약 32.7)`);
  check(r.types.slice(0, 5).join(',') === 'ready,count,count,count,go', '출발 순서 ready → 3,2,1 → go ' + r.types.slice(0, 5).join(','));
  check(r.said.includes('ready') && r.said.includes('go') && r.said.includes('win'), '해설: ready, go, win ' + [...new Set(r.said)].join(','));
  check(r.said.includes('lead_small') || r.said.includes('lead_big'), '해설: 앞서는 구간');
}
// 2) 경주 일반런 패배 + 상대 먼저 도착
{
  const r = sim({ mode: 'race', type: 'normal', distM: 1000, pace: 300 }, () => 10);
  check(r.fin.margin < 0 && Math.abs(r.fin.margin + 60) < 2, `경주 패배 차이 ${r.fin.margin.toFixed(1)}초 (기대 -60)`);
  check(r.types.includes('oppDone') && r.said.includes('opp_finished'), '상대 먼저 도착 알림');
  check(r.said.includes('overtaken') === false, '같이 출발해 처지기만 했으면 추월 아님');
  check(r.said.includes('lose'), '해설: lose');
}
// 3) 추월. 처음엔 느리다가 빨라진다
{
  const r = sim({ mode: 'race', type: 'normal', distM: 2000, pace: 360 }, (t) => (t < 120 ? 9 : 12));
  check(r.said.includes('overtake_me'), '내가 추월 ' + r.said.filter(k => k.startsWith('over')).join(','));
  check(r.said.includes('half') && r.said.includes('last_500') && r.said.includes('last_100'), '절반·500·100 표지');
}
// 4) 공포 일반런. 느리면 잡힌다. 출발 간격 = 15초 거리
{
  const r = sim({ mode: 'horror', type: 'normal', distM: 1000, pace: 360 }, () => 9);
  const go = r.ev.find(e => e.type === 'go');
  check(Math.abs(go.headM - 41.67) < 0.1, `공포 출발 간격 ${go.headM.toFixed(1)}m`);
  check(r.g.caught >= 1 && r.types.includes('caught'), `공포 잡힘 ${r.g.caught}회`);
  const fast = sim({ mode: 'horror', type: 'normal', distM: 1000, pace: 360 }, () => 11);
  check(fast.g.caught === 0 && fast.fin && !fast.fin.quit, '빠르면 안 잡힌다');
  const minGap = Math.min(...fast.snaps.filter(s => s.phase === 'run').map(s => s.gap));
  check(minGap > 35, `빠를 때 최소 거리 ${minGap.toFixed(1)}m`);
}
// 5) 빌드업 5km 6:30 → 5:00. 설정 시간 28분 45초, 상대는 점점 빨라진다
{
  const cfg = { mode: 'race', type: 'build', distM: 5000, p0: 390, p1: 300 };
  check(G.planTimeS(G.plan(cfg).sets[0]) === 1725, '빌드업 설정 시간 1725초');
  const r = sim(cfg, () => 3600 / 345);   // 평균 페이스 5:45로 고르게
  check(Math.abs(r.fin.margin) < 8, `빌드업 고른 페이스 ≈ 비김 (차이 ${r.fin.margin.toFixed(1)}초)`);
  const run = r.snaps.filter(s => s.phase === 'run');
  check(run[10].oppPace > run[run.length - 10].oppPace + 60, `상대 페이스 ${run[10].oppPace.toFixed(0)} → ${run[run.length - 10].oppPace.toFixed(0)}`);
  check(r.said.filter(k => k === 'build_faster').length >= 4, '빌드업 페이스 올림 알림 ' + r.said.filter(k => k === 'build_faster').length + '회');
  check(r.said.filter(k => k === 'km').length === 4, 'km 표지 4회(1,2,3,4. 2.5는 절반)');
}
// 6) 인터벌 200m × 3, 4:00, 회복 30초. 회복 중엔 상대 없음
{
  const r = sim({ mode: 'race', type: 'interval', setM: 200, sets: 3, ipace: 240, restS: 30 }, (t, g) => (g.phase === 'rest' ? 5 : 16));
  const ends = r.ev.filter(e => e.type === 'setEnd');
  check(ends.length === 3 && ends.every(e => e.win), '인터벌 3세트 모두 승리');
  check(r.types.filter(x => x === 'rest').length === 2, '회복 2번');
  check(r.types.includes('setSoon') && r.types.includes('restSoon'), '다음 세트 예고, 회복 끝 알림');
  const rest = r.snaps.filter(s => s.phase === 'rest');
  check(rest.length > 0 && rest.every(s => s.gap === 0), '회복 중 상대 없음');
  check(r.said.includes('set_win') && r.said.includes('rest') && r.said.includes('last_set') && r.said.includes('interval_win'), '인터벌 해설 ' + [...new Set(r.said)].join(','));
  const restLen = r.snaps.filter(s => s.phase === 'rest' || s.phase === 'count').length;
  check(restLen >= 60 && restLen <= 66, `회복+카운트 총 ${restLen}초`);
}
// 7) 공포 인터벌. 세트마다 출발 간격을 새로 준다
{
  const r = sim({ mode: 'horror', type: 'interval', setM: 400, sets: 2, ipace: 270, restS: 20 }, (t, g) => (g.phase === 'rest' ? 4 : 10));
  check(r.ev.filter(e => e.type === 'go').length === 2 && r.g.caught > 0 && r.fin, `공포 인터벌 2세트, 잡힘 ${r.g.caught}`);
}
// 8) 자동 일시정지: 멈추면 5초 뒤 상대도 멈춘다
{
  const r = sim({ mode: 'race', type: 'normal', distM: 1000, pace: 360 }, (t) => (t > 60 && t < 90 ? 0 : 10));
  check(r.types.includes('pause') && r.types.includes('resume'), '자동 일시정지/재개');
  const ps = r.snaps.filter(s => s.phase === 'run' && s.frozen);
  check(ps.length >= 20 && ps.length <= 27, `동결 ${ps.length}초`);
  const o1 = ps[0].opp, o2 = ps[ps.length - 1].opp;
  check(o1 === o2, '동결 중 상대 정지');
  check(r.said.includes('pause'), '해설: pause');
}
// 9) GPS 끊김: 상대 정지
{
  const r = sim({ mode: 'horror', type: 'normal', distM: 1000, pace: 360 }, () => 10, { lost: (t) => t > 50 && t < 70 });
  check(r.types.includes('gpsLost') && r.types.includes('gpsBack'), 'GPS 끊김/복귀');
}
// 10) 중도 종료
{
  const p = G.plan({ mode: 'race', type: 'normal', distM: 5000, pace: 360 }), g = new G.Game(p); g.ready();
  for (let i = 0; i < 30; i++) g.tick({ distCm: i * 280, speedCms: 280, accM: 5, ok: true });
  const e = g.stop(); const t = new G.Talk(p).feed(g.snap(), e).map(x => x.key);
  check(e[0].type === 'finish' && e[0].quit && t[0] === 'quit', '중도 종료 → quit');
}
// 11) 말 채우기
{
  check(G.fill('{gap} 차이, {margin}, {pace}, {km}, {status}', { gap: 23.4, margin: 75, pace: 330, km: 3, status: -12 }) === '23미터 차이, 1분 15초, 5분 30초, 3킬로, 내가 12미터 앞', G.fill('{gap} 차이, {margin}, {pace}, {km}, {status}', { gap: 23.4, margin: 75, pace: 330, km: 3, status: -12 }));
  check(G.fill('{모름} {gap}', { gap: 5 }) === '{모름} 5미터', '모르는 변수는 그대로');
  const pick = G.picker(), L = ['a', 'b', 'c'], got = new Set([pick('k', L), pick('k', L), pick('k', L)]);
  check(got.size === 3, '한 바퀴 돌기 전에는 같은 대사 반복 없음');
}
process.exit(fails ? 1 : 0);
