"""소리 검수 페이지 만들기. 사람이 귀로 빨리 고르게 한 장에 모은다

- 입력
  - web/sounds/*.mp3, credits.json, README.md(기대 소리)
  - audit/report.json (audit.py 분류기 결과), audit/judge.json (AI 판정. 없으면 분류기 판정)
  - audit/marks.json (사람 검수 결과. 있으면 미리 채운다)
  - candidates/<슬롯>/<번호>.mp3 + candidates/candidates.json (교체 후보. 있으면 맨 위에 "후보 고르기")
- 출력
  - review/index.html: 더블클릭으로 연다(인터넷 없어도 된다). 표시는 브라우저에 저장, "결과 복사"로 AI에게 붙여 넣는다
  - audit/todo.json: 교체할 슬롯 목록(사람이 틀리다고 한 것 + 사람이 안 본 것 중 AI가 교체 추천한 것)
실행
  python3 web/sounds/review.py
  python3 web/sounds/review.py --base sounds/ --out 경로/index.html   # 오디오 경로를 바꿔 다른 곳에 올릴 때
"""
import os, re, json, argparse, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
KIND_KO = {'roam': '배회', 'sprint': '돌진', 'tired': '지침', 'step': '발소리', 'line': '대사'}
LINE_KO = {'spot': '발견', 'sprint': '돌진', 'near': '코앞', 'hit': '잡음', 'escape': '멀어짐', 'taunt': '도발'}
CLASS_KO = {'bird': '새 무리 공용', 'canine': '개 무리 공용', 'feline': '고양이 무리 공용', 'reptile': '파충류 공용', 'hoof': '발굽 동물 공용', 'small': '작은 동물 공용', 'monster': '괴물 공용'}
MONSTER_KO = {'dokkaebi': '도깨비', 'jeoseung': '저승사자'}
ORDER_CLASS = ['bird', 'canine', 'feline', 'reptile', 'hoof', 'small']


def load(p, default):
    try: return json.load(open(p, encoding='utf-8'))
    except FileNotFoundError: return default


