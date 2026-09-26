# 동물 소리 녹음 규격

- 목적: 합성음 대신 실제 동물 녹음을 쓴다
- 방향(좌우, 앞뒤)과 거리(크기, 먹먹함, 잔향)는 앱이 입힌다. 녹음은 "가까이서 녹음한 마른 소리" 하나면 된다
- 파일이 없는 동물은 합성음으로 대체된다. 일부만 넣어도 된다
- 앱은 고른 동물의 파일만 받는다. 25종을 다 넣어도 첫 로딩은 늘지 않는다

## 파일 이름

- `web/sounds/<동물id>_<상태>_<번호>.mp3`
- 상태
  - roam: 평상시, 배회. 멀리서 존재를 알리는 소리
  - sprint: 돌진. 달려드는 순간의 공격적인 소리
  - tired: 지침. 헐떡임, 거친 숨
- 번호: 1, 2, 3. 같은 상태에 2~3개를 넣으면 번갈아 쓴다. 같은 소리 반복이 가장 먼저 질린다
- 동물군 공용: `<동물군>_<상태>_<번호>.mp3`. 동물별 파일이 없으면 이것으로 대체한다
  - 동물군: bird, canine, feline, reptile, hoof, small
- 이름 규칙이 틀리면 빌드가 "건너뜀"으로 알려준다

## 동물과 소리

순서가 우선순위다. 코끼리부터.

| 순서 | id | 이름 | 동물군 | roam | sprint | tired |
|---|---|---|---|---|---|---|
| 1 | elephant | 코끼리 | hoof | 낮은 럼블, 코 킁 | 나팔 소리(트럼펫) | 코로 내쉬는 거친 숨 |
| 2 | chicken | 닭 | bird | 꼬꼬 평상 울음 | 놀란 꽥꽥, 날갯짓 | 짧고 빠른 꾸꾸 |
| 3 | sloth | 세발가락나무늘보 | small | 나뭇가지 바스락 | 높은 휘파람 울음 | 느린 숨 |
| 4 | loris | 늘보로리스 | small | 짧은 찍 소리 | 쉭 경고음 | 작은 숨 |
| 5 | gila | 힐라몬스터 | reptile | 약한 쉭 | 강한 쉭 | 느린 쉭 |
| 6 | chihuahua | 치와와 | canine | 낮은 으르렁 | 날카로운 짖음 | 헐떡임 |
| 7 | crocodile | 나일악어 | reptile | 낮은 울음(벨로우) | 쉭, 턱 닫는 소리 | 거친 숨 |
| 8 | komodo | 코모도왕도마뱀 | reptile | 쉭 | 강한 쉭, 발톱 긁음 | 느린 숨 |
| 9 | squirrel | 다람쥐 | small | 짹짹 수다 | 빠른 경고 찍찍 | 짧은 헐떡임 |
| 10 | koala | 코알라 | small | 낮은 벨로우 | 크고 거친 벨로우 | 거친 숨 |
| 11 | cat | 집고양이 | feline | 야옹 | 하악, 싸움 울음 | 헐떡임 |
| 12 | pig | 돼지 | hoof | 꿀꿀 | 꽥 비명 | 거친 꿀꿀 |
| 13 | armadillo | 아홉띠아르마딜로 | small | 킁킁, 땅 파기 | 빠른 발소리 | 숨 |
| 14 | hippo | 하마 | hoof | 낮은 그르렁 | 크게 우는 포효 | 물 뿜는 숨 |
| 15 | greyhound | 그레이하운드 | canine | 낮은 으르렁 | 짖음 | 헐떡임 |
| 16 | kangaroo | 붉은캥거루 | hoof | 끙끙, 기침 같은 소리 | 쿵쿵 뛰는 발소리 | 거친 숨 |
| 17 | cheetah | 치타 | feline | 새 같은 짹 울음 | 쉭, 으르렁 | 심한 헐떡임 |
| 18 | hare | 유럽산토끼 | small | 풀 바스락, 발 구름 | 빠른 발소리 | 짧은 숨 |
| 19 | wolf | 회색늑대 | canine | 하울링 또는 으르렁 | 으르렁, 짖음 | 헐떡임 |
| 20 | jindo | 진돗개 | canine | 낮은 으르렁 | 짖음 | 헐떡임 |
| 21 | horse | 지구력경주마 | hoof | 콧김, 푸르르 | 히이잉, 질주 발굽 | 거친 콧김 |
| 22 | camel | 단봉낙타 | hoof | 그르렁 신음 | 크게 울부짖음 | 거친 숨 |
| 23 | sleddog | 알래스칸허스키 | canine | 웅얼거림, 하울링 | 짖음 | 헐떡임 |
| 24 | ostrich | 타조 | bird | 낮은 붐 울음 | 쉭, 쿵쿵 발소리 | 숨 |
| 25 | pronghorn | 프롱혼 | hoof | 콧김 | 경고 콧김, 질주 발굽 | 거친 숨 |
| - | bird, canine, feline, reptile, hoof, small | 동물군 공용 | - | 그 무리의 대표 소리 | | |

