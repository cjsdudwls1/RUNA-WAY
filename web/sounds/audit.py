"""소리 파일 검사. 파일 이름이 말하는 동물 소리가 맞는지 AudioSet 분류기(527종)로 본다

- 사람 귀 대신이 아니라 사람 귀 앞의 거름망이다. 걸린 것을 사람이 먼저 듣는다
- 두 모델(CED-base, Zipformer)의 점수 중 큰 값을 쓴다. 한 모델만 틀리는 일이 잦다
- AudioSet에 없는 동물(코끼리, 하마, 낙타, 캥거루, 나무늘보 등)은 "기대 소리"를 넓게 잡고 "다른 동물로 들림"만 강하게 본다

준비 (1회, 약 700MB. GitHub 릴리스)
  pip install sherpa-onnx soundfile numpy imageio-ffmpeg
  mkdir -p web/sounds/.models && cd web/sounds/.models
  curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/audio-tagging-models/sherpa-onnx-ced-base-audio-tagging-2024-04-19.tar.bz2
  curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/audio-tagging-models/sherpa-onnx-zipformer-audio-tagging-2024-04-09.tar.bz2
  tar xjf sherpa-onnx-ced-base*.bz2 && tar xjf sherpa-onnx-zipformer-audio*.bz2 && rm *.bz2
실행
  python3 web/sounds/audit.py                         # web/sounds/*.mp3 전부 → web/sounds/audit/report.json
  python3 web/sounds/audit.py 파일.mp3 --as pig_sprint  # 후보 파일을 '돼지 돌진'으로 검사
  python3 web/sounds/audit.py web/sounds/candidates    # candidates/<슬롯>/<번호>.mp3 전부 (슬롯 이름으로 검사)
판정
  BAD      다른 동물(또는 사람 말)로 들린다. 기대 소리보다 뚜렷하다
  SUSPECT  기대 소리가 거의 안 잡히거나, 다른 동물 기미가 있거나, 길이·음량이 규격 밖
  OK       기대 소리가 잡히고 다른 동물 기미가 없다
"""
import os, sys, json, re, subprocess, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.environ.get('AUDIT_MODELS', os.path.join(HERE, '.models'))

# ---------- 소리 무리 (AudioSet 라벨 이름 그대로) ----------
G = {
    'dog': ['Dog', 'Bark', 'Yip', 'Howl', 'Bow-wow', 'Growling', 'Whimper (dog)', 'Canidae, dogs, wolves'],
    'cat': ['Cat', 'Purr', 'Meow', 'Caterwaul', 'Roaring cats (lions, tigers)'],
    'horse': ['Horse', 'Clip-clop', 'Neigh, whinny'],
    'cattle': ['Cattle, bovinae', 'Moo'],
    'pig': ['Pig', 'Oink'],
    'goat': ['Goat', 'Bleat', 'Sheep'],
    'chicken': ['Fowl', 'Chicken, rooster', 'Cluck', 'Crowing, cock-a-doodle-doo', 'Turkey', 'Gobble'],
    'duck': ['Duck', 'Quack', 'Goose', 'Honk'],
    'bird': ['Bird', 'Bird vocalization, bird call, bird song', 'Chirp, tweet', 'Squawk', 'Pigeon, dove', 'Coo', 'Crow', 'Caw', 'Owl', 'Hoot', 'Bird flight, flapping wings'],
    'rodent': ['Rodents, rats, mice', 'Mouse'],
    'insect': ['Insect', 'Cricket', 'Mosquito', 'Fly, housefly', 'Buzz', 'Bee, wasp, etc.'],
    'frog': ['Frog', 'Croak'],
    'whale': ['Whale vocalization'],
    'speech': ['Speech', 'Male speech, man speaking', 'Female speech, woman speaking', 'Child speech, kid speaking', 'Conversation', 'Narration, monologue', 'Babbling'],
    'baby': ['Baby cry, infant cry'],
    'music': ['Music', 'Musical instrument', 'Singing'],
    # 동물 무리가 아닌 기대 소리
    'hiss': ['Hiss', 'Snake'],
    'breath': ['Breathing', 'Pant', 'Gasp', 'Wheeze', 'Snort', 'Snoring', 'Sniff'],
    'growl': ['Growling', 'Roar', 'Grunt', 'Groan', 'Roaring cats (lions, tigers)'],
    'steps': ['Walk, footsteps', 'Run', 'Thump, thud', 'Patter', 'Clip-clop'],
    'rustle': ['Rustle', 'Rustling leaves', 'Scratch', 'Crunch', 'Scrape'],
    'squeak': ['Squeak', 'Squeal', 'Chirp, tweet', 'Whistle'],
    'chirp': ['Chirp, tweet', 'Bird vocalization, bird call, bird song'],   # 새 무리 전체가 아니라 짹 소리만. 치타·다람쥐·나무늘보 울음
    'scream': ['Screaming', 'Squeal', 'Yell', 'Shout'],
    'trumpet': ['Trumpet', 'Brass instrument'],
    'wild': ['Animal', 'Wild animals', 'Domestic animals, pets', 'Livestock, farm animals, working animals'],
}
# 특정 종 라벨. 기대 소리보다 크면 다른 동물이다(2026-09-26 검토: 까마귀가 다람쥐로, 비둘기가 타조로 통과했다)
SPECIES = ['Crow', 'Caw', 'Pigeon, dove', 'Coo', 'Chicken, rooster', 'Cluck', 'Fowl', 'Turkey', 'Gobble', 'Duck', 'Quack', 'Goose', 'Honk', 'Owl', 'Hoot',
           'Cattle, bovinae', 'Moo', 'Frog', 'Croak', 'Pig', 'Oink', 'Horse', 'Neigh, whinny', 'Goat', 'Bleat', 'Sheep', 'Cat', 'Meow', 'Dog', 'Bark', 'Yip', 'Mouse', 'Cricket']
