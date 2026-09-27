"""관제 음성 생성기. Qwen3-TTS를 Modal GPU에서 돌려 wav 후보를 받는다 → bake.py가 고르고 팩을 만든다

- 이 컴퓨터(CPU)는 키를 나눠 보내고 받기만 한다. 후처리·선택·팩은 bake.py(VOICE_SRC)
- 모델 3개(CustomVoice, VoiceDesign, Base)는 Modal Volume에 한 번만 받는다
- 한 목소리가 최우선. 문장마다 VoiceDesign으로 새 목소리를 만들지 않는다
  - A: CustomVoice 내장 화자 고정(Sohee, 한국어 여성). 감정은 instruct
  - B: VoiceDesign으로 관제사 목소리를 감정별 참조로 한 번 만들고(--refs), Base로 복제. 감정별 참조는 중립 참조와 화자 임베딩이 가장 가까운 것
  - C: CustomVoice 남성 화자 + 한국어. 감정은 instruct. 외국인 억양 위험은 bake.py의 ASR 점수로 거른다
- 감정: instruct = lines.MOOD[mood_of(key)]['en']. B는 그 감정의 참조 음성
- 끊겨도 이어서: 이미 있는 <키>__<번호>.wav는 건너뛴다. 받는 대로 쓴다
- 앱은 임시 앱(app.run)이라 끝나면 멈춘다. 끝에 modal app stop으로 한 번 더 확인한다. GPU를 켜 둔 채 기다리지 않는다

준비
  pip install modal
  modal token set  (또는 환경 변수 MODAL_TOKEN_ID, MODAL_TOKEN_SECRET)
실행
  python3 web/voice/qwen_modal.py --download                          # 모델을 Volume에 받는다(1회, CPU)
  python3 web/voice/qwen_modal.py --method A --n 3                    # 405키 × 후보 3 → web/voice/src/<키>__<번호>.wav
  python3 web/voice/qwen_modal.py --method A --keys @audition --out web/voice/audition/A/src
  python3 web/voice/qwen_modal.py --refs --voice op1 --out web/voice/audition/B/refs   # 방식 B 참조(감정 6개) 만들기
  python3 web/voice/qwen_modal.py --refs --voice op1 --moods urgent --k 10            # 한 감정만 다시(나머지 참조는 둔다)
  python3 web/voice/qwen_modal.py --method B --voice op1 --keys hold,spotted --n 3
  python3 web/voice/qwen_modal.py --probe                             # CustomVoice 남성 화자 비교(방식 C 화자 고르기)
  python3 web/voice/qwen_modal.py --bill                              # 실행별 실제 청구 금액(오늘부터)
옵션: --keys 키,키 | @audition | @all(기본)  --n 후보 수  --gpu L4|A10G  --workers 동시 컨테이너 수
"""
import os, sys, io, json, time, re, argparse, hashlib, subprocess

import modal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

APP_NAME = 'runaway-qwen-tts'
GPU = os.environ.get('QWEN_GPU', 'L4')
MODELS = {'custom': 'Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice', 'design': 'Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign', 'base': 'Qwen/Qwen3-TTS-12Hz-1.7B-Base'}
MALE = ['Uncle_Fu', 'Dylan', 'Eric', 'Ryan', 'Aiden']
SPEAKER = {'A': 'Sohee', 'C': os.environ.get('QWEN_MALE', 'Ryan')}
# 방식 B 관제사 목소리(README 초안). 감정 문구는 MOOD의 en을 뒤에 붙인다
VOICE_DESC = ('Korean. A Korean man in his thirties working as a field radio controller. Mid-low baritone, crisp and clear articulation. '
              'Not a broadcast announcer: a man watching danger unfold on a screen and speaking into a radio.')