- 토끼 비명, 동물 학대로 들리는 소리는 쓰지 않는다
- 소리가 거의 없는 동물(나무늘보, 로리스, 아르마딜로, 토끼)은 움직이는 소리(바스락, 발소리)로 대신한다
- 좋은 녹음이 없으면 억지로 채우지 않는다. 비워 두면 동물군 파일이나 합성음이 나온다

## 음향 규격

| 항목 | 값 |
|---|---|
| 형식 | mp3, 모노, 44.1kHz, 96kbps |
| 길이 roam | 0.4~2.0초 |
| 길이 sprint | 0.3~1.2초. 가까우면 초당 3번까지 울린다. 길면 겹쳐서 뭉개진다 |
| 길이 tired | 0.8~2.5초 |
| 길이 step | 0.2~0.5초. 괴물 발소리 한 걸음. 앱이 괴물 속도에 맞춰 이어 튼다(아래 괴물 절) |
| 시작 | 첫 소리 전 무음 20ms 이하. 앱이 울리는 순간이 곧 거리 신호다 |
| 끝 | 30ms 페이드아웃 |
| 음량 | 피크 -1 dBFS. 평균(RMS)은 -20~-14 dBFS 안. 동물끼리 크기가 들쭉날쭉하면 거리 신호가 틀어진다 |
| 공간감 | 마른 소리. 가까이서 녹음해 잔향과 메아리가 적은 것. 거리감은 앱이 입힌다 |
| 잡음 | 사람 목소리, 음악, 다른 동물, 바람, 차 소리, 녹음기 잡음이 없어야 한다. 잡음 제거는 가볍게(소리가 뭉개지면 안 된다) |
| 크기 | 파일 하나 60KB 이하 권장, 동물 하나 300KB 이하 |

ffmpeg 예시. 짧은 소리(3초 미만)는 loudnorm(LUFS)이 부정확하다. 피크로 맞춘다

```
# 1) 자르기, 모노, 앞 무음 제거, 끝 페이드
ffmpeg -ss 1.20 -t 0.90 -i 원본.wav -af "silenceremove=start_periods=1:start_threshold=-45dB,afade=t=out:st=0.85:d=0.03" -ac 1 -ar 44100 tmp.wav
# 2) 피크 확인: 출력의 max_volume (예: -7.3 dB)
ffmpeg -i tmp.wav -af volumedetect -f null - 2>&1 | grep -E "max_volume|mean_volume"
# 3) 피크를 -1 dB로 (위 예시면 +6.3dB). mean_volume이 -20~-14 dB 안인지 본다
ffmpeg -i tmp.wav -af "volume=6.3dB" -b:a 96k web/sounds/elephant_sprint_1.mp3
```

## 라이선스

- 앱은 무료지만 나중에 광고나 유료화가 붙을 수 있다. 상업 이용 가능한 것만 쓴다
- 허용: CC0, 퍼블릭 도메인, Pixabay 콘텐츠 라이선스, CC-BY(출처 표시)
- 조건부: CC-BY-SA. 다른 선택지가 없을 때만. credits.json에 표시
- 금지: NC(비영리), ND(변경 금지), "개인용만", 출처 불명, 유튜브·게임·영화에서 추출, 라이선스 표기가 없는 사이트
- freesound는 파일마다 라이선스가 다르다. 하나씩 확인한다
- xeno-canto(새 소리)는 대부분 NC라 금지

