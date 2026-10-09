"""소리 후보 모으기 (개발 테스트용). 실제 녹음을 찾아 다듬어 web/sounds/<id>/에 넣는다
- 출처 1: freesound.org 검색 결과 중 CC0만. 미리듣기(HQ mp3)를 받는다
- 출처 2: 괴물런 시절 녹음(claude/inspiring-goodall-v6mfyx 브랜치 web/sounds/) 중 CC0·퍼블릭 도메인
- 다듬기: 모노 44.1kHz, 앞 무음 자르기, 길이 제한, 페이드, 음량 맞춤. 발소리·심장은 한 번씩 잘라 묶음으로, 깔리는 소리는 끊김 없는 루프로
- 기록: web/sounds/credits.json (file, title, author, source_url, license, edits)
실행: python3 web/sounds/collect.py [id ...]   (id를 주면 그 소리만 다시 모은다. 이미 받은 후보는 건너뛴다)
"""
import html, json, os, re, subprocess, sys, time, urllib.parse, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SR = 44100
OLD = 'origin/claude/inspiring-goodall-v6mfyx'

# id: (방식, 최대 길이초, [(검색어, 개수, 원본 최대 길이초)])
# 방식: one = 한 번 소리, hits = 한 번씩 잘라 묶음(발소리), beat = 쿵쿵 한 쌍씩 묶음(심장), loop = 끊김 없는 루프
PLAN = {
    'step':    ('hits', 0.4, [('footsteps running gravel', 2, 60), ('running footsteps dirt', 2, 60), ('footsteps forest walking', 1, 60), ('heavy footsteps', 2, 60), ('footsteps snow', 1, 60), ('boots footsteps', 1, 60), ('footsteps leaves', 1, 60)]),
    'heart':   ('beat', 0.7, [('heartbeat', 3, 60), ('heart beat', 2, 60)]),
    'breath':  ('one', 2.6, [('heavy breathing', 2, 30), ('panting man', 2, 30), ('out of breath', 2, 30), ('creepy breathing', 2, 30), ('monster breathing', 2, 30), ('breathing woman panting', 1, 30), ('dog panting', 1, 30)]),
    'growl':   ('one', 2.6, [('monster growl', 3, 15), ('dog growl', 2, 15), ('bear growl', 2, 15), ('creature growl', 2, 15), ('zombie growl', 2, 15), ('wolf growl', 1, 15)]),
    'pounce':  ('one', 2.4, [('monster roar', 3, 15), ('lion roar', 2, 15), ('bear roar', 2, 15), ('tiger roar', 2, 15), ('creature roar', 2, 15)]),
    'scream':  ('one', 2.6, [('woman scream', 3, 15), ('man scream', 3, 15), ('horror scream', 2, 15), ('terrified scream', 2, 15), ('death scream', 1, 15)]),
    'howl':    ('one', 4.0, [('wolf howl', 3, 30), ('coyote howl', 1, 30), ('dog howling', 2, 30)]),
    'whisper': ('one', 3.0, [('creepy whisper', 3, 20), ('ghost whisper', 2, 20), ('whispering', 2, 20)]),
    'creak':   ('one', 3.0, [('door creak', 3, 20), ('creaking gate', 2, 20), ('wood creak', 2, 20), ('rusty hinge', 1, 20)]),
    'ring':    ('one', 3.0, [('hand bell ring', 2, 20), ('small bell', 2, 20), ('temple bell', 1, 20)]),
    'drag':    ('one', 3.0, [('dragging feet', 2, 20), ('drag body', 2, 20), ('chain drag', 2, 20), ('shuffling feet', 1, 20)]),
    'bell':    ('one', 6.0, [('church bell toll', 3, 30), ('bell toll', 2, 30), ('large bell', 1, 30)]),
    'tick':    ('hits', 0.25, [('clock tick', 3, 30)]),
    'close':   ('one', 3.5, [('horror stinger', 3, 15), ('jump scare', 2, 15), ('cinematic boom', 2, 15), ('reverse swell', 1, 15)]),
    'safe':    ('one', 5.0, [('eerie music box', 3, 40), ('creepy music box', 2, 40), ('dark ambient pad', 2, 60), ('ominous choir', 1, 60)]),
    'door':    ('one', 4.0, [('door slam', 3, 20), ('heavy door close', 2, 20), ('metal door slam', 1, 20)]),
    'drone':   ('loop', 16, [('dark drone', 2, 300), ('horror ambience', 2, 300), ('low drone', 1, 300)]),
    'wind':    ('loop', 16, [('wind howling', 2, 300), ('night wind', 2, 300), ('strong wind', 1, 300)]),
    'tension': ('loop', 12, [('horror strings', 2, 120), ('dissonant violin', 2, 120), ('creepy cello', 1, 120), ('eerie strings', 1, 120)]),
}
# 괴물런 녹음 중 쓸 만한 것 (CC0·퍼블릭 도메인만). (id, 원래 파일, 후보 이름)
OLDPICK = [
    ('growl', 'chihuahua_roam_1', 'old-dog-growl-1'), ('growl', 'chihuahua_roam_3', 'old-dog-growl-2'), ('growl', 'greyhound_roam_2', 'old-dog-growl-3'),
    ('growl', 'jindo_roam_1', 'old-dog-snarl-1'), ('growl', 'jindo_roam_2', 'old-dog-snarl-2'), ('growl', 'crocodile_roam_1', 'old-alligator'),
    ('growl', 'reptile_roam_2', 'old-snake-snarl'), ('growl', 'pig_roam_1', 'old-pig-grunt'),
    ('breath', 'chihuahua_tired_1', 'old-dog-breath'), ('breath', 'jindo_tired_1', 'old-hound-pant'), ('breath', 'sleddog_tired_1', 'old-retriever-pant'),
    ('breath', 'horse_tired_1', 'old-horse-breath-1'), ('breath', 'horse_roam_1', 'old-horse-breath-2'), ('breath', 'hoof_tired_1', 'old-mule-breath'),
    ('pounce', 'cat_sprint_2', 'old-cat-yowl'), ('pounce', 'cat_sprint_1', 'old-cat-hiss'), ('pounce', 'greyhound_sprint_2', 'old-big-dog-bark'),
    ('pounce', 'pig_sprint_1', 'old-angry-pig'), ('pounce', 'elephant_sprint_1', 'old-elephant'), ('pounce', 'horse_sprint_1', 'old-horse-neigh'),
    ('howl', 'sleddog_roam_2', 'old-dog-howl'),
]
# 제목에 이 말이 있어야 받는다. 검색이 엉뚱한 걸 섞어 준다(발소리 검색에 자물쇠 소리)
MUST = {'step': r'foot|step|run|walk|gravel|jog', 'heart': r'heart', 'breath': r'breath|pant|gasp|exhal|inhal', 'growl': r'growl|snarl|grunt|monster|creature|zombie|beast',
        'pounce': r'roar|monster|creature|beast|growl', 'scream': r'scream|shriek|yell', 'howl': r'howl', 'whisper': r'whisper', 'creak': r'creak|squeak|hinge',
        'ring': r'bell|ring', 'drag': r'drag|shuffl|chain', 'bell': r'bell|toll', 'tick': r'tick|clock', 'close': r'stinger|scare|boom|hit|impact|swell|whoosh|horror',
        'safe': r'music.?box|pad|ambient|drone|choir', 'door': r'door|slam', 'drone': r'drone|ambien|dark|horror', 'wind': r'wind', 'tension': r'string|violin|cello|viola|horror'}
