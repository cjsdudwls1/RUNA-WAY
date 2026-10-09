"""'잡았다~' 기괴한 목소리 후보 만들기 (개발 테스트용) → web/sounds/gotcha/
- 목소리: Supertonic 3 (모델 OpenRAIL-M, 코드 MIT). 로컬 CPU. 화자 0~9 중 몇 명, 문장 몇 개
- 가공: 실제 TTS 목소리를 공포 영화 방식으로 비튼다
  - clear: 원음 + 잔향(가장 또렷), deep: 조금 낮게(또렷)
  - low: 느리고 낮게(괴물)
  - demon: 원음 + 한 옥타브 아래 겹침 + 찌그러짐(악마)
  - drag: 끝을 길게 늘임 "잡았다아아~"(시간만 늘이고 높이는 낮게)
  - child: 높고 가늘게 + 긴 잔향(섬뜩한 아이 같은)
  - whisper: 노이즈 보코더로 속삭임(성대 울림 없이 숨소리로만)
  - reverse: 잔향을 거꾸로 앞에 깔고 말(빨려 들어오는 목소리)
- 괴물런 시절 도깨비 대사 '으하하하! 잡았다!'(Qwen3-TTS, Apache-2.0)도 후보로
준비: pip install sherpa-onnx numpy, 모델은 아래 MODEL 경로(sherpa-onnx tts-models 릴리스의 supertonic-3-tts-int8)
실행: python3 web/sounds/gotcha.py
"""
import json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from collect import SR, decode, encode, fade, level   # 같은 다듬기
MODEL = os.environ.get('TTS_MODEL', '')
LINES = ['잡았다~', '잡았다아~', '히히히… 잡았다.', '찾았다… 잡았다.']
SPEAKERS = [9, 6, 2, 4]   # 남 둘, 여 둘
OUT = os.path.join(HERE, 'gotcha')


def tts(text, sid, speed=0.9):
    import sherpa_onnx as so
    D = MODEL + '/'
    t = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(supertonic=so.OfflineTtsSupertonicModelConfig(
        duration_predictor=D + 'duration_predictor.int8.onnx', text_encoder=D + 'text_encoder.int8.onnx',
        vector_estimator=D + 'vector_estimator.int8.onnx', vocoder=D + 'vocoder.int8.onnx', tts_json=D + 'tts.json',
        unicode_indexer=D + 'unicode_indexer.bin', voice_style=D + 'voice.bin'), num_threads=os.cpu_count() or 4, provider='cpu')))
    g = so.GenerationConfig(); g.sid = sid; g.num_steps = 10; g.speed = speed; g.extra['lang'] = 'ko'
    a = t.generate(text, g)
    x = np.array(a.samples, dtype=np.float32)
    return resample(x, a.sample_rate, SR)


def resample(x, a, b):
    return np.interp(np.arange(0, len(x) - 1, a / b), np.arange(len(x)), x).astype(np.float32) if a != b else x


def ff(x, af):
    """ffmpeg 필터 한 번 통과"""
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 'pipe:0', '-af', af, '-ac', '1', '-ar', str(SR), '-f', 'f32le', 'pipe:1'],
                       input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32).copy()


def verb(x, sec=1.6, wet=0.45):
    """잔향. 젖은 소리는 마른 소리와 같은 에너지로 맞춘 뒤 wet만큼 더한다(넘치면 말이 뭉개진다)"""
    n = int(SR * sec); t = np.arange(n) / SR
    ir = (np.random.RandomState(7).randn(n) * np.exp(-t / (sec / 6))).astype(np.float32)
    L = len(x) + n; F = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:L].astype(np.float32)
    rx = np.sqrt(np.mean(x ** 2)) or 1e-9; ry = np.sqrt(np.mean(y[:len(x)] ** 2)) or 1e-9
    return np.concatenate([x, np.zeros(n, np.float32)]) + y * (rx / ry) * wet


def mix(a, b):
    n = max(len(a), len(b)); out = np.zeros(n, np.float32); out[:len(a)] += a; out[:len(b)] += b; return out


