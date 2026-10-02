"""괴물런 목소리 모델 비교 2회차: VoxCPM2(openbmb/VoxCPM2, OpenBMB, 2B, Apache-2.0)를 Modal L4에서 돌린다

- 엔진 이름: voxcpm (PyPI voxcpm 2.0.3)
- 대사: web/voice/model_test.py의 LINES(역할 6 × 5줄). 참조 목소리: model_test/refs/<역할>.wav
- 테이크
  - 1 = 목소리 설계: "(역할 묘사 요약, 그 줄의 영어 지시)대사"
  - 2 = 제어 가능한 복제: reference_wav_path=역할 참조 + "(그 줄의 영어 지시)대사"
    - 참조 문장(prompt_text)은 넣지 않는다. 문서상 참조 문장을 같이 넣으면 Hi-Fi 복제가 되고 괄호 지시가 무시된다(공식 데모도 이때 지시를 끈다)
- 시드: voxcpm 2.0.3 generate에 seed 인자가 없어서 줄마다 torch 시드를 직접 고정한다(시드 + 줄 번호, 1회차와 같은 규칙)
- 예산: 실패 포함 0.1달러. 누적 추정 0.08달러에서 멈춘다(단가: modal.com/pricing, 2026-10-02)
  - 가중치는 GPU 없는 함수(fetch)로 Volume runaway-tts-lab:/voxcpm 에 먼저 받는다
  - GPU 실행은 한 번: 모델 로드 → 첫 2개(스모크)를 로컬 ASR로 확인 → 이어서 생성. torch.compile 끔
  - 조각마다 Volume에 저장하고 바로 로컬로 보낸다(시간 초과가 나도 남는다)
  - 순서: 스모크 2개 → 테이크 1 나머지 → 테이크 2(줄 번호 순으로 역할을 돌아가며). 예산 시간이 지나면 새 조각을 시작하지 않는다
- 결과: web/voice/model_test/voxcpm/<역할>__<번호>__<테이크>.wav (48kHz). 비용 장부: 같은 폴더 _cost.json

실행(저장소 루트에서, PYTHONPATH에 프록시용 sitecustomize)
  python3 web/voice/lab/voxcpm_test.py --dry     # 만들 대사·지시만 출력(Modal 안 씀)
  python3 web/voice/lab/voxcpm_test.py --fetch   # CPU: 가중치 받기 + 점검
  python3 web/voice/lab/voxcpm_test.py           # GPU: 생성
  python3 web/voice/lab/voxcpm_test.py --cer     # 로컬 ASR 검증만
  python3 web/voice/lab/voxcpm_test.py --pull ap-...   # 로컬에 못 받은 조각을 Volume에서 받기(컴퓨팅 비용 없음)
"""
import os, sys, io, json, math, time, re, argparse, subprocess, threading

import modal

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = os.path.dirname(HERE)
OUT = os.path.join(VOICE, 'model_test', 'voxcpm')
REFS = os.path.join(VOICE, 'model_test', 'refs')
COST = os.path.join(OUT, '_cost.json')
APP_NAME = 'runaway-lab-voxcpm'
GPU = 'L4'
MODEL_DIR = '/lab/voxcpm/VoxCPM2'

# 단가(modal.com/pricing, 2026-10-02). GPU 컨테이너는 CPU 2코어·메모리 10GiB를 쓴다고 넉넉히 잡는다
L4_USD_S, CPU_USD_S, MEM_USD_S = 0.000222, 0.0000131, 0.00000222
GPU_RATE = L4_USD_S + 2 * CPU_USD_S + 10 * MEM_USD_S      # 0.0002704/초
CPU_RATE = 2 * CPU_USD_S + 2 * MEM_USD_S                    # 0.0000306/초(받기·점검 함수)
CAP_USD, STOP_USD = 0.10, 0.08
GPU_TIMEOUT = 250            # GPU 함수 본문 상한(초). 시작 35초 + 250초 ≈ 0.077달러
STARTUP_S, TAIL_S = 35, 15   # 함수 본문 전 컨테이너 시작, 마지막 조각 마무리 여유
PATCH_S = 0.16               # VoxCPM2 1스텝(패치) = 오디오 0.16초(25Hz 잠재 × 4)
CFG, STEPS, SEED = 2.0, 10, 2026