SKIP_WORDS = re.compile(r'\b(child|kid|baby|girl|boy|music|song|loop pack|voice over|vocal|say|says|word)\b', re.I)


def get(url, binary=False):
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (runaway sound collect)'})
            with urllib.request.urlopen(req, timeout=40) as r:
                b = r.read()
                return b if binary else b.decode('utf-8', 'replace')
        except Exception as e:
            if i == 4: raise
            time.sleep(3 * (i + 1))


def search(q):
    url = 'https://freesound.org/search/?' + urllib.parse.urlencode({'q': q, 'f': 'license:"Creative Commons 0"', 's': 'Downloads (most first)'})
    h = get(url); out = []
    for b in h.split('class="bw-search__result"')[1:]:
        m = lambda p: (re.search(p, b) or [None, None])[1]
        sid, mp3, dur, lic = m(r'data-sound-id="(\d+)"'), m(r'data-mp3="([^"]+)"'), m(r'data-duration="([^"]+)"'), m(r'title="License: ([^"]+)"')
        lab = re.search(r'aria-label="Sound (.*?) by ([^"]+)"', b)
        if not (sid and mp3 and lab): continue
        out.append({'sid': sid, 'mp3': mp3.replace('-lq.mp3', '-hq.mp3'), 'dur': float(dur or 0), 'lic': lic or '', 'title': html.unescape(lab.group(1)), 'user': html.unescape(lab.group(2))})
    return out


