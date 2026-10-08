// 러너웨이 규칙. 상대는 설정 페이스 그대로 달리는 가상 주자다(경주: 옆에서 같이 출발, 공포: 뒤에서 쫓아온다)
// 화면과 소리에서 떼어 두었다. node로 시험한다: node web/test_game.mjs
const GAME = (() => {
  const C = {
    READY_S: 4,        // 위치를 잡고 출발 전 숨 고르기. 경주모드는 이때 상대가 첫 말을 건다
    COUNT_S: 3,        // 3, 2, 1
    HEAD_S: 15,        // 공포모드 출발 간격. 설정 페이스로 15초 갈 거리만큼 뒤에서 출발한다
    HEAD_MIN_M: 25,
    PAUSE_CMS: 100,    // 이보다 느리면 멈춘 것(초속 1m)
    PAUSE_AFTER_S: 5,  // 5초 넘게 멈추면 자동 일시정지. 상대도 멈춘다. 신호등에서 무리하지 않게
    GATE_ACC_M: 30,    // GPS 정확도가 이보다 나쁘면 판정 동결(상대도 멈춘다)
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
    return { mode: cfg.mode, type: cfg.type, sets, restS: cfg.type === 'interval' ? cfg.restS : 0 };
  }
  /** x m 지점의 목표 페이스(초/km). 빌드업은 거리에 따라 시작→종료 페이스로 곧게 빨라진다 */
  const paceAt = (seg, x) => seg.p0 + (seg.p1 - seg.p0) * clamp(x / seg.distM, 0, 1);
  /** 설정 페이스로 완주하는 시간(초). 페이스가 거리에 대해 직선이라 평균 페이스 × 거리 */
  const planTimeS = (seg) => seg.distM / 1000 * (seg.p0 + seg.p1) / 2;
  const headM = (seg) => Math.max(C.HEAD_MIN_M, C.HEAD_S * 1000 / seg.p0);

  class Game {
    constructor(p) {
      this.p = p; this.phase = 'wait'; this.si = 0; this.t = 0; this.cd = 0; this.rest = 0;
      this.dist = null; this.me0 = 0; this.me = 0; this.opp = 0; this.oppDone = false; this.oppT = null; this.setS = 0; this.v = 0;
      this.caught = 0; this.setCaught = 0; this.results = []; this.spd = []; this.adv = []; this.slow = 0; this.auto = false; this.lost = false;
      this.moving = 0; this.paused = 0; this.done = false; this.quit = false; this.minGap = null;
    }
    get seg() { return this.p.sets[Math.min(this.si, this.p.sets.length - 1)]; }
    get horror() { return this.p.mode === 'horror'; }
    /** 첫 위치를 잡았다 */
    ready() { if (this.phase !== 'wait') return []; this.phase = 'ready'; this.cd = C.READY_S; return [{ type: 'ready', set: 1, sets: this.p.sets.length }]; }
    startSet(ev) {
      const s = this.seg;
      this.phase = 'run'; this.me0 = this.dist || 0; this.me = 0; this.setS = 0; this.oppDone = false; this.oppT = null; this.setCaught = 0; this.adv = [];
      this.opp = this.horror ? -headM(s) : 0;
      ev.push({ type: 'go', set: this.si + 1, sets: this.p.sets.length, headM: this.horror ? headM(s) : 0 });
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
          if (!this.oppDone) {
            this.v = 1000 / paceAt(s, Math.max(0, this.opp));
            this.opp += this.v;
            if (!this.horror && this.opp >= s.distM) {
              this.oppT = this.setS - (this.opp - s.distM) / this.v; this.opp = s.distM; this.oppDone = true;
              ev.push({ type: 'oppDone' });
            }
          }
        }
        if (this.horror && !frozen && this.me - this.opp <= 0) {
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
      // 상대가 아직 못 왔으면 남은 거리를 지금 속도로 간다고 본다
      const oppT = this.horror ? planTimeS(s) : this.oppDone ? this.oppT : this.setS + (s.distM - this.opp) / (this.v || 1000 / s.p0);
      const r = { set: this.si + 1, distM: s.distM, myT, oppT, margin: oppT - myT, win: oppT - myT > 0, caught: this.setCaught };
      this.results.push(r); ev.push({ type: 'setEnd', last: this.si === this.p.sets.length - 1, ...r });
      if (this.si + 1 >= this.p.sets.length) this.finish(ev);
      else { this.si++; this.phase = 'rest'; this.rest = this.p.restS; this.me = 0; this.opp = 0; ev.push({ type: 'rest', s: this.p.restS, set: this.si + 1 }); }
    }
    summary() {
      const R = this.results, wins = R.filter(r => r.win).length;
      return { mode: this.p.mode, kind: this.p.type, results: R, wins, losses: R.length - wins, caught: this.caught, margin: R.length ? R[R.length - 1].margin : 0,
        quit: this.quit, sets: this.p.sets.length, moving: this.moving, paused: this.paused, dist: this.dist || 0, minGap: this.minGap };
    }
    finish(ev) { this.phase = 'done'; this.done = true; ev.push({ type: 'finish', ...this.summary() }); }
    /** 사용자가 종료를 눌렀다 */
    stop() { if (this.done) return []; this.quit = true; const ev = []; this.finish(ev); return ev; }
    snap(frozen, manual) {
      const s = this.seg, a = this.adv, v = a.length >= 5 ? a.reduce((x, y) => x + y, 0) / a.length : 0;
      return { phase: this.phase, set: this.si + 1, sets: this.p.sets.length, cd: this.cd, rest: this.rest, me: this.me, opp: this.opp, gap: this.me - this.opp,
        distM: s.distM, target: paceAt(s, Math.max(0, this.me)), oppPace: paceAt(s, Math.max(0, this.opp)), myPace: v > 0.5 ? 1000 / v : null,
        frozen: !!frozen, manual: !!manual, auto: this.auto, lost: this.lost, caught: this.caught, moving: this.moving, setS: this.setS, dist: this.dist || 0, oppDone: this.oppDone };
    }
  }

  // ---------- 경주모드 해설 ----------
  // 어떤 상황에 어떤 대사 묶음을 쓸지만 정한다. 대사 자체는 web/race_lines.md
  const Z = { TIE: 5, MID: 20, BIG: 50, SWAP: 3, DEBOUNCE_S: 4, REPEAT_S: 75, IDLE_S: 100, SLOW_D: 20, SLOW_S: 15, FAST_D: 30, FAST_S: 20, NAG_CD: 150, BUILD_STEP: 15 };
  function zoneOf(gap) {
    const g = Math.abs(gap);
    if (g < Z.TIE) return 'tie';
    const k = g < Z.MID ? 'small' : g < Z.BIG ? 'big' : 'huge';
    return (gap > 0 ? 'lead_' : 'behind_') + k;
  }
  const PRI = { CRIT: 0, HIGH: 1, NORM: 2 };
  class Talk {
    constructor(p) { this.p = p; this.reset(); this.lastAny = 0; this.t = 0; this.nagAt = -1e9; }
    reset() { this.zone = null; this.cand = null; this.candN = 0; this.zoneAt = 0; this.sign = 0; this.swapAt = -1e9; this.km = 0; this.flags = {}; this.slowN = 0; this.fastN = 0; this.buildAt = null; }
    /** 한 틱의 스냅샷과 사건 → 할 말 목록 [{ key, vars, pri }] */
    feed(snap, ev) {
      const out = [], say = (key, vars, pri) => { out.push({ key, vars: vars || {}, pri: pri === undefined ? PRI.HIGH : pri }); this.lastAny = this.t; };
      this.t++;
      const gap = snap.gap, inter = this.p.type === 'interval';
      for (const e of ev) {
        if (e.type === 'ready') say('ready', {}, PRI.CRIT);
        else if (e.type === 'go') { this.reset(); if (e.set === 1) say('go', {}, PRI.CRIT); }
        else if (e.type === 'setSoon') say(e.last ? 'last_set' : 'set_start', { set: e.set }, PRI.CRIT);
        else if (e.type === 'rest') say('rest', {}, PRI.HIGH);
        else if (e.type === 'restSoon') say('rest_end', {}, PRI.HIGH);
        else if (e.type === 'pause') say('pause', {}, PRI.NORM);
        else if (e.type === 'resume') say('resume', {}, PRI.NORM);
        else if (e.type === 'gpsLost') say('gps_lost', {}, PRI.NORM);
        else if (e.type === 'oppDone') say('opp_finished', {}, PRI.HIGH);
        else if (e.type === 'setEnd' && inter && !e.last) say(e.win ? 'set_win' : 'set_lose', { set: e.set }, PRI.CRIT);
        else if (e.type === 'finish') {
          if (e.quit) say('quit', {}, PRI.CRIT);
          else if (inter) say(e.wins > e.losses ? 'interval_win' : e.wins < e.losses ? 'interval_lose' : 'draw', {}, PRI.CRIT);
          else { const m = e.margin, close = Math.abs(m) <= 3; say(m > 0 ? (close ? 'win_close' : 'win') : (close ? 'lose_close' : 'lose'), {}, PRI.CRIT); }
        }
      }
      if (snap.phase !== 'run' || snap.frozen) return out;
      const s = this.p.sets[snap.set - 1], early = snap.setS < 6;
      // 추월: 3m 넘게 앞뒤가 바뀌어야 인정한다. 나란히 달릴 때 매초 추월이라고 떠들지 않게
      const sign = gap >= Z.SWAP ? 1 : gap <= -Z.SWAP ? -1 : this.sign;
      if (!early && sign !== this.sign && this.sign !== 0 && !snap.oppDone) { say(sign > 0 ? 'overtake_me' : 'overtaken', {}, PRI.CRIT); this.swapAt = this.t; }
      this.sign = sign;
      // 거리 구간. 4초 머물러야 바뀐 걸로 본다. 같은 구간에 오래 있으면 75초마다 한 마디
      const z = zoneOf(gap);
      if (z === this.cand) this.candN++; else { this.cand = z; this.candN = 1; }
      if (!early && !snap.oppDone && this.candN >= Z.DEBOUNCE_S) {
        if (z !== this.zone) { this.zone = z; this.zoneAt = this.t; if (this.t - this.swapAt > 8) say(z, {}, PRI.HIGH); }
        else if (this.t - this.zoneAt >= Z.REPEAT_S) { this.zoneAt = this.t; say(z, {}, PRI.NORM); }
      }
      // 거리 표지
      const D = s.distM, me = snap.me, F = this.flags;
      if (!inter) { const k = Math.floor(me / 1000); if (k > this.km && me < D - 50) { this.km = k; if (!(D >= 2000 && Math.abs(me - D / 2) < 60)) say('km', { km: k }, PRI.HIGH); } }
      if (D >= 2000 && me >= D / 2 && !F.half) { F.half = 1; say('half', {}, PRI.HIGH); }
      if (D >= 1500 && me >= D - 500 && !F.l500) { F.l500 = 1; say('last_500', {}, PRI.HIGH); }
      if (D >= 300 && me >= D - 100 && !F.l100) { F.l100 = 1; say('last_100', {}, PRI.CRIT); }
      // 페이스 잔소리. 상대와의 거리와 별개로, 목표보다 크게 처지거나 크게 앞서 달리면
      if (snap.myPace !== null) {
        this.slowN = snap.myPace - snap.target >= Z.SLOW_D ? this.slowN + 1 : 0;
        this.fastN = snap.target - snap.myPace >= Z.FAST_D ? this.fastN + 1 : 0;
        if (this.t - this.nagAt >= Z.NAG_CD) {
          if (this.slowN >= Z.SLOW_S) { this.slowN = 0; this.nagAt = this.t; say('my_slow', {}, PRI.NORM); }
          else if (this.fastN >= Z.FAST_S) { this.fastN = 0; this.nagAt = this.t; say('my_fast', {}, PRI.NORM); }
        }
      }
      // 빌드업: 상대 페이스가 15초 빨라질 때마다
      if (this.p.type === 'build' && s.p1 < s.p0) {
        if (this.buildAt === null) this.buildAt = s.p0;
        if (this.buildAt - snap.oppPace >= Z.BUILD_STEP) { this.buildAt = snap.oppPace; say('build_faster', {}, PRI.NORM); }
      }
      if (this.t - this.lastAny >= Z.IDLE_S) say('idle', {}, PRI.NORM);
      return out;
    }
  }

  // ---------- 말로 바꾸기 ----------
  // 대사는 미리 구운 음성으로 튼다. 그래서 변수는 값이 정해진 범위인 둘만 쓴다(web/linebook.py가 값마다 통째로 굽는다)
  const VARS = { km: [1, 41], set: [1, 20] };
  const secText = (s) => { s = Math.abs(s); if (s < 10) return `${Number(s.toFixed(1))}초`; s = Math.round(s); const m = Math.floor(s / 60), r = s % 60; return m ? `${m}분` + (r ? ` ${r}초` : '') : `${r}초`; };   // 10초 안쪽은 소수 한 자리
  const paceText = (p) => { p = Math.round(p); const m = Math.floor(p / 60), r = p % 60; return `${m}분` + (r ? ` ${r}초` : ''); };
  /** 대사에 든 변수와 값. 없으면 null. 구운 조각의 이름(대사|값)을 만들 때 쓴다 */
  function lineVar(line, v) { const m = /\{(km|set)\}/.exec(line); return m && v[m[1]] !== undefined ? v[m[1]] : null; }
  /** 화면과 기기 음성용 문장. {km} → 3킬로, {set} → 2 */
  function fill(line, v) { return line.replace(/\{(km|set)\}/g, (m, k) => (v[k] === undefined ? m : k === 'km' ? `${v[k]}킬로` : `${v[k]}`)); }
  const clipId = (line, v) => { const x = lineVar(line, v); return line + '|' + (x === null ? '' : x); };
  /** 같은 묶음에서 방금 쓴 대사는 다 돌 때까지 다시 안 쓴다 */
  function picker() {
    const bag = {};
    return (key, lines) => {
      if (!lines || !lines.length) return null;
      if (!bag[key] || !bag[key].length) { bag[key] = lines.map((_, i) => i).sort(() => Math.random() - 0.5); }
      return lines[bag[key].pop()];
    };
  }
  return { C, Z, PRI, VARS, plan, paceAt, planTimeS, headM, Game, Talk, zoneOf, fill, lineVar, clipId, picker, secText, paceText };
})();
if (typeof module !== 'undefined') module.exports = GAME;
