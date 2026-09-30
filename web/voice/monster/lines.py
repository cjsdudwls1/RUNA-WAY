"""괴물런 대사 후보 읽기. 검수 페이지, 녹음 대본, 굽기가 같이 쓴다

- lines.txt(MVP 4종 + 내레이터)와 parts/*.txt(나머지 괴물·모드)를 합쳐 읽는다
- 같은 모드의 괴물은 상황 틀이 같다. 틀은 lines.txt의 도깨비(경주)와 처녀귀신(공포)

  python3 web/voice/monster/lines.py                    # 역할별 후보 수, 추천 수, 긴 대사
  python3 web/voice/monster/lines.py --check 파일        # 형식·상황 틀·후보 수·금지어·중복 검사
  python3 web/voice/monster/lines.py --skeleton 경주|공포  # 빈 틀 출력(상황 머리줄 + 후보 수)
"""
import os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, 'lines.txt')
TEMPLATE_ROLE = {'경주': 'dokkaebi', '공포': 'cheonyeo'}
NARRATORS = {'caster', 'narrator'}   # 괴물이 아니라 틀 비교에서 뺀다
BANNED = re.compile(r'씨발|시발|병신|좆|존나|개새|미친놈|미친년|죽어버|자살|목매|손목')
LONG = 26          # 약 4초. 소개(intro*)는 30


def parse_file(path):
    roles, role, sit = [], None, None
    for n, raw in enumerate(open(path, encoding='utf-8'), 1):
        line = raw.rstrip('\n')
        if line.startswith('# role '):
            rid, name, mode, who, note = [x.strip() for x in line[len('# role '):].split('|')]
            role = {'id': rid, 'name': name, 'mode': mode, 'who': who, 'note': note, 'sits': [], 'file': os.path.basename(path)}
            roles.append(role); sit = None
        elif line.startswith('## '):
            sid, name, cond, want, d = [x.strip() for x in line[3:].split('|')]
            sit = {'id': sid, 'name': name, 'cond': cond, 'want': int(want), 'dir': d, 'cands': []}
            role['sits'].append(sit)
        elif line.startswith('- '):
            if sit is None: raise ValueError(f'{path}:{n} 상황 머리줄(##)보다 대사가 먼저 나왔다')
            text, _, d = line[2:].partition(' // ')
            i = len(sit['cands']) + 1
            sit['cands'].append({'id': f"{role['id']}.{sit['id']}.{i:02d}", 'text': text.strip(), 'dir': d.strip(), 'rec': i <= sit['want']})
        elif line.strip() and not line.startswith('#'):
            raise ValueError(f'{path}:{n} 알 수 없는 줄: {line}')
    for r in roles:
        for s in r['sits']:
            if s['want'] > len(s['cands']): raise ValueError(f"{r['id']}.{s['id']}: 고를 수 {s['want']} > 후보 {len(s['cands'])}")
    return roles


def files():
    return [MAIN] + sorted(glob.glob(os.path.join(HERE, 'parts', '*.txt')))


def parse(paths=None):
    roles = [r for p in (paths or files()) for r in parse_file(p)]
    seen = set()
    for r in roles:
        if r['id'] in seen: raise ValueError(f"역할 아이디가 겹친다: {r['id']}")
        seen.add(r['id'])
    return roles


def syllables(t):
    return len(re.findall(r'[가-힣]', t))


def templates():
    main = {r['id']: r for r in parse_file(MAIN)}
    return {mode: main[rid] for mode, rid in TEMPLATE_ROLE.items()}


def check(path):
    """틀과 같은 상황(아이디·조건·고를 수), 같은 후보 수, 길이·금지어·중복. 반환: (오류, 경고)
    상황 이름과 기본 지시는 괴물마다 바꿔도 된다. 다른 상황끼리 같은 대사는 경고(공포의 반복은 허용)"""
    errs, warns = [], []
    try:
        roles = parse_file(path)
    except ValueError as e:
        return [str(e)], []
    T = templates()
    for r in roles:
        t = T.get(r['mode'])
        if not t: errs.append(f"{r['id']}: 모드는 경주 또는 공포"); continue
        if r['id'] not in NARRATORS:
            want = [(s['id'], s['cond'], s['want'], len(s['cands'])) for s in t['sits']]
            got = [(s['id'], s['cond'], s['want'], len(s['cands'])) for s in r['sits']]
            if [g[:3] for g in got] != [w[:3] for w in want]:
                errs.append(f"{r['id']}: 상황 아이디·조건·고를 수가 틀과 다르다(--skeleton {r['mode']} 그대로 쓸 것)")
            for g, w in zip(got, want):
                if g[3] != w[3]: errs.append(f"{r['id']}.{g[0]}: 후보 {g[3]}개, {w[3]}개여야 한다")
        texts = {}
        for s in r['sits']:
            for c in s['cands']:
                n = syllables(c['text']); lim = 30 if s['id'].startswith('intro') else LONG
                if n > lim: errs.append(f"{c['id']}: {n}음절, {lim} 넘음: {c['text']}")
                if BANNED.search(c['text']): errs.append(f"{c['id']}: 금지어: {c['text']}")
                k = re.sub(r'[^가-힣a-z0-9]', '', c['text'])
                if k in texts:
                    same = texts[k].rsplit('.', 1)[0] == c['id'].rsplit('.', 1)[0]
                    (errs if same else warns).append(f"{c['id']}: {texts[k]}와 같은 대사")
                texts[k] = c['id']
    return errs, warns


def skeleton(mode):
    t = templates()[mode]
    out = []
    for s in t['sits']:
        out.append(f"## {s['id']} | {s['name']} | {s['cond']} | {s['want']} | {s['dir']}")
        out.append(f"#> 후보 {len(s['cands'])}개. 위에서부터 {s['want']}개가 추천")
    return '\n'.join(out)


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--check':
        e, w = check(sys.argv[2])
        for x in w: print('경고', x)
        print('\n'.join('오류 ' + x for x in e) if e else '통과')
        sys.exit(1 if e else 0)
    if len(sys.argv) > 2 and sys.argv[1] == '--skeleton':
        print(skeleton(sys.argv[2])); sys.exit(0)
    R = parse()
    tc = tw = 0
    for r in R:
        c = sum(len(s['cands']) for s in r['sits']); w = sum(s['want'] for s in r['sits'])
        tc += c; tw += w
        print(f"{r['id']:12s} {r['name']:8s} {r['mode']} 녹음 {r['who']:4s} 상황 {len(r['sits']):2d} 후보 {c:3d} 고를 수 {w:3d}")
    print(f'합계 역할 {len(R)}, 후보 {tc}, 고를 수 {tw}')
    long = [(syllables(c['text']), c['id'], c['text']) for r in R for s in r['sits'] for c in s['cands'] if syllables(c['text']) > LONG]
    print(f'{LONG + 1}음절 넘는 대사(약 4초 넘음) {len(long)}개')
    for x in sorted(long, reverse=True)[:20]: print(' ', *x)