def vocode_whisper(x, bands=16):
    """밴드별 크기만 따라가는 노이즈 = 성대 없는 속삭임"""
    noise = np.random.RandomState(3).randn(len(x)).astype(np.float32)
    edges = np.geomspace(150, 9000, bands + 1); out = np.zeros_like(x)
    for lo, hi in zip(edges[:-1], edges[1:]):
        f = f'bandpass=f={(lo * hi) ** .5:.0f}:width_type=h:w={hi - lo:.0f}'
        e = ff(np.abs(ff(x, f)), 'lowpass=f=40')
        out += ff(noise, f) * e[:len(noise)]
    return out


def rev(x, sec=2.0):
    """거꾸로 잔향: 말 앞에 잔향이 빨려 들어온다"""
    n = int(SR * sec); r = verb(x[::-1], sec, 1.0)[::-1]
    return mix(r * 0.7, np.concatenate([np.zeros(n, np.float32), x]))


FX = {
    'clear':   lambda x: verb(x, 1.4, 0.3),   # 원음에 잔향만. 가장 또렷하다
    'deep':    lambda x: verb(ff(x, 'rubberband=pitch=0.82:formant=preserved'), 1.6, 0.35),   # 조금 낮게, 말은 또렷
    'low':     lambda x: verb(ff(x, 'rubberband=pitch=0.7:tempo=0.85:formant=shifted'), 1.2, 0.3),
    'demon':   lambda x: ff(mix(x * 0.6, ff(x, 'rubberband=pitch=0.5:formant=shifted')), 'asoftclip=type=tanh:param=2,bass=g=6:f=120'),
    'drag':    lambda x: verb(ff(x, 'rubberband=tempo=0.6:pitch=0.85'), 1.8, 0.35),
    'child':   lambda x: verb(ff(x, 'rubberband=pitch=1.35:formant=shifted'), 2.4, 0.5),
    'whisper': lambda x: verb(vocode_whisper(x), 1.0, 0.25),
    'reverse': lambda x: rev(x),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    cpath = os.path.join(HERE, 'credits.json'); credits = {c['file']: c for c in json.load(open(cpath))}
    base = {'author': '러너웨이', 'source_url': 'https://huggingface.co/Supertone/supertonic', 'license': '생성: Supertonic 3 (모델 OpenRAIL-M, 코드 MIT)', 'license_url': 'https://github.com/supertone-inc/supertonic'}
    plan = [(li, sp, fx) for li, line in enumerate(LINES) for sp in SPEAKERS for fx in FX]
    # 다 만들면 96개. 조합을 골라 줄인다: 문장마다 화자 둘, 가공은 전부
    plan = [(li, sp, fx) for (li, sp, fx) in plan if SPEAKERS.index(sp) % 2 == li % 2]
    raw = {}
    for li, sp, fx in plan:
        rel = f'gotcha/s{sp}-l{li + 1}-{fx}.mp3'
        if rel in credits: continue
        if (li, sp) not in raw: raw[(li, sp)] = tts(LINES[li], sp); print('tts', sp, LINES[li])
        y = FX[fx](raw[(li, sp)])
        y = level(fade(y, 0.003, 0.25))
        encode(y, os.path.join(HERE, rel)); credits[rel] = {'file': rel, 'title': f'"{LINES[li]}" 화자 {sp} · {fx}', **base, 'edits': f'Supertonic 3 화자 {sp}, 가공 {fx}'}
        print(rel)
    # 도깨비 대사
    OLD = 'origin/claude/inspiring-goodall-v6mfyx'
    b = subprocess.check_output(['git', '-C', os.path.dirname(os.path.dirname(HERE)), 'show', f'{OLD}:web/sounds/dokkaebi_line_hit_1.mp3'])
    x = decode(b)
    for fx in ('orig', 'low', 'demon'):
        rel = f'gotcha/dokkaebi-{fx}.mp3'
        y = x if fx == 'orig' else FX[fx](x)
        encode(level(fade(y, 0.003, 0.2)), os.path.join(HERE, rel))
        credits[rel] = {'file': rel, 'title': f'도깨비 "으하하하! 잡았다!" · {fx}', 'author': '러너웨이', 'source_url': 'https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign', 'license': '생성: Qwen3-TTS VoiceDesign (Apache-2.0)', 'license_url': 'https://www.apache.org/licenses/LICENSE-2.0', 'from': 'dokkaebi_line_hit_1.mp3 (괴물런)', 'edits': '가공 ' + fx}
    json.dump(sorted(credits.values(), key=lambda c: c['file']), open(cpath, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