# 감정별 참조 문장. 앱 대사와 같은 말투의 새 문장(5~8초). 복제는 이 말투를 따라간다
REF_TEXT = {
    'calm': '여기는 러너웨이 관제. 녀석들은 아직 풀숲에 있다. 호흡을 고르고 천천히 페이스를 올려라.',
    'tense': '한 마리가 돌아왔다. 오른쪽 뒤, 백 미터. 시속 삼십 킬로. 속도 유지해.',
    'urgent': '뒤에서 온다! 지금 뛰어! 멈추지 마, 계속 달려!',
    'eager': '지쳤다! 녀석이 헐떡인다. 지금이야, 밀어붙여! 더 벌려!',
    'triumph': '도착! 해냈다, 탈출 성공이다. 한 번도 안 잡혔다. 잘했다!',
    'grim': '잡혔다. 탈출 실패다. 오늘은 여기까지다.',
}
AUDITION = ['intro_head', 'name_cheetah', 'cnt1', 'intro_hide', 'intro_max', 'kmh100', 'intro_tail', 'spotted', 'dc_rb', 'kmh35', 'hold', 'again', 'dx_l',
            'kmh28', 'dr_lb', 'm120', 'tired1', 'caught1', 'hit2', 'half1', 'cool', 'end_arrive', 'end_hits0', 'end_final', 'n12', 'unit_min', 'n30', 'unit_sec', 'end_fail']

app = modal.App(APP_NAME)
vol = modal.Volume.from_name('runaway-qwen-tts', create_if_missing=True)
image = (modal.Image.debian_slim(python_version='3.12')
         .apt_install('sox', 'libsox-fmt-all', 'ffmpeg')
         .pip_install('torch==2.8.0', 'torchaudio==2.8.0', 'qwen-tts==0.1.1', 'hf_transfer==0.1.9')
         .env({'HF_HOME': '/models/hf', 'HF_HUB_ENABLE_HF_TRANSFER': '1', 'TOKENIZERS_PARALLELISM': 'false'}))


def local_dir(name): return '/models/' + MODELS[name].split('/')[1]


@app.function(image=image, volumes={'/models': vol}, timeout=3600, cpu=4, memory=8192)
def download():
    """세 모델을 Volume에 받는다. 이미 있으면 건너뛴다"""
    from huggingface_hub import snapshot_download
    out = {}
    for k, repo in MODELS.items():
        d = local_dir(k)
        if not os.path.exists(os.path.join(d, 'model.safetensors')) or not os.path.exists(os.path.join(d, 'speech_tokenizer', 'model.safetensors')):
            snapshot_download(repo, local_dir=d)
        out[k] = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(d) for f in fs) // 2 ** 20
    vol.commit()
    return out


def wav_bytes(x, sr):
    import numpy as np, soundfile as sf
    b = io.BytesIO(); sf.write(b, np.asarray(x, dtype='float32'), sr, format='WAV', subtype='PCM_16'); return b.getvalue()


