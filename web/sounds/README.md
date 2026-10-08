# 소리 녹음

- 이 폴더의 녹음이 합성음보다 먼저 쓰인다. 녹음이 없는 id는 합성음
- 목록과 검수표: docs/prd/18-horror-sounds.md. 앱에서는 설정 > 소리 검수
- 출처: credits.json. 전부 CC0(출처 표시 의무 없음)

## 지금 들어 있는 녹음

- 2026-10-08 괴물런 시절 녹음(claude/inspiring-goodall-v6mfyx 브랜치 web/sounds/)에서 옮김. 새로 만든 것 없음

| id | 파일 | 원래 파일 | 소리 |
|---|---|---|---|
| step | step_1~4 | dokkaebi_step_1~4 | 무거운 발 한 걸음 |
| breath | breath_1 | dokkaebi_tired_1 | 낮고 거친 헐떡임 |
| breath | breath_2 | jeoseung_roam_3 | 낮은 깊은 숨 |
| breath | breath_3~4 | wolf_tired_1~2 | 짐승 숨소리 |
| growl | growl_1~2 | dokkaebi_roam_1~2 | 콧김, 낮은 그르렁 |
| growl | growl_3 | canine_roam_1 | 짐승 으르렁 |
| pounce | pounce_1~2 | dokkaebi_sprint_1~2 | 포효. 잡힐 때만 |
| howl | howl_1~2 | wolf_roam_1~2 | 먼 늑대 울부짖음 |
| ring | ring_1 | jeoseung_roam_2 | 방울(요령) 한 번 |
| drag | drag_1 | jeoseung_roam_1 | 발 끄는 소리 |

- 안 옮긴 것: 괴물 대사(말 없음 원칙), 배경음악(밝은 게임풍이라 공포와 안 맞음), CC BY 녹음(출처 화면 없음)

## 파일 이름

- `<id>_<번호>.mp3` 예: `step_1.mp3`, `caught_1.mp3`
- id는 검수표의 id. 목록에 없는 이름은 빌드가 "건너뜀"으로 알려준다
- 같은 id에 여러 개를 넣으면 번갈아 쓴다(직전 것은 피한다). 발소리처럼 반복되는 소리는 3개 이상
- 형식: mp3, m4a, ogg, wav

## 종류별 규격

| 종류 | id | 녹음 |
|---|---|---|
| 깔리는 소리 | drone, wind, tension | 끊김 없이 반복되는 루프. 10~30초. 시작과 끝이 이어져야 한다 |
| 박자 소리 | step, heart, breath | 한 번 분량. step은 발 한 번(0.2~0.5초), heart는 쿵쿵 한 쌍, breath는 들숨+날숨 한 번(1~2초) |
| 한 번 소리 | 나머지 | 그 사건 하나. 앞 무음은 0.02초 이하 |

## 녹음 조건

- 가까이서 녹음한 마른 소리. 잔향, 거리감, 좌우는 앱이 입힌다
- 피크 -1 dBFS 이하, 클리핑 없음. 소리끼리 체감 음량을 비슷하게
- 44.1kHz 또는 48kHz, 모노 권장
- 라이선스: 상업 이용 가능한 것만. CC0 권장. 출처 표시가 필요한 소리는 출처 화면을 먼저 만들고 넣는다