## 출처 기록 (필수)

- `web/sounds/credits.json`. 파일마다 한 줄. 기록이 없는 파일은 넣지 않는다

```json
[
  {
    "file": "elephant_sprint_1.mp3",
    "animal": "elephant",
    "kind": "sprint",
    "title": "원본 제목",
    "source_url": "https://...",
    "author": "올린 사람",
    "license": "CC0 1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    "original_file": "원본 파일 이름",
    "edits": "1.20~2.10초 자름, 모노, 음량 정규화"
  }
]
```

- 빌드가 이 파일로 출처 페이지(credits.html)를 만들고, 앱 설정에 "동물 소리 출처" 링크를 붙인다. CC-BY의 출처 표시 의무가 이것으로 채워진다

## 찾을 곳 (예)

- freesound.org: 라이선스 필터에서 Creative Commons 0 또는 Attribution
- Wikimedia Commons 오디오: 파일마다 라이선스 확인
- Pixabay 효과음
- BigSoundBank
- OpenGameArt: CC0, CC-BY만

## 확인

- `python3 web/build.py` → 출력의 "sounds: N files [키 목록]"에 넣은 것이 전부 나오는가. "건너뜀"이 없는가
- `ffprobe` 로 파일마다 모노, 길이 범위 확인
- 들어보기: `python3 -m http.server -d docs/app 8000` → 브라우저에서 설정 > 동물 고르기 > 소리 테스트
  - 왼쪽 뒤에서 오른쪽 뒤로 한 바퀴, 그다음 바로 뒤에서 멀리서 가까이 다가온다
- 커밋은 `web/sounds/` 안의 파일만. 빌드 결과(docs/app, web/dist)는 커밋하지 않는다

## 검사와 교체 (2026-09-26 추가)

- 계기: 사용자가 들어 보니 엉뚱한 소리가 섞여 있었다. 코끼리 돌진에서 개 소리, 그레이하운드 돌진이 치와와 깽깽, 돼지 돌진이 닭 소리
- 원인: 원본에서 구간을 자를 때 아무도 듣지 않았다. 0.3~0.5초 조각은 사람도 무슨 동물인지 못 가린다
- 이제부터 모든 소리는 두 관문을 지난다. 분류기(audit.py) → 사람 귀(검수 페이지)

### 도구

| 파일 | 하는 일 |
|---|---|
| audit.py | AudioSet 분류기 2개(527종)로 "파일 이름의 동물 소리가 맞나"를 본다. BAD / SUSPECT / OK |
| audit/report.json | 전체 검사 결과 |
| audit/judge.json | AI 판정(교체 추천 / 들어볼 것 / 문제없음)과 이유, 교체 힌트 |
| audit/marks.json | 사람 검수 결과(맞다 / 틀리다, 메모) |
| audit/todo.json | replace: 교체할 슬롯(사람이 틀리다 + 사람이 안 본 것 중 AI 교체 추천). add: 전용 파일이 없어 공용 파일(다른 동물)이 나는 슬롯, priority high부터 |
| audit/classes.json | 동물 → 동물군(app.html CLASS와 같다) |
| audit/tried.json | 지난 회차 후보 기록(고른 것, 안 고른 것, 사람 메모) |
| review.py | 검수 페이지 review/index.html을 만든다. 더블클릭으로 연다 |
| candidates/ | 교체 후보. 앱에 안 들어간다(빌드는 web/sounds 맨 위 파일만 읽는다) |

### 후보 규격