def readme():
    """README 표 → 기대 소리. 동물 표(id별 roam/sprint/tired)와 괴물 표(파일별)"""
    names, expect, byfile = {}, {}, {}
    for line in open(os.path.join(HERE, 'README.md'), encoding='utf-8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) == 7 and re.fullmatch(r'\d+', c[0]) and re.fullmatch(r'[a-z]+', c[1]):
            names[c[1]] = c[2]; expect[c[1]] = {'roam': c[4], 'sprint': c[5], 'tired': c[6]}
        elif len(c) >= 2 and re.match(r'^(dokkaebi|jeoseung|monster)_', c[0]):
            m = re.match(r'^([a-z]+_(?:line_[a-z]+|[a-z]+))(?:_(\d+)(?:~(\d+))?)?$', c[0])
            if m:
                lo = int(m.group(2) or 1); hi = int(m.group(3) or m.group(2) or 1)
                for n in range(lo, hi + 1): byfile[f'{m.group(1)}_{n}'] = c[1]
    return names, expect, byfile


def parse(stem):
    m = re.match(r'^([a-z]+)_(roam|sprint|tired|step|line_[a-z]+)(?:_(\d+))?$', stem)
    return (m.group(1), m.group(2), int(m.group(3) or 1)) if m else (None, None, None)


def build(base='../', out=None, artifact=False):
    names, expect, byfile = readme()
    report = {os.path.basename(r['file']): r for r in load(os.path.join(HERE, 'audit', 'report.json'), [])}
    judge = load(os.path.join(HERE, 'audit', 'judge.json'), {})
    jitems = judge.get('items', {})
    marks = load(os.path.join(HERE, 'audit', 'marks.json'), {}).get('marks', {})
    credits = {r['file']: r for r in load(os.path.join(HERE, 'credits.json'), [])}
    files = []
    for f in sorted(os.listdir(HERE)):
        stem, ext = os.path.splitext(f)
        if ext.lower() not in ('.mp3', '.ogg', '.m4a', '.wav'): continue
        animal, kind, n = parse(stem)
        if not animal: continue
        r = report.get(f, {}); j = jitems.get(f)
        ai = j['verdict'] if j else {'BAD': 'REPLACE', 'SUSPECT': 'CHECK', 'OK': 'KEEP'}.get(r.get('verdict'), 'CHECK')
        k0 = kind.split('_')[0]
        if stem in byfile: exp = byfile[stem]
        elif animal in expect and k0 in expect[animal]: exp = expect[animal][k0]
        elif kind.startswith('line_'): exp = '대사'
        else: exp = CLASS_KO.get(animal, '')
        c = credits.get(f, {})
        files.append({
            'file': f, 'animal': animal, 'kind': kind, 'n': n,
            'kindKo': KIND_KO.get(k0, k0) + (' · ' + LINE_KO.get(kind[5:], kind[5:]) if kind.startswith('line_') else ''),
            'expect': exp, 'ai': ai, 'conf': (j or {}).get('confidence', ''),
            'reason': (j or {}).get('reason_ko') or '; '.join(r.get('notes', [])) or '분류기 이상 없음',
            'listen': (j or {}).get('listen_ko', ''), 'hint': (j or {}).get('replace_hint', ''),
            'auto': r.get('verdict', ''), 'top': r.get('top', [])[:4], 'dur': r.get('dur'), 'f0': r.get('f0'),
            'src': {'title': c.get('title', ''), 'url': c.get('source_url', ''), 'author': c.get('author', ''), 'license': c.get('license', ''), 'edits': c.get('edits', '')},
        })
    # 후보
    cands = {}
    cj = load(os.path.join(HERE, 'candidates', 'candidates.json'), [])
    cinfo = {(x.get('slot'), x.get('file')): x for x in cj}
    caud = {r['file'].replace(os.sep, '/'): r for r in load(os.path.join(HERE, 'candidates', 'audit.json'), [])}   # audit.py --json 결과
    for d in sorted(glob.glob(os.path.join(HERE, 'candidates', '*'))):
        if not os.path.isdir(d): continue
        slot = os.path.basename(d)
        items = []
        for f in sorted(os.listdir(d), key=lambda s: (len(s), s)):
            if not f.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')): continue
            rel = f'candidates/{slot}/{f}'
            x = cinfo.get((slot, rel)) or cinfo.get((slot, f)) or {}
            au = x.get('audit') or caud.get(rel) or {}
            items.append({'file': rel, 'label': os.path.splitext(f)[0], 'title': x.get('title', ''), 'url': x.get('source_url', ''), 'author': x.get('author', ''),
                          'license': x.get('license', ''), 'edits': x.get('edits', ''), 'note': x.get('note', ''), 'dur': x.get('dur') or au.get('dur'),
                          'auto': au.get('verdict', ''), 'top': au.get('top', [])[:4]})
        if items:
            animal = slot.split('_')[0]
            cur = [f['file'] for f in files if f"{f['animal']}_{f['kind']}" == slot]
            cands[slot] = {'items': items, 'current': cur, 'expect': expect.get(animal, {}).get(slot.split('_', 1)[1], '')}
    # 동물 순서: README 표 순서, 동물군, 괴물
    order = list(names) + ORDER_CLASS + ['dokkaebi', 'jeoseung']
    groups = [a for a in order if any(f['animal'] == a for f in files)] + sorted({f['animal'] for f in files} - set(order))
    gname = {a: names.get(a) or CLASS_KO.get(a) or MONSTER_KO.get(a) or a for a in groups}
    data = {'generated': datetime.date.today().isoformat(), 'base': base, 'groups': [[a, gname[a]] for a in groups], 'files': files,
            'cands': cands, 'seed': marks, 'cross': judge.get('cross_issues', [])}
    tpl = open(os.path.join(HERE, 'review_template.html'), encoding='utf-8').read()
    html = tpl.replace('/*DATA*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
    if not artifact:   # 파일로 여는 판은 완전한 문서로. claude.ai 게시판은 본문만(게시할 때 머리를 붙인다)
        html = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                '</head><body>' + html + '</body></html>')
    out = out or os.path.join(HERE, 'review', 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(html)
    # 할 일: 사람이 틀리다 → 교체. 사람이 안 본 것 중 AI가 교체 추천 → 교체. 사람이 맞다 → 둔다
    todo = {}
    for f in files:
        mk = marks.get(f['file'], {}).get('v')
        if mk == 'ng' or (mk is None and f['ai'] == 'REPLACE'):
            slot = f"{f['animal']}_{f['kind']}"
            t = todo.setdefault(slot, {'slot': slot, 'animal': f['animal'], 'name': gname.get(f['animal'], f['animal']), 'kind': f['kind'], 'expect': f['expect'],
                                       'replace': [], 'keep': [], 'why': [], 'hints': []})
            t['replace'].append(f['file']); t['why'].append(f"{f['file']}: " + (marks.get(f['file'], {}).get('note') or f['reason']) + (' (사람 확인)' if mk == 'ng' else ' (AI 추천)'))
            if f['hint']: t['hints'].append(f['hint'])
    # 이미 뺀 파일(사람이 틀리다 → 앱에서 뺌)도 자리는 채워야 한다
    present = {f['file'] for f in files}
    for fn, mk in marks.items():
        if mk.get('v') != 'ng' or fn in present: continue
        animal, kind, n = parse(os.path.splitext(fn)[0])
        if not animal: continue
        slot = f'{animal}_{kind}'
        k0 = kind.split('_')[0]
        t = todo.setdefault(slot, {'slot': slot, 'animal': animal, 'name': names.get(animal) or CLASS_KO.get(animal) or MONSTER_KO.get(animal) or animal, 'kind': kind,
                                   'expect': expect.get(animal, {}).get(k0, ''), 'replace': [], 'keep': [], 'why': [], 'hints': []})
        t['replace'].append(fn); t['why'].append(f'{fn}: ' + (mk.get('note') or '') + ' (사람 확인, 앱에서 뺐다)')
        h = (jitems.get(fn) or {}).get('replace_hint')
        if h: t['hints'].append(h)
    for t in todo.values():
        t['keep'] = [f['file'] for f in files if f"{f['animal']}_{f['kind']}" == t['slot'] and f['file'] not in t['replace']]
    prio = judge.get('priority', [])
    rows = sorted(todo.values(), key=lambda t: min([prio.index(x) for x in t['replace'] if x in prio] or [999]))
    # 추가: 전용 파일이 없어 동물군 공용 파일(다른 동물 소리)이 나는 슬롯. 타조 평상 = 비둘기, 캥거루 = 말 콧김 식
    cls_of = load(os.path.join(HERE, 'audit', 'classes.json'), {})
    add = []
    for a in names:
        for k in ('roam', 'sprint', 'tired'):
            if any(f['animal'] == a and f['kind'] == k for f in files) or f'{a}_{k}' in todo: continue
            c = cls_of.get(a, '')
            fb = [f['file'] for f in files if f['animal'] == c and f['kind'] == k]
            # 먼저 할 것: 공용 파일이 교체 대상이거나, 공용 파일이 뚜렷이 다른 동물(타조 ← 비둘기·올빼미, 캥거루 ← 말)
            high = any(f['ai'] == 'REPLACE' for f in files if f['file'] in fb) or f'{a}_{k}' in ('ostrich_roam', 'ostrich_tired', 'kangaroo_roam', 'kangaroo_sprint')
            add.append({'slot': f'{a}_{k}', 'animal': a, 'name': names[a], 'kind': k, 'expect': expect.get(a, {}).get(k, ''),
                        'fallback_now': fb or ['합성음'], 'class': c, 'priority': 'high' if high else 'low'})
    add.sort(key=lambda x: x['priority'] != 'high')
    json.dump({'note': 'replace: 틀린 파일 교체(먼저). add: 전용 파일이 없어 다른 동물 소리(공용 파일)나 합성음이 나는 슬롯(여유 있을 때, 공용 파일이 전혀 다른 동물이면 먼저)',
               'replace': rows, 'add': add}, open(os.path.join(HERE, 'audit', 'todo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n = {v: sum(f['ai'] == v for f in files) for v in ('REPLACE', 'CHECK', 'KEEP')}
    print(f"{out}: {len(files)}개 (교체 추천 {n['REPLACE']}, 들어볼 것 {n['CHECK']}, 문제없음 {n['KEEP']}), 후보 슬롯 {len(cands)}, 할 일 슬롯 {len(rows)}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='../', help='페이지에서 web/sounds까지의 경로')
    ap.add_argument('--out')
    ap.add_argument('--artifact', action='store_true', help='claude.ai 게시용(문서 머리 없이 본문만)')
    a = ap.parse_args()
    build(a.base, a.out, a.artifact)
