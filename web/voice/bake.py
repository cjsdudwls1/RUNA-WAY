"""음성 팩 굽기. lines.py → web/static/voice/*.bin + web/voice_manifest.js + web/voice/qa.tsv

- TTS: Supertonic 3 (모델 OpenRAIL-M, 코드 MIT). 로컬 CPU 추론. 비용 0, 운영 서버 0
- 문장마다 후보 N개를 만들어 한국어 ASR로 되읽고, 글자 오류율(CER)이 가장 낮은 것을 고른다
- 결과는 .cache에 문장+설정 해시로 저장한다. 대사를 고치면 그 줄만 다시 굽는다

준비 (1회, 약 250MB)
  pip install sherpa-onnx soundfile scipy imageio-ffmpeg
  cd web/voice && mkdir -p models && cd models
  curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2
  curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-korean-2024-06-24.tar.bz2
  tar xjf *supertonic*.bz2 && tar xjf *korean*.bz2
실행
  python3 web/voice/bake.py
"""
import os, sys, json, hashlib, subprocess, re
import numpy as np, soundfile as sf
import scipy.signal as ss

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lines as L

MODELS = os.environ.get('VOICE_MODELS', os.path.join(HERE, 'models'))
TTS_DIR = os.path.join(MODELS, 'sherpa-onnx-supertonic-3-tts-int8-2026-05-11')
ASR_DIR = os.path.join(MODELS, 'sherpa-onnx-zipformer-korean-2024-06-24')
CACHE = os.path.join(HERE, '.cache')
OUT = os.path.join(HERE, '..', 'static', 'voice')
N_CAND = int(os.environ.get('VOICE_CAND', '3'))
RETRY_N = 5          # 오류율이 RETRY_CER를 넘으면 더 뽑는 후보 수
RETRY_CER = 0.25     # 최종 mp3 기준. 같은 음성도 ASR이 0.15~0.2는 틀린다(신규 생성 24문장 실측 원본 0.19)
SR_OUT = 24000
THREADS = int(os.environ.get('VOICE_THREADS', os.cpu_count() or 4))


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


_tts = _asr = None


def tts():
    global _tts
    if _tts is None:
        import sherpa_onnx as so
        D = TTS_DIR + '/'
        _tts = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(supertonic=so.OfflineTtsSupertonicModelConfig(
            duration_predictor=D + 'duration_predictor.int8.onnx', text_encoder=D + 'text_encoder.int8.onnx',
            vector_estimator=D + 'vector_estimator.int8.onnx', vocoder=D + 'vocoder.int8.onnx', tts_json=D + 'tts.json',
            unicode_indexer=D + 'unicode_indexer.bin', voice_style=D + 'voice.bin'), num_threads=THREADS, provider='cpu')))
    return _tts


def asr():
    global _asr
    if _asr is None:
        import sherpa_onnx as so
        D = ASR_DIR + '/'
        _asr = so.OfflineRecognizer.from_transducer(encoder=D + 'encoder-epoch-99-avg-1.int8.onnx', decoder=D + 'decoder-epoch-99-avg-1.onnx',
                                                    joiner=D + 'joiner-epoch-99-avg-1.int8.onnx', tokens=D + 'tokens.txt', num_threads=THREADS)
    return _asr


def transcribe(x, sr):
    y = ss.resample_poly(x, 16000, sr).astype('float32')
    pad = np.zeros(int(16000 * 0.4), dtype='float32')   # 앞뒤 무음이 없으면 ASR이 끝 단어를 흘린다
    y = np.concatenate([pad, y, pad])
    s = asr().create_stream(); s.accept_waveform(16000, y); asr().decode_stream(s)
    return s.result.text


def num_ko(m):
    n = int(m.group(0))
    if n == 0: return '영'
    out = ''
    for unit, w in [(10000, '만'), (1000, '천'), (100, '백')]:
        q, n = divmod(n, unit)
        if q: out += ('' if q == 1 else L.SINO[q]) + w
    return out + (L.sino(n) if n else '')


def norm(t):
    t = t.replace('GPS', '지피에스')
    t = re.sub(r'\d+', num_ko, t)
    return re.sub(r'[^가-힣a-zA-Z]', '', t)


def cer(ref, hyp):
    r, h = norm(ref), norm(hyp)
    if not r: return 0.0
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        p, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (r[i - 1] != h[j - 1]))
    return d[len(h)] / len(r)


def trim(x, sr):
    """앞뒤 무음 제거. 이어 붙일 때 틈이 벌어지지 않게"""
    a = np.abs(x); thr = max(1e-4, a.max() * 0.02)
    idx = np.where(a > thr)[0]
    if not len(idx): return x
    pad = int(sr * 0.02)
    return x[max(0, idx[0] - pad): idx[-1] + pad]