- 폴더: `candidates/<슬롯>/<번호>.mp3`. 슬롯은 `<동물>_<상태>` (예: `pig_sprint`)
- 슬롯마다 후보 3~5개. 서로 다른 원본 녹음에서 2개 이상
- todo.json의 avoid_sources(지난 회차에 사람이 안 고른 것)와 human_notes(사람 메모)를 먼저 읽는다
- 음향 규격(위 표) 그대로. 단 sprint는 0.5초 이상(0.3초 조각은 못 알아듣는다)
- 기록: `candidates/candidates.json`에 후보마다 credits.json과 같은 칸 + `slot`, `file`(candidates/...), `note`(왜 골랐나 한 줄), `dur`
- 분류기 관문: `python3 web/sounds/audit.py web/sounds/candidates --json web/sounds/candidates/audit.json`
  - BAD는 후보에 올리지 않는다
  - SUSPECT는 note에 이유를 적을 때만(예: AudioSet에 코끼리가 없어 기대 소리가 약하게 나온다)
  - 큰 개 돌진(그레이하운드, 진돗개, 늑대, 허스키, 개 무리 공용 canine): 1.5kHz 위/아래 에너지 비 0.10 이하가 조건. 0.10~0.18은 SUSPECT, 0.18 넘으면 BAD. Yip이 Bark·Bow-wow보다 크면 SUSPECT. 이 두 가지는 note로 봐주지 않는다(큰 개는 0.00~0.07, 치와와·뺀 그레이하운드 0.19~0.33)
  - 다른 종 라벨(까마귀, 비둘기, 닭, 소, 개구리 등)이 기대 소리보다 크면 BAD
  - 약한 슬롯(AudioSet에 그 동물이 없는 것): 동물 기미가 전혀 없고 맨 위가 차·바람·효과음이면 SUSPECT
  - 음악 라벨은 SUSPECT까지만(하울링, 트럼펫, 괴물 목소리가 음악으로 잘 잡힌다)
  - 원본을 이미 다른 동물이 쓰면 BAD. credits.json과 candidates.json을 함께 본다(다른 슬롯 후보끼리도). freesound 주소는 번호로 맞춘다. 생성 모델 출력(라이선스 "생성: …")은 빼고 본다
  - candidates.json에 줄이 없는 후보는 BAD(출처 모름)
  - 판정은 파일 내용 해시(h)에 묶인다. 후보 파일을 고치면 audit.py를 다시 돌린다
- 이미 다른 동물에 쓴 원본은 쓰지 않는다. 같은 녹음이 두 동물 소리가 되면 안 된다
- 후보를 넣었으면 `python3 web/sounds/review.py` → review/index.html 맨 위 "후보 고르기"에 나온다

### 사람 검수

- `web/sounds/review/index.html` 더블클릭. 인터넷이 없어도 된다
- 파일마다 재생 → 맞다 / 틀리다(+메모). 후보는 "쓴다"를 1~3개, 없으면 "다 별로"
- 키보드: Space 재생, 1 맞다, 2 틀리다, J/K 다음·이전
- 끝나면 "결과 복사" → AI에게 붙여 넣는다

### 마무리 (AI가 한다)

사람이 "결과 복사"를 붙여 넣으면 한다. 결과 끝의 `<json>` 블록이 기준이다(round가 audit/todo.json의 round와 다르면 옛 페이지 결과다. 사람에게 알린다).

1. 교체 대상을 정한다
   - 사람이 틀리다(이번 결과 + audit/marks.json에서 gone이 아닌 것) + 사람이 안 들은 AI 교체 추천(결과의 "안 들어 본 교체 추천")
   - 사람이 맞다고 한 파일은 AI가 뭐라 해도 둔다. "메모만"은 판정이 아니다. 참고만
2. 슬롯마다 채운다
   - 고른 후보를 교체 대상 자리에 넣는다. 사람 틀리다 자리부터, 그다음 AI 교체 추천 자리, 그다음 빈 번호
   - 이름은 `<슬롯>_<번호>.mp3`. 번호는 1부터 빈 것. 남기는 파일 + 새 파일이 3개를 넘지 않는다(페이지가 "최대 n개"로 막는다)
   - 후보를 못 고른 교체 대상("다 별로", "안 고름", 후보 슬롯 없음)은 web/sounds에서 뺀다. 동물군 파일이나 합성음이 대신 난다
