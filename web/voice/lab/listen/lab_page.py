#!/usr/bin/env python3
"""목소리 모델 테스트 검수 페이지: model_test/ → out/(mp3, index.html, files.json)
- 줄마다 6개(엔진 3 × 테이크 2)를 섞어 1~6번으로 보인다. 엔진은 "공개"를 눌러야 보인다
- 괴물 역할은 변조(DSP) 버전도 만든다
- 음량은 모두 같은 기준(활성 구간 RMS -18dBFS, 피크 -1dBFS)으로 맞춘다
"""
import os, sys, json, random, subprocess, hashlib
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

ROOT = '/home/user/RUNA-WAY'
MT = f'{ROOT}/web/voice/model_test'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = f'{MT}/_page1'   # model_test/는 git에서 뺀다
sys.path[:0] = [f'{ROOT}/web/voice']
import bake  # noqa: E402
import model_test as T  # noqa: E402
FF = bake.ffmpeg()
SR = 44100
ENGINES = {'qwen': ('Qwen3-TTS', {1: '줄마다 목소리 설계(연기 지시)', 2: '기준 목소리 복제'}),
           'cosy': ('CosyVoice 3', {1: '지시문(감정 목록)', 2: '기준 목소리 말투 복제'}),
           'cbox': ('Chatterbox', {1: '감정 과장 0.5', 2: '감정 과장 0.85'})}
ROLE_KO = {'caster': ('경주 캐스터', '스포츠 중계. 흥분, 과장'), 'narrator': ('공포 낭독자', '괴담 라디오. 낮고 느림'),
           'dokkaebi': ('도깨비 · 경주', '허풍 센 아재, 귀엽게'), 'halmae': ('홍콩할매 · 경주', '잔소리 할머니, 귀엽게'),
           'cheonyeo': ('처녀귀신 · 공포', '흐느낌, 속삭임'), 'jeoseung': ('저승사자 · 공포', '낮고 느림, 감정 없음')}
# 변조 초안(docs/prd/19-monster-sound.md 7장). 속도는 유지하고 피치·음색만
DSP = {'dokkaebi': {'pitch': 0.89, 'drive': 1.6, 'rt': 0.4, 'wet': 0.12},
       'halmae': {'pitch': 1.05, 'drive': 1.3, 'rt': 0.35, 'wet': 0.1},
       'cheonyeo': {'pitch': 1.0, 'rt': 1.8, 'wet': 0.35, 'rev_pre': True, 'trem': (6.0, 0.18)},
       'jeoseung': {'pitch': 0.84, 'rt': 2.6, 'wet': 0.3, 'lp': 5000}}