def decode(src_bytes):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'pipe:0', '-ac', '1', '-ar', str(SR), '-f', 'f32le', 'pipe:1'], input=src_bytes, capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32).copy()


def encode(x, path, kbps=96):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 'pipe:0', '-b:a', f'{kbps}k', path], input=np.clip(x, -1, 1).astype(np.float32).tobytes(), check=True)


def env(x, ms=5):
    k = max(1, int(SR * ms / 1000)); return np.convolve(np.abs(x), np.ones(k) / k, mode='same')


def fade(x, a=0.005, b=0.03):
    x = x.copy(); na, nb = int(SR * a), int(SR * b)
    if na: x[:na] *= np.linspace(0, 1, na)
    if nb and len(x) > nb: x[-nb:] *= np.linspace(1, 0, nb)
    return x


def level(x, peak_db=-1.0, rms_max_db=-14.0):
    p = np.max(np.abs(x)) or 1; x = x * (10 ** (peak_db / 20) / p)
    r = np.sqrt(np.mean(x ** 2)) or 1e-9; lim = 10 ** (rms_max_db / 20)
    return x * (lim / r) if r > lim else x


def one(x, maxlen):
    e = env(x); thr = 0.06 * e.max()
    i = int(np.argmax(e > thr)); i = max(0, i - int(0.02 * SR))
    y = x[i:i + int(maxlen * SR)]
    # 뒤쪽 긴 무음 자르기
    ee = env(y); j = len(y) - int(np.argmax(ee[::-1] > 0.03 * ee.max()))
    y = y[:min(len(y), j + int(0.15 * SR))]
    return level(fade(y, 0.004, min(0.3, len(y) / SR / 4)))


def hits(x, maxlen, n=6, sep=0.28):
    """소리 한 번씩. 크기 순으로 n개, 시간 순으로 돌려준다"""
    e = env(x, 4); thr = 0.25 * e.max(); s = int(sep * SR); peaks = []
    i = 0
    while i < len(e):
        if e[i] > thr:
            j = i + int(np.argmax(e[i:i + s])); peaks.append(j); i = j + s
        else: i += 1
    peaks = sorted(sorted(peaks, key=lambda p: -e[p])[:n])
    out = []
    for p in peaks:
        a = max(0, p - int(0.012 * SR)); y = x[a:a + int(maxlen * SR)]
        if len(y) > 0.08 * SR: out.append(level(fade(y, 0.002, maxlen / 3), -1, -16))
    return out


def loop(x, length):
    n, f = int(length * SR), int(1.5 * SR)
    if len(x) < n + f + SR: return None
    a = (len(x) - n - f) // 2
    seg = x[a:a + n + f]
    y = seg[:n].copy(); t = np.linspace(0, 1, f)
    y[:f] = seg[n:n + f] * np.cos(t * np.pi / 2) + seg[:f] * np.sin(t * np.pi / 2)   # 끝을 처음에 겹쳐 이음새를 없앤다
    return level(y, -3, -24)


def save(credits, rel, x, meta, kbps=96):
    encode(x, os.path.join(HERE, rel), kbps)
    credits[rel] = {'file': rel, **meta}