app = modal.App(APP_NAME)
lab = modal.Volume.from_name('runaway-tts-lab', create_if_missing=True)
ENV = {'HF_HUB_ENABLE_HF_TRANSFER': '1', 'TOKENIZERS_PARALLELISM': 'false', 'TQDM_DISABLE': '1'}
# voxcpm은 의존성 없이 깔고 실행에 쓰는 것만 넣는다(gradio·funasr·modelscope 등은 데모·학습·잡음 제거용)
vox_image = (modal.Image.debian_slim(python_version='3.11')
             .pip_install('torch==2.8.0', 'torchaudio==2.8.0')
             .pip_install('transformers==4.56.2', 'einops==0.8.1', 'pydantic==2.11.9', 'safetensors==0.6.2', 'librosa==0.11.0',
                          'soundfile==0.13.1', 'tqdm', 'hf_transfer==0.1.9')
             .pip_install('voxcpm==2.0.3', extra_options='--no-deps')
             .env(ENV))

# 테이크 1의 역할 묘사: model_test.ROLES 영어 묘사 요약(감정은 줄 지시에 맡기고 음색·정체만)
SUMMARY = {
    'caster': 'An energetic Korean male sports commentator in his thirties, bright broadcast voice',
    'narrator': 'A Korean male horror storyteller in his fifties, low, breathy voice close to the microphone',
    'dokkaebi': 'A boastful Korean goblin, a boisterous middle-aged man with a big hearty voice, cartoonish',
    'halmae': 'A chatty Korean grandmother in her seventies, raspy voice, Gyeongsang dialect, comedic',
    'cheonyeo': 'A young Korean female ghost, fragile, trembling, eerie voice',
    'jeoseung': 'The Korean grim reaper, a deep, cold, authoritative male voice',
}

if modal.is_local():
    sys.path.insert(0, VOICE)
    import model_test as T   # LINES, ROLES, stop_app, log_run


def wav_bytes(x, sr):
    import numpy as np, soundfile as sf
    b = io.BytesIO(); sf.write(b, np.asarray(x, dtype='float32').reshape(-1), sr, format='WAV', subtype='PCM_16'); return b.getvalue()


@app.function(image=vox_image, volumes={'/lab': lab}, timeout=600, cpu=1.0, memory=2048, max_containers=1, retries=0)
def fetch(refs, texts):
    """CPU: 가중치를 Volume에 받고(한 번만), GPU 전에 import·generate 인자·한국어 토큰·참조 wav 읽기를 점검한다"""
    t0, rep = time.time(), {}
    done = os.path.join(MODEL_DIR, '.done')
    if not os.path.exists(done):
        from huggingface_hub import snapshot_download
        snapshot_download('openbmb/VoxCPM2', local_dir=MODEL_DIR)
        open(done, 'w').write('ok')
        lab.commit()
    rep['dl_s'] = round(time.time() - t0, 1)
    rep['files'] = {f: os.path.getsize(os.path.join(MODEL_DIR, f)) for f in sorted(os.listdir(MODEL_DIR)) if os.path.isfile(os.path.join(MODEL_DIR, f))}
    import inspect, torch, torchaudio, transformers, librosa
    from voxcpm import VoxCPM
    from voxcpm.model.utils import mask_multichar_chinese_tokens
    from transformers import LlamaTokenizerFast
    rep['ver'] = {'torch': str(torch.__version__), 'torchaudio': str(torchaudio.__version__), 'transformers': str(transformers.__version__), 'librosa': str(librosa.__version__)}   # TorchVersion을 그대로 보내면 로컬(torch 없음)에서 못 푼다
    rep['args'] = list(inspect.signature(VoxCPM._generate).parameters)
    tok = LlamaTokenizerFast.from_pretrained(MODEL_DIR)
    w = mask_multichar_chinese_tokens(tok)
    rep['tok'] = []
    for t in texts:
        ids = w(t)
        names = tok.convert_ids_to_tokens(ids)
        rep['tok'].append({'text': t, 'n': len(ids), 'unk': sum(1 for i in ids if i == tok.unk_token_id),
                           'byte': sum(1 for s in names if s.startswith('<0x')), 'back': tok.decode(ids)})
    rep['refs'] = {}
    for role, b in refs.items():
        p = f'/tmp/{role}.wav'; open(p, 'wb').write(b)
        y, sr = librosa.load(p, sr=16000, mono=True)
        rep['refs'][role] = round(len(y) / sr, 2)
    rep['total_s'] = round(time.time() - t0, 1)
    return rep


@app.function(image=vox_image, gpu=GPU, volumes={'/lab': lab}, timeout=GPU_TIMEOUT, max_containers=1,
              scaledown_window=2, single_use_containers=True)   # generator 함수는 재시도가 없다