@app.cls(image=image, gpu=GPU, volumes={'/models': vol}, timeout=3600, scaledown_window=20, max_containers=4)
class TTS:
    @modal.enter()
    def boot(self):
        self.t_enter = time.time()
        self.m = {}
        self.prompts = {}
        self.load_s = 0.0

    def model(self, name):
        if name not in self.m:
            import torch
            from qwen_tts import Qwen3TTSModel
            t = time.time()
            if not os.path.exists(os.path.join(local_dir(name), 'model.safetensors')):
                raise RuntimeError(f'모델이 Volume에 없다: {name}. 먼저 --download')
            self.m[name] = Qwen3TTSModel.from_pretrained(local_dir(name), device_map='cuda:0', dtype=torch.bfloat16, attn_implementation='sdpa')
            self.load_s += time.time() - t
        return self.m[name]

    def stamp(self, t0):
        return {'task': os.environ.get('MODAL_TASK_ID', ''), 't_enter': self.t_enter, 't_end': time.time(), 'gen_s': time.time() - t0, 'load_s': self.load_s}

    @modal.method()
    def gen(self, job):
        """job: {method, speaker, voice, seed, idx, items:[{key, text, instruct, mood}]} → 후보 1벌(items 순서대로 wav)"""
        import torch
        t0 = time.time()
        items = job['items']
        texts = [it['text'] for it in items]
        torch.manual_seed(job['seed']); torch.cuda.manual_seed_all(job['seed'])
        if job['method'] in ('A', 'C'):
            wavs, sr = self.model('custom').generate_custom_voice(text=texts, language=['Korean'] * len(texts), speaker=[job['speaker']] * len(texts),
                                                                  instruct=[it['instruct'] for it in items])
        else:
            prompt = self.prompt(job['voice'], items[0]['mood'])   # 한 묶음은 한 감정
            wavs, sr = self.model('base').generate_voice_clone(text=texts, language=['Korean'] * len(texts), voice_clone_prompt=prompt * len(texts))
        out = [{'key': it['key'], 'idx': job['idx'], 'wav': wav_bytes(w, sr), 'sec': len(w) / sr} for it, w in zip(items, wavs)]
        return {'out': out, 'stat': self.stamp(t0)}

    def prompt(self, voice, mood):
        k = (voice, mood)
        if k not in self.prompts:
            import soundfile as sf
            d = f'/models/refs/{voice}'
            meta = json.load(open(f'{d}/refs.json', encoding='utf-8'))
            x, sr = sf.read(f'{d}/{mood}.wav', dtype='float32')
            self.prompts[k] = self.model('base').create_voice_clone_prompt(ref_audio=(x, sr), ref_text=meta[mood]['text'], x_vector_only_mode=False)
        return self.prompts[k]

    @modal.method()
    def design(self, job):
        """방식 B 참조 후보: 같은 묘사 + 감정 문구로 k개씩. 화자 임베딩(Base 모델)도 같이 돌려준다"""
        import torch, numpy as np, librosa
        t0 = time.time()
        res = []
        for mood, text, instruct in job['moods']:
            for i in range(job['k']):
                torch.manual_seed(job['seed'] + i); torch.cuda.manual_seed_all(job['seed'] + i)
                w, sr = self.model('design').generate_voice_design(text=text, language='Korean', instruct=instruct)
                x = np.asarray(w[0], dtype='float32')
                xe = x if sr == 24000 else librosa.resample(x, orig_sr=sr, target_sr=24000)
                emb = self.model('base').model.extract_speaker_embedding(audio=xe, sr=24000).float().cpu().numpy().reshape(-1)
                res.append({'mood': mood, 'i': i, 'text': text, 'wav': wav_bytes(x, sr), 'emb': emb.tolist(), 'sec': len(x) / sr})
        return {'out': res, 'stat': self.stamp(t0)}

    @modal.method()
    def embed(self, wavs):
        """wav 바이트들 → 화자 임베딩(같은 사람인지 확인용)"""
        import numpy as np, soundfile as sf, librosa
        t0 = time.time()
        out = []
        for b in wavs:
            x, sr = sf.read(io.BytesIO(b), dtype='float32', always_2d=True); x = x.mean(1)
            if sr != 24000: x = librosa.resample(x, orig_sr=sr, target_sr=24000)
            out.append(self.model('base').model.extract_speaker_embedding(audio=x, sr=24000).float().cpu().numpy().reshape(-1).tolist())
        return {'out': out, 'stat': self.stamp(t0)}


@app.function(image=image, volumes={'/models': vol}, timeout=600)
def put_refs(voice, files):
    """방식 B 참조를 Volume에 둔다: files = {파일 이름: 바이트}"""
    d = f'/models/refs/{voice}'
    os.makedirs(d, exist_ok=True)
    for n, b in files.items(): open(f'{d}/{n}', 'wb').write(b)
    vol.commit()
    return sorted(os.listdir(d))


# ---------------- 이 컴퓨터 쪽 ----------------
def rows():
    import lines as L
    return [(k, t) for k, t, _ in L.OP + L.HIT]


def say(t):
    """읽기만 바꾼다(문장은 lines.py 그대로)"""
    return t.replace('GPS', '지피에스')


def pick_keys(spec):
    allk = [k for k, _ in rows()]
    if not spec or spec == '@all': return allk
    if spec == '@audition': return list(AUDITION)
    ks = [k.strip() for k in spec.split(',') if k.strip()]
    bad = [k for k in ks if k not in allk]
    if bad: sys.exit('lines.py에 없는 키: ' + ' '.join(bad))
    return ks