3. credits.json
   - 뺀 파일의 줄은 지운다
   - 새 파일의 줄 = candidates.json의 그 후보 줄에서 `file`을 최종 이름으로 바꾸고 `slot`, `note`, `dur`, `audit`를 뺀 것. `animal`, `kind`는 슬롯대로
   - 빌드가 검사한다: web/sounds의 소리 파일에 credits.json 줄이 없으면 빌드가 멈춘다
4. audit/marks.json
   - 교체하거나 뺀 파일의 옛 줄은 지운다(같은 이름의 새 파일에 옛 판정이 붙지 않게. 내용 해시로도 막지만 파일을 정리해 둔다)
   - 뺀 파일은 `{"v": "removed", "note": "이유"}`로 적는다. 다음 회차 todo.json의 교체 목록에 남는다
   - 새로 넣은 파일은 `{"v": "ok", "note": "후보 n번 선택"}`. 이번 결과의 맞다·틀리다(파일이 그대로인 것)도 합친다
5. audit/tried.json에 이번 회차를 덧붙인다. 다음 검색이 같은 구간을 또 가져오지 않게
   - `{"slot", "date", "none": 다 별로 여부, "note": 사람 메모, "used": [고른 후보의 source_url], "rejected": [{"source_url", "title", "edits", "note"}]}`
   - review.py가 todo.json 슬롯마다 human_notes, avoid_sources로 붙인다
6. candidates/ 폴더를 지운다 → `python3 web/sounds/audit.py` → `python3 web/sounds/review.py` → 커밋
   - judge.json은 고치지 않는다. 내용 해시가 달라진 파일에는 옛 AI 판정이 붙지 않고 새 분류기 결과가 쓰인다

## 괴물 (2026-09-25 추가)

- 괴물은 동물과 같은 폴더, 같은 규격이다. 차이는 두 가지
  - 녹음이 아니라 만들어진 소리다. 라이선스는 "생성 모델 출력"으로 기록한다
  - 대사 파일이 있다: `<괴물id>_line_<사건>_<번호>.mp3`
- 괴물 id: `dokkaebi`(도깨비, 인터벌), `jeoseung`(저승사자, 지속주)
- 동물군 공용 `monster_<상태>_<번호>.mp3`를 넣으면 괴물 녹음이 없을 때 대신 쓴다

### 괴성 (말이 아닌 소리)

| 파일 | 내용 | 길이 |
|---|---|---|
| dokkaebi_roam_1~2 | 큰 몸집의 콧김, 낮은 그르렁 | 0.6~1.5초 |
| dokkaebi_sprint_1~2 | 괴성 포효. 쿵쿵 발소리가 섞여도 좋다 | 0.5~1.2초 |
| dokkaebi_tired_1 | 낮고 거친 헐떡임 | 1.0~2.0초 |
| dokkaebi_step_1~4 | 무거운 발 한 걸음(쿵). 쫓아올 때 앱이 괴물 속도에 맞춰 이어 튼다 | 0.2~0.5초 |
| jeoseung_roam_1~3 | 짚신 끄는 발소리, 방울(요령) 한 번, 낮은 바람 같은 숨. 셋 중 하나씩 | 0.8~2.0초 |

- 만드는 법 1순위: CC0 동물 녹음(곰, 사자, 멧돼지, 소)을 겹치고 피치를 3~7반음 내린다. 영화 괴물 소리의 표준 방식
- 2순위: Stable Audio Open 1.0 같은 효과음 생성 모델. 라이선스 조건(상업 이용 한도)을 credits.json에 적는다
- TTS로 괴성을 만들지 않는다. 말 모델이라 포효를 못 만든다
- 발소리(step, 2026-09-26 추가)
  - 파일은 걸음 하나. 박자는 앱이 괴물 속도에 맞춰 정한다. 같은 파일이 연달아 나오지 않게 4개를 돌려 쓴다
  - 앱 반영 전에는 소리가 나지 않고, 빌드가 이 4개를 "건너뜀"으로 알린다
  - 앱에서 고칠 곳: build.py 파일 이름 규칙에 step 추가, app.html 소리 불러오기와 발걸음 예약
  - 저승사자는 발소리 파일이 없다. 짚신 끄는 소리는 jeoseung_roam_1

### 대사