def post(x, sr, tempo=1.0, pitch=1.0):
    """템포·피치 → 음량 정규화 → mp3. 반환: (mp3 bytes, 길이 초)"""
    x = trim(x, sr)
    filt = []
    if abs(pitch - 1) > 1e-3 or abs(tempo - 1) > 1e-3:
        filt.append(f'rubberband=pitch={pitch}:tempo={tempo}:formant=shifted')
    filt.append(f'aresample={SR_OUT}')
    p = subprocess.run([ffmpeg(), '-v', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-', '-af', ','.join(filt),
                        '-f', 'f32le', '-'], input=x.astype('float32').tobytes(), capture_output=True, check=True)
    y = np.frombuffer(p.stdout, dtype='float32').copy()
    # RMS -16 dBFS에 맞추고 피크는 -1 dBFS로 누른다. 조각마다 크기가 다르면 이어 붙인 문장이 들쭉날쭉하다
    act = y[np.abs(y) > 0.01]
    rms = np.sqrt((act ** 2).mean()) if len(act) else 1e-3
    y *= 10 ** (-16 / 20) / max(rms, 1e-4)
    pk = np.abs(y).max()
    if pk > 0.89: y = np.tanh(y / 0.89 * 1.2) / np.tanh(1.2) * 0.89     # 부드러운 리미터
    y = y.astype('float32')   # tanh 뒤엔 float64가 된다. 그 바이트를 f32로 넘기면 길이 2배의 잡음(=무음 판정)이 나온다
    fade = int(SR_OUT * 0.008); y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
    p = subprocess.run([ffmpeg(), '-v', 'error', '-f', 'f32le', '-ar', str(SR_OUT), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame',
                        '-b:a', '64k', '-f', 'mp3', '-'], input=y.tobytes(), capture_output=True, check=True)
    return p.stdout, len(y) / SR_OUT


def decode(data):
    p = subprocess.run([ffmpeg(), '-v', 'error', '-i', '-', '-f', 'f32le', '-ac', '1', '-ar', str(SR_OUT), '-'], input=data, capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype='float32')


def num_part(text):
    return norm(re.sub(r'시속|킬로|미터', '', text))


def score(key, text, hyp):
    """낮을수록 좋다. 숫자 구절은 숫자가 들리는지가 먼저다. ASR은 '킬로'를 '킬러'로 적는 버릇이 있어 CER만 보면 숫자가 틀린 후보가 이긴다"""
    e = cer(text, hyp)
    if NUMKEY.match(key):
        return (0 if num_part(text) in norm(hyp) else 1) + e
    return e


NUMKEY = re.compile(r'(kmh|m)\d')


def bake(key, text, sid, speed, tempo=1.0, pitch=1.0):
    h = hashlib.sha1(json.dumps([text, sid, speed, tempo, pitch, N_CAND, 5 if NUMKEY.match(key) else 4]).encode()).hexdigest()[:16]
    # 동물 대사는 의성어가 섞여 ASR이 원래 못 읽는다. 문턱을 따로 둔다
    retry_cer = RETRY_CER if abs(pitch - 1) < 1e-3 else 0.4
    if NUMKEY.match(key): retry_cer = 0.2   # 숫자 구절: 숫자가 들리고(점수 1 미만) 나머지 오류가 작을 때까지
    cp = os.path.join(CACHE, h + '.json'); mp = os.path.join(CACHE, h + '.mp3')
    old = None
    if os.path.exists(cp) and os.path.exists(mp):
        old = json.load(open(cp))
        if old.get('score', old['cer']) <= retry_cer or old.get('retried'):
            return old, open(mp, 'rb').read()
    import sherpa_onnx as so
    best = None
    # 첫 판은 N_CAND개. 오류율이 높으면 RETRY_N개까지 더 뽑는다 (문장 끝 짧은 외침이 잘리는 경우가 있다)
    for i in range(RETRY_N if old else N_CAND + RETRY_N):
        if not old and i >= N_CAND and best[0] <= retry_cer: break
        g = so.GenerationConfig(); g.sid = sid; g.num_steps = 10; g.speed = speed; g.extra['lang'] = 'ko'
        a = tts().generate(text, g)
        x = np.array(a.samples, dtype='float32', copy=True)   # asarray는 엔진 버퍼를 가리킨다. 다음 생성 때 풀려 무음이 된다
        # 사람이 듣는 건 굽고 난 mp3다. 원본으로 고르면 후처리에서 무너진 것을 못 거른다
        data, dur = post(x, a.sample_rate, tempo, pitch)
        y = decode(data)
        if len(y) == 0 or np.abs(y).max() < 0.1:
            raise RuntimeError(f'{key}: 최종 mp3가 무음')
        hyp = transcribe(y, SR_OUT); e = score(key, text, hyp)
        if best is None or e < best[0]: best = (e, hyp, data, dur)
        if e <= (0.2 if NUMKEY.match(key) else 0): break
    e, hyp, data, dur = best
    if old and e >= old.get('score', old['cer']):
        old['retried'] = True; json.dump(old, open(cp, 'w'), ensure_ascii=False)
        return old, open(mp, 'rb').read()
    meta = {'key': key, 'text': text, 'cer': round(cer(text, hyp), 3), 'score': round(e, 3), 'asr': hyp, 'dur': round(dur, 3), 'retried': True}
    os.makedirs(CACHE, exist_ok=True)
    json.dump(meta, open(cp, 'w'), ensure_ascii=False); open(mp, 'wb').write(data)
    return meta, data


