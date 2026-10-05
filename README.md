# 러너웨이 (RunAway)

- 러닝 앱. 상대는 사용자가 정한 페이스 그대로 달리는 가상 주자
- 경주 모드: 당신을 긁는 짜증나는 상대와 경주. 상대가 상황마다 약 올린다
- 공포 모드: 쫓아오는 아무개씨를 피해 도망. 말 없이 발소리, 브금, 효과음만
- 운동 종류: 일반런(거리, 페이스), 빌드업(시작·종료 페이스, 거리), 인터벌(페이스, 세트 거리, 세트 수, 회복)

## 상태

- 2026-10-05 개편. 동물 추격자, 동물별 소리·대사, 관제 음성 팩, 지도 삭제. 명세는 docs/prd/17-modes.md
- 경주 대사: 초안. 사용자가 web/race_lines.md를 직접 쓴다
- 공포 소리: 합성음 초안. 검수표 docs/prd/18-horror-sounds.md

## 문서

| 파일 | 내용 |
|---|---|
| docs/prd/17-modes.md | 개편 명세. 경주/공포 모드, 일반런/빌드업/인터벌, 규칙 |
| docs/prd/18-horror-sounds.md | 공포 모드 소리 목록과 검수표 |
| web/race_lines.md | 경주 모드 대사표. 상황 37개. 빌드가 그대로 읽는다 |
| web/sounds/README.md | 합성음을 녹음으로 바꾸는 규격 |
| docs/prd/03-prd.md | PRD 핵심 (v0.6) |
| docs/prd/05-appendix.md | PRD 부록. 지표, 안전, 법률, 소셜, 비용 등 상세 |
| docs/prd/06-tts-research.md | TTS 공급자 조사 |
| docs/prd/07-art-directions.md | 아트·프론트엔드 방향 초안 5종 |
| docs/prd/08-m0-findings.md | M0 시뮬 결과와 티어 재배치 제안 |
| docs/prd/09-feedback.md | 사용자 피드백 로그와 조치 |
| docs/prd/15-voice-pack.md | 신경망 음성 팩. TTS 선택, 굽기, ASR 역검증 |
| docs/prd/16-ios.md | 아이폰 대응. 무음 스위치, 나침반, 다크 지도 |
| docs/app/index.html | 웹 앱 (GitHub Pages용 사본) |
| sim/ | (이전 버전) 동물 추격 GPX 시뮬레이터. 보관 |
| core/ | (이전 버전) 동물 추격 Kotlin 코어. 보관. 웹은 GPS 거리 계산만 같은 규칙을 쓴다 |
| android/ | (이전 버전) 네이티브 앱 스캐폴드. 미빌드 |
| docs/prd/04-animal-data.md | (이전 버전) 추격자 동물 실측 데이터 |
| docs/prd/02-decisions.md | 결정 로그 |
| docs/prd/00-questionnaire.md | PRD 질문지 336개 |
| docs/prd/01-research.md | 경쟁사, 기술, 법률 리서치 |
| docs/prd/00-idea.md | 원본 아이디어 |
| docs/ideas/ | 이 레포의 이전 아이디어 보관 |

## 핵심 규칙

- 상대 속도 = 설정 페이스. 지도 없음. 내 이동 거리 대 상대 이동 거리
- 경주: 옆에서 같이 출발. 결승 시간으로 승패. 인터벌은 세트별 승패
- 공포: 설정 페이스로 15초 갈 거리만큼 뒤에서 출발. 0m면 잡힘(+1회), 다시 뒤로. 주행은 계속
- 5초 넘게 멈추거나 GPS가 약하면 상대도 멈춘다. 신호등에서 무리하지 않게
- 인터벌 회복 중에는 상대 없음

## 이전 버전

- 2026-09까지는 실측 동물 25종이 지도 위에서 추격하는 게임이었다. 문서 00~16, sim/, core/, android/에 남아 있다

## 주소

- 저장소: https://github.com/cjsdudwls1/RUNA-WAY (원래 `my-girlfriend-is-two`에서 이름 변경)
- 웹 앱: https://cjsdudwls1.github.io/RUNA-WAY/ (경로 대소문자 구분)
- 배포: `gh-pages` 브랜치 루트의 index.html = `docs/app/index.html` (web/build.py 산출물)
