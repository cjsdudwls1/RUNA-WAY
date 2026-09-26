"""음성 팩 대사표. bake.py가 이걸 읽어 조각별 mp3를 굽는다.

- 관제사(op): 문장 조각. 런타임에 이어 붙인다 (내비게이션 방식)
- 동물 목소리는 뺐다. 사람이 의성어를 읽는 것이라 어색했다(사용자 피드백 2026-09-24)
- 숫자는 한글로 적는다. 모델이 숫자를 영어로 읽는 사고를 막는다
- tempo: 굽고 나서 템포만 올린다. 모델 속도를 올리면 발음이 무너진다(1.35에서 확인)
- MOOD: 감정 연기 지시. 감정을 받는 TTS(Qwen3-TTS 등)로 외부에서 구울 때 쓴다. Supertonic은 무시한다
"""

# 관제사 음색. Supertonic 3 화자 번호(0~4 여성, 5~9 남성). 9번이 한국어 ASR 역검증에서 가장 정확했다
OP_SID = 9
OP_SPEED = 1.15

SINO = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구']


def sino(n):
    """1~99 한자어 수사"""
    t, o = divmod(n, 10)
    s = ('' if t == 0 else ('' if t == 1 else SINO[t]) + '십') + SINO[o]
    return s


DIRS = {  # 키 → 말. 러너가 즉시 알아듣는 여덟 방위
    'front': '정면', 'back': '바로 뒤', 'lf': '왼쪽 앞', 'rf': '오른쪽 앞',
    'l': '왼쪽', 'r': '오른쪽', 'lb': '왼쪽 뒤', 'rb': '오른쪽 뒤',
}

# (키, 문장, 템포). 템포 1.1 이상은 다급한 말
OP = [
    ('intro_head', '여기는 러너웨이 관제.', 1.0),
    ('intro_hide', '근처 풀숲에 숨어 있다.', 1.0),
    ('intro_top', '최고 시속', 1.0),
    ('intro_max', '최고 속도는', 1.0),
    ('intro_kmh', '킬로.', 1.0),
    ('intro_tail', '아직 널 못 봤다. 조용히 페이스를 올려라.', 1.0),
    ('intro_now', '바로 뒤에 있다. 이미 널 봤다. 뛰어!', 1.12),
    ('warn60', '일 분 뒤, 녀석들이 널 본다.', 1.05),
    ('warn15', '곧이다. 페이스 올려!', 1.12),
    ('spotted', '녀석들이 널 봤다. 뛰어!', 1.15),   # '들켰다! 뛰어!'는 모델이 뒤 절반을 뭉갠다(ASR 역검증 4/4 실패)
    ('sisok', '시속', 1.08),
    ('hold', '버텨!', 1.12),
    ('again', '또 온다!', 1.12),
    ('stick', '붙는다!', 1.12),
    ('meter', '미터.', 1.08),
    ('hit1', '잡혔다! 첫 번째. 무리가 물러난다.', 1.12),
    ('hit2', '잡혔다! 두 번째. 한 번 더 잡히면 끝이다!', 1.12),
    ('hit3', '세 번째다. 끝났다.', 1.05),
    ('tired1', '지쳤다. 헐떡인다. 지금이 기회다, 밟아!', 1.1),
    ('tired2', '지쳤다. 벌려!', 1.12),
    ('tired3', '헐떡인다. 지금이다!', 1.12),
    ('tired4', '지쳤다.', 1.08),
    ('tired5', '기회다.', 1.08),
    ('recover1', '숨 고르는 중. 다시 올 거다.', 1.0),
    ('recover2', '멀어진다. 아직 끝난 게 아니다.', 1.0),
    ('lost', 'GPS가 흔들린다. 녀석들이 냄새를 잃었다.', 1.0),
    ('half1', '절반이다. 뛰어!', 1.15),
    ('half2', '잡힌다! 밟아!', 1.15),
    ('cool', '쿨다운 구간. 녀석들은 포기했다. 천천히.', 1.0),
    ('end_fail', '잡혔다. 탈출 실패.', 1.0),
    ('end_arrive', '도착! 탈출 성공.', 1.05),
    ('end_hits0', '한 번도 안 잡혔다.', 1.0),
    ('end_hits1', '한 번 잡혔다.', 1.0),
    ('end_hits2', '두 번 잡혔다.', 1.0),
    ('end_final', '최종 기록', 1.0),
    ('unit_min', '분', 1.0),
    ('unit_sec', '초.', 1.0),
    ('end_stop', '세션 종료.', 1.0),
    ('wait', '위치 잡는 중이다. 하늘이 보이는 곳에서 잠깐 기다려라.', 1.0),
    ('wait_coarse', '위치 정확도가 너무 낮다. 크롬 위치 권한에서 정확한 위치를 켜라.', 1.0),
    ('pocket', '주머니 모드. 이제 소리만 듣고 달려라.', 1.0),
    ('test_tail', '지금 소리가 왼쪽에서 오른쪽으로 지나갔으면 정상이다.', 1.0),
    ('zero', '영', 1.0),
]
for n, w in [(1, '한'), (2, '두'), (3, '세'), (4, '네'), (5, '다섯')]:
    OP.append((f'cnt{n}', f'{w} 마리가', 1.0))
