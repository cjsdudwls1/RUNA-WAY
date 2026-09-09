#!/usr/bin/env python3
"""Render workflow output JSON -> docs/prd/00-questionnaire.md (Korean)."""
import json, sys, re
from collections import OrderedDict

src, dst = sys.argv[1], sys.argv[2]
data = json.load(open(src, encoding='utf-8'))
qs = data['questions']

SECTIONS = OrderedDict([
    ('vision',      ('VIS', '제품 비전 · 타깃 사용자 · 성공 지표')),
    ('scope',       ('SCO', 'MVP 범위 · 일정 · 예산 · 팀 · 프로세스')),
    ('naming',      ('NAM', '네이밍 · 브랜딩 · 세계관')),
    ('gameplay',    ('GAM', '핵심 게임플레이 · 추격 · 난이도 · 타임어택')),
    ('modes',       ('MOD', '게임 모드 · 콘텐츠 · 진행 · 리텐션')),
    ('running',     ('RUN', '러닝 · 피트니스 · 건강 데이터')),
    ('map_geo',     ('GEO', '지도 · 위치 · 경로 · 목적지 생성')),
    ('ar_visual',   ('ART', 'AR 카메라 · 비주얼 · 아트')),
    ('audio',       ('AUD', '오디오 · 음성 생성 AI · 사운드')),
    ('wearables',   ('WEA', '워치 · 스마트 글래스')),
    ('social',      ('SOC', '소셜 · 리더보드 · 경쟁 · 부정행위 방지')),
    ('ux',          ('UX',  'UX · 온보딩 · 러닝 중 조작 · 알림')),
    ('tech',        ('TEC', '기술 스택 · 아키텍처 · 백엔드')),
    ('safety_legal',('LAW', '안전 · 법률 · 개인정보 · 접근성')),
    ('business',    ('BIZ', '비즈니스 · 수익화 · GTM · 마케팅')),
])
PRIO = {'P0': 0, 'P1': 1, 'P2': 2}

def idnum(q):
    m = re.search(r'(\d+)$', q.get('id', ''))
    return int(m.group(1)) if m else 9999

by_sec = {k: [] for k in SECTIONS}
for q in qs:
    by_sec.setdefault(q['section'], []).append(q)
def is_edited(k, q):
    return q.get('id', '').startswith(SECTIONS[k][0] + '-') if k in SECTIONS else False

for k in by_sec:
    if all(is_edited(k, q) for q in by_sec[k]):
        by_sec[k].sort(key=lambda q: (idnum(q), PRIO.get(q['priority'], 3)))
    else:
        by_sec[k].sort(key=lambda q: (PRIO.get(q['priority'], 3), q.get('id', '')))
RAW_SECTIONS = [k for k in by_sec if by_sec[k] and not all(is_edited(k, q) for q in by_sec[k])]

def anchor(q):
    return q['id'].lower()

total = len(qs)
p0 = [q for q in qs if q['priority'] == 'P0']
p1 = [q for q in qs if q['priority'] == 'P1']
p2 = [q for q in qs if q['priority'] == 'P2']

out = []
w = out.append
w('# RunAway(가제) PRD 질문지')
w('')
w('- 목적: PRD 작성 전 제품 오너가 내려야 할 결정 수집')
w('- 원본 아이디어: [00-idea.md](00-idea.md)')
w('- 질문 근거 리서치: [01-research.md](01-research.md)')
w('')
w('## 답변 방법')
w('')
w('- P0부터 답변. P0만 답해도 MVP PRD 초안 작성 가능')
w('- 채팅 답변 형식: `GAM-03: B` 또는 `GEO-01: 네이버 지도, 이유 ...`')
w('- 파일 직접 편집: 각 질문의 `답:` 칸 채우기')
w('- `기본값` 이라고만 답하면 추천 기본값 채택. `P1/P2 전부 기본값` 처럼 묶음 답변 가능')
w('- 질문의 전제가 틀렸으면 그 지적이 가장 중요한 답변')
w('')
w('## 현황')
w('')
w('| 구분 | 개수 |')
w('|---|---|')
w(f'| 전체 | {total} |')
w(f'| P0 (MVP 설계 필수) | {len(p0)} |')
w(f'| P1 (출시 전 필요) | {len(p1)} |')
w(f'| P2 (나중 결정 가능) | {len(p2)} |')
w('')
if RAW_SECTIONS:
    w('- 미편집 섹션(중복 병합·문체 정리 전, 질문 ID가 관점 약어): ' + ', '.join(SECTIONS[k][0] for k in RAW_SECTIONS if k in SECTIONS))
    w('')
w('## 목차')
w('')
for k, (abbr, title) in SECTIONS.items():
    n = len(by_sec.get(k, []))
    n0 = len([q for q in by_sec.get(k, []) if q['priority'] == 'P0'])
    if n:
        w(f'- [{abbr} {title}](#{abbr.lower()}) - {n}개 (P0 {n0})')
w('')
FIRST = ['SCO-01','SCO-02','SCO-03','VIS-01','VIS-03','VIS-04','SCO-06','SCO-07','GAM-01','GAM-03','GAM-05','UX-01','ART-01','SOC-04','TEC-01']
qmap = {q['id']: q for q in qs}
w('## 먼저 답할 15개')
w('')
w('- 이 15개만 답하면 MVP PRD 초안 작성 가능. 나머지는 이후 순차 진행')
w('')
for i in FIRST:
    q = qmap.get(i)
    if q:
        w(f'{FIRST.index(i)+1}. [{i}](#{anchor(q)}) {q["question"]}')
w('')
w('## 나머지 P0 목록')
w('')
for k, (abbr, title) in SECTIONS.items():
    p0s = [q for q in by_sec.get(k, []) if q['priority'] == 'P0' and q['id'] not in FIRST]
    if not p0s:
        continue
    w(f'- {abbr} {title}')
    for q in p0s:
        w(f'  - [{q["id"]}](#{anchor(q)}) {q["question"]}')
w('')
w('---')
w('')
for k, (abbr, title) in SECTIONS.items():
    items = by_sec.get(k, [])
    if not items:
        continue
    w(f'<a id="{abbr.lower()}"></a>')
    w(f'## {abbr} {title}')
    w('')
    for q in items:
        w(f'<a id="{anchor(q)}"></a>')
        w(f'### [{q["priority"]}] {q["id"]}. {q["question"]}')
        w('')
        w(f'- 왜: {q["why"]}')
        if q.get('depends_on'):
            w(f'- 선행: {", ".join(q["depends_on"])}')
        w('- 선택지:')
        for i, o in enumerate(q.get('options', [])):
            letter = chr(ord('A') + i)
            note = o.get('note', '').strip()
            w(f'  - [ ] {letter}. {o["label"]} - {note}' if note else f'  - [ ] {letter}. {o["label"]}')
        w(f'- 추천: {q["recommended"]}')
        w('- 답: ')
        w('')
w('---')
w('')
w('## 검토 메모')
w('')
w('- 검토 관점: 게임 프로듀서, 한국 앱 창업자, 마라톤 뛰는 엔지니어')
for n in data.get('critic_notes', []):
    if n:
        w(f'- {n}')
w('')
open(dst, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(f'wrote {dst}: {total} questions (P0={len(p0)}, P1={len(p1)}, P2={len(p2)})')
