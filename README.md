# 러너웨이 (RunAway)

- 러닝 AR 추격 게임 + 운동 앱
- 지도에 뜬 가상 추격자를 피해, 제한 시간 안에 목적지를 찍고 출발점으로 복귀
- 컨셉의 축은 현실성. 적의 속도와 지구력은 모두 실측 데이터

## 상태

- PRD v0.9
- M0 완료(`sim/`), Kotlin 코어 이식·검증 완료(`core/`)
- 웹 앱 출시 가능 (2026-09-24). 신경망 음성 팩, 지도 끌기, 오프라인 캐시, 헤드리스 QA 통과. 판정은 docs/prd/12-launch.md

## 문서

| 파일 | 내용 |
|---|---|
| docs/prd/03-prd.md | PRD 핵심 (v0.6) |
| docs/prd/05-appendix.md | PRD 부록. 지표, 안전, 법률, 소셜, 비용 등 상세 |
| docs/prd/06-tts-research.md | TTS 공급자 조사 |
| docs/prd/07-art-directions.md | 아트·프론트엔드 방향 초안 5종 |
| docs/prd/08-m0-findings.md | M0 시뮬 결과와 티어 재배치 제안 |
| docs/prd/09-feedback.md | 사용자 피드백 로그와 조치 |
| docs/prd/15-voice-pack.md | 신경망 음성 팩. TTS 선택, 굽기, ASR 역검증 |
| docs/prd/16-ios.md | 아이폰 대응. 무음 스위치, 나침반, 다크 지도 |
| docs/prd/17-monster.md | 몬스터 추가 기획 토의 초안. 적응형 속도, 소리 도구 |
| web/sounds/README.md | 실제 동물 녹음 규격. 파일 이름, 길이, 음량, 라이선스, 출처 기록 |
| docs/app/index.html | 웹 프로토타입 (GitHub Pages용 사본) |
| sim/ | GPX 리플레이 시뮬레이터 (Python, 정수 코어) |
| core/ | Kotlin 코어. 상태 머신·판정·세션·GPX. Python과 골든 테스트로 일치 검증 |
| android/ | 네이티브 앱 스캐폴드. 이 환경에서 미빌드 |
| docs/prd/04-animal-data.md | 추격자 동물 실측 데이터와 출처 |
| docs/prd/02-decisions.md | 결정 로그 |
| docs/prd/00-questionnaire.md | PRD 질문지 336개 |
| docs/prd/01-research.md | 경쟁사, 기술, 법률 리서치 |
| docs/prd/00-idea.md | 원본 아이디어 |
| docs/ideas/ | 이 레포의 이전 아이디어 보관 |

## 핵심 컨셉

- 지도 위에 내 위치와 적 위치가 함께 표시됨
- 적은 내가 지나온 궤적을 따라 추격
- 위협 게이지: 30m 진입 시 상승, 50m 이탈 시 2배로 감소, 4초에 100%
- 피격 1회 = +30초 페널티. 3회면 실패하지만 러닝 기록은 계속 저장
- 난이도는 동물 티어. 정규 15종(나무늘보~그레이하운드) + 못 깨는 것들 10종(캥거루~프롱혼). 순서는 추격 시뮬 결과

## 설계의 근거

- 인간은 스프린트에서 거의 모든 동물에 진다
- 인간은 지구력에서 거의 모든 동물을 이긴다
- 그래서 이 게임은 빠르게 달려 이기는 게임이 아니라, 적의 스프린트를 버텨내는 게임
- 칼라하리 수렵민은 쿠두를 2~5시간 추격해 잡았고, 웨일스의 34km 레이스에서 인간이 말을 이긴 적이 두 번 있다

## 주소

- 저장소: https://github.com/cjsdudwls1/RUNA-WAY (원래 `my-girlfriend-is-two`에서 이름 변경)
- 웹 프로토타입 (GPS·지도 동작): https://cjsdudwls1.github.io/runa-way/
- 배포: `gh-pages` 브랜치 루트의 index.html = `docs/app/index.html` (web/build.py 산출물)
