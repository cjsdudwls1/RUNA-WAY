// 규칙 시험. 실행: node web/test_game.mjs
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const G = require('./game.js');
let fails = 0;
const check = (ok, msg) => { console.log((ok ? 'OK   ' : 'FAIL ') + msg); if (!ok) fails++; };

/** speed(t) km/h로 달리는 가상 러너. 끝날 때까지 돌리고 사건을 모은다 */
function sim(cfg, speed, opt = {}) {
  const p = G.plan(cfg), g = new G.Game(p), ev = [...g.ready()];
  let d = 0, t = 0; const snaps = [];
  while (!g.done && t < (opt.maxT || 20000)) {
    const kmh = speed(t, g); t++;
    const ok = !(opt.lost && opt.lost(t));
    if (ok) d += kmh / 3.6;
    const r = g.tick({ distCm: Math.round(d * 100), speedCms: ok ? Math.round(kmh / 0.036) : 0, accM: 8, ok }, false);
    ev.push(...r.ev); snaps.push(r.snap);
  }
  return { g, ev, snaps, types: ev.map(e => e.type), fin: ev.find(e => e.type === 'finish') };
}

// 1) 일반런. 느리면 잡힌다. 출발 간격 = 15초 거리
{
  const r = sim({ type: 'normal', distM: 1000, pace: 360 }, () => 9);
  const go = r.ev.find(e => e.type === 'go');
  check(r.types.slice(0, 5).join(',') === 'ready,count,count,count,go', '출발 순서 ready → 3,2,1 → go ' + r.types.slice(0, 5).join(','));
  check(Math.abs(go.headM - 41.67) < 0.1, `출발 간격 ${go.headM.toFixed(1)}m`);
  check(r.g.caught >= 1 && r.types.includes('caught'), `느리면 잡힘 ${r.g.caught}회`);
  const after = r.snaps[r.snaps.findIndex((s, i) => i > 0 && s.caught > r.snaps[i - 1].caught)];
  check(after && Math.abs(after.gap - 41.67) < 0.1, `잡히면 다시 출발 간격만큼 뒤로 (${after && after.gap.toFixed(1)}m)`);
  const fast = sim({ type: 'normal', distM: 1000, pace: 360 }, () => 11);
  check(fast.g.caught === 0 && fast.fin && !fast.fin.quit, '빠르면 안 잡힌다');
  const minGap = Math.min(...fast.snaps.filter(s => s.phase === 'run').map(s => s.gap));
  check(minGap > 35, `빠를 때 최소 거리 ${minGap.toFixed(1)}m`);
}
// 2) 빌드업 5km 6:30 → 5:00. 설정 시간 28분 45초, 아무개씨는 점점 빨라진다
{
  const cfg = { type: 'build', distM: 5000, p0: 390, p1: 300 };
  check(G.planTimeS(G.plan(cfg).sets[0]) === 1725, '빌드업 설정 시간 1725초');
  const r = sim(cfg, () => 3600 / 330);
  const run = r.snaps.filter(s => s.phase === 'run');
  check(run[10].oppPace > run[run.length - 10].oppPace + 60, `아무개씨 페이스 ${run[10].oppPace.toFixed(0)} → ${run[run.length - 10].oppPace.toFixed(0)}`);
  check(r.fin && !r.fin.quit, '빌드업 완주');
}
// 3) 인터벌 200m × 3, 4:00, 회복 30초. 회복 중엔 아무개씨 없음, 세트마다 다시 출발 간격
{
  const r = sim({ type: 'interval', setM: 200, sets: 3, ipace: 240, restS: 30 }, (t, g) => (g.phase === 'rest' ? 5 : 16));
  check(r.ev.filter(e => e.type === 'setEnd').length === 3 && r.ev.filter(e => e.type === 'go').length === 3, '인터벌 3세트, 출발 3번');
  check(r.types.filter(x => x === 'rest').length === 2, '회복 2번');
  check(r.types.includes('setSoon') && r.types.includes('restSoon'), '다음 세트 예고, 회복 끝 알림');
  const rest = r.snaps.filter(s => s.phase === 'rest');
  check(rest.length > 0 && rest.every(s => s.gap === 0), '회복 중 아무개씨 없음');
  const restLen = r.snaps.filter(s => s.phase === 'rest' || s.phase === 'count').length;
  check(restLen >= 60 && restLen <= 66, `회복+카운트 총 ${restLen}초`);
  const slow = sim({ type: 'interval', setM: 400, sets: 2, ipace: 270, restS: 20 }, (t, g) => (g.phase === 'rest' ? 4 : 10));
  check(slow.g.caught > 0 && slow.fin && slow.fin.results.every(x => x.caught >= 0), `느린 인터벌 잡힘 ${slow.g.caught}`);
}
// 4) 자동 일시정지: 멈추면 5초 뒤 아무개씨도 멈춘다
{
  const r = sim({ type: 'normal', distM: 1000, pace: 420 }, (t) => (t > 60 && t < 90 ? 0 : 10));
  check(r.types.includes('pause') && r.types.includes('resume'), '자동 일시정지/재개');
  const ps = r.snaps.filter(s => s.phase === 'run' && s.frozen);
  check(ps.length >= 20 && ps.length <= 27, `동결 ${ps.length}초`);
  check(ps[0].opp === ps[ps.length - 1].opp, '동결 중 아무개씨 정지');
}
// 5) GPS 끊김: 아무개씨 정지
{
  const r = sim({ type: 'normal', distM: 1000, pace: 360 }, () => 10, { lost: (t) => t > 50 && t < 70 });
  check(r.types.includes('gpsLost') && r.types.includes('gpsBack'), 'GPS 끊김/복귀');
}
// 6) 중도 종료
{
  const p = G.plan({ type: 'normal', distM: 5000, pace: 360 }), g = new G.Game(p); g.ready();
  for (let i = 0; i < 30; i++) g.tick({ distCm: i * 280, speedCms: 280, accM: 5, ok: true });
  const e = g.stop();
  check(e[0].type === 'finish' && e[0].quit, '중도 종료 → quit');
}
process.exit(fails ? 1 : 0);