def gen(jobs, refs, deadline_s, seed, run_id):
    """GPU: 모델을 한 번 올리고 jobs를 차례로 만든다. 조각마다 Volume에 쓰고 바로 돌려준다(generator)"""
    t0 = time.time()
    try:
        import random, numpy as np, torch
        from voxcpm import VoxCPM
        t_imp = time.time() - t0
        m = VoxCPM.from_pretrained(MODEL_DIR, load_denoiser=False, optimize=False, device='cuda')
        sr = m.tts_model.sample_rate
        ref_paths = {}
        for role, b in refs.items():
            ref_paths[role] = f'/tmp/ref_{role}.wav'; open(ref_paths[role], 'wb').write(b)
        d = f'/lab/voxcpm/out/{run_id}'; os.makedirs(d, exist_ok=True)
    except Exception as e:
        yield {'kind': 'fatal', 'err': repr(e)[:800], 't': time.time() - t0}
        return
    yield {'kind': 'loaded', 'import_s': round(t_imp, 1), 'load_s': round(time.time() - t0, 1), 'sr': sr,
           'gpu': str(torch.cuda.get_device_name(0)), 'torch': str(torch.__version__)}
    gen_s, bad_run = 0.0, 0
    for i, j in enumerate(jobs):
        el = time.time() - t0
        if el > deadline_s:
            yield {'kind': 'stop', 'done': i, 't': el}
            break
        s = seed + j['n']
        random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)
        kw = dict(text=j['text'], cfg_value=CFG, inference_timesteps=STEPS, max_len=j['max_len'], retry_badcase=False, normalize=False, denoise=False)
        if j['take'] == 2:
            kw['reference_wav_path'] = ref_paths[j['role']]
        name = f"{j['role']}__{j['n']}__{j['take']}"
        t1 = time.time()
        try:
            x = m.generate(**kw)
            g = time.time() - t1; gen_s += g
            b = wav_bytes(x, sr)
            open(f'{d}/{name}.wav', 'wb').write(b)
            dur = len(x) / sr
            bad_run = 0
            yield {'kind': 'clip', 'name': name, 'wav': b, 'gen_s': round(g, 2), 'dur': round(dur, 2),
                   'hit_max': dur >= (j['max_len'] - 2) * PATCH_S, 't': round(time.time() - t0, 1)}
        except Exception as e:
            bad_run += 1
            yield {'kind': 'clip', 'name': name, 'err': repr(e)[:400], 't': round(time.time() - t0, 1)}
            if bad_run >= 3:
                yield {'kind': 'stop', 'done': i + 1, 't': time.time() - t0, 'why': '연속 실패 3회'}
                break
        if (i + 1) % 10 == 0:
            lab.commit()
    lab.commit()
    yield {'kind': 'end', 'gen_s': round(gen_s, 1), 't': round(time.time() - t0, 1)}


# ---------------- 이 컴퓨터 쪽 ----------------
def clean(s):
    """괄호 지시 안에 괄호가 있으면 형식이 깨진다(공식 데모와 같은 처리)"""
    return re.sub(r'[()（）]', '', s).strip()


def max_len_of(text):
    """대사 길이로 생성 상한(패치 수)을 잡는다. 말이 안 끝나도 시간이 묶이게(최소 5초, 최대 18초)"""
    syl = sum(1 for c in text if '가' <= c <= '힣')
    pause = sum(text.count(c) for c in ',.!?~…')
    sec = min(18.0, max(5.0, 2.0 + 0.4 * syl + 0.5 * pause))
    return int(math.ceil(sec / PATCH_S))


def make_jobs():
    one, two = [], []
    for role, n, text, _ko, en, _cosy in T.LINES:
        one.append({'role': role, 'n': n, 'take': 1, 'line': text, 'text': f'({clean(SUMMARY[role] + ", " + en)}){text}', 'max_len': max_len_of(text)})
        two.append({'role': role, 'n': n, 'take': 2, 'line': text, 'text': f'({clean(en)}){text}', 'max_len': max_len_of(text)})
    order = {r: i for i, r in enumerate(T.ROLES)}
    rest2 = sorted(two[1:], key=lambda j: (j['n'], order[j['role']]))   # 예산이 모자라도 역할마다 고르게
    return [one[0], two[0]] + one[1:] + rest2


def cost_book():
    try: return json.load(open(COST, encoding='utf-8'))
    except Exception: return []


