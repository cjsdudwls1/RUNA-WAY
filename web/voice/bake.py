"""경주 대사 굽기. web/race_lines.md → web/static/voice/race.bin + web/voice_manifest.js + web/voice/qa.tsv

- TTS: Supertonic 3 (모델 OpenRAIL-M, 코드 MIT). 로컬 CPU 추론. 비용 0, 운영 서버 0
- 대사 한 줄을 통째로 굽는다. {km}, {set}이 든 줄은 값마다 따로(web/linebook.py)
- 문장마다 후보를 여러 개 만들어 한국어 ASR로 되읽고, 글자 오류율(CER)이 가장 낮은 것을 고른다
- 결과는 .cache에 문장+설정 해시로 저장한다. 대사를 고치면 그 줄만 다시 굽는다

준비 (1회, 약 450MB)
  pip install sherpa-onnx scipy numpy   (ffmpeg 필요)
  cd web/voice && mkdir -p models && cd models
  curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2
  curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-korean-2024-06-24.tar.bz2
  tar xjf *supertonic*.bz2 && tar xjf *korean*.bz2
실행
  python3 web/voice/bake.py                    전체 굽기
  python3 web/voice/bake.py voices "문장"      화자 0~9로 같은 문장을 구워 web/dist/voices/에. 목소리 고르기용
"""
import os, sys, json, hashlib, subprocess, re, shutil
import numpy as np
import scipy.signal as ss

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import linebook as B

# 상대 목소리. Supertonic 3 화자 번호(0~4 여성, 5~9 남성). 바꾸면 전부 다시 굽는다
SID = int(os.environ.get('VOICE_SID', '9'))
SPEED = float(os.environ.get('VOICE_SPEED', '1.1'))
MODELS = os.environ.get('VOICE_MODELS', os.path.join(HERE, 'models'))
TTS_DIR = os.path.join(MODELS, 'sherpa-onnx-supertonic-3-tts-int8-2026-05-11')
ASR_DIR = os.path.join(MODELS, 'sherpa-onnx-zipformer-korean-2024-06-24')
CACHE = os.path.join(HERE, '.cache')
OUT = os.path.join(HERE, '..', 'static', 'voice')
N_CAND = int(os.environ.get('VOICE_CAND', '2'))
RETRY_N = 4          # 오류율이 RETRY_CER를 넘으면 더 뽑는 후보 수
RETRY_CER = 0.25     # 같은 음성도 ASR이 0.15~0.2는 틀린다
SR_OUT = 24000
THREADS = int(os.environ.get('VOICE_THREADS', os.cpu_count() or 4))


def ffmpeg():
    return shutil.which('ffmpeg') or __import__('imageio_ffmpeg').get_ffmpeg_exe()


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
    return B.sino(int(m.group(0)))


def norm(t):
    t = t.replace('GPS', '지피에스').replace('킬로', '').replace('키로', '')
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
                        '-b:a', '48k', '-f', 'mp3', '-'], input=y.tobytes(), capture_output=True, check=True)
    return p.stdout, len(y) / SR_OUT


def decode(data):
    p = subprocess.run([ffmpeg(), '-v', 'error', '-i', '-', '-f', 'f32le', '-ac', '1', '-ar', str(SR_OUT), '-'], input=data, capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype='float32')


def score(text, hyp, num):
    """낮을수록 좋다. 숫자가 든 문장은 숫자가 들리는지가 먼저다"""
    e = cer(text, hyp)
    if num:
        return (0 if norm(num) in norm(hyp) else 1) + e
    return e


def gen(text, sid, speed):
    import sherpa_onnx as so
    g = so.GenerationConfig(); g.sid = sid; g.num_steps = 10; g.speed = speed; g.extra['lang'] = 'ko'
    a = tts().generate(text, g)
    return np.array(a.samples, dtype='float32', copy=True), a.sample_rate   # asarray는 엔진 버퍼를 가리킨다. 다음 생성 때 풀려 무음이 된다


