"""경주 대사표(web/race_lines.md) 읽기. build.py와 voice/bake.py가 같이 쓴다

- 대사 한 줄 = 구운 음성 조각 하나. 변수가 든 줄은 값마다 하나씩
- 조각 이름 = '대사|값' (값이 없으면 '대사|'). 앱이 같은 규칙으로 찾는다(game.js clipId). 대사를 고치면 이름이 바뀌니 안 구운 줄은 기기 음성으로 샌다
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
# 변수: 값 범위, 쓸 수 있는 상황. game.js VARS와 같아야 한다
VARS = {
    'km': (range(1, 42), {'km'}),
    'set': (range(1, 21), {'set_start', 'last_set', 'set_win', 'set_lose'}),
}
SINO = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구']


def sino(n):
    """0~9999 한자어 수사. 모델이 아라비아 숫자를 영어로 읽는 사고를 막는다"""
    if n == 0:
        return '영'
    out = ''
    for unit, w in [(1000, '천'), (100, '백'), (10, '십')]:
        q, n = divmod(n, unit)
        if q:
            out += ('' if q == 1 else SINO[q]) + w
    return out + SINO[n]


def parse(md=None):
    """## 키 · 설명 → 그 아래 '- ' 줄들. 첫 헤딩 전(쓰는 법)은 건너뛴다"""
    if md is None:
        md = open(os.path.join(HERE, 'race_lines.md'), encoding='utf-8').read()
    lines, info, key = {}, {}, None
    for raw in md.splitlines():
        m = re.match(r'^##\s+([a-z0-9_]+)\s*(?:·\s*(.*))?$', raw.strip())
        if m:
            key = m.group(1); lines[key] = []; info[key] = (m.group(2) or key).strip(); continue
        if key and raw.startswith('- '):
            t = raw[2:].strip()
            if t:
                lines[key].append(t)
    return lines, info


def check(lines):
    """규칙 위반 목록. 모르는 변수, 허용 안 된 상황의 변수, 한 줄에 변수 둘 이상"""
    errs = []
    for key, L in lines.items():
        for t in L:
            vs = re.findall(r'\{([^}]*)\}', t)
            for v in vs:
                if v not in VARS:
                    errs.append(f'{key}: 쓸 수 없는 변수 {{{v}}} → "{t}"')
                elif key not in VARS[v][1]:
                    errs.append(f'{key}: {{{v}}}는 {", ".join(sorted(VARS[v][1]))}에서만 → "{t}"')
            if len(vs) > 1:
                errs.append(f'{key}: 변수는 한 줄에 하나 → "{t}"')
    return errs


def spoken(t, var=None, v=None):
    """굽는 문장. 변수와 숫자를 한글로"""
    if var:
        t = t.replace('{' + var + '}', sino(v) + (' 킬로' if var == 'km' else ''))
    return re.sub(r'\d+', lambda m: sino(int(m.group(0))), t)


def clips(lines):
    """[(조각 이름, 굽는 문장, 상황 키)]. 같은 대사가 두 상황에 있어도 한 번만"""
    out, seen = [], set()
    for key, L in lines.items():
        for t in L:
            m = re.search(r'\{(km|set)\}', t)
            for var, v in ([(m.group(1), v) for v in VARS[m.group(1)][0]] if m else [(None, None)]):
                cid = t + '|' + ('' if v is None else str(v))
                if cid in seen:
                    continue
                seen.add(cid); out.append((cid, spoken(t, var, v), key))
    return out


if __name__ == '__main__':
    L, _ = parse()
    for e in check(L):
        print('오류', e)
    c = clips(L)
    print(len(L), '상황,', sum(len(x) for x in L.values()), '줄 →', len(c), '조각')