def jobs_for(method, keys, n, out, speaker, voice, batch):
    import lines as L
    text = dict(rows())
    todo = []
    for idx in range(1, n + 1):
        miss = [k for k in keys if not os.path.exists(os.path.join(out, f'{k}__{idx}.wav'))]
        # 한 묶음은 한 감정(B는 감정별 참조가 하나라서, A·C는 비슷한 길이·말투끼리 묶으려고)
        by = {}
        for k in miss: by.setdefault(L.mood_of(k), []).append(k)
        for mood, ks in by.items():
            for i in range(0, len(ks), batch):
                chunk = ks[i:i + batch]
                seed = int(hashlib.sha1(f'{method}{speaker}{voice}{idx}{",".join(chunk)}'.encode()).hexdigest()[:8], 16)
                todo.append({'method': method, 'speaker': speaker, 'voice': voice, 'idx': idx, 'seed': seed,
                             'items': [{'key': k, 'text': say(text[k]), 'mood': mood, 'instruct': L.MOOD[mood]['en']} for k in chunk]})
    return todo


def cost(stats, gpu, wall):
    """컨테이너마다 (처음 들어온 때 ~ 마지막 끝난 때) + 기동·정리 여유. Modal 요금(2026-09): L4 $0.000222/s, A10G $0.000306/s, CPU $0.0000131/코어/s, 메모리 $0.00000222/GiB/s"""
    rate = {'L4': 0.000222, 'A10G': 0.000306, 'A10': 0.000306}.get(gpu, 0.000222) + 0.0000131 * 0.125 + 0.00000222 * 8
    span = {}
    for s in stats:
        a, b = span.get(s['task'], (s['t_enter'], s['t_end']))
        span[s['task']] = (min(a, s['t_enter']), max(b, s['t_end']))
    boot = 40 + 20   # 컨테이너 기동(이미지·GPU 붙이기) 추정 + 유휴 정리(scaledown_window)
    secs = sum(b - a + boot for a, b in span.values())
    return {'containers': len(span), 'gpu_s': round(secs), 'usd': round(secs * rate, 3), 'wall_s': round(wall), 'gen_s': round(sum(s['gen_s'] for s in stats)),
            'load_s': round(max([s['load_s'] for s in stats] or [0]))}


def run_gen(a):
    import lines as L  # noqa: F401
    keys = pick_keys(a.keys)
    out = a.out
    os.makedirs(out, exist_ok=True)
    speaker = a.speaker or SPEAKER.get(a.method)
    jobs = jobs_for(a.method, keys, a.n, out, speaker, a.voice, a.batch)
    total = sum(len(j['items']) for j in jobs)
    if not jobs: print('다 있다. 할 일 없음'); return None
    print(f'{a.method} {speaker or a.voice}: 묶음 {len(jobs)}개, 조각 {total}개 → {out} (GPU {GPU}, 동시 {a.workers})', flush=True)
    t0 = time.time(); stats = []; done = 0
    with modal.enable_output() if a.verbose else _Null(), app.run():
        app_id = app.app_id
        fn = TTS.with_options(gpu=GPU, max_containers=a.workers)()
        for r in fn.gen.map(jobs, order_outputs=False, return_exceptions=True):
            if isinstance(r, Exception): print('  실패:', repr(r)[:300], flush=True); continue
            for o in r['out']:
                p = os.path.join(out, f"{o['key']}__{o['idx']}.wav")
                tmp = p + '.part'; open(tmp, 'wb').write(o['wav']); os.replace(tmp, p)
            stats.append(r['stat']); done += len(r['out'])
            print(f'  {done}/{total} ({time.time() - t0:.0f}s)', flush=True)
    c = cost(stats, GPU, time.time() - t0)
    rec = {'method': a.method, 'speaker': speaker, 'voice': a.voice, 'keys': len(keys), 'n': a.n, 'clips': done, 'gpu': GPU, 'app_id': app_id, **c}
    print(json.dumps(rec, ensure_ascii=False), flush=True)
    log = os.path.join(out, '..', 'runs.jsonl')
    open(log, 'a', encoding='utf-8').write(json.dumps({**rec, 'at': time.strftime('%Y-%m-%d %H:%M:%S')}, ensure_ascii=False) + '\n')
    stop_app(app_id)
    return rec


class _Null:
    def __enter__(self): return self
    def __exit__(self, *a): return False