ANIMAL_GROUPS = ['dog', 'cat', 'horse', 'cattle', 'pig', 'goat', 'chicken', 'duck', 'bird', 'rodent', 'insect', 'frog', 'whale', 'speech', 'baby', 'music']

# ---------- 동물·상태별 기대 무리 ----------
# 'strong': AudioSet에 그 동물 라벨이 있다. 기대 점수가 낮으면 의심
# 'weak': 없다. 다른 동물로 들리는지만 강하게 본다
DOGS = {'roam': ['dog', 'growl'], 'sprint': ['dog'], 'tired': ['breath', 'dog']}
EXPECT = {
    'elephant': ('weak', {'roam': ['growl', 'wild', 'trumpet'], 'sprint': ['trumpet', 'growl', 'wild', 'scream'], 'tired': ['breath', 'wild']}),
    'chicken': ('strong', {'roam': ['chicken'], 'sprint': ['chicken', 'bird'], 'tired': ['chicken']}),
    'sloth': ('weak', {'roam': ['rustle'], 'sprint': ['squeak', 'chirp'], 'tired': ['breath']}),
    'loris': ('weak', {'roam': ['squeak', 'chirp', 'rodent'], 'sprint': ['hiss', 'squeak'], 'tired': ['breath']}),
    'gila': ('weak', {'roam': ['hiss'], 'sprint': ['hiss'], 'tired': ['hiss', 'breath']}),
    'chihuahua': ('strong', DOGS),
    'crocodile': ('weak', {'roam': ['growl', 'wild', 'frog'], 'sprint': ['hiss', 'growl'], 'tired': ['breath', 'hiss']}),
    'komodo': ('weak', {'roam': ['hiss'], 'sprint': ['hiss', 'rustle'], 'tired': ['breath', 'hiss']}),
    'squirrel': ('weak', {'roam': ['squeak', 'chirp', 'rodent'], 'sprint': ['squeak', 'chirp', 'rodent'], 'tired': ['breath']}),
    'koala': ('weak', {'roam': ['growl', 'pig', 'breath'], 'sprint': ['growl', 'pig'], 'tired': ['breath']}),
    'cat': ('strong', {'roam': ['cat'], 'sprint': ['cat', 'hiss'], 'tired': ['breath', 'cat']}),
    'pig': ('strong', {'roam': ['pig'], 'sprint': ['pig', 'scream'], 'tired': ['pig', 'breath']}),
    'armadillo': ('weak', {'roam': ['rustle', 'breath'], 'sprint': ['steps', 'rustle'], 'tired': ['breath']}),
    'hippo': ('weak', {'roam': ['growl', 'wild'], 'sprint': ['growl', 'wild'], 'tired': ['breath']}),
    'greyhound': ('strong', DOGS),
    'kangaroo': ('weak', {'roam': ['growl', 'breath'], 'sprint': ['steps'], 'tired': ['breath']}),
    'cheetah': ('strong', {'roam': ['chirp', 'cat', 'squeak'], 'sprint': ['hiss', 'growl', 'cat'], 'tired': ['breath', 'cat']}),
    'hare': ('weak', {'roam': ['rustle', 'steps'], 'sprint': ['steps', 'rustle'], 'tired': ['breath']}),
    'wolf': ('strong', DOGS),
    'jindo': ('strong', DOGS),
    'horse': ('strong', {'roam': ['horse', 'breath'], 'sprint': ['horse', 'steps'], 'tired': ['breath', 'horse']}),
    'camel': ('weak', {'roam': ['growl', 'wild', 'cattle'], 'sprint': ['growl', 'wild', 'cattle', 'scream'], 'tired': ['breath']}),
    'sleddog': ('strong', DOGS),
    'ostrich': ('weak', {'roam': ['growl', 'wild'], 'sprint': ['hiss', 'steps'], 'tired': ['breath']}),   # 타조 붐 울음은 낮은 '웅'. 비둘기 구구가 통과하면 안 된다
    'pronghorn': ('weak', {'roam': ['breath'], 'sprint': ['breath', 'steps'], 'tired': ['breath']}),
    # 동물군 공용
    'bird': ('strong', {'roam': ['bird', 'chicken'], 'sprint': ['bird', 'chicken'], 'tired': ['bird', 'chicken', 'breath']}),
    'canine': ('strong', DOGS),
    'feline': ('strong', {'roam': ['cat'], 'sprint': ['cat', 'hiss'], 'tired': ['breath', 'cat']}),
    'reptile': ('weak', {'roam': ['hiss', 'growl'], 'sprint': ['hiss'], 'tired': ['breath', 'hiss']}),
    'hoof': ('weak', {'roam': ['horse', 'cattle', 'pig', 'goat', 'breath', 'growl'], 'sprint': ['horse', 'steps', 'pig', 'cattle'], 'tired': ['breath']}),
    'small': ('weak', {'roam': ['rustle', 'squeak', 'rodent'], 'sprint': ['squeak', 'rodent', 'steps'], 'tired': ['breath']}),
    # 괴물: 만든 소리. 괴성은 사람 비명·으르렁이 섞여도 된다. 대사는 사람 말이어야 한다
    'monster': ('weak', {'roam': ['growl', 'scream', 'breath'], 'sprint': ['growl', 'scream'], 'tired': ['breath', 'growl'], 'step': ['steps'], 'line': ['speech', 'scream']}),
}
MONSTERS = {'dokkaebi', 'jeoseung'}
BIG_DOGS = {'greyhound', 'wolf', 'jindo', 'sleddog'}
# 규격 길이(초). README 음향 규격. sprint 하한은 0.5초로 올려 본다: 0.34초 조각은 사람도 무슨 동물인지 못 가린다(2026-09-26 그레이하운드)
DUR = {'roam': (0.4, 2.0), 'sprint': (0.5, 1.2), 'tired': (0.8, 2.5), 'step': (0.2, 0.5), 'line': (0.3, 6.0)}


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def load(f, sr=16000):
    p = subprocess.run([ffmpeg(), '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype='float32').copy()


_T = None


def taggers():
    global _T
    if _T is None:
        import sherpa_onnx as so
        out = {}
        d = os.path.join(MODELS, 'sherpa-onnx-ced-base-audio-tagging-2024-04-19')
        if os.path.isdir(d):
            out['ced'] = so.AudioTagging(so.AudioTaggingConfig(model=so.AudioTaggingModelConfig(ced=os.path.join(d, 'model.onnx'), num_threads=4, provider='cpu'),
                                                               labels=os.path.join(d, 'class_labels_indices.csv'), top_k=527))
        d = os.path.join(MODELS, 'sherpa-onnx-zipformer-audio-tagging-2024-04-09')
        if os.path.isdir(d):
            out['zip'] = so.AudioTagging(so.AudioTaggingConfig(model=so.AudioTaggingModelConfig(zipformer=so.OfflineZipformerAudioTaggingModelConfig(model=os.path.join(d, 'model.onnx')), num_threads=4, provider='cpu'),
                                                               labels=os.path.join(d, 'class_labels_indices.csv'), top_k=527))
        if not out: sys.exit(f'분류 모델이 없다: {MODELS}\n  이 파일 맨 위 준비 절 참고')
        _T = out
    return _T


def tag(x):
    """모델별 {라벨: 확률}"""
    if len(x) < 16000: x = np.concatenate([x, np.zeros(16000 - len(x), dtype='float32')])   # 1초 미만은 무음으로 채운다
    res = {}
    for k, t in taggers().items():
        s = t.create_stream(); s.accept_waveform(16000, x)
        res[k] = {e.name: float(e.prob) for e in t.compute(s, 527)}
    return res


def f0(x, sr=16000):
    """유성 구간의 기본 주파수 중앙값(Hz). 개 크기(굵은 짖음 vs 높은 깽깽) 참고용. 없으면 None"""
    n, hop = 1024, 256
    vals = []
    thr = max(1e-4, np.abs(x).max() * 0.1)
    for i in range(0, len(x) - n, hop):
        w = x[i:i + n] * np.hanning(n)
        if np.sqrt((w ** 2).mean()) < thr * 0.3: continue
        ac = np.fft.irfft(np.abs(np.fft.rfft(w, 2 * n)) ** 2)[:n]
        lo, hi = int(sr / 2000), int(sr / 80)   # 80~2000Hz
        if ac[0] <= 0: continue
        j = lo + int(np.argmax(ac[lo:hi]))
        if ac[j] / ac[0] > 0.45: vals.append(sr / j)
    return float(np.median(vals)) if len(vals) >= 3 else None


def parse(name):
    """파일 이름 → (동물, 상태). candidates/<슬롯>/n.mp3는 슬롯 이름으로"""
    k = os.path.splitext(os.path.basename(name))[0]
    m = re.match(r'^([a-z]+)_(roam|sprint|tired|step|line)(?:_[a-z]+)?(?:_\d+)?$', k)
    return (m.group(1), m.group(2)) if m else (None, None)


def judge(animal, kind, probs, dur, rms_db, peak_db, hz, hf=None):
    m = {}
    for k in probs:
        for lab, p in probs[k].items(): m[lab] = max(m.get(lab, 0), p)
    grp = lambda g: max(((m.get(l, 0), l) for l in G[g]), default=(0, ''))
    cls = 'monster' if animal in MONSTERS else animal
    strength, table = EXPECT.get(cls, ('weak', {}))
    want = table.get(kind, [])
    exp = max([grp(g) for g in want], default=(0, ''))
    # 기대 무리에 든 동물 무리는 '남'이 아니다. 말(speech)은 대사에서만 남이 아니다
    others = [(grp(g)[0], g, grp(g)[1]) for g in ANIMAL_GROUPS if g not in want]
    others.sort(reverse=True)
    wrong = others[0] if others else (0, '', '')
    notes = []
    verdict = 'OK'
    wanted = {l for g in want for l in G[g]}
    species = max(((m.get(l, 0), l) for l in SPECIES if l not in wanted), default=(0, ''))
    if wrong[0] >= 0.3 and wrong[0] > exp[0]: verdict = 'BAD'; notes.append(f'{wrong[1]}로 들림({wrong[2]} {wrong[0]:.2f})')
    elif species[0] >= 0.25 and species[0] > exp[0]: verdict = 'BAD'; notes.append(f'다른 종으로 들림({species[1]} {species[0]:.2f})')
    elif wrong[0] >= 0.15: verdict = 'SUSPECT'; notes.append(f'{wrong[1]} 기미({wrong[2]} {wrong[0]:.2f})')
    if strength == 'strong' and exp[0] < 0.1:
        verdict = 'BAD' if verdict == 'BAD' or exp[0] < 0.03 else 'SUSPECT'; notes.append(f'기대 소리 약함({exp[1] or "-"} {exp[0]:.2f})')
    if animal in BIG_DOGS and kind == 'sprint':
        yip, big = m.get('Yip', 0), max(m.get('Bark', 0), m.get('Bow-wow', 0))
        if yip > big: verdict = 'SUSPECT' if verdict == 'OK' else verdict; notes.append(f'작은 개 깽깽(Yip {yip:.2f} > Bark {big:.2f})')
        # 짖음은 유성 구간이 짧아 음높이가 불안정하다. 1.5kHz 위/아래 에너지 비가 더 믿을 만하다. 큰 개 0.00~0.07, 치와와·뺀 그레이하운드 0.19~0.33
        if hf is not None and hf > 0.12: verdict = 'BAD' if hf > 0.18 else ('SUSPECT' if verdict == 'OK' else verdict); notes.append(f'고역 비 {hf:.2f}. 작은 개 짖음(큰 개는 0.10 이하)')
        elif hz and hz > 700: verdict = 'SUSPECT' if verdict == 'OK' else verdict; notes.append(f'음높이 {hz:.0f}Hz. 큰 개치고 높다')
    lo, hi = DUR.get(kind, (0, 99))
    if dur < lo or dur > hi: verdict = 'SUSPECT' if verdict == 'OK' else verdict; notes.append(f'길이 {dur:.2f}초(규격 {lo}~{hi})')
    if rms_db < -24 or rms_db > -12: verdict = 'SUSPECT' if verdict == 'OK' else verdict; notes.append(f'평균 음량 {rms_db:.1f}dBFS')
    top = sorted(m.items(), key=lambda kv: -kv[1])[:5]
    return {'verdict': verdict, 'notes': notes, 'expect': [exp[1], round(exp[0], 3)], 'wrong': [wrong[1], wrong[2], round(wrong[0], 3)],
            'top': [[l, round(p, 3)] for l, p in top]}


def audit(path, as_slot=None):
    animal, kind = parse(as_slot or path)
    if not animal: return None
    x = load(path)
    X = load(path, 44100)   # 음량과 고역은 원래 대역으로
    dur = len(X) / 44100
    act = X[np.abs(X) > 0.01]
    rms_db = 20 * np.log10(max(1e-6, np.sqrt((act ** 2).mean()) if len(act) else 1e-6))
    peak_db = 20 * np.log10(max(1e-6, np.abs(X).max()))
    sp = np.abs(np.fft.rfft(X)) ** 2; fr = np.fft.rfftfreq(len(X), 1 / 44100)
    lo_e = sp[(fr >= 80) & (fr < 1500)].sum(); hf = float(sp[fr >= 1500].sum() / lo_e) if lo_e > 0 else None
    hz = f0(x)
    r = judge(animal, kind, tag(x), dur, rms_db, peak_db, hz, hf)
    r['hf_ratio'] = round(hf, 3) if hf is not None else None
    r.update({'file': os.path.relpath(path, HERE), 'animal': animal, 'kind': kind, 'dur': round(float(dur), 2), 'rms_db': round(float(rms_db), 1), 'peak_db': round(float(peak_db), 1), 'f0': int(round(hz)) if hz else None})
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='*', default=[HERE])
    ap.add_argument('--as', dest='slot', help='후보 파일을 이 슬롯으로 검사 (예: pig_sprint)')
    ap.add_argument('--json', help='결과 JSON 경로 (기본: web/sounds 전체 검사일 때 web/sounds/audit/report.json)')
    a = ap.parse_args()
    files = []
    for p in a.paths:
        if os.path.isdir(p):
            for root, _, fs in os.walk(p):
                if '.models' in root or os.sep + 'review' in root: continue
                for f in sorted(fs):
                    if f.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                        slot = os.path.basename(root) if parse(os.path.basename(root))[0] else None   # candidates/<슬롯>/n.mp3
                        files.append((os.path.join(root, f), slot))
        else: files.append((p, a.slot))
    out = []
    used = {}   # 원본 주소 → 쓰는 동물들 (credits.json)
    try:
        for c in json.load(open(os.path.join(HERE, 'credits.json'), encoding='utf-8')):
            used.setdefault(c.get('source_url', ''), set()).add(c.get('animal', ''))
    except FileNotFoundError: pass
    cinfo = {}
    try:
        for c in json.load(open(os.path.join(HERE, 'candidates', 'candidates.json'), encoding='utf-8')): cinfo[os.path.basename(c.get('file', ''))] = c; cinfo[c.get('file', '')] = c
    except FileNotFoundError: pass
    for f, slot in files:
        r = audit(f, slot)
        if r is None: continue
        if slot:
            r['slot'] = slot
            c = cinfo.get(r['file'].replace(os.sep, '/')) or {}
            others = used.get(c.get('source_url', ''), set()) - {r['animal']} - {''}
            if others: r['verdict'] = 'BAD'; r['notes'].append('원본을 이미 다른 동물이 쓴다: ' + ', '.join(sorted(others)))
        out.append(r)
        print(f"{r['verdict']:8} {r['file']:42} {r['dur']:5.2f}s  기대 {r['expect'][0] or '-'} {r['expect'][1]:.2f}  " + ('; '.join(r['notes']) or '') + f"  | {', '.join(l for l, _ in r['top'][:3])}", flush=True)
    dst = a.json or (os.path.join(HERE, 'audit', 'report.json') if a.paths == [HERE] else None)
    if dst:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n = {v: sum(r['verdict'] == v for r in out) for v in ('BAD', 'SUSPECT', 'OK')}
    print(f"\n{len(out)}개 · BAD {n['BAD']} · SUSPECT {n['SUSPECT']} · OK {n['OK']}" + (f' → {dst}' if dst else ''))


if __name__ == '__main__':
    main()