for k, w in DIRS.items():
    OP.append((f'dc_{k}', f'{w}에서 온다!', 1.12))   # 첫 돌진
    # 짧게. '{w}!'만 두면 끝 음절이 잘린다 → '이다/다'를 붙여 문장으로 끝낸다
    OP.append((f'dx_{k}', f'{w}{"이다" if (ord(w[-1]) - 0xAC00) % 28 else "다"}!', 1.1))
    OP.append((f'dr_{k}', f'한 마리가 돌아왔다. {w}.', 1.05))
for n in range(1, 100):
    OP.append((f'n{n}', sino(n), 1.08))
# 숫자는 구절째로 굽는다. 조각을 이으면 ASR이 "시속 육십"을 "시속 6시"로 듣는 식으로 60~70%만 맞았다
def sino3(n):
    return ('백' + sino(n - 100)) if n >= 100 else sino(n)
for n in range(1, 121):
    OP.append((f'kmh{n}', f'시속 {sino3(n)} 킬로!', 1.08))
for n in list(range(1, 50)) + list(range(50, 301, 10)):
    OP.append((f'm{n}', f'{sino3(n) if n < 100 else ("" if n < 200 else sino(n // 100)) + "백" + sino(n % 100)} 미터.', 1.08))
for h in range(1, 10):
    OP.append((f'n{h * 100}', ('' if h == 1 else SINO[h]) + '백', 1.08))

# 동물 이름 (관제사 목소리). 소개와 소리 테스트에 쓴다
NAMES = {
    'sloth': '세발가락나무늘보', 'loris': '늘보로리스', 'gila': '힐라몬스터', 'chicken': '닭', 'chihuahua': '치와와',
    'crocodile': '나일악어', 'komodo': '코모도왕도마뱀', 'squirrel': '다람쥐', 'koala': '코알라', 'cat': '집고양이',
    'pig': '돼지', 'armadillo': '아홉띠아르마딜로', 'hippo': '하마', 'elephant': '코끼리', 'greyhound': '그레이하운드',
    'kangaroo': '붉은캥거루', 'cheetah': '치타', 'hare': '유럽산토끼', 'wolf': '회색늑대', 'jindo': '진돗개',
    'horse': '지구력경주마', 'camel': '단봉낙타', 'sleddog': '알래스칸허스키', 'ostrich': '타조', 'pronghorn': '프롱혼',
    'dokkaebi': '도깨비', 'jeoseung': '저승사자',
}
for k, w in NAMES.items():
    OP.append((f'name_{k}', w, 1.0))

# 잡힘 알림. 관제 음성을 꺼도 나온다(잡힌 걸 모르면 안 된다). 작은 별도 팩(hit.bin)이라 항상 받는다
HIT = [
    ('caught1', '한 번 잡혔다!', 1.1),
    ('caught2', '두 번 잡혔다!', 1.1),
    ('caught3', '세 번 잡혔다. 끝났다.', 1.05),
]

# 감정. 키 → 연기 지시. 외부 TTS(Qwen3-TTS)의 instruct로 넘긴다. ko는 사람용 설명
# 조각은 런타임에 이어 붙는다. 한 문장 안에서 감정이 튀지 않게 이웃 조각끼리 같은 계열로 묶었다
#   돌진: dc_(urgent) + kmh(tense) + hold(urgent) / 소개: intro_head + name + cnt + intro_hide + intro_max + kmh + intro_tail
#   끝: end_arrive + end_hits + end_final + n + unit_min + n + unit_sec
MOOD = {
    'calm': {'ko': '차분하고 낮게. 상황 브리핑. 밑에 긴장이 깔려 있다',
             'en': 'Calm, low and steady field briefing over a radio. Controlled, confident, a hint of tension underneath. Natural Korean intonation, not an announcer.'},
    'tense': {'ko': '긴장. 짧게 끊어 또렷하게. 소리를 낮춘 경고',
              'en': 'Tense and clipped. Quick, firm, clearly articulated warning. Focused, slightly hushed, urgency held back.'},
    'urgent': {'ko': '다급한 외침. 빠르고 높게. 당장 뛰라고 소리친다',
               'en': 'Urgent shout. Fast, loud, pitch rising, breathless alarm, yelling at someone to run right now. Real panic in the voice, but every word clear.'},
    'eager': {'ko': '흥분. 기회를 잡았다. 몰아붙인다',
              'en': 'Excited and eager, seizing a chance. Fast, energetic, pushing hard: now is the moment, go go go.'},
    'triumph': {'ko': '안도와 환호. 밝게',
                'en': 'Relieved and triumphant. Bright, warm, cheering, breathing out after a close call.'},
    'grim': {'ko': '무겁고 낙담. 끝이 내려간다',
             'en': 'Heavy and grim. Disappointed, slower, pitch falling at the end. It is over.'},
}
_MOOD_KEY = [   # 앞에서부터 처음 맞는 규칙
    ('grim', r'^(end_fail|hit3|caught3)$'),
    ('triumph', r'^end_arrive$'),
    ('eager', r'^tired\d$'),
    ('urgent', r'^(intro_now|spotted|again|stick|hold|half\d|hit\d|caught\d|dc_|dx_)'),
    ('tense', r'^(warn|dr_|kmh|m\d|meter$|sisok$)'),
]


def mood_of(key):
    import re
    for m, pat in _MOOD_KEY:
        if re.match(pat, key): return m
    return 'calm'