def stop_app(app_id):
    """임시 앱은 with를 나오면 멈춘다. 이번 실행의 앱이 아직 살아 있으면 멈춘다(같은 이름의 다른 실행, 다른 앱은 건드리지 않는다)"""
    if not app_id: return
    try:
        r = subprocess.run(['modal', 'app', 'list', '--json'], capture_output=True, text=True, timeout=60)
        for x in json.loads(r.stdout or '[]'):
            if x.get('app_id') == app_id and x.get('state') not in ('stopped', 'stopping'):
                subprocess.run(['modal', 'app', 'stop', '-y', app_id], timeout=60)
                print('  modal app stop', app_id, flush=True)
    except Exception as e:
        print(f'  앱 상태 확인 실패(수동 확인: modal app list, {app_id}):', e, flush=True)


def asr_cer(wav_b, text):
    """이 컴퓨터의 한국어 ASR(bake.py와 같은 모델)로 읽은 CER"""
    import numpy as np, soundfile as sf
    import bake
    x, sr = sf.read(io.BytesIO(wav_b), dtype='float32', always_2d=True)
    hyp = bake.transcribe(x.mean(1), sr)
    return bake.cer(text, hyp), hyp


def run_refs(a):
    """방식 B: 감정마다 k개 → 중립(calm)은 ASR 오류가 가장 적은 것, 나머지는 중립과 화자 유사도가 높고 말이 또렷한 것(유사도 - 0.15 × 오류율, 오류 0.3 이하 중)"""
    import numpy as np
    import lines as L
    out = a.out or os.path.join(HERE, 'audition', 'B', 'refs')
    os.makedirs(out, exist_ok=True)
    only = [m for m in (a.moods or '').split(',') if m]
    if only: return redo_refs(a, out, only)
    moods = [(m, REF_TEXT[m], VOICE_DESC + ' ' + L.MOOD[m]['en']) for m in L.MOOD]
    t0 = time.time()
    with modal.enable_output() if a.verbose else _Null(), app.run():
        app_id = app.app_id
        fn = TTS.with_options(gpu=GPU, max_containers=a.workers)()
        jobs = [{'moods': [mm], 'k': a.k, 'seed': 1000 + 97 * j} for j, mm in enumerate(moods)]
        res, stats = [], []
        for r in fn.design.map(jobs, order_outputs=False):
            res += r['out']; stats.append(r['stat'])
        for r in res:
            r['cer'], r['asr'] = asr_cer(r['wav'], r['text'])
            open(os.path.join(out, f"cand_{r['mood']}_{r['i']}.wav"), 'wb').write(r['wav'])
        cos = lambda u, v: float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-9))
        calm = sorted([r for r in res if r['mood'] == 'calm'], key=lambda r: (r['cer'], -r['sec']))
        base = calm[0]
        chosen = {'calm': base}
        for m in L.MOOD:
            if m == 'calm': continue
            cs = [r for r in res if r['mood'] == m]
            for r in cs: r['sim'] = cos(r['emb'], base['emb'])
            ok = [r for r in cs if r['cer'] <= 0.3] or cs
            chosen[m] = max(ok, key=lambda r: r['sim'] - 0.15 * r['cer'])   # 유사도가 거의 같으면 말이 또렷한 참조(복제가 참조 글과 소리를 맞춰 본다)
        base['sim'] = 1.0
        meta = {m: {'text': r['text'], 'cer': round(r['cer'], 3), 'asr': r['asr'], 'sim': round(r.get('sim', 1.0), 3), 'cand': r['i'], 'sec': round(r['sec'], 2),
                    'sims_all': [round(x.get('sim', 1.0), 3) for x in res if x['mood'] == m]} for m, r in chosen.items()}
        files = {f'{m}.wav': r['wav'] for m, r in chosen.items()}
        files['refs.json'] = json.dumps(meta, ensure_ascii=False, indent=1).encode()
        for n, b in files.items(): open(os.path.join(out, n), 'wb').write(b)
        print(put_refs.remote(a.voice, files), flush=True)
    c = cost(stats, GPU, time.time() - t0)
    c['app_id'] = app_id
    print(json.dumps({'refs': a.voice, **c}, ensure_ascii=False))
    for m, x in meta.items(): print(f"  {m:8} 유사도 {x['sim']:.3f} CER {x['cer']:.2f} {x['sec']}s 후보 {x['cand']} (전체 {x['sims_all']}) ASR: {x['asr']}")
    open(os.path.join(out, '..', 'runs.jsonl'), 'a', encoding='utf-8').write(json.dumps({'refs': a.voice, 'at': time.strftime('%Y-%m-%d %H:%M:%S'), **c}, ensure_ascii=False) + '\n')
    stop_app(app_id)