def cost_add(rec):
    os.makedirs(OUT, exist_ok=True)
    book = cost_book() + [rec]
    json.dump(book, open(COST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return sum(r['usd_est'] for r in book)


def spent():
    return sum(r['usd_est'] for r in cost_book())


def asr_cer(path, text):
    import numpy as np, soundfile as sf
    import bake
    x, sr = sf.read(path, dtype='float32', always_2d=True); x = x.mean(1)
    hyp = bake.transcribe(x, sr)
    return bake.cer(bake.norm(text), bake.norm(hyp)), hyp, len(x) / sr


def do_fetch(a):
    refs = {r: open(os.path.join(REFS, f'{r}.wav'), 'rb').read() for r in T.ROLES}
    texts = [l[2] for l in T.LINES]
    t0 = time.time(); app_id = None
    with modal.enable_output(), app.run():
        app_id = app.app_id
        tc = time.time()
        try:
            rep = fetch.remote(refs, texts)
        except Exception as e:
            rep = {'err': repr(e)[:400]}
        call_s = time.time() - tc
    usd = round(call_s * CPU_RATE, 4)
    total = cost_add({'what': 'fetch', 'app_id': app_id, 'call_s': round(call_s), 'wall_s': round(time.time() - t0), 'usd_est': usd})
    print(json.dumps(rep, ensure_ascii=False, indent=1), flush=True)
    print(f'  fetch: 호출 {call_s:.0f}초, 추정 {usd:.4f}달러, 누적 {total:.4f}달러', flush=True)
    T.stop_app(app_id)


def do_gen(a):
    import numpy as np, soundfile as sf
    import bake
    before = spent()
    avail = (STOP_USD - before) / GPU_RATE
    deadline = min(GPU_TIMEOUT - TAIL_S, avail - STARTUP_S - TAIL_S)
    print(f'  누적 {before:.4f}달러, GPU 가능 {avail:.0f}초(L4+CPU·메모리), 새 조각 마감 {deadline:.0f}초', flush=True)
    if deadline < 90:
        print('  예산 부족: 실행하지 않는다', flush=True); return
    jobs = make_jobs()
    refs = {r: open(os.path.join(REFS, f'{r}.wav'), 'rb').read() for r in T.ROLES}
    os.makedirs(OUT, exist_ok=True)
    bake.transcribe(np.zeros(8000, dtype='float32'), 16000)   # ASR 미리 올려 스모크 확인을 빠르게
    meta, got, clips, errs, gen_s, why = {}, 0, 0, 0, 0.0, ''
    t0 = time.time(); app_id = None
    with modal.enable_output() if a.verbose else T._Null(), app.run():
        app_id = app.app_id
        tc = time.time()
        # 감시: 조각 소식이 끊겨도(시작·로드가 늘어져도) 예산 시간이 지나면 앱을 멈춘다
        wd = threading.Timer(avail, lambda: (print('  예산 시간 초과 → 앱 강제 정지', flush=True),
                                             subprocess.run(['modal', 'app', 'stop', '-y', app_id], timeout=60)))
        wd.daemon = True; wd.start()
        try:
            for r in gen.remote_gen(jobs, refs, deadline, a.seed, app_id):
                el = time.time() - tc
                k = r['kind']
                if k == 'fatal':
                    print(f'  [{el:5.0f}s] 모델 로드 실패: {r["err"]}', flush=True); why = 'fatal'; break
                if k == 'loaded':
                    print(f'  [{el:5.0f}s] 로드 {r["load_s"]}초(import {r["import_s"]}초) {r["gpu"]} torch {r["torch"]} sr {r["sr"]}', flush=True)
                elif k == 'clip':
                    got += 1
                    if 'err' in r:
                        errs += 1; meta[r['name']] = {'err': r['err']}
                        print(f'  [{el:5.0f}s] 실패 {r["name"]}: {r["err"]}', flush=True)
                    else:
                        p = os.path.join(OUT, r['name'] + '.wav'); open(p, 'wb').write(r['wav'])
                        clips += 1; gen_s += r['gen_s']
                        meta[r['name']] = {k2: r[k2] for k2 in ('gen_s', 'dur', 'hit_max', 't')}
                        print(f'  [{el:5.0f}s] {r["name"]:14s} {r["dur"]:5.2f}s 생성 {r["gen_s"]:5.2f}s{" 상한" if r["hit_max"] else ""}', flush=True)
                    if got <= 2:   # 스모크: 첫 두 조각의 한국어를 로컬 ASR로 본다
                        line = next(j['line'] for j in jobs if f"{j['role']}__{j['n']}__{j['take']}" == r['name'])
                        if 'err' not in r:
                            c, hyp, _ = asr_cer(p, line); meta[r['name']]['cer'] = round(c, 3)
                            print(f'    스모크 CER {c:.2f}  {hyp}', flush=True)
                        if got == 2:
                            ok = [v for v in (meta[jj] for jj in list(meta)[:2]) if 'cer' in v and v['cer'] <= 0.5]
                            if not ok:
                                print('  스모크 실패: 한국어가 알아들을 수 없다 → 중단', flush=True); why = 'smoke'; break
                            print('  스모크 통과 → 계속', flush=True)
                elif k == 'stop':
                    why = r.get('why', '예산 시간'); print(f'  [{el:5.0f}s] 멈춤({why}): {r["done"]}/{len(jobs)}', flush=True)
                elif k == 'end':
                    print(f'  [{el:5.0f}s] 끝: 생성 합계 {r["gen_s"]}초, 함수 {r["t"]}초', flush=True)
                if before + (time.time() - tc) * GPU_RATE >= STOP_USD:
                    print('  누적 추정이 0.08달러에 닿음 → 중단', flush=True); why = 'budget'; break
        except Exception as e:
            print('  원격 오류:', repr(e)[:400], flush=True); why = why or 'remote-error'
        wd.cancel()
    gpu_s = time.time() - tc
    usd = round(gpu_s * GPU_RATE, 4)
    total = cost_add({'what': 'gen', 'app_id': app_id, 'gpu_wall_s': round(gpu_s), 'usd_est': usd, 'clips': clips, 'errs': errs, 'stop': why})
    json.dump(meta, open(os.path.join(OUT, f'_clips_{app_id}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'  voxcpm: {clips}개, 실패 {errs}, 생성 {gen_s:.0f}초, GPU 컨테이너(호출~앱 정지) {gpu_s:.0f}초, 이번 {usd:.4f}달러, 누적 {total:.4f}달러', flush=True)
    T.log_run({'what': 'voxcpm', 'app_id': app_id, 'clips': clips, 'errs': errs, 'gen_s': round(gen_s), 'wall_s': round(time.time() - t0),
               'gpu': GPU, 'usd_est': round(total, 4)})
    T.stop_app(app_id)


def do_cer(a):
    import numpy as np
    text = {f'{r}__{n}': t for r, n, t, *_ in T.LINES}
    rows = []
    for f in sorted(os.listdir(OUT)):
        if not f.endswith('.wav'): continue
        role, n, take = f[:-4].split('__')
        c, hyp, dur = asr_cer(os.path.join(OUT, f), text[f'{role}__{n}'])
        rows.append((f, int(take), c, dur, hyp))
        print(f'  {f:22s} {dur:5.2f}s CER {c:.2f}  {hyp}', flush=True)
    for take in (1, 2, None):
        rs = [r for r in rows if take is None or r[1] == take]
        if rs:
            cs = [r[2] for r in rs]
            print(f'  테이크 {take or "전체"}: {len(rs)}개, 평균 CER {np.mean(cs):.3f}, 0.3 초과 {sum(c > 0.3 for c in cs)}개', flush=True)


def do_pull(a):
    d = os.path.join(OUT, '_pull'); os.makedirs(d, exist_ok=True)
    subprocess.run(['modal', 'volume', 'get', '--force', 'runaway-tts-lab', f'/voxcpm/out/{a.pull}', d], check=False)
    for root, _, fs in os.walk(d):
        for f in fs:
            if f.endswith('.wav') and not os.path.exists(os.path.join(OUT, f)):
                os.replace(os.path.join(root, f), os.path.join(OUT, f)); print('  받음', f, flush=True)


def do_dry(a):
    for j in make_jobs():
        print(f"  {j['role']:9s} {j['n']} t{j['take']} max {j['max_len'] * PATCH_S:4.1f}s  {j['text']}")
    print(f'  GPU 단가 {GPU_RATE:.7f}달러/초 → 0.08달러 = {STOP_USD / GPU_RATE:.0f}초(L4만 {STOP_USD / L4_USD_S:.0f}초), 누적 {spent():.4f}달러')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--cer', action='store_true')
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--pull')
    ap.add_argument('--seed', type=int, default=SEED)
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()
    if a.dry: do_dry(a)
    elif a.fetch: do_fetch(a)
    elif a.cer: do_cer(a)
    elif a.pull: do_pull(a)
    else: do_gen(a)


if __name__ == '__main__':
    main()
