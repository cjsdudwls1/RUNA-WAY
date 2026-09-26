# 관제 음성 다시 굽기 (Qwen3-TTS)

- 2026-09-26 사용자 판정: 지금 관제 음성(Supertonic 3)은 말투가 어색하다. 감정 섞인 높낮이가 없다
- 목표: 감정 연기가 되는 TTS로 관제 조각 405개(OP 402 + HIT 3)를 다시 굽는다. 앱 코드는 안 바뀐다
- GPU가 필요하다. 사용자 로컬에서 굽고, 여기(web/voice/bake.py)는 받아서 후처리·선택·팩만 한다

## 반드시 지킬 것

- 한 목소리. 조각을 런타임에 이어 붙인다("왼쪽 뒤에서 온다!" + "시속 삼십오 킬로!" + "버텨!"). 조각마다 목소리가 다르면 두세 사람이 번갈아 말하는 꼴이 된다
  - 그래서 VoiceDesign으로 문장마다 새로 만들면 안 된다. 같은 묘사여도 매번 다른 사람이 나온다
- 문장은 lines.py 그대로. 키도 그대로. 숫자는 이미 한글이다
  - 읽기만 바꿔야 하면(예: GPS → 지피에스) 생성 스크립트에서 치환한다
  - 문장 자체를 고치면 lines.py를 고친다. 브라우저 TTS 대체 문장과 화면 기록도 같이 바뀐다
- 감정은 lines.py의 `MOOD`, `mood_of(key)`. 여섯 가지: calm, tense, urgent, eager, triumph, grim
  - 이웃 조각끼리 같은 계열로 묶어 뒀다. 한 문장 안에서 감정이 튀지 않게

## 방식 (오디션으로 고른다)

| 방식 | 모델 | 목소리 고정 | 감정 | 비고 |
|---|---|---|---|---|
| A | Qwen3-TTS-12Hz-1.7B-CustomVoice | 내장 화자 고정 | instruct로 조각마다 | 가장 확실. 한국어 원어민 화자는 여성(Sohee). 모델 카드에서 화자 목록 확인 |
| B | VoiceDesign으로 관제사 목소리 1개 → Base로 복제 | 참조 음성 고정 | 감정별 참조 음성 | 남성 관제사를 원할 때. 감정별 참조가 같은 사람인지 화자 임베딩으로 확인 |
| C | CustomVoice 남성 화자 + 한국어 | 고정 | instruct | 외국인 억양 위험. ASR 점수로 거른다 |

- B의 감정별 참조: VoiceDesign에 같은 묘사 + 감정만 바꿔 여러 번 뽑고, 중립 참조와 화자 유사도가 가장 높은 것을 감정마다 하나 고른다
- 관제사 묘사(초안): 30대 한국인 남성 무전 관제사. 중저음, 또렷한 발음. 방송 아나운서가 아니라 위험을 보며 무전기에 대고 말하는 사람
- 어느 방식이든 문장마다 후보 3개(시드만 바꿔서)

## 오디션 (전체 굽기 전에 사용자가 귀로 고른다)

- 방식마다 아래를 굽는다. web/voice/audition/<방식>/
- 이어 붙이기 미리듣기는 앱과 같은 규칙: 조각 사이 0.035초, 조각이 . ! ?로 끝나면 0.1초

| 이름 | 조각 |
|---|---|
| 소개 | intro_head + name_cheetah + cnt1 + intro_hide + intro_max + kmh100 + intro_tail |
| 발견 | spotted |
| 첫 돌진 | dc_rb + kmh35 + hold |
| 두 번째 돌진 | again + dx_l + kmh28 |
| 복귀 | dr_lb + m120 |
| 지침 | tired1 |
| 잡힘 | caught1, hit2 |
| 절반 | half1 |
| 쿨다운 | cool |
| 성공 | end_arrive + end_hits0 + end_final + n12 + unit_min + n30 + unit_sec |
| 실패 | end_fail |

## 파일 규격

- `web/voice/src/<키>__<번호>.wav` (후보 하나면 `<키>.wav`)
- wav, 모노, 24kHz 이상. 앞뒤 무음, 음량은 신경 쓰지 않는다. bake.py가 자르고 맞춘다
- src/, audition/, preview/는 커밋하지 않는다(.gitignore)

## 팩 만들기

```
pip install sherpa-onnx soundfile scipy imageio-ffmpeg
# 한국어 ASR 모델만 받는다(Supertonic 모델은 필요 없다). 받는 주소는 bake.py 맨 위 준비 절
#   web/voice/models/sherpa-onnx-zipformer-korean-2024-06-24/
VOICE_SRC=web/voice/src VOICE_ENGINE="Qwen3-TTS (Qwen, Apache-2.0)" python3 web/voice/bake.py
```

- 키가 하나라도 없으면 멈춘다. 팩은 안 바뀐다
- ASR 모델이 없으면 멈춘다. 검사 없이 첫 후보로 만들려면 VOICE_NO_ASR=1 (권하지 않는다)
- 빈 파일, 0.1초 미만, 무음, 못 읽는 wav는 그 후보만 버린다. 한 키의 후보가 전부 망가졌으면 키 이름과 이유를 대고 멈춘다
- 후보 선택: 최종 mp3를 ASR로 되읽은 점수. 숫자 구절은 숫자가 들리는지가 먼저
- 길이 검사: 글자당 0.35초 + 1.2초를 넘으면 벌점(말 되풀이, 끝 웅얼거림)
- 템포: 기본은 안 입힌다. 감정 연기가 속도를 낸다. 입히려면 VOICE_SRC_TEMPO=1
- 결과
  - web/static/voice/op.bin, hit.bin
  - web/voice_manifest.js (engine 필드 → 앱 설정 화면 출처 표기가 자동으로 바뀐다)
  - web/voice/qa.tsv (감정, CER, 길이, ASR이 들은 말, 고른 후보)

## 확인

- qa.tsv에서 CER 0.3 넘는 조각은 사람이 듣는다. 틀렸으면 그 키의 후보만 지우고 다시 뽑는다
  - 한 음절 숫자(n1~n9, "일", "이")와 외침은 ASR이 원래 못 읽는다. 사람 귀로
- 오디션 표의 이어 붙이기를 최종 팩으로 다시 만들어 듣는다(web/voice/preview/)
- 확인 항목: 한 사람 목소리인가, 조각 경계에서 높낮이가 튀지 않는가, 다급한 말이 다급한가, 숫자가 또렷한가

## 커밋

- 올린다: web/static/voice/*.bin, web/voice_manifest.js, web/voice/qa.tsv, 생성 스크립트(web/voice/qwen_gen.py), lines.py를 고쳤으면 lines.py
- 안 올린다: src/, audition/, preview/, .cache/, models/
- 라이선스: Qwen3-TTS 모델과 코드 Apache-2.0. 상업 이용 가능. 배포하는 건 합성된 음성 파일