def redo_refs(a, out, only):
    """이미 고른 참조는 두고 일부 감정만 다시 뽑는다. 유사도는 지금 중립(calm) 참조에 대고 잰다"""
    import numpy as np
    import lines as L
    meta = json.load(open(os.path.join(out, 'refs.json'), encoding='utf-8'))
    calm = open(os.path.join(out, 'calm.wav'), 'rb').read()
    t0 = time.time(); stats = []
    with modal.enable_output() if a.verbose else _Null(), app.run():
        app_id = app.app_id
        fn = TTS.with_options(gpu=GPU, max_containers=a.workers)()
        e = fn.embed.remote([calm]); stats.append(e['stat']); base = e['out'][0]
        jobs = [{'moods': [(m, REF_TEXT[m], VOICE_DESC + ' ' + L.MOOD[m]['en'])], 'k': a.k, 'seed': 5000 + 131 * j} for j, m in enumerate(only)]
        res = []
        for r in fn.design.map(jobs, order_outputs=False):
            res += r['out']; stats.append(r['stat'])
        cos = lambda u, v: float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-9))
        files = {}
        for m in only:
            cs = [r for r in res if r['mood'] == m]
            for r in cs:
                r['cer'], r['asr'] = asr_cer(r['wav'], r['text']); r['sim'] = cos(r['emb'], base)
                open(os.path.join(out, f"redo_{m}_{r['i']}.wav"), 'wb').write(r['wav'])
            ok = [r for r in cs if r['cer'] <= 0.3] or cs
            b = max(ok, key=lambda r: r['sim'] - 0.15 * r['cer'])
            old = meta.get(m, {})
            if old and (old['sim'] - 0.15 * old['cer']) >= (b['sim'] - 0.15 * b['cer']) and not a.force:
                print(f'  {m}: 새 후보가 지금 참조보다 낫지 않다(지금 {old["sim"]:.3f}/{old["cer"]:.2f}, 새 {b["sim"]:.3f}/{b["cer"]:.2f})'); continue
            meta[m] = {'text': b['text'], 'cer': round(b['cer'], 3), 'asr': b['asr'], 'sim': round(b['sim'], 3), 'cand': f"redo{b['i']}", 'sec': round(b['sec'], 2),
                       'sims_all': [round(r['sim'], 3) for r in cs], 'cers_all': [round(r['cer'], 3) for r in cs]}
            files[f'{m}.wav'] = b['wav']
            print(f"  {m}: 새 참조 유사도 {b['sim']:.3f} CER {b['cer']:.2f} ASR: {b['asr']}")
        if files:
            files['refs.json'] = json.dumps(meta, ensure_ascii=False, indent=1).encode()
            for n, b in files.items(): open(os.path.join(out, n), 'wb').write(b)
            print(put_refs.remote(a.voice, files), flush=True)
    c = cost(stats, GPU, time.time() - t0); c['app_id'] = app_id
    print(json.dumps({'refs': a.voice, 'redo': only, **c}, ensure_ascii=False))
    open(os.path.join(out, '..', 'runs.jsonl'), 'a', encoding='utf-8').write(json.dumps({'refs': a.voice, 'redo': only, 'at': time.strftime('%Y-%m-%d %H:%M:%S'), **c}, ensure_ascii=False) + '\n')
    stop_app(app_id)