def load(p):
    x, sr = sf.read(p, dtype='float32', always_2d=True)
    x = x.mean(1)
    if sr != SR:
        r = subprocess.run([FF, '-v', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-'],
                           input=x.tobytes(), capture_output=True)
        x = np.frombuffer(r.stdout, dtype='float32').copy()
    return x


def level(x):
    fr = int(0.02 * SR); e = np.sqrt(np.convolve(x ** 2, np.ones(fr) / fr, mode='same') + 1e-12)
    act = x[e > e.max() * 0.1] if e.max() > 0 else x
    rms = np.sqrt(np.mean(act ** 2)) + 1e-9
    y = x * (10 ** (-18 / 20) / rms)
    pk = np.max(np.abs(y))
    return y * (0.89 / pk) if pk > 0.89 else y


def mp3(x, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    r = subprocess.run([FF, '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '96k', path],
                       input=level(x).astype('float32').tobytes(), capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode()[-300:])


def ir(rt, seed=7):
    n = int(rt * SR); t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    h = rng.standard_normal(n) * np.exp(-6.9 * t / rt)
    h[:int(0.005 * SR)] *= np.linspace(0, 1, int(0.005 * SR))
    return (h / np.sqrt(np.sum(h ** 2))).astype('float32')


def pitch(x, r):
    if abs(r - 1) < 1e-3: return x
    af = f'asetrate={int(SR * r)},aresample={SR},atempo={1 / r:.5f}'
    p = subprocess.run([FF, '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', af, '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-'],
                       input=x.astype('float32').tobytes(), capture_output=True)
    return np.frombuffer(p.stdout, dtype='float32').copy()


def dsp(x, c):
    y = pitch(x, c.get('pitch', 1.0))
    if c.get('drive'): y = np.tanh(y * 4 * c['drive']) / np.tanh(4 * c['drive'])
    if c.get('lp'): y = sosfilt(butter(4, c['lp'], fs=SR, output='sos'), y).astype('float32')
    if c.get('trem'):
        f, d = c['trem']; y = y * (1 - d + d * np.sin(2 * np.pi * f * np.arange(len(y)) / SR)).astype('float32')
    tail = np.zeros(int(c['rt'] * SR), dtype='float32')
    if c.get('rev_pre'):   # 역잔향: 뒤집어 잔향을 걸고 다시 뒤집는다. 말 앞에 소리가 차오른다
        w = fftconvolve(np.concatenate([tail, y])[::-1], ir(c['rt']))[:len(y) + len(tail)][::-1]
        y = np.concatenate([tail, y])
    else:
        y = np.concatenate([y, tail]); w = fftconvolve(y, ir(c['rt']))[:len(y)]
    out = (1 - c['wet']) * y + c['wet'] * w * (np.std(y) / (np.std(w) + 1e-9))
    return out.astype('float32')


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(20260927)
    files, roles = {}, []
    refs = json.load(open(f'{MT}/refs/refs.json', encoding='utf-8'))
    have = {e: os.path.isdir(f'{MT}/{e}') for e in ENGINES}
    stats = {e: {'cer': [], 'miss': 0} for e in ENGINES}
    for role in T.ROLES:
        ko, sub = ROLE_KO[role]
        x = load(f'{MT}/refs/{role}.wav'); rf = f'ref/{role}.mp3'; mp3(x, f'{OUT}/{rf}'); files[rf] = f'{OUT}/{rf}'
        lines = []
        for r, n, text, dko, _, _ in [l for l in T.LINES if l[0] == role]:
            clips = []
            for e in ENGINES:
                for take in (1, 2):
                    p = f'{MT}/{e}/{role}__{n}__{take}.wav'
                    if not os.path.exists(p):
                        stats[e]['miss'] += 1; continue
                    y = load(p)
                    hyp = bake.transcribe(y, SR); cer = bake.cer(bake.norm(text), bake.norm(hyp))
                    stats[e]['cer'].append(cer)
                    cid = hashlib.sha1(f'{role}{n}{e}{take}'.encode()).hexdigest()[:8]
                    f = f'a/{cid}.mp3'; mp3(y, f'{OUT}/{f}'); files[f] = f'{OUT}/{f}'
                    c = {'id': cid, 'engine': e, 'take': take, 'file': f, 'dur': round(len(y) / SR, 1), 'cer': round(cer, 2), 'asr': hyp}
                    if role in DSP:
                        fd = f'd/{cid}.mp3'; mp3(dsp(y, DSP[role]), f'{OUT}/{fd}'); files[fd] = f'{OUT}/{fd}'; c['dsp'] = fd
                    clips.append(c)
            rng.shuffle(clips)
            lines.append({'id': f'{role}{n}', 'n': n, 'text': text, 'dir': dko, 'clips': clips})
        roles.append({'id': role, 'ko': ko, 'sub': sub, 'ref': rf, 'ref_text': refs[role]['text'], 'dsp': role in DSP, 'lines': lines})
    sfx = []
    sj = f'{MT}/sfx/sfx.json'
    if os.path.exists(sj):
        for kid, v in json.load(open(sj, encoding='utf-8')).items():
            for it in v['items']: files[it['file']] = f"{MT}/{it['file']}"
            sfx.append({'id': kid, 'name': v['name'], 'items': v['items']})
    runs = [json.loads(l) for l in open(f'{MT}/runs.jsonl', encoding='utf-8')] if os.path.exists(f'{MT}/runs.jsonl') else []
    bill = json.load(open(f'{HERE}/bill.json')) if os.path.exists(f'{HERE}/bill.json') else {}
    D = {'engines': {e: {'name': v[0], 'takes': v[1], 'cer': round(float(np.mean(stats[e]['cer'])), 3) if stats[e]['cer'] else None,
                         'over': int(sum(c > 0.3 for c in stats[e]['cer'])), 'miss': stats[e]['miss'], 'ran': have[e]} for e, v in ENGINES.items()},
         'roles': roles, 'sfx': sfx,
         'runs': [{'what': r['what'], 'gpu': r.get('gpu'), 'clips': r.get('clips', '-'), 'wall_s': r.get('wall_s'), 'usd': bill.get(r.get('app_id'))} for r in runs]}
    tpl = open(f'{HERE}/lab_page.html', encoding='utf-8').read()
    open(f'{OUT}/index.html', 'w', encoding='utf-8').write(tpl.replace('/*DATA*/null', json.dumps(D, ensure_ascii=False).replace('</', '<\\/')))
    json.dump(files, open(f'{OUT}/files.json', 'w'), ensure_ascii=False, indent=1)
    print('파일', len(files), {e: (D['engines'][e]['cer'], D['engines'][e]['over'], D['engines'][e]['miss']) for e in ENGINES})


if __name__ == '__main__':
    main()