- 도구: Qwen3-TTS VoiceDesign (`Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`, Apache-2.0). 목소리를 글로 설계한다
- 문장마다 3번 이상 생성해 가장 좋은 것. 끝 음절이 잘리거나 말이 뭉개진 건 버린다
- 앱은 대사를 괴물이 있는 방향에서, 약간 멀게 튼다. 파일은 가까이서 말한 마른 소리로

도깨비. 목소리 설계문

```
Korean. A huge, gruff old male dokkaebi (Korean goblin). Deep, raspy, booming voice. Shouts in an old-fashioned Korean historical-drama tone, mischievous but threatening, like a village ogre scolding a thief.
```

| 파일 | 대사 |
|---|---|
| dokkaebi_line_spot_1 | 킁킁… 사람 냄새가 나는구나! |
| dokkaebi_line_spot_2 | 게 누구냐! |
| dokkaebi_line_sprint_1 | 네 이노오옴!!! |
| dokkaebi_line_sprint_2 | 게 섰거라아!! |
| dokkaebi_line_sprint_3 | 이놈! 거기 서지 못할까! |
| dokkaebi_line_near_1 | 방망이 맛 좀 보아라! |
| dokkaebi_line_near_2 | 코앞이다, 이놈! |
| dokkaebi_line_hit_1 | 으하하하! 잡았다! |
| dokkaebi_line_hit_2 | 혼쭐이 나 봐라! |
| dokkaebi_line_escape_1 | 헉… 헉… 날쌘 놈이로구나… |
| dokkaebi_line_escape_2 | 어이쿠, 숨이야… |
| dokkaebi_line_taunt_1 | 어딜 도망가느냐! |
| dokkaebi_line_taunt_2 | 도망쳐 봐야 도깨비 손바닥 안이다! |
| dokkaebi_line_taunt_3 | 금 나와라 뚝딱! 네 다리 느려져라 뚝딱! |

저승사자. 목소리 설계문

```
Korean. An ancient Korean grim reaper (jeoseung saja). Low, slow, cold male voice, almost a whisper, with long pauses between words. Calm, emotionless and chilling.
```

| 파일 | 대사 |
|---|---|
| jeoseung_line_spot_1 | …찾았다. |
| jeoseung_line_spot_2 | 명부에… 네 이름이 있구나. |
| jeoseung_line_near_1 | 멈추면… 데려간다. |
| jeoseung_line_near_2 | 숨소리가… 들린다. |
| jeoseung_line_hit_1 | 가자… 저승으로. |
| jeoseung_line_hit_2 | 네 차례다… |
| jeoseung_line_escape_1 | 도망쳐도… 소용없다. |
| jeoseung_line_escape_2 | 언젠가는… 따라잡는다. |
| jeoseung_line_taunt_1 | 발이… 느려졌구나. |
| jeoseung_line_taunt_2 | 거기… 서거라… |

- 저승사자는 돌진하지 않는다. sprint 대사와 sprint 괴성은 필요 없다

### 괴물 목소리로 만드는 후처리

TTS 날것은 "사람이 무섭게 연기한 소리"다. 괴물처럼 들리게 하는 건 후처리다.

```
# 도깨비: 3반음 내림(목이 커 보이게 포먼트도 같이), 저역 강조, 약한 찌그러짐
ffmpeg -i raw.wav -af "rubberband=pitch=0.84:formant=shifted,bass=g=5:f=120,asoftclip=type=tanh:param=1.5,volume=-2dB" -ac 1 tmp.wav
# 저승사자: 2반음 내림, 고역을 조금 깎아 어둡게, 짧은 메아리
ffmpeg -i raw.wav -af "rubberband=pitch=0.89:formant=preserved,lowpass=f=5500,aecho=0.8:0.6:70|140:0.25|0.15" -ac 1 tmp.wav
```

- 그다음은 위 음향 규격 그대로: 앞 무음 제거, 피크 -1dB, 모노 mp3 96kbps
- 대사 길이: 0.6~3.0초
- credits.json: `"license": "생성: Qwen3-TTS VoiceDesign (Apache-2.0)"`, `"source_url": "https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"`, `"author": "러너웨이"`, edits에 설계문 요약과 후처리 체인