def bake(text, num=None, sid=SID, speed=SPEED):
    h = hashlib.sha1(json.dumps([text, sid, speed, N_CAND, 'race1']).encode()).hexdigest()[:16]
    cp = os.path.join(CACHE, h + '.json'); mp = os.path.join(CACHE, h + '.mp3')
    if os.path.exists(cp) and os.path.exists(mp):
        return json.load(open(cp)), open(mp, 'rb').read()
    best = None
    for i in range(N_CAND + RETRY_N):
        if i >= N_CAND and best[0] <= RETRY_CER: break
        x, sr = gen(text, sid, speed)
        # 사람이 듣는 건 굽고 난 mp3다. 원본으로 고르면 후처리에서 무너진 것을 못 거른다
        data, dur = post(x, sr)
        y = decode(data)
        if len(y) == 0 or np.abs(y).max() < 0.1:
            raise RuntimeError(f'최종 mp3가 무음: {text}')
        hyp = transcribe(y, SR_OUT); e = score(text, hyp, num)
        if best is None or e < best[0]: best = (e, hyp, data, dur)
        if e <= 0.05: break
    e, hyp, data, dur = best
    meta = {'text': text, 'cer': round(cer(text, hyp), 3), 'score': round(e, 3), 'asr': hyp, 'dur': round(dur, 3)}
    os.makedirs(CACHE, exist_ok=True)
    json.dump(meta, open(cp, 'w'), ensure_ascii=False); open(mp, 'wb').write(data)
    return meta, data


def voices(text):
    """같은 문장을 화자 0~9로. 목소리 고르기용"""
    out = os.path.join(HERE, '..', 'dist', 'voices'); os.makedirs(out, exist_ok=True)
    for sid in range(10):
        x, sr = gen(B.spoken(text), sid, SPEED)
        data, dur = post(x, sr)
        f = os.path.join(out, f'voice{sid}_{"여" if sid < 5 else "남"}.mp3'); open(f, 'wb').write(data)
        print(f, round(dur, 2), 's')


def main():
    lines, _ = B.parse()
    errs = B.check(lines)
    if errs:
        print('\n'.join(errs)); sys.exit(1)
    items = B.clips(lines)
    os.makedirs(OUT, exist_ok=True)
    buf, idx, qa = bytearray(), {}, []
    for i, (cid, text, key) in enumerate(items):
        m = re.search(r'\|(\d+)$', cid)
        num = (B.sino(int(m.group(1)))) if m else None
        meta, data = bake(text, num)
        idx[cid] = [len(buf), len(data)]; buf += data
        qa.append((key, cid, meta))
        print(f'[{i + 1}/{len(items)}] {key} cer={meta["cer"]} {text} → {meta["asr"]}', flush=True)
    open(os.path.join(OUT, 'race.bin'), 'wb').write(bytes(buf))
    man = {'clips': idx, 'sid': SID, 'speed': SPEED}
    man['ver'] = hashlib.sha1(json.dumps(man, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:10]
    open(os.path.join(HERE, '..', 'voice_manifest.js'), 'w', encoding='utf-8').write(
        '// 자동 생성. web/voice/bake.py. 조각 이름 = 대사|값\nconst VOICE_PACK = ' + json.dumps(man, ensure_ascii=False, separators=(',', ':')) + ';\n'
        'if (typeof module !== "undefined") module.exports = VOICE_PACK;\n')
    with open(os.path.join(HERE, 'qa.tsv'), 'w', encoding='utf-8') as f:
        f.write('key\tcer\tdur\ttext\tasr\n')   # cer·asr는 최종 mp3를 다시 풀어 ASR로 읽은 값
        for k, c, m in qa: f.write(f'{k}\t{m["cer"]}\t{m["dur"]}\t{m["text"]}\t{m["asr"]}\n')
    e = [m['cer'] for k, c, m in qa]
    print(f'ver {man["ver"]} · {len(e)}조각 평균 CER {np.mean(e):.3f} · CER>0.3 {sum(x > 0.3 for x in e)}개 · {len(buf) // 1024} KB')


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'voices':
        voices(sys.argv[2])
    else:
        main()
