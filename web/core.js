// 러너웨이 코어 (JS). sim/runaway_sim, core/ Kotlin과 동일 규칙·정수 연산. 골든 테스트로 일치 검증.
const RW = (() => {
  const fl = Math.floor;

  // ---------- Animal ----------
  function cycleParams(a, n) {
    let sp = a.sprintCms, du = a.sprintS, rc = a.recoverS;
    for (let i = 0; i < n; i++) { sp = fl(sp * a.dvPm / 1000); du = fl(du * a.dtPm / 1000); rc = fl(rc * a.gPm / 1000); }
    return [sp, Math.max(du, 1), Math.max(rc, 2)];
  }

  // ---------- Enemy ----------
  const ROAM = 'roam', SPRINT = 'sprint', TIRED = 'tired', RECOVER = 'recover', LOST = 'lost';
  const ROAM_PM = 800, TIRED_PM = 500, LOST_ACC_M = 40;
  class Enemy {
    constructor(animal, startGapCm) {
      this.a = animal; this.gap = startGapCm; this.state = ROAM; this.cycle = 0; this.timer = 0;
      this.speed = 0; this.sprints = 0; this.movedTotal = 0;
      [this.sp, this.du, this.rc] = cycleParams(animal, 0);
    }
    startSprint() { [this.sp, this.du, this.rc] = cycleParams(this.a, this.cycle); this.state = SPRINT; this.timer = this.du; this.sprints++; }
    reposition(gapCm, afterHit = false) {
      this.gap = gapCm;
      if (afterHit && !this.a.constant) { this.state = TIRED; this.timer = fl(this.rc / 2); }
      else { this.state = ROAM; this.timer = 0; }
    }
    clampGapAtLeast(g) { if (this.gap < g) this.gap = g; }
    tick(adv, accM, { frozen = false, forceChase = false, stalkCms = null, canDetect = true } = {}) {
      const a = this.a;
      if (frozen) { this.speed = 0; this.gap = Math.max(0, this.gap + adv); return this.state; }
      if (accM > LOST_ACC_M && !forceChase) { this.speed = 0; this.gap = Math.max(0, this.gap + adv); return LOST; }
      if (a.constant) { this.speed = a.cruiseCms; this.state = ROAM; }
      else {
        const detected = forceChase || (canDetect && this.gap <= a.detectCm);
        if (this.state === ROAM) {
          this.speed = stalkCms !== null ? stalkCms : fl(a.cruiseCms * ROAM_PM / 1000);
          if (detected) { this.startSprint(); this.speed = this.sp; }
        } else if (this.state === SPRINT) {
          this.speed = this.sp; this.timer--;
          if (this.timer <= 0) { this.state = TIRED; this.timer = fl(this.rc / 2); }
        } else if (this.state === TIRED) {
          this.speed = fl(a.cruiseCms * TIRED_PM / 1000); this.timer--;
          if (this.timer <= 0) { this.state = RECOVER; this.timer = this.rc - fl(this.rc / 2); }
        } else if (this.state === RECOVER) {
          this.speed = a.cruiseCms; this.timer--;
          if (this.timer <= 0) { this.cycle++; if (detected) { this.startSprint(); this.speed = this.sp; } else this.state = ROAM; }
        }
      }
      this.movedTotal += this.speed;
      this.gap = Math.max(0, this.gap + adv - this.speed);
      return this.state;
    }
  }

  // ---------- Threat ----------
  const T = { ENTER_CM: 3000, EXIT_CM: 5000, FILL: 250, DECAY: 500, ACC_SLOW: 25, ACC_FREEZE: 40, INVULN: 3, HIT_PENALTY_S: 30, RESPAWN_GAP_CM: 20000, MAX_HITS: 3 };
  class Threat {
    constructor() { this.inside = false; this.gauge = 0; this.hits = 0; this.invuln = 0; this.lowAccTicks = 0; }
    tick(gapCm, accM, active = true) {
      if (gapCm <= T.ENTER_CM) this.inside = true; else if (gapCm >= T.EXIT_CM) this.inside = false;
      if (this.invuln > 0) this.invuln--;
      if (accM > T.ACC_FREEZE) { this.lowAccTicks++; return false; }
      const rate = accM <= T.ACC_SLOW ? T.FILL : fl(T.FILL / 2);
      this.gauge = (this.inside && active && this.invuln === 0) ? Math.min(1000, this.gauge + rate) : Math.max(0, this.gauge - T.DECAY);
      if (this.gauge >= 1000) { this.gauge = 0; this.hits++; this.invuln = T.INVULN; return true; }
      return false;
    }
  }

  // ---------- Gpx / TrackBuilder ----------
  const G = { GATE_ACC_M: 30, GATE_SPEED_MS: 8, DROPOUT_S: 20, SMOOTH_ALPHA: 0.35, JUMP_RESET_N: 3 };
  const R = 6371000;
  function haversineM(lat1, lon1, lat2, lon2) {
    const p1 = lat1 * Math.PI / 180, p2 = lat2 * Math.PI / 180, dp = p2 - p1, dl = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dp / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(a));
  }
  // round half to even (Python round / Kotlin round)
  function rhe(x) { const r = Math.round(x); if (Math.abs(x % 1) === 0.5) return (r % 2 === 0) ? r : r - 1; return r; }
  class TrackBuilder {
    constructor() { this.dist = 0; this.slat = NaN; this.slon = NaN; this.plat = NaN; this.plon = NaN; this.ignored = 0; this.lastLat = NaN; this.lastLon = NaN; }
    push(t, lat, lon, acc) {
      // 정확도 게이트를 먼저. 나쁜 점이 평활화 시드가 되면 좌표가 통째로 날아간다
      if (acc > G.GATE_ACC_M) return { t, distCm: rhe(this.dist * 100), speedCms: 0, accM: acc };
      if (Number.isNaN(this.slat)) { this.slat = lat; this.slon = lon; this.plat = lat; this.plon = lon; }
      this.slat = G.SMOOTH_ALPHA * lat + (1 - G.SMOOTH_ALPHA) * this.slat;
      this.slon = G.SMOOTH_ALPHA * lon + (1 - G.SMOOTH_ALPHA) * this.slon;
      this.lastLat = this.slat; this.lastLon = this.slon;
      let step = haversineM(this.plat, this.plon, this.slat, this.slon);
      if (step > G.GATE_SPEED_MS) { this.ignored++; if (this.ignored >= G.JUMP_RESET_N) { this.plat = this.slat; this.plon = this.slon; this.ignored = 0; } step = 0; }
      else { this.ignored = 0; this.plat = this.slat; this.plon = this.slon; }
      this.dist += step;
      return { t, distCm: rhe(this.dist * 100), speedCms: rhe(step * 100), accM: acc };
    }
  }
  function parseGpx(xml) {
    const out = []; let t0 = null;
    const re = /<trkpt[^>]*lat="([^"]+)"[^>]*lon="([^"]+)"[^>]*>([\s\S]*?)<\/trkpt>/g; let m;
    while ((m = re.exec(xml))) {
      const body = m[3]; const tm = /<time>([^<]+)<\/time>/.exec(body); if (!tm) continue;
      const ms = Date.parse(tm[1].trim()); if (t0 === null) t0 = ms;
      const am = /<accuracy>([^<]+)<\/accuracy>/.exec(body), hm = /<hdop>([^<]+)<\/hdop>/.exec(body);
      const acc = am ? parseFloat(am[1]) : hm ? parseFloat(hm[1]) * 5 : 8;
      out.push({ t: (ms - t0) / 1000, lat: parseFloat(m[1]), lon: parseFloat(m[2]), acc });
    }
    return out;
  }
  function resample1Hz(raw) {
    const out = []; let i = 0; const tEnd = fl(raw[raw.length - 1].t);
    for (let t = 0; t <= tEnd; t++) {
      while (i + 1 < raw.length && raw[i + 1].t <= t) i++;
      const a = raw[i];
      if (i + 1 < raw.length) {
        const b = raw[i + 1];
        if (b.t - a.t > G.DROPOUT_S && t > a.t) { out.push({ t, lat: a.lat, lon: a.lon, acc: 99 }); continue; }
        let f = b.t === a.t ? 0 : (t - a.t) / (b.t - a.t); f = Math.max(0, Math.min(1, f));
        out.push({ t, lat: a.lat + (b.lat - a.lat) * f, lon: a.lon + (b.lon - a.lon) * f, acc: a.acc + (b.acc - a.acc) * f });
      } else out.push({ t, lat: a.lat, lon: a.lon, acc: a.acc });
    }
    return out;
  }
  function loadTrack(xml) { const b = new TrackBuilder(); return resample1Hz(parseGpx(xml)).map(p => b.push(fl(p.t), p.lat, p.lon, p.acc)); }

  // ---------- Session (streaming) ----------
  const S = { WARMUP_S: 180, WARMUP_MIN_GAP_CM: 10000, COOLDOWN_PCT: 87, START_GAP_EXTRA_CM: 10000, REENGAGE_INSIDE_CM: 2000, PAUSE_SPEED_CMS: 100, PAUSE_AFTER_S: 8, PAUSE_CAP_S: 180 };
  class Session {
    constructor(animal, courseCm) {
      this.a = animal; this.courseCm = courseCm;
      this.enemy = new Enemy(animal, animal.detectCm + S.START_GAP_EXTRA_CM);
      this.warmGap = Math.min(S.WARMUP_MIN_GAP_CM, animal.detectCm - S.REENGAGE_INSIDE_CM);
      this.threat = new Threat();
      this.prevDist = 0; this.elapsed = 0; this.slow = 0; this.lastCycle = 0; this.recent = [];
      this.hits = 0; this.failed = false; this.moving = 0; this.paused = 0; this.dist = 0; this.minGap = null;
      this.enemyMoved = 0; this.enemyActive = 0; this.lost = 0; this.reengages = 0; this.done = false; this.first = true;
    }
    tick(row) {
      if (this.first) { this.prevDist = row.distCm; this.first = false; }
      const adv = row.distCm - this.prevDist; this.prevDist = row.distCm; this.elapsed++;
      this.recent.push(row.speedCms); if (this.recent.length > 5) this.recent.shift();
      const avg = fl(this.recent.reduce((x, y) => x + y, 0) / this.recent.length);
      if (avg < S.PAUSE_SPEED_CMS) this.slow++; else this.slow = 0;
      const paused = this.slow >= S.PAUSE_AFTER_S; if (paused) this.paused++; else this.moving++;
      const warmup = this.elapsed <= S.WARMUP_S;
      const cooldown = row.distCm >= fl(this.courseCm * S.COOLDOWN_PCT / 100);
      const frozen = paused || cooldown;
      let stalk = null;
      if (warmup && this.enemy.gap > this.warmGap) { const rem = Math.max(1, S.WARMUP_S - this.elapsed + 1); stalk = adv + Math.max(20, fl((this.enemy.gap - this.warmGap) / rem)); }
      const state = this.enemy.tick(adv, row.accM, { frozen, stalkCms: stalk, canDetect: !warmup });
      if (warmup) this.enemy.clampGapAtLeast(this.warmGap);
      const ev = { sprintStart: false, hit: false, reengage: false, state };
      if (this.enemy.cycle > this.lastCycle) { this.lastCycle = this.enemy.cycle; if (!warmup && !frozen && this.enemy.gap > this.a.detectCm) { this.enemy.reposition(this.a.detectCm - S.REENGAGE_INSIDE_CM); this.reengages++; ev.reengage = true; } }
      if (!frozen) { this.enemyActive++; this.enemyMoved += this.enemy.speed; }
      if (state === LOST) this.lost++;
      const hit = this.threat.tick(this.enemy.gap, row.accM, !warmup && !frozen);
      if (hit) { this.hits++; this.enemy.reposition(T.RESPAWN_GAP_CM, true); if (this.hits >= T.MAX_HITS) this.failed = true; ev.hit = true; }
      if (this.minGap === null || this.enemy.gap < this.minGap) this.minGap = this.enemy.gap;
      this.dist = row.distCm; if (row.distCm >= this.courseCm) this.done = true;
      return { t: row.t, playerCms: row.speedCms, distCm: row.distCm, state: this.enemy.state, enemyCms: this.enemy.speed, gapCm: this.enemy.gap, gauge: this.threat.gauge, hits: this.hits, failed: this.failed, paused, warmup, cooldown, accM: row.accM, cycle: this.enemy.cycle, done: this.done, ev };
    }
    get penaltyS() { return this.hits * T.HIT_PENALTY_S; }
    get excessPauseS() { return Math.max(0, this.paused - S.PAUSE_CAP_S); }
    get finalTimeS() { return this.moving + this.excessPauseS + this.penaltyS; }
  }
  function runTrack(track, animal, courseCm) { const s = new Session(animal, courseCm); for (const r of track) { s.tick(r); if (s.done) break; } s.sprints = s.enemy.sprints; return s; }

  return { cycleParams, Enemy, Threat, TrackBuilder, parseGpx, resample1Hz, loadTrack, haversineM, Session, runTrack, S, T, G, states: { ROAM, SPRINT, TIRED, RECOVER, LOST } };
})();
if (typeof module !== 'undefined') module.exports = RW;
