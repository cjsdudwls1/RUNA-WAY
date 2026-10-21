"""사람 추격자 소리 후보 (2026-10-21). 동물·괴물 후보를 지우고 사람 소리만 남긴다
- 받기: OpenGameArt.org CC0 녹음(웃음, 숨). freesound는 이 환경에서 막혀 있다
- 웃음(laugh): 남자 웃음 3개 + 조금 낮춘 변형(0.86배속, 약 2.6반음 내림. 목소리가 높은 것만)
- 숨(breath): 지친 숨 1개 추가
- 지우기: 동물·괴물·여자·아이 후보. 휘파람(whistle)과 붙잡힘(pounce)은 합성음
실행: python3 web/sounds/human.py
"""
import json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from collect import SR, decode, encode, get, one

OGA = 'https://opengameart.org/sites/default/files/'
CC0 = {'license': 'CC0 1.0', 'license_url': 'https://creativecommons.org/publicdomain/zero/1.0/'}
# (소리, 후보, 파일, 제목, 작가, 페이지, 최대 길이초, 낮춘 변형도)
GET = [
    ('laugh', 'oga-qubodup', 'qubodupevillaughter.flac', 'Evil Laughter', 'qubodup', 'evil-laughter', 3.2, False),
    ('laugh', 'oga-antum1', 'laugh-evil-1_0.ogg', 'Evil Laugh', 'Antum Deluge', 'evil-laugh', 2.6, True),
    ('laugh', 'oga-antum2', 'evil_laugh_02.flac', 'Evil Laugh 2', 'Antum Deluge', 'evil-laugh-2', 2.0, True),
    ('breath', 'oga-tired', 'breathing%20tired.wav', 'Breathing tired', 'mikeask', 'breathing-tired', 2.6, False),
]
# 사람 추격자에 안 맞는 후보. 이름 앞부분으로 지운다
DROP = {
    'step': ['dokkaebi', 'fs240732', 'fs352870'],   # 도깨비, 행진(잔향이 길다), 낙엽
    'breath': ['dokkaebi', 'jeoseung', 'mon-', 'old-', 'fs119515', 'fs121584', 'fs181767', 'fs276577', 'fs511319', 'fs567723'],
    'growl': [''], 'pounce': [''],                  # 짐승 울음과 포효. 사람은 휘파람, 웃음, 붙잡힘
    'scream': ['mon-', 'fs333832'],                 # 괴물화 비명, 악마 비명
    'gotcha': ['dokkaebi', 's2-', 's4-', 's6-l2-child', 's6-l4-child', 's9-l1-child', 's9-l3-child', 's6-l2-reverse', 's6-l4-reverse', 's9-l1-reverse', 's9-l3-reverse'],
}


def slow(x, k):
    """k배속으로 늘인다(높이도 같이 내려간다)"""
    n = int(len(x) / k); return np.interp(np.arange(n) * k, np.arange(len(x)), x).astype(np.float32)


def main():
    cpath = os.path.join(HERE, 'credits.json')
    credits = {c['file']: c for c in json.load(open(cpath))}
    for sid, pre in DROP.items():
        d = os.path.join(HERE, sid)
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if any(f.startswith(p) for p in pre):
                os.remove(os.path.join(d, f)); credits.pop(f'{sid}/{f}', None); print('지움', sid, f)
    for sid, cand, f, title, author, page, maxlen, low in GET:
        x = decode(get(OGA + f, True))
        meta = {'title': title, 'author': author, 'source_url': 'https://opengameart.org/content/' + page, **CC0}
        rel = f'{sid}/{cand}.mp3'
        encode(one(x, maxlen), os.path.join(HERE, rel)); credits[rel] = {'file': rel, **meta, 'edits': f'OpenGameArt 원본, 모노, 앞 무음 자름, 최대 {maxlen}초, 페이드, 피크 -1dBFS'}
        if low:
            rel = f'{sid}/{cand}-low.mp3'
            encode(one(slow(x, 0.86), maxlen), os.path.join(HERE, rel)); credits[rel] = {'file': rel, **meta, 'title': '낮춤 ' + title, 'edits': '0.86배속(약 2.6반음 내림), 모노, 앞 무음 자름, 페이드, 피크 -1dBFS'}
        print('받음', sid, cand)
    json.dump(sorted(credits.values(), key=lambda c: c['file']), open(cpath, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
