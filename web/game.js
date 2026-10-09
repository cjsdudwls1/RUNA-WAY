// 러너웨이 규칙. 추격자는 설정 페이스 그대로 뒤에서 쫓아오는 가상 주자다
// 화면과 소리에서 떼어 두었다. node로 시험한다: node web/test_game.mjs
const GAME = (() => {
  const C = {
    READY_S: 4,        // 위치를 잡고 출발 전 숨 고르기
    COUNT_S: 3,        // 3, 2, 1
    HEAD_S: 15,        // 출발 간격. 설정 페이스로 15초 갈 거리만큼 뒤에서 출발한다
    HEAD_MIN_M: 25,
    PAUSE_CMS: 100,    // 이보다 느리면 멈춘 것(초속 1m)
    PAUSE_AFTER_S: 5,  // 5초 넘게 멈추면 자동 일시정지. 추격자도 멈춘다. 신호등에서 무리하지 않게
    GATE_ACC_M: 30,    // GPS 정확도가 이보다 나쁘면 판정 동결(추격자도 멈춘다)
    PACE_WIN_S: 15,    // 내 페이스 = 최근 15초 평균
    SET_SOON_S: 6,     // 인터벌: 회복이 6초 남으면 다음 세트 예고
    REST_SOON_S: 15,   // 인터벌: 회복이 15초 남으면 알림(회복이 25초 이상일 때만)
  };
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  /** 설정 → 세트 목록. 일반런·빌드업은 세트 하나짜리 */
  function plan(cfg) {
    const one = (distM, p0, p1) => ({ distM, p0, p1 });
    let sets;
    if (cfg.type === 'build') sets = [one(cfg.distM, cfg.p0, cfg.p1)];
    else if (cfg.type === 'interval') sets = Array.from({ length: cfg.sets }, () => one(cfg.setM, cfg.ipace, cfg.ipace));
    else sets = [one(cfg.distM, cfg.pace, cfg.pace)];
    return { type: cfg.type, sets, restS: cfg.type === 'interval' ? cfg.restS : 0 };
  }
  /** x m 지점의 목표 페이스(초/km). 빌드업은 거리에 따라 시작→종료 페이스로 곧게 빨라진다 */
  const paceAt = (seg, x) => seg.p0 + (seg.p1 - seg.p0) * clamp(x / seg.distM, 0, 1);
  /** 설정 페이스로 완주하는 시간(초). 페이스가 거리에 대해 직선이라 평균 페이스 × 거리 */
  const planTimeS = (seg) => seg.distM / 1000 * (seg.p0 + seg.p1) / 2;
  const headM = (seg) => Math.max(C.HEAD_MIN_M, C.HEAD_S * 1000 / seg.p0);

  class Game {
    constructor(p) {
      this.p = p; this.phase = 'wait'; this.si = 0; this.t = 0; this.cd = 0; this.rest = 0;
      this.dist = null; this.me0 = 0; this.me = 0; this.opp = 0; this.setS = 0; this.v = 0;
      this.caught = 0; this.setCaught = 0; this.results = []; this.spd = []; this.adv = []; this.slow = 0; this.auto = false; this.lost = false;
      this.moving = 0; this.paused = 0; this.done = false; this.quit = false; this.minGap = null;
    }
    get seg() { return this.p.sets[Math.min(this.si, this.p.sets.length - 1)]; }
    /** 첫 위치를 잡았다 */
    ready() { if (this.phase !== 'wait') return []; this.phase = 'ready'; this.cd = C.READY_S; return [{ type: 'ready', set: 1, sets: this.p.sets.length }]; }
    startSet(ev) {
      const s = this.seg;
      this.phase = 'run'; this.me0 = this.dist || 0; this.me = 0; this.setS = 0; this.setCaught = 0; this.adv = [];
      this.opp = -headM(s);
      ev.push({ type: 'go', set: this.si + 1, sets: this.p.sets.length, headM: headM(s) });
    }
    /** 1초에 한 번. row = { distCm, speedCms, accM, ok(위치 수신 중) }, manual = 사용자가 일시정지 버튼을 눌렀다 */
    tick(row, manual) {
      const ev = []; this.t++;
      const d = row.distCm / 100, adv = this.dist === null ? 0 : Math.max(0, d - this.dist); this.dist = d;
      this.spd.push(row.ok ? row.speedCms : 0); if (this.spd.length > 3) this.spd.shift();
      const avg = this.spd.reduce((a, b) => a + b, 0) / this.spd.length;
      this.slow = avg < C.PAUSE_CMS ? this.slow + 1 : 0;
      const auto = this.slow >= C.PAUSE_AFTER_S, lost = !row.ok || row.accM > C.GATE_ACC_M, run = this.phase === 'run';
      if (auto !== this.auto) { this.auto = auto; if (run && !lost) ev.push({ type: auto ? 'pause' : 'resume' }); }
      if (lost !== this.lost) { this.lost = lost; if (run) ev.push({ type: lost ? 'gpsLost' : 'gpsBack' }); }
      const frozen = !!manual || auto || lost;
      const s = this.seg;
      if (this.phase === 'ready') {
        if (!manual && --this.cd <= 0) { this.phase = 'count'; this.cd = C.COUNT_S; ev.push({ type: 'count', n: this.cd, set: this.si + 1 }); }
      } else if (this.phase === 'count') {
        if (!manual) { if (--this.cd > 0) ev.push({ type: 'count', n: this.cd, set: this.si + 1 }); else this.startSet(ev); }
      } else if (this.phase === 'rest') {
        if (!manual) {
          this.rest--;
          if (this.rest === C.REST_SOON_S && this.p.restS >= 25) ev.push({ type: 'restSoon', left: this.rest });
          if (this.rest === C.SET_SOON_S) ev.push({ type: 'setSoon', set: this.si + 1, sets: this.p.sets.length, last: this.si === this.p.sets.length - 1 });
          if (this.rest <= C.COUNT_S) { this.phase = 'count'; this.cd = C.COUNT_S; ev.push({ type: 'count', n: this.cd, set: this.si + 1 }); }
        }
      } else if (run) {
        this.me = d - this.me0;
        if (frozen) this.paused++;
        else {
          this.moving++; this.setS++;
          this.adv.push(adv); if (this.adv.length > C.PACE_WIN_S) this.adv.shift();
          this.v = 1000 / paceAt(s, Math.max(0, this.opp));
          this.opp += this.v;
        }
        if (!frozen && this.me - this.opp <= 0) {
          this.caught++; this.setCaught++; this.opp = this.me - headM(s);
          ev.push({ type: 'caught', n: this.caught });
        }
        const gap = this.me - this.opp;
        if (this.minGap === null || gap < this.minGap) this.minGap = gap;
        if (this.me >= s.distM) this.endSet(ev, adv);
      }
      return { ev, snap: this.snap(frozen, manual) };
    }
    endSet(ev, adv) {
      const s = this.seg, over = this.me - s.distM;
      const myT = Math.max(1, this.setS - (adv > 0 ? Math.min(1, over / adv) : 0));
      const r = { set: this.si + 1, distM: s.distM, myT, caught: this.setCaught };
      this.results.push(r); ev.push({ type: 'setEnd', last: this.si === this.p.sets.length - 1, ...r });
      if (this.si + 1 >= this.p.sets.length) this.finish(ev);
      else { this.si++; this.phase = 'rest'; this.rest = this.p.restS; this.me = 0; this.opp = 0; ev.push({ type: 'rest', s: this.p.restS, set: this.si + 1 }); }
    }
    summary() {
      return { kind: this.p.type, results: this.results, caught: this.caught,
        quit: this.quit, sets: this.p.sets.length, moving: this.moving, paused: this.paused, dist: this.dist || 0, minGap: this.minGap };
    }
    finish(ev) { this.phase = 'done'; this.done = true; ev.push({ type: 'finish', ...this.summary() }); }
    /** 사용자가 종료를 눌렀다 */
    stop() { if (this.done) return []; this.quit = true; const ev = []; this.finish(ev); return ev; }
    snap(frozen, manual) {
      const s = this.seg, a = this.adv, v = a.length >= 5 ? a.reduce((x, y) => x + y, 0) / a.length : 0;
      return { phase: this.phase, set: this.si + 1, sets: this.p.sets.length, cd: this.cd, rest: this.rest, me: this.me, opp: this.opp, gap: this.me - this.opp,
        distM: s.distM, target: paceAt(s, Math.max(0, this.me)), oppPace: paceAt(s, Math.max(0, this.opp)), myPace: v > 0.5 ? 1000 / v : null,
        frozen: !!frozen, manual: !!manual, auto: this.auto, lost: this.lost, caught: this.caught, moving: this.moving, setS: this.setS, dist: this.dist || 0 };
    }
  }

  return { C, plan, paceAt, planTimeS, headM, Game };
})();
if (typeof module !== 'undefined') module.exports = GAME;