def run_probe(a):
    """CustomVoice 남성 화자마다 몇 문장 → ASR 오류율. 외국인 억양이 가장 적은 화자를 방식 C로"""
    import lines as L
    keys = ['intro_head', 'intro_tail', 'spotted', 'dc_rb', 'kmh35', 'tired1', 'end_arrive', 'end_fail']
    text = dict(rows())
    jobs = [{'method': 'C', 'speaker': s, 'voice': None, 'idx': 1, 'seed': 7,
             'items': [{'key': k, 'text': say(text[k]), 'mood': L.mood_of(k), 'instruct': L.MOOD[L.mood_of(k)]['en']} for k in keys]} for s in MALE]
    out = a.out or os.path.join(HERE, 'audition', 'probe')
    os.makedirs(out, exist_ok=True)
    t0 = time.time(); stats = []
    with modal.enable_output() if a.verbose else _Null(), app.run():
        app_id = app.app_id
        fn = TTS.with_options(gpu=GPU, max_containers=a.workers)()
        res = {}
        for j, r in zip(jobs, list(fn.gen.map(jobs))):   # 다 받고 나서 돈다(생성기를 덜 읽고 앱을 닫으면 aclose 오류)
            stats.append(r['stat'])
            es = []
            for o in r['out']:
                open(os.path.join(out, f"{j['speaker']}_{o['key']}.wav"), 'wb').write(o['wav'])
                e, hyp = asr_cer(o['wav'], text[o['key']]); es.append(e)
            res[j['speaker']] = sum(es) / len(es)
    for s, e in sorted(res.items(), key=lambda kv: kv[1]): print(f'  {s:10} 평균 CER {e:.3f}')
    print(json.dumps(cost(stats, GPU, time.time() - t0)))
    stop_app(app_id)


def bill(since='today'):
    """Modal 청구 내역에서 이 앱(runaway-qwen-tts) 실행마다 실제 비용. 반환: {app_id: 달러}"""
    rng = ['--for', since] if since in ('today', 'yesterday', 'this month', 'last month') else ['--start', since]
    r = subprocess.run(['modal', 'billing', 'report', *rng, '--resolution', 'h', '--show-resources', '--json'], capture_output=True, text=True, timeout=120)
    if r.returncode: raise SystemExit('청구 내역을 못 받았다: ' + (r.stderr or r.stdout)[-300:])
    out = {}
    for x in json.loads(r.stdout or '[]'):
        if x.get('description') == APP_NAME: out[x['object_id']] = out.get(x['object_id'], 0) + float(x['cost'])
    return out


def main():
    global GPU
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--method', choices=['A', 'B', 'C'])
    ap.add_argument('--keys', default='@all')
    ap.add_argument('--n', type=int, default=3)
    ap.add_argument('--out', default=None)
    ap.add_argument('--speaker', help='A·C 화자(기본 A=Sohee, C=Ryan 또는 QWEN_MALE)')
    ap.add_argument('--voice', default='op1', help='방식 B 목소리 이름(Volume의 refs/<이름>)')
    ap.add_argument('--gpu', default=GPU)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--batch', type=int, default=12)
    ap.add_argument('--k', type=int, default=6, help='--refs: 감정마다 참조 후보 수')
    ap.add_argument('--moods', help='--refs: 이 감정만 다시 뽑는다(예: urgent,triumph). 나머지 참조는 둔다')
    ap.add_argument('--force', action='store_true', help='--refs --moods: 새 후보가 더 낫지 않아도 바꾼다')
    ap.add_argument('--download', action='store_true')
    ap.add_argument('--refs', action='store_true')
    ap.add_argument('--probe', action='store_true')
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--bill', metavar='시작일', nargs='?', const='today', help='이 앱의 실행별 실제 청구 금액(Modal billing report)')
    a = ap.parse_args()
    GPU = a.gpu
    if a.bill:
        b = bill(a.bill)
        for k, v in b.items(): print(f'{k} ${v:.4f}')
        print(f'합계 ${sum(b.values()):.4f}'); return
    if a.download:
        with modal.enable_output() if a.verbose else _Null(), app.run():
            app_id = app.app_id
            print(download.remote())
        stop_app(app_id); return
    if a.refs: return run_refs(a)
    if a.probe: return run_probe(a)
    if not a.method: ap.error('--method가 필요하다')
    a.out = a.out or os.path.join(HERE, 'src')
    run_gen(a)


if __name__ == '__main__':
    main()