def pack(items):
    """mp3 조각을 한 파일로. 요청 1번, 조각별 디코드는 런타임에 필요할 때"""
    buf, idx = bytearray(), {}
    for key, data in items:
        idx[key] = [len(buf), len(data)]; buf += data
    return bytes(buf), idx


def main():
    shard = os.environ.get('VOICE_SHARD', 'all')   # op | animals | all. 굽기를 두 프로세스로 나눠 돌릴 때
    if shard.startswith('op'):   # op 또는 op:1/2 (나눠 굽기)
        i, n = (int(v) for v in shard[3:].split('/')) if ':' in shard else (0, 1)
        for j, (key, t, tempo) in enumerate(L.OP):
            if j % n == i: bake(key, t, L.OP_SID, L.OP_SPEED, tempo)
        return
    if shard == 'animals':
        for aid, (sid, pitch, speed, lines) in L.ANIMALS.items():
            for key, t in lines.items(): bake(f'{aid}_{key}', t, sid, speed, 1.0, pitch)
        return
    os.makedirs(OUT, exist_ok=True)
    qa = []
    items, text = [], {}
    for i, (key, t, tempo) in enumerate(L.OP):
        meta, data = bake(key, t, L.OP_SID, L.OP_SPEED, tempo)
        items.append((key, data)); text[key] = t; qa.append(('op', key, meta))
        print(f'[op {i + 1}/{len(L.OP)}] {key} cer={meta["cer"]} {t} → {meta["asr"]}', flush=True)
    b, idx = pack(items)
    open(os.path.join(OUT, 'op.bin'), 'wb').write(b)
    man = {'op': idx, 'text': text, 'animals': {}, 'atext': {}}
    for aid, (sid, pitch, speed, lines) in L.ANIMALS.items():
        items, atext = [], {}
        for key, t in lines.items():
            meta, data = bake(f'{aid}_{key}', t, sid, speed, 1.0, pitch)
            items.append((key, data)); atext[key] = t; qa.append((aid, key, meta))
            print(f'[{aid}] {key} cer={meta["cer"]} {t} → {meta["asr"]}', flush=True)
        b, idx = pack(items)
        open(os.path.join(OUT, f'a_{aid}.bin'), 'wb').write(b)
        man['animals'][aid] = idx; man['atext'][aid] = atext
    ver = hashlib.sha1(json.dumps(man, sort_keys=True).encode()).hexdigest()[:10]
    man['ver'] = ver
    open(os.path.join(HERE, '..', 'voice_manifest.js'), 'w', encoding='utf-8').write(
        '// 자동 생성. web/voice/bake.py\nconst VOICE_PACK = ' + json.dumps(man, ensure_ascii=False, separators=(',', ':')) + ';\n'
        'if (typeof module !== "undefined") module.exports = VOICE_PACK;\n')
    with open(os.path.join(HERE, 'qa.tsv'), 'w', encoding='utf-8') as f:
        f.write('voice\tkey\tcer\tdur\ttext\tasr\n')   # cer·asr는 최종 mp3를 다시 풀어 ASR로 읽은 값
        for v, k, m in qa: f.write(f'{v}\t{k}\t{m["cer"]}\t{m["dur"]}\t{m["text"]}\t{m["asr"]}\n')
    op = [m['cer'] for v, k, m in qa if v == 'op']
    size = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    an = [m['cer'] for v, k, m in qa if v != 'op']
    print(f'ver {ver} · 동물 {len(an)}조각 평균 CER {np.mean(an):.3f} · 관제 {len(op)}조각 평균 CER {np.mean(op):.3f} · CER>0.3 {sum(e > 0.3 for e in op)}개 · 총 {size // 1024} KB')


if __name__ == '__main__':
    main()