def main(only):
    cpath = os.path.join(HERE, 'credits.json')
    credits = {c['file']: c for c in json.load(open(cpath))} if os.path.exists(cpath) else {}
    used = {re.search(r'fs(\d+)', k).group(1) for k in credits if re.search(r'/fs\d+', k)}
    for sid, (mode, maxlen, queries) in PLAN.items():
        if only and sid not in only: continue
        for q, n, maxd in queries:
            try: res = search(q)
            except Exception as e: print('검색 실패', q, e); continue
            got = 0
            for r in res:
                if got >= n: break
                if r['sid'] in used or 'Creative Commons 0' not in r['lic'] or r['dur'] > maxd or r['dur'] < 0.3 or (SKIP_WORDS.search(r['title']) and not (sid == 'safe' and not re.search(r'child|kid|baby', r['title'], re.I))) or not re.search(MUST[sid], r['title'], re.I): continue
                try: x = decode(get(r['mp3'], True))
                except Exception as e: print('받기 실패', r['sid'], e); continue
                used.add(r['sid'])
                meta = {'title': r['title'], 'author': r['user'], 'source_url': f"https://freesound.org/people/{urllib.parse.quote(r['user'])}/sounds/{r['sid']}/",
                        'license': 'CC0 1.0', 'license_url': 'https://creativecommons.org/publicdomain/zero/1.0/', 'query': q}
                name = f"{sid}/fs{r['sid']}"
                if mode == 'one':
                    save(credits, name + '.mp3', one(x, maxlen), {**meta, 'edits': f'Freesound HQ 미리듣기, 모노, 앞 무음 자름, 최대 {maxlen}초, 페이드, 피크 -1dBFS'})
                elif mode in ('hits', 'beat'):
                    hs = hits(x, maxlen, n=6, sep=0.28 if mode == 'hits' else 0.5)
                    if len(hs) < 3: used.discard(r['sid']); continue
                    for k, h in enumerate(hs): save(credits, f'{name}-{k + 1}.mp3', h, {**meta, 'edits': f'Freesound HQ 미리듣기, 모노, 소리 한 번씩 {len(hs)}개로 자름({maxlen}초), 피크 -1dBFS'})
                elif mode == 'loop':
                    y = loop(x, maxlen)
                    if y is None: used.discard(r['sid']); continue
                    save(credits, name + '.mp3', y, {**meta, 'edits': f'Freesound HQ 미리듣기, 모노, 가운데 {maxlen}초를 끝·처음 1.5초 교차로 이어 끊김 없는 루프, 피크 -3dBFS'}, kbps=64)
                got += 1; print(sid, q, '→', r['sid'], r['title'][:50])
                time.sleep(0.5)
            time.sleep(1)
    # 괴물런 녹음
    old = {c['file']: c for c in json.loads(subprocess.check_output(['git', '-C', REPO, 'show', OLD + ':web/sounds/credits.json']))}
    for sid, f, cand in OLDPICK:
        if only and sid not in only: continue
        rel = f'{sid}/{cand}.mp3'
        c = old[f + '.mp3']
        if not (c['license'].startswith('CC0') or c['license'].lower().startswith('public')): continue
        b = subprocess.check_output(['git', '-C', REPO, 'show', f'{OLD}:web/sounds/{f}.mp3'])
        open(os.path.join(HERE, rel), 'wb').write(b)
        m = {k: v for k, v in c.items() if k not in ('file', 'animal', 'kind')}
        credits[rel] = {'file': rel, **m, 'from': f + '.mp3 (괴물런)'}
    json.dump(sorted(credits.values(), key=lambda c: c['file']), open(cpath, 'w'), ensure_ascii=False, indent=1)
    print('후보', len(credits))


# 괴물화: 실제 녹음을 느리고 낮게(0.72배). 몸집이 커 보인다. 영화 괴물 소리의 기본 방식
MONSTER = {'growl': 5, 'pounce': 5, 'breath': 4, 'scream': 3, 'whisper': 2}


def monsterize(only):
    cpath = os.path.join(HERE, 'credits.json'); credits = {c['file']: c for c in json.load(open(cpath))}
    for sid, n in MONSTER.items():
        if only and sid not in only: continue
        src = [k for k in sorted(credits) if k.startswith(sid + '/fs')][:n]
        for rel in src:
            out = rel.replace('/fs', '/mon-fs')
            if out in credits: continue
            x = decode(open(os.path.join(HERE, rel), 'rb').read())
            y = np.interp(np.arange(0, len(x) - 1, 0.72), np.arange(len(x)), x)   # 0.72배속 = 약 5.7반음 내림
            y = level(fade(y.astype(np.float32), 0.004, 0.2))
            save(credits, out, y, {**{k: v for k, v in credits[rel].items() if k != 'file'}, 'title': '괴물화 ' + credits[rel]['title'], 'edits': credits[rel].get('edits', '') + ' → 0.72배속(약 5.7반음 내림)'})
    json.dump(sorted(credits.values(), key=lambda c: c['file']), open(cpath, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] == ['monster']: monsterize(set(args[1:]))
    else: main(set(args))
