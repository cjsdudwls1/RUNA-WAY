"""오디션 표 이어 붙이기 미리듣기. 앱과 같은 규칙: 조각 사이 0.035초, 조각이 . ! ?로 끝나면 0.1초(app.html playPack)

- 조각 출처
  - --src <폴더>: 외부에서 구운 wav 후보(<키>__<번호>.wav). bake.py와 같은 방법(최종 mp3를 ASR로 되읽은 점수 + 길이 검사)으로 고른다
  - --pack: 지금 팩(web/static/voice/op.bin, hit.bin + web/voice_manifest.js)
- 결과: <out>/<이름>.mp3, <out>/preview.json(조각마다 고른 후보, CER, ASR이 들은 말, 길이)
실행
  python3 web/voice/preview.py --src web/voice/audition/A/src --out web/voice/audition/A/preview
  python3 web/voice/preview.py --pack --out web/voice/preview
"""
import os, sys, json, re, argparse, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lines as L  # noqa: E402

# README 오디션 표. 한 줄에 여러 문장이면(잡힘) 문장 사이를 0.8초 띄운다
TABLE = [
    ('intro', '소개', [['intro_head', 'name_cheetah', 'cnt1', 'intro_hide', 'intro_max', 'kmh100', 'intro_tail']]),
    ('spotted', '발견', [['spotted']]),
    ('sprint1', '첫 돌진', [['dc_rb', 'kmh35', 'hold']]),
    ('sprint2', '두 번째 돌진', [['again', 'dx_l', 'kmh28']]),
    ('rejoin', '복귀', [['dr_lb', 'm120']]),
    ('tired', '지침', [['tired1']]),
    ('caught', '잡힘', [['caught1'], ['hit2']]),
    ('half', '절반', [['half1']]),
    ('cool', '쿨다운', [['cool']]),
    ('success', '성공', [['end_arrive', 'end_hits0', 'end_final', 'n12', 'unit_min', 'n30', 'unit_sec']]),
    ('fail', '실패', [['end_fail']]),
]
SR = 24000


def keys():
    return [k for _, _, seqs in TABLE for s in seqs for k in s]


def text_of():
    return {k: t for k, t, _ in L.OP + L.HIT}


def from_pack():
    src = open(os.path.join(HERE, '..', 'voice_manifest.js'), encoding='utf-8').read()
    man = json.loads(re.search(r'const VOICE_PACK = (\{.*\});', src).group(1))
    op = open(os.path.join(HERE, '..', 'static', 'voice', 'op.bin'), 'rb').read()
    hit = open(os.path.join(HERE, '..', 'static', 'voice', 'hit.bin'), 'rb').read()
    out = {}
    for k in keys():
        a, n = (man.get('hit') or {}).get(k) or man['op'][k]
        out[k] = ({'key': k, 'engine': man.get('engine', '')}, (hit if k in (man.get('hit') or {}) else op)[a:a + n])
    return out


def from_src(folder):
    import bake
    bake.SRC = folder
    t = text_of()
    tempo = {k: tp for k, _, tp in L.OP + L.HIT}
    out = {}
    for k in keys():
        r = bake.from_src(k, t[k], tempo[k])
        if r is None: sys.exit(f'{k}: 후보 wav가 없다 ({folder})')
        out[k] = r
    return out


def ff():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def decode(b):
    p = subprocess.run([ff(), '-v', 'error', '-i', '-', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], input=b, capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype='float32')


def encode(y, path):
    subprocess.run([ff(), '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '96k', path],
                   input=y.astype('float32').tobytes(), check=True)


def build(clips, out):
    os.makedirs(out, exist_ok=True)
    t = text_of()
    res = {'rows': [], 'clips': {}}
    for name, ko, seqs in TABLE:
        parts = []
        for si, seq in enumerate(seqs):
            if si: parts.append(np.zeros(int(SR * 0.8), dtype='float32'))
            for k in seq:
                parts.append(decode(clips[k][1]))
                parts.append(np.zeros(int(SR * (0.1 if re.search(r'[.!?]$', t[k]) else 0.035)), dtype='float32'))
        y = np.concatenate(parts[:-1])
        encode(y, os.path.join(out, name + '.mp3'))
        res['rows'].append({'name': name, 'ko': ko, 'seqs': seqs, 'text': [' '.join(t[k] for k in s) for s in seqs], 'dur': round(len(y) / SR, 2)})
    for k, (m, _) in clips.items():
        res['clips'][k] = {x: m.get(x) for x in ('cer', 'score', 'asr', 'dur', 'file', 'n') if x in m}
    cers = [c['cer'] for c in res['clips'].values() if isinstance(c.get('cer'), (int, float)) and c['cer'] >= 0]
    if cers: res['cer_mean'] = round(float(np.mean(cers)), 3); res['cer_over_03'] = [k for k, c in res['clips'].items() if (c.get('cer') or 0) > 0.3]
    json.dump(res, open(os.path.join(out, 'preview.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src'); ap.add_argument('--pack', action='store_true'); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    if not a.src and not a.pack: ap.error('--src 또는 --pack')
    clips = from_pack() if a.pack else from_src(a.src)
    r = build(clips, a.out)
    print(f"{a.out}: {len(r['rows'])}개, CER 평균 {r.get('cer_mean')}, 0.3 넘는 조각 {r.get('cer_over_03')}")


if __name__ == '__main__':
    main()
