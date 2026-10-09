// 러너웨이 공포 모드 소리. 합성음(Web Audio)이 기본이라 파일 없이도 돈다.
// 같은 id의 녹음(web/sounds/<id>_<번호>.mp3)이 있으면 그 소리는 녹음으로 바뀐다. 목록은 LIST, 규격은 web/sounds/README.md
// growl, pounce, howl, ring, drag는 녹음만 있다(합성음 없음). 어떤 녹음 후보를 쓸지는 앱이 정해 넣는다(E.samples, E.synth)
// 실시간(AudioContext)과 오프라인(OfflineAudioContext)에서 같은 코드가 돈다. 검수용 WAV(web/render_sounds.mjs)도 이걸로 굽는다
const SND = (() => {
  // kind: loop = 계속 깔리는 소리, beat = 박자마다 반복, one = 한 번. dur = 미리듣기 길이(초)
  const LIST = [
    { id: 'scene', kind: 'demo', dur: 28, name: '전체 장면', when: '검수용. 추격자가 100m 뒤에서 붙을 때까지', desc: '드론, 바람, 발소리, 울부짖음, 심장, 으르렁, 불협 현, 접근 경고, 숨소리, 덮침을 실제 순서대로 섞었다' },
    { id: 'drone', kind: 'loop', dur: 9, name: '저음 드론', when: '공포모드 내내 깔린다. 가까워질수록 커진다', desc: '41Hz 톱니파 둘을 살짝 어긋나게 겹친 맥놀이 + 서브 + 저역 럼블. 필터가 느리게 숨 쉰다' },
    { id: 'wind', kind: 'loop', dur: 7, name: '바람', when: '공포모드 내내. 정적을 메운다', desc: '브라운 노이즈 + 저역 통과. 돌풍처럼 천천히 일렁인다' },
    { id: 'tension', kind: 'loop', dur: 8, name: '불협 현', when: '추격자가 약 45m 안으로 들어오면 서서히 커진다', desc: '반음씩 붙은 고음 현 네 줄의 떨림 + 저음 단2도. 공포 영화 바이올린' },
    { id: 'step', kind: 'beat', dur: 11, name: '추격자 발소리', when: '달리는 내내 끊기지 않는다. 박자는 설정 페이스의 케이던스, 크기와 밝기는 거리', desc: '무거운 발 쿵. 좌우 발이 번갈아 뒤에서 들린다. 미리듣기는 100m에서 0m까지' },
    { id: 'heart', kind: 'beat', dur: 8, name: '내 심장', when: '달리는 내내. 가까워질수록 빨라진다(70~160bpm)', desc: '쿵쿵 두 박. 미리듣기는 느림에서 빠름까지' },
    { id: 'breath', kind: 'beat', dur: 6, name: '추격자 숨소리', when: '12m 안. 한 번이 끝나면 다음 숨', desc: '낮고 거친 헐떡임. 뒤에서, 바로 귀 뒤에서' },
    { id: 'growl', kind: 'one', dur: 2.2, name: '으르렁', when: '45m 안. 8~20초마다 한 번, 뒤에서. 가까울수록 크다', desc: '큰 짐승의 콧김과 낮은 그르렁' },
    { id: 'tick', kind: 'one', dur: 1.2, name: '카운트다운', when: '출발 3, 2, 1초 전. 인터벌은 회복 끝 3초 전', desc: '낮은 시계 초침' },
    { id: 'bell', kind: 'one', dur: 6, name: '출발 종', when: '출발 순간. 추격자가 움직이기 시작한다', desc: '낮은 G 교회 종. 비배음 배음이 길게 운다' },
    { id: 'close', kind: 'one', dur: 4, name: '접근 경고', when: '20m 안으로 들어오는 순간(35m 밖으로 나가야 다시 울림)', desc: '거꾸로 빨려드는 스웰 뒤 쾅. 진동 함께' },
    { id: 'pounce', kind: 'one', dur: 1.6, name: '덮침 포효', when: '거리 0m. 잡힘과 같이, 반드시', desc: '괴물 포효. 바로 뒤에서 크게' },
    { id: 'caught', kind: 'one', dur: 2.6, name: '잡힘 비명', when: '거리 0m. 잡힌 횟수 +1, 추격자는 다시 뒤로', desc: '찢어지는 비명 + 쾅. 화면 번쩍, 긴 진동' },
    { id: 'gotcha', kind: 'one', dur: 4, name: '잡았다 목소리', when: '잡힐 때 반드시. 포효·비명 1초 뒤, 귀 바로 앞에서', desc: '기괴한 목소리로 "잡았다~"' },
    { id: 'scream', kind: 'one', dur: 2.4, name: '먼 비명', when: '주행 중 가끔(50~110초마다 비명이나 포효 중 하나). 멀리 한쪽에서', desc: '누군가 멀리서 지르는 비명. 쾅 없이 비명만' },
    { id: 'roar', kind: 'one', dur: 1.8, name: '먼 포효', when: '주행 중 가끔(50~110초마다 비명이나 포효 중 하나). 추격자 자리(뒤)에서, 거리만큼 작게', desc: '덮침 포효 녹음과 같은 소리. 녹음이 없으면 조용' },
    { id: 'creak', kind: 'one', dur: 3.5, name: '먼 삐걱임', when: '25m 밖일 때. 35~80초마다 한 번, 왼쪽이나 오른쪽 멀리서', desc: '녹슨 철문이 멀리서 끼익. 좌우 한쪽에서 울린다' },
    { id: 'howl', kind: 'one', dur: 2.4, name: '먼 울부짖음', when: '25m 밖일 때. 삐걱임 대신 가끔, 멀리 한쪽에서', desc: '늑대 하울링이 멀리서 길게' },
    { id: 'ring', kind: 'one', dur: 2.4, name: '방울', when: '25m 밖일 때. 삐걱임 대신 가끔, 한쪽에서', desc: '저승사자 요령이 한 번 울린다' },
    { id: 'drag', kind: 'one', dur: 1.4, name: '발 끄는 소리', when: '25m 밖일 때. 삐걱임 대신 가끔, 한쪽에서', desc: '자갈 위로 발을 질질 끈다' },
    { id: 'whisper', kind: 'one', dur: 2.6, name: '속삭임', when: '25m 안일 때. 삐걱임 대신 35~80초마다 한 번, 귀 옆에서', desc: '숨 섞인 하아아. 말은 없다' },
    { id: 'safe', kind: 'one', dur: 5, name: '잠시 안전', when: '인터벌 세트 끝, 회복 시작. 발소리가 멎는다', desc: '낮은 단조 화음이 천천히 떴다 가라앉는다' },
    { id: 'door', kind: 'one', dur: 4, name: '탈출', when: '목표 거리 완주', desc: '문이 끼익 열리고 쾅 닫힌 뒤 걸쇠가 걸린다' },
  ];
  const BY = Object.fromEntries(LIST.map(x => [x.id, x]));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  function engine(ctx, out) {
    const E = { ctx, samples: {}, synth: {}, last: {}, near: 0, breathAt: 0, spm: 165, stepsOn: false, heartOn: false, nextStep: 0, nextBeat: 0, stepN: 0, holdUntil: 0, loops: {} };
    const sr = ctx.sampleRate, R = Math.random;
    const noise = (sec, brown) => {
      const n = Math.floor(sr * sec), b = ctx.createBuffer(1, n, sr), d = b.getChannelData(0);
      let last = 0; for (let i = 0; i < n; i++) { const w = R() * 2 - 1; if (brown) { last = (last + 0.02 * w) / 1.02; d[i] = last * 3.5; } else d[i] = w; }
      return b;
    };
    const WHITE = noise(2), BROWN = noise(4, true);
    const G = (v, dest) => { const g = ctx.createGain(); g.gain.value = v; if (dest) g.connect(dest); return g; };
    const F = (type, f, q, dest) => { const b = ctx.createBiquadFilter(); b.type = type; b.frequency.value = f; if (q !== undefined) b.Q.value = q; if (dest) b.connect(dest); return b; };
    const O = (type, f, dest) => { const o = ctx.createOscillator(); o.type = type; o.frequency.value = f; if (dest) o.connect(dest); return o; };
    const N = (buf, dest, rate) => { const s = ctx.createBufferSource(); s.buffer = buf || WHITE; if (rate) s.playbackRate.value = rate; if (dest) s.connect(dest); return s; };
    /** 0.0001에서 peak까지 a초에 올라가고 dur초에 사라지는 지수 엔벌로프 */
    const env = (p, t, a, peak, dur) => { p.setValueAtTime(0.0001, t); p.exponentialRampToValueAtTime(Math.max(0.0002, peak), t + a); p.exponentialRampToValueAtTime(0.0001, t + dur); };
    const play = (src, t, dur) => { src.start(t); src.stop(t + dur); };

    // ---------- 버스 ----------
    const lim = ctx.createDynamicsCompressor();          // 합성음이 겹치면 클리핑한다
    lim.threshold.value = -8; lim.knee.value = 4; lim.ratio.value = 12; lim.attack.value = 0.003; lim.release.value = 0.2;
    lim.connect(out);
    E.master = G(0.8, lim);
    // 잔향. 어둡고 긴 야외 공간. 멀수록 직접음보다 잔향이 많이 들린다
    {
      const n = Math.floor(sr * 2.6), pre = Math.floor(sr * 0.03), ir = ctx.createBuffer(2, n, sr);
      for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = pre; i < n; i++) { const t = (i - pre) / sr; d[i] = (R() * 2 - 1) * Math.exp(-t / 0.55) * Math.min(1, t / 0.02); } }
      E.verb = ctx.createConvolver(); E.verb.buffer = ir; E.verb.connect(F('lowpass', 2600, 0.5, E.master));
    }
    E.bgm = G(1, E.master);
    E.ui = G(1, E.master);
    // 추격자 체인: 바로 뒤. 거리 = 크기 + 고음 + 잔향 비율
    E.chaseIn = G(1);
    E.chaseLP = F('lowpass', 800, 0.7);
    E.chaseGain = G(0.05);
    E.chaseIn.connect(E.chaseLP); E.chaseLP.connect(E.chaseGain);
    let tail = E.chaseGain;
    if (typeof ctx.createPanner === 'function') {
      try {
        const p = ctx.createPanner(); p.panningModel = 'HRTF'; p.distanceModel = 'linear'; p.rolloffFactor = 0;
        if (p.positionX) { p.positionX.value = 0; p.positionY.value = 0; p.positionZ.value = 1; } else p.setPosition(0, 0, 1);   // 듣는 사람은 -z를 본다. +z = 바로 뒤
        tail.connect(p); tail = p;
      } catch (e) { }
    }
    tail.connect(E.master);
    E.chaseVerb = G(0.5, E.verb); E.chaseLP.connect(E.chaseVerb);

    /** 좌우 한쪽에서 나는 소리. side -1 왼쪽 ~ +1 오른쪽, far 0 가까움 ~ 1 멀다 */
    function sideOut(side, far) {
      const g = G(1 - 0.75 * far), lp = F('lowpass', 7000 - 5500 * far, 0.7);
      let t = lp; lp.connect(g);
      if (ctx.createStereoPanner) { const p = ctx.createStereoPanner(); p.pan.value = clamp(side, -0.95, 0.95); g.connect(p); t = p; } else t = g;
      t.connect(E.master); const v = G(0.3 + 0.7 * far, E.verb); lp.connect(v);
      return lp;
    }

    // ---------- 녹음 ----------
    // E.samples[id] = 고른 녹음들, E.synth[id] = 합성음도 고름. 둘 다 있으면 매번 무작위(합성음은 녹음 하나와 같은 몫)
    // 아무것도 안 넣은 엔진(E.synth 비어 있음)은 합성음만 낸다. 앱이 고른 것만 넣는다
    E.pickRec = (id) => { const n = (E.samples[id] || []).length; if (!n) return false; return E.synth[id] ? R() < n / (n + 1) : true; };
    E.silent = (id) => E.synth[id] === false && !(E.samples[id] || []).length;   // 다 끔
    /** 같은 id에 녹음이 여러 개면 직전 것과 다른 걸 고른다. 같은 소리 반복이 제일 먼저 질린다 */
    function sample(id) {
      const l = E.samples[id]; if (!l || !l.length) return null;
      let i = Math.floor(R() * l.length); if (l.length > 1 && i === E.last[id]) i = (i + 1) % l.length;
      E.last[id] = i; return l[i];
    }
    /** 녹음 재생. 틀었으면 길이(초), 녹음이 없으면 0 */
    function playSample(id, t, dest, vol) {
      const b = sample(id); if (!b) return 0;
      const s = N(b), g = G(vol === undefined ? 1 : vol, dest); s.connect(g); s.playbackRate.value = 0.95 + R() * 0.1; s.start(t);
      return b.duration || 1;
    }
    /** 받은 바이트를 디코드해 둔다. 실패한 파일은 합성음으로 남는다 */
    E.addSample = (id, bytes) => ctx.decodeAudioData(bytes).then(b => { (E.samples[id] = E.samples[id] || []).push(b); return true; }).catch(() => false);

    // ---------- 합성음 ----------
    const S = {};
    S.step = (t, dest, v) => {
      const k = 0.85 + 0.3 * R();
      const o = O('sine', 105 * k), g = G(0); o.frequency.setValueAtTime(105 * k, t); o.frequency.exponentialRampToValueAtTime(42, t + 0.09);
      env(g.gain, t, 0.004, 0.9 * v, 0.14); o.connect(g); g.connect(dest); play(o, t, 0.16);
      const n = N(WHITE, null, 0.8 + 0.4 * R()), bp = F('bandpass', 1300 + 1500 * R(), 0.9), ng = G(0);
      env(ng.gain, t + 0.004, 0.003, 0.45 * v, 0.08); n.connect(bp); bp.connect(ng); ng.connect(dest); play(n, t, 0.1);
      if (R() < 0.35) { const s = N(WHITE, null, 1.4), hp = F('highpass', 3200), sg = G(0); env(sg.gain, t + 0.05, 0.02, 0.12 * v, 0.16); s.connect(hp); hp.connect(sg); sg.connect(dest); play(s, t + 0.05, 0.2); }   // 가끔 끌린다
    };
    S.heart = (t, dest, v) => {
      for (const [dt, k] of [[0, 1], [0.14, 0.65]]) {
        const o = O('sine', 62), g = G(0); o.frequency.setValueAtTime(62, t + dt); o.frequency.exponentialRampToValueAtTime(34, t + dt + 0.12);
        env(g.gain, t + dt, 0.006, v * k, 0.16); o.connect(g); g.connect(dest); play(o, t + dt, 0.18);
      }
    };
    S.breath = (t, dest, v) => {
      // 들숨(짧고 높게) + 날숨(길고 낮게). 포먼트 두 개를 통과한 노이즈에 목 긁힘(낮은 톱니)을 섞는다
      for (const [dt, len, f1, f2, k] of [[0, 0.32, 1500, 2700, 0.55], [0.36, 0.55, 750, 1250, 1]]) {
        const n = N(WHITE), a = F('bandpass', f1, 2.2), b = F('bandpass', f2, 3), g = G(0);
        n.connect(a); n.connect(b); a.connect(g); b.connect(g); g.connect(dest);
        g.gain.setValueAtTime(0.0001, t + dt); g.gain.exponentialRampToValueAtTime(0.9 * v * k, t + dt + len * 0.35); g.gain.exponentialRampToValueAtTime(0.0001, t + dt + len);
        play(n, t + dt, len + 0.02);
        const r = O('sawtooth', 85 + 20 * R()), rl = F('bandpass', f1, 4), rg = G(0); r.connect(rl); rl.connect(rg); rg.connect(dest);
        rg.gain.setValueAtTime(0.0001, t + dt); rg.gain.exponentialRampToValueAtTime(0.12 * v * k, t + dt + len * 0.4); rg.gain.exponentialRampToValueAtTime(0.0001, t + dt + len);
        play(r, t + dt, len + 0.02);
      }
    };
    S.tick = (t, dest) => {
      const o = O('square', 1150), bp = F('bandpass', 1150, 6), g = G(0); env(g.gain, t, 0.001, 0.5, 0.05); o.connect(bp); bp.connect(g); g.connect(dest); play(o, t, 0.06);
      const n = N(WHITE), hp = F('highpass', 2500), ng = G(0); env(ng.gain, t, 0.001, 0.35, 0.03); n.connect(hp); hp.connect(ng); ng.connect(dest); play(n, t, 0.04);
      const tail = G(0.35, E.verb); g.connect(tail);
    };
    S.bell = (t, dest) => {
      const base = 98;   // G2
      const P = [[0.5, 1, 5.5], [1, 0.8, 4.5], [1.183, 0.5, 3.5], [1.506, 0.45, 3], [2, 0.35, 2.6], [2.514, 0.25, 2], [2.662, 0.2, 1.8], [3.011, 0.15, 1.5], [4.166, 0.1, 1.1]];
      const bus = G(0.32, dest); const v = G(0.5, E.verb); bus.connect(v);
      for (const [r, a, d] of P) for (const det of [-0.7, 0.7]) {
        const o = O('sine', base * r + det), g = G(0); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(a * 0.5, t + 0.006); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
        o.connect(g); g.connect(bus); play(o, t, d + 0.05);
      }
      const n = N(WHITE), bp = F('bandpass', 2400, 1.5), ng = G(0); env(ng.gain, t, 0.001, 0.25, 0.08); n.connect(bp); bp.connect(ng); ng.connect(bus); play(n, t, 0.1);   // 타격음
    };
    S.close = (t, dest) => {
      const T = 1.5;
      // 1) 빨려드는 스웰
      const n = N(WHITE), bp = F('bandpass', 300, 1.2), g = G(0);
      bp.frequency.setValueAtTime(300, t); bp.frequency.exponentialRampToValueAtTime(3200, t + T);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.55, t + T - 0.02); g.gain.setValueAtTime(0.0001, t + T);
      n.connect(bp); bp.connect(g); g.connect(dest); play(n, t, T);
      for (const f of [220, 233, 247]) {
        const o = O('sawtooth', f), lp = F('lowpass', 900), og = G(0); o.frequency.setValueAtTime(f, t); o.frequency.exponentialRampToValueAtTime(f * 2.6, t + T);
        og.gain.setValueAtTime(0.0001, t); og.gain.exponentialRampToValueAtTime(0.09, t + T - 0.02); og.gain.setValueAtTime(0.0001, t + T);
        o.connect(lp); lp.connect(og); og.connect(dest); play(o, t, T);
      }
      // 2) 쾅
      const h = t + T;
      const b = O('sine', 58), bg = G(0); b.frequency.setValueAtTime(58, h); b.frequency.exponentialRampToValueAtTime(28, h + 0.9); env(bg.gain, h, 0.004, 1, 1.1); b.connect(bg); bg.connect(dest); play(b, h, 1.2);
      const c = N(WHITE), cl = F('lowpass', 2200), cg = G(0); env(cg.gain, h, 0.002, 0.7, 0.35); c.connect(cl); cl.connect(cg); cg.connect(dest); play(c, h, 0.4);
      const v = G(0.6, E.verb); cg.connect(v);
      for (const f of [1480, 1568, 1661, 1760]) { const o = O('sawtooth', f), lp = F('lowpass', 4000), og = G(0); env(og.gain, h, 0.005, 0.05, 1.6); o.connect(lp); lp.connect(og); og.connect(dest); og.connect(v); play(o, h, 1.7); }
    };
    /** 비명만. 잡힘(caught)은 여기에 쾅을 더한다. 주행 중 먼 비명(scream)은 이것만 */
    S.scream = (t, dest) => {
      const ws = ctx.createWaveShaper(), cv = new Float32Array(512); for (let i = 0; i < 512; i++) { const x = i / 256 - 1; cv[i] = Math.tanh(4 * x); } ws.curve = cv;
      const f1 = F('bandpass', 1300, 1.4), f2 = F('bandpass', 2700, 2.5), g = G(0); ws.connect(f1); ws.connect(f2); f1.connect(g); f2.connect(g); g.connect(dest);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.75, t + 0.06); g.gain.setValueAtTime(0.75, t + 0.9); g.gain.exponentialRampToValueAtTime(0.0001, t + 1.7);
      const v = G(0.5, E.verb); g.connect(v);
      for (const [f0, f1x] of [[520, 1350], [537, 1420], [790, 1610]]) {
        const o = O('sawtooth', f0), vib = O('sine', 9), vg = G(f1x * 0.04); vib.connect(vg); vg.connect(o.frequency);
        o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(f1x, t + 0.3); o.frequency.setValueAtTime(f1x, t + 0.95); o.frequency.exponentialRampToValueAtTime(f1x * 0.55, t + 1.7);
        const og = G(0.3); o.connect(og); og.connect(ws); play(o, t, 1.75); play(vib, t, 1.75);
      }
      const n = N(WHITE), hp = F('highpass', 1800), ng = G(0); env(ng.gain, t, 0.01, 0.4, 0.5); n.connect(hp); hp.connect(ng); ng.connect(dest); play(n, t, 0.55);
    };
    S.caught = (t, dest) => { S.scream(t, dest); S.boom(t, dest); };
    S.boom = (t, dest) => {
      const b = O('sine', 45), bg = G(0); b.frequency.setValueAtTime(60, t); b.frequency.exponentialRampToValueAtTime(30, t + 1); env(bg.gain, t, 0.005, 1, 1.2); b.connect(bg); bg.connect(dest); play(b, t, 1.3);
    };
    S.creak = (t, dest) => {
      // 스틱슬립: 불규칙한 저주파 펄스열이 좁은 공명 여러 개를 때린다 = 녹슨 경첩
      const len = 2.2, src = O('sawtooth', 24), g = G(0), bus = G(2.5);
      for (let x = 0; x < len; x += 0.04) src.frequency.setValueAtTime(clamp(14 + 30 * Math.sin(x * 2.3) ** 2 + 8 * R(), 10, 60), t + x);
      src.connect(g); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(1, t + 0.25); g.gain.setValueAtTime(1, t + len - 0.5); g.gain.exponentialRampToValueAtTime(0.0001, t + len);
      for (const [f, q, a] of [[540, 30, 1], [1320, 28, 0.7], [2230, 25, 0.5], [3420, 22, 0.3]]) { const b = F('bandpass', f, q), bg = G(a * 1.6); g.connect(b); b.connect(bg); bg.connect(bus); b.frequency.setValueAtTime(f, t); b.frequency.linearRampToValueAtTime(f * 1.08, t + len); }
      bus.connect(dest); play(src, t, len + 0.05);
    };
    S.whisper = (t, dest) => {
      const len = 2.2, n = N(WHITE), hp = F('highpass', 900), g = G(0), bus = G(1.4, dest);
      n.connect(hp);
      for (const [f, q, a, f2] of [[750, 4, 1, 650], [1150, 5, 0.8, 1300], [2600, 6, 0.6, 2400]]) { const b = F('bandpass', f, q), bg = G(a); b.frequency.setValueAtTime(f, t); b.frequency.linearRampToValueAtTime(f2, t + len); hp.connect(b); b.connect(bg); bg.connect(g); }
      g.connect(bus);
      // 음절처럼 세 번 부풀었다 꺼진다
      g.gain.setValueAtTime(0.0001, t);
      [[0, 0.55], [0.6, 0.5], [1.15, 1.0]].forEach(([dt, d]) => { g.gain.exponentialRampToValueAtTime(0.9, t + dt + d * 0.4); g.gain.exponentialRampToValueAtTime(0.02, t + dt + d); });
      g.gain.exponentialRampToValueAtTime(0.0001, t + len);
      play(n, t, len + 0.05);
    };
    S.safe = (t, dest) => {
      const bus = G(0.25, dest), lp = F('lowpass', 900); lp.connect(bus); const v = G(0.6, E.verb); bus.connect(v);
      for (const f of [110, 130.8, 164.8, 220]) for (const det of [-1.2, 1.2]) {
        const o = O('triangle', f + det), g = G(0); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.3, t + 1.4); g.gain.exponentialRampToValueAtTime(0.0001, t + 4.6);
        o.connect(g); g.connect(lp); play(o, t, 4.7);
      }
    };
    S.door = (t, dest) => {
      const c = G(0.6, dest); S.creak(t, c);
      const h = t + 1.7;
      const b = O('sine', 75), bg = G(0); b.frequency.setValueAtTime(75, h); b.frequency.exponentialRampToValueAtTime(34, h + 0.4); env(bg.gain, h, 0.003, 1, 0.5); b.connect(bg); bg.connect(dest); play(b, h, 0.55);
      const n = N(WHITE), lp = F('lowpass', 1600), ng = G(0); env(ng.gain, h, 0.002, 0.8, 0.3); n.connect(lp); lp.connect(ng); ng.connect(dest); play(n, h, 0.35);
      const v = G(0.8, E.verb); ng.connect(v); bg.connect(v);
      const k = h + 0.55, m = O('square', 2200), mb = F('bandpass', 2200, 8), mg = G(0); env(mg.gain, k, 0.001, 0.3, 0.04); m.connect(mb); mb.connect(mg); mg.connect(dest); play(m, k, 0.05);   // 걸쇠
      const m2 = O('square', 1700), mg2 = G(0); env(mg2.gain, k + 0.07, 0.001, 0.25, 0.05); m2.connect(mb); mb.connect(mg2); mg2.connect(dest); play(m2, k + 0.07, 0.06);
    };
    /** 한 번 나는 소리. 녹음이 있으면 녹음, 없으면 합성. o.side/o.far를 주면 좌우 한쪽에서, o.chase면 추격자 자리(뒤, 거리 반영)에서 */
    E.one = (id, o) => {
      o = o || {}; const t = o.at !== undefined ? o.at : ctx.currentTime + 0.02;
      const dest = o.dest || (o.chase ? E.chaseIn : o.side !== undefined ? sideOut(o.side, o.far || 0) : id === 'tick' ? E.ui : E.master);
      if (E.silent(id)) { if (id === 'caught') S.boom(t, dest); return; }
      if (E.pickRec(id) && playSample(id, t, dest, o.vol)) { if (id === 'caught') S.boom(t, dest); return; }   // 잡힘은 녹음 비명이어도 쾅은 같이
      if (S[id]) S[id](t, o.vol !== undefined ? G(o.vol, dest) : dest, o.v === undefined ? 1 : o.v);
    };

    // ---------- 깔리는 소리 ----------
    function loopSample(id, g) { const b = sample(id); if (!b) return null; const s = N(b); s.loop = true; s.connect(g); return [s]; }
    const LOOPS = {
      drone(g) {
        const lp = F('lowpass', 160, 4, g), srcs = [];
        for (const f of [41.2, 41.2 * 1.012]) { const o = O('sawtooth', f, lp); srcs.push(o); }
        const sub = O('sine', 27.5), sg = G(0.5, g); sub.connect(sg); srcs.push(sub);
        const lfo = O('sine', 0.07), lg = G(70); lfo.connect(lg); lg.connect(lp.frequency); srcs.push(lfo);
        const n = N(BROWN), nl = F('lowpass', 140), ng = G(0.5, g); n.loop = true; n.connect(nl); nl.connect(ng); srcs.push(n);
        return srcs;
      },
      wind(g) {
        const n = N(BROWN), lp = F('lowpass', 420, 0.8, g); n.loop = true; n.connect(lp);
        const lfo = O('sine', 0.11), lg = G(180); lfo.connect(lg); lg.connect(lp.frequency);
        const n2 = N(WHITE, null, 0.5), bp = F('bandpass', 900, 0.6), g2 = G(0.04, g); n2.loop = true; n2.connect(bp); bp.connect(g2); const l2 = O('sine', 0.05), lg2 = G(400); l2.connect(lg2); lg2.connect(bp.frequency);
        return [n, lfo, n2, l2];
      },
      tension(g) {
        const srcs = [], bp = F('bandpass', 1300, 0.6), hi = G(0.5, g); bp.connect(hi);
        [1046.5, 1108.7, 1174.7, 1244.5].forEach((f, i) => {
          const o = O('triangle', f, bp), v = O('sine', 5 + i * 0.6), vg = G(7); v.connect(vg); vg.connect(o.frequency);
          srcs.push(o, v);
        });
        const lo = F('lowpass', 700, 1, G(0.5, g));
        for (const f of [73.4, 77.8]) srcs.push(O('sawtooth', f, lo));
        const tr = O('sine', 0.8), tg = G(0.25); tr.connect(tg); tg.connect(hi.gain); srcs.push(tr);
        return srcs;
      },
    };
    /** 깔리는 소리를 켠다. level은 AudioParam. 녹음이 있으면 녹음을 반복 재생 */
    E.loop = (id, at) => {
      if (E.loops[id]) return E.loops[id];
      const t = at !== undefined ? at : ctx.currentTime, g = G(0, E.bgm);
      const srcs = E.silent(id) ? [] : (E.pickRec(id) && loopSample(id, g)) || LOOPS[id](g);
      for (const s of srcs) s.start(t);
      return (E.loops[id] = { level: g.gain, stop(t2) { const w = t2 !== undefined ? t2 : ctx.currentTime; g.gain.cancelScheduledValues(w); g.gain.setValueAtTime(g.gain.value, w); g.gain.linearRampToValueAtTime(0, w + 1.2); for (const s of srcs) try { s.stop(w + 1.3); } catch (e) { } delete E.loops[id]; } });
    };
    E.stopLoops = (at) => { for (const k of Object.keys(E.loops)) E.loops[k].stop(at); };

    // ---------- 거리 → 소리 ----------
    const LV = {   // near 0(100m 밖) ~ 1(붙음)
      chase: (n) => 0.03 + 0.97 * n * n,
      lp: (n) => 450 + 7500 * n * n,
      verb: (n) => 0.12 + 0.55 * (1 - n),
      drone: (n) => 0.12 + 0.3 * n,          // 깔리는 소리는 발소리를 덮으면 안 된다
      tension: (n) => 0.25 * clamp((n - 0.55) / 0.45, 0, 1),
      bpm: (n) => 70 + 90 * Math.pow(n, 1.4),
      heart: (n) => 0.12 + 0.45 * n,
    };
    E.LV = LV;
    /** 거리 반영. ramp를 주면 at 시각까지 직선으로(미리듣기), 아니면 부드럽게 따라간다(실시간) */
    E.setNear = (near, at, ramp) => {
      near = clamp(near, 0, 1); E.near = near;
      const t = at !== undefined ? at : ctx.currentTime;
      const set = (p, v) => { if (ramp) p.linearRampToValueAtTime(v, t); else p.setTargetAtTime(v, t, 0.35); };
      set(E.chaseGain.gain, LV.chase(near)); set(E.chaseLP.frequency, LV.lp(near)); set(E.chaseVerb.gain, LV.verb(near));
      if (E.loops.drone) set(E.loops.drone.level, LV.drone(near));
      if (E.loops.tension) set(E.loops.tension.level, LV.tension(near));
    };
    /** 미리듣기용. t0~t1 동안 거리 곡선을 0.25초 간격 점으로 찍는다(직선 하나로 이으면 거리감이 틀린다) */
    function rampNear(t0, t1, nearAt) {
      const P = [[E.chaseGain.gain, LV.chase], [E.chaseLP.frequency, LV.lp], [E.chaseVerb.gain, LV.verb]];
      for (const [p, f] of P) { p.cancelScheduledValues(t0); p.setValueAtTime(f(nearAt(t0)), t0); for (let t = t0 + 0.25; t <= t1; t += 0.25) p.linearRampToValueAtTime(f(nearAt(t)), t); }
    }
    /** 발소리와 심장을 until 시각까지 미리 예약한다. 실시간은 60ms마다 0.3초 앞까지, 미리듣기는 한 번에 끝까지.
     *  nearAt(t)를 주면 시각별 거리를 쓴다(미리듣기의 접근 연출) */
    E.pump = (until, nearAt) => {
      const now = ctx.currentTime;
      if (E.nextStep < now) E.nextStep = now + 0.02;
      if (E.nextBeat < now) E.nextBeat = now + 0.02;
      while (E.nextStep < until) {
        const t = E.nextStep, n = nearAt ? nearAt(t) : E.near;
        if (E.stepsOn && t >= E.holdUntil) {
          E.stepN++;
          const sp = ctx.createStereoPanner ? ctx.createStereoPanner() : null, d = sp || E.chaseIn;   // 왼발 오른발
          if (sp) { sp.pan.value = E.stepN % 2 ? -0.14 : 0.14; sp.connect(E.chaseIn); }
          if (!E.silent('step') && !(E.pickRec('step') && playSample('step', t, d, 0.6 + 0.4 * n))) S.step(t, d, 0.6 + 0.4 * n);
          if (n > 0.88 && t >= E.breathAt && !E.silent('breath')) E.breathAt = t + 0.25 + ((E.pickRec('breath') && playSample('breath', t, E.chaseIn, 0.9)) || (S.breath(t, E.chaseIn, 0.5 + 0.5 * n), 0.95));
        }
        E.nextStep += (60 / E.spm) * (1 + (R() - 0.5) * 0.05);
      }
      while (E.nextBeat < until) {
        const t = E.nextBeat, n = nearAt ? nearAt(t) : E.near;
        if (E.heartOn && !E.silent('heart')) { if (!(E.pickRec('heart') && playSample('heart', t, E.master, LV.heart(n)))) S.heart(t, E.master, LV.heart(n)); }
        E.nextBeat += 60 / LV.bpm(n);
      }
    };
    /** 실시간 예약 루프 */
    E.run = () => { if (E.timer) return; E.timer = setInterval(() => E.pump(ctx.currentTime + 0.3), 60); };
    E.halt = () => { clearInterval(E.timer); E.timer = null; };
    /** 페이스(초/km) → 발 박자(걸음/분). 6:00/km 약 165, 4:00/km 약 180 */
    E.cadence = (paceS) => clamp(150 + (3600 / paceS - 8) * 4.5, 150, 190);

    // ---------- 미리듣기 ----------
    /** 검수 화면과 WAV 굽기가 같이 쓴다. 길이(초)를 돌려준다 */
    E.demo = (id) => {
      const t0 = ctx.currentTime + 0.05, it = BY[id]; if (!it) return 0;
      const end = t0 + it.dur;
      if (it.kind === 'one') {
        const far = { creak: 0.7, howl: 0.8, ring: 0.5, drag: 0.4, scream: 0.75 };
        if (far[id] !== undefined) E.one(id, { at: t0, side: -0.8, far: far[id] });
        else if (id === 'whisper') E.one(id, { at: t0, side: 0.7, far: 0.1 });
        else if (id === 'growl' || id === 'roar') { E.setNear(0.75, t0); E.one(id, { at: t0, chase: true }); }
        else E.one(id, { at: t0 });
        return it.dur;
      }
      if (id === 'drone' || id === 'wind' || id === 'tension') {
        const l = E.loop(id, t0); l.level.setValueAtTime(0, t0);
        const top = id === 'drone' ? LV.drone(1) : id === 'tension' ? LV.tension(1) : 0.35;
        l.level.linearRampToValueAtTime(top * (id === 'drone' ? 0.45 : 0.6), t0 + 1.5); l.level.linearRampToValueAtTime(top, end - 2);
        l.stop(end - 1.3); return it.dur;
      }
      if (id === 'step' || id === 'breath') {
        const nearAt = id === 'step' ? (t) => clamp((t - t0) / (it.dur - 1), 0, 1) : () => 1;
        E.spm = 168; E.stepsOn = true; E.heartOn = false; E.nextStep = t0;
        rampNear(t0, end, nearAt);
        E.pump(end - 0.6, nearAt); E.stepsOn = false; return it.dur;
      }
      if (id === 'heart') { E.heartOn = true; E.stepsOn = false; E.nextBeat = t0; E.pump(end - 0.4, (t) => clamp((t - t0) / (it.dur - 1), 0, 1)); E.heartOn = false; return it.dur; }
      if (id === 'scene') {
        // 실제 주행과 같은 순서: 종 → 발소리가 100m에서 다가온다 → 20m에서 접근 경고 → 0m 잡힘
        const run0 = t0 + 3, catchAt = end - 5, nearAt = (t) => clamp((t - run0) / (catchAt - run0), 0, 1);
        const d = E.loop('drone', t0), w = E.loop('wind', t0), te = E.loop('tension', t0);
        d.level.setValueAtTime(0, t0); d.level.linearRampToValueAtTime(LV.drone(0), t0 + 2);
        w.level.setValueAtTime(0, t0); w.level.linearRampToValueAtTime(0.3, t0 + 2);
        te.level.setValueAtTime(0, t0);
        for (let t = run0; t <= catchAt; t += 0.5) { const n = nearAt(t); d.level.linearRampToValueAtTime(LV.drone(n), t); te.level.linearRampToValueAtTime(LV.tension(n), t); }
        te.level.linearRampToValueAtTime(0, catchAt + 0.3);
        E.one('bell', { at: t0 + 0.3 });
        E.one('creak', { at: run0 + 3, side: -0.8, far: 0.8 });
        rampNear(t0, catchAt, (t) => (t < run0 ? 0 : nearAt(t)));
        E.spm = 168; E.stepsOn = true; E.heartOn = true; E.nextStep = run0; E.nextBeat = run0;
        E.pump(catchAt, nearAt); E.stepsOn = false; E.heartOn = false;
        const closeAt = run0 + (catchAt - run0) * 0.8 - 1.5;   // 20m = near 0.8 지점에 쾅이 맞도록
        E.one('close', { at: closeAt });
        E.one('howl', { at: run0 + 6, side: 0.85, far: 0.85 });
        E.one('scream', { at: run0 + 10, side: -0.9, far: 0.75 });
        E.one('growl', { at: run0 + (catchAt - run0) * 0.5, chase: true });
        E.one('whisper', { at: run0 + (catchAt - run0) * 0.62, side: 0.75, far: 0.1 });
        E.one('pounce', { at: catchAt }); E.one('caught', { at: catchAt + 0.2 }); E.one('gotcha', { at: catchAt + 1.2 });
        d.stop(end - 1.4); w.stop(end - 1.4); te.stop(end - 1.4);
        return it.dur;
      }
      return 0;
    };
    return E;
  }
  // 합성음이 없는 소리(녹음만). 앱 검수 화면이 '합성음' 후보를 빼는 데 쓴다
  const NOSYN = ['growl', 'pounce', 'roar', 'howl', 'ring', 'drag', 'gotcha'];
  // 같은 녹음 후보를 쓰는 소리. 먼 포효 = 덮침 포효 녹음, 잡힘 = 비명 녹음
  const POOL = { roar: 'pounce', caught: 'scream' };
  return { LIST, BY, engine, NOSYN, POOL };
})();
if (typeof module !== 'undefined') module.exports = SND;
