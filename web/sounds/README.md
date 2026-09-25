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
