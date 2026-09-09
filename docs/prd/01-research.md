# 사전 리서치 노트

- 기준일: 2026-09-07. 웹 검색 기반
- "(확인 필요)" 표시: 출처 확인 더 필요
- 각 절 끝 "PRD 질문에 반영할 시사점"이 질문지 근거

## 목차

- [경쟁사 · 시장 리서치](#competitors)
- [기술 타당성 리서치](#tech)
- [법률 · 안전 · 정책 리서치](#legal_safety)

<a id="competitors"></a>
## 경쟁사 · 시장 리서치

### 요약

- 오디오 추격 원조 Zombies, Run!: 14년간 약 1,160만 다운로드·누적 매출 약 790만 달러(Appmagic 추정). 2025년 사실상 개발 중단, 2025년 11월 원작자 Naomi Alderman이 high six-figure 달러에 재인수
- 지도 위 적 배치+목적지 타임어택에 가장 가까운 앱: 2026년 8월 Show HN 무료 브라우저 게임 Run With Zombies. 상용 완성형 앱은 뚜렷하지 않음(확인 필요)
- 한국: 러닝 인구 1,000만 추정, 서울 러닝 크루 100개 이상, 2025년 검색량 전년 대비 +82%. Strava는 2025년 3월 한국 철수. 네이버·카카오·삼성이 2026년 러닝 진입
- 리뷰 불만 공통: GPS 튐, 배터리, 구독 가격, 콘텐츠 반복, 워치 미지원
- 워치·글래스 네이티브는 비어 있는 차별화 포인트

### 주요 경쟁 앱 비교

| 앱 | 개발사/출시 | 핵심 루프 | 과금 | 비고 |
|---|---|---|---|---|
| Zombies, Run! | Six to Start → Naomi Alderman, 2012 | 오디오 드라마 미션+좀비 추격+기지 건설 | 월 6.99달러/연 49.99달러/VIP 연 89.99달러(2024.5) | 지도 위 적 위치 없음. 10~11개 시즌·500개 이상 미션. 시즌 1 한국어 더빙 |
| Marvel Move | Six to Start/ZRX, 2023 | 마블 IP 오디오 러닝 | 월 5.99달러/연 59.99달러 | ZR 동일 엔진 |
| Run With Zombies | 개인 개발, 2026.8 | GPS 주변 좀비 스폰, 스태미나, 추출 지점, 글로벌 리더보드 | 무료·무계정·PWA | 우리 아이디어와 가장 유사 |
| Zombie Streets | 소규모 개발 | GPS 맵 좀비 슈터, 자원, 길드 | F2P | 4.7점·1,000+ 다운로드(확인 필요) |
| Run An Empire | Location Games(영국), 2016 | 걷기/달리기로 영토 점령 | 무료+구독 | 활동 정체(확인 필요) |
| Stride | 같은 팀, 2020~ | 루프 면적=영토, 탈취/방어, 주간 리그 | 무료 | 런픽과 유사 |
| Ghost Pacer | Kickstarter 2020 | AR 글래스 홀로그램 페이서 | 199~349달러 예정 | 공급망 문제로 취소. 특허 Peloton 인수 |
| Walkr | Fourdesire(대만) | 걸음→우주선 에너지 | F2P+IAP | GPS 미사용, 에너지 게이팅 불만 |
| 런픽 | 국내 | 영토 점령+커뮤니티 | 무료 | - |
| 모두의 러너 | 국내, 2025~ | 스탬프 투어+챌린지 | 무료 | - |

- ZR 추격 규칙: 직전 30초 평균 페이스 대비 20% 빠르게 약 1분(100초) 유지. 잡히면 보급품 손실. 구독자는 증속률 10~30% 조정, 추격 off 가능
- ZR 사업 이력: 2021년 OliveX(Animoca Brands 계열)가 665만+성과연동 285만 달러에 인수. 2023년 10월 50% 이상 감원·CEO 퇴사. 2025년 3월 2명 제외 전원 해고. 2025년 11월 24일 Alderman 재인수. 2026년 신규 시즌·스마트워치 오디오 지원 예고
- ZR MAU 약 30만, 유료 약 5만(확인 필요)
- 결론: 지도 위 적 배치+지형 회피+목적지 타임어택+난이도+리더보드를 상용 품질로 묶은 앱 없음. 컨셉은 직관적. 실행 품질·안전·워치·콘텐츠 운영이 차별점

### Niantic 계열 교훈

- 2025년 3월 Scopely가 Niantic 게임 사업부를 35억 달러에 인수. 지리공간 AI는 Niantic Spatial로 분사(자본 2.5억 달러, Ingress·Peridot 보유). 2026년 7월 6일 게임 팀 "Scopely Explore"로 개명
- 규모: MAU 3,000만 이상, 2024년 매출 10억 달러 이상. Pokémon GO 주간 활성 2,000만
- Peridot 모바일 2026년 5월 14일 스토어 삭제, 8월 31일 서버 종료. Snap Spectacles용 Peridot Beyond로 이동
- 설계 원칙: 탐험·운동·사교. POI 기준(Wayfarer): 영구적·식별 가능·안전·공공 접근
- 안전·법적: 추락·차도 진입·무단침입 집단소송. 대응은 약관·"주변 확인" 팝업·POI 삭제 절차
- Pokémon GO 2019년 7월 1일 Apple Watch 앱 종료. Adventure Sync(헬스 데이터 연동)로 대체
- 한국 수용성: 2017년 Pokémon GO 첫날 DAU 390만, 설 연휴 620만

### 한국 러닝 앱 시장

- 수요: 한국갤럽 달리기 경험률 2021년 23% → 2023년 32% → 2025년 31%. 2025년 검색량 +82%, 러닝화 판매 +10%. 2026년 검색량 +16.4%. 러닝코어 패션 거래 72%가 2030
- 이벤트: 포켓몬 런 2026(5월 5일 뚝섬, 5,000명), 나이키 애프터 다크 서울 10K(2025년 5월 10일 여의도, 여성 7,000명), 카카오프렌즈 런 2026(10월 10일 탄천, 1만 명)
- Strava 2025 Year in Sport: 러닝 클럽 3.5배 성장. Gen Z는 이벤트가 주 동기일 확률 X세대보다 75% 높음

| 앱 | 과금 | 특징 | 한국 상태 |
|---|---|---|---|
| NRC | 무료 | 오디오 가이드 런, 챌린지, Apple Watch·Wear OS 단독 | 2030 인지도 최상. GPS 오차 사례(워치 4km vs NRC 1.93km). 커뮤니티 약함 |
| 런데이(한빛소프트, 2015) | 무료+광고/프리미엄(가격 확인 필요) | 100% 한국어 음성 코칭, 크루, 155개국, Apple Watch 단독 | 입문자 1위. 거리 오류·기록 누락·배터리·광고 불만 |
| Strava | 월 11.99달러/연 79.99달러 | 세그먼트·클럽·리더보드 | 2023년 8월 한국어 종료. 2025년 3월 앱 권한(마이크) 동의 이슈로 철수 |
| 트랭글 | 무료 | 1.2만 종 배지·경험치·랭킹. 등산·자전거 중심 | 게이미피케이션 선례 |
| 삼성 헬스 | 무료(갤럭시 워치) | 러닝 코치(레벨 1~10, 160여 프로그램). 2026년 5월 14일 자세 6지표 분석 | "천만 러너" 공략 선언 |
| 네이버·카카오(2026.7) | - | 네이버 지도 도보 코스 만들기. 카카오맵 친구 위치+마라톤 | 코스·커뮤니티 흡수 중 |

- 관찰: 기록·코칭은 포화. 지도 기반 경쟁/게임은 Strava 철수 후 공백
- 크루 논란: 2026년 3월 한강 20명 크루 3열 충돌 논란. 2025년 9월 여의도공원 'No 4' 안내판. 서초구 반포 트랙 5인 이상 단체 제한. 한강 자전거 사고 3년간 308건

### 사용자 불만 테마

1. GPS 튐/거리 오차: 다리 밑·고층 빌딩·터널. 적 위치가 GPS에 묶이면 "억울한 사망"
2. 배터리: GPS+오디오+화면 상시. ZR "enormous drain"
3. 안전: 스프린트 유도·헤드폰·화면 응시·야간
4. 반복성/콘텐츠 고갈: 스토리 예측 가능, 신규 시즌 정체
5. 가격: 연 49.99~79.99달러 표준. 월 churn 중앙값 10~13%(상위 4~6%). 자동갱신·환불 불만
6. 워치 미지원/불안정: "폰 없이 못 뛴다". ZR 워치 앱 수년째 고장
7. 권한/프라이버시: Strava 철수 사례(정보통신망법)

### 워치/글래스 지원 현황(2026년 9월)

| 앱 | Apple Watch | Wear OS/갤럭시 | 글래스 |
|---|---|---|---|
| Zombies, Run! | 컴패니언만(폰 필수, 사실상 고장) | 없음("계획 중") | 없음 |
| Pokémon GO | 2019.7 종료 → Adventure Sync | 없음 | 없음 |
| Pikmin Bloom | 없음(확인 필요) | 없음 | 없음 |
| Peridot | 모바일 종료 | 모바일 종료 | Snap Spectacles(Peridot Beyond), Quest/Vision Pro |
| NRC | 단독 실행 | 단독 실행 | 없음 |
| Strava | 단독 실행 | 단독 실행 | Meta Ray-Ban/Oakley Meta Vanguard: Garmin 실시간 페이스 음성, Strava 오버레이 |
| 런데이 | 단독 실행 | (확인 필요) | 없음 |
| 삼성 헬스 | - | 네이티브 | Android XR 글래스(2026 가을, 1세대 디스플레이 없음) |
| Run With Zombies | 없음 | 없음 | 없음 |

- 글래스 타임라인: Meta Ray-Ban Display(2025.9), Oakley Meta Vanguard(2025.10, Garmin 연동), Snap Specs 2026, 삼성·구글 Android XR 2026년 가을, AR 디스플레이판 2027년 예상
- 2026~27년 글래스 주류는 디스플레이 없는 오디오+카메라+AI. 음성 알림·AI 성우·방향 힌트 우선, HUD 지도는 2027 이후

### PRD 질문에 반영할 시사점

1. 포지셔닝: ZR 긴박감 + Stride/Ingress 지도 경쟁 + Strava 공백(리더보드/클럽). 지도 위 실체 있는 적을 5초 내 시연
2. 추격 규칙: ZR 공식(30초 평균 대비 +20%/1분)이 출발점. 적 속도는 최근 5분 평균 페이스 대비 배율. 증속률·on/off·사운드 강도 조정 가능. 초보 모드 스프린트 강요 금지
3. GPS 신뢰도: 칼만 필터·속도 상한. 정확도 20m 초과 시 적 정지(무적) 상태. 워치 GPS 우선. 판정 이의 제기(리플레이)
4. 배터리: 1시간 러닝 15% 이하 목표. Audio-first 모드, 지도 렌더링 최소화, 온디바이스 계산
5. 안전: 차도 100m 이내·횡단보도·지하차도·계단·사유지 제외 POI. 야간 조명 코스만·강도 하향. 반경 200m 내 5명 이상이면 목적지 분산. 세션별 안전 고지. 미성년자 야간 제한
6. 콘텐츠: 음성 생성 AI+절차적 적 배치로 무한 미션. 시즌제 스토리+동물/좀비 컬렉션
7. 가격: 글로벌 월 6.99~11.99달러/연 49.99~79.99달러. 한국 2030 대상 연 3~5만원대+무료 코어+코스메틱/시즌패스. 무료 유저 매일 1회 추격 미션
8. 워치: 1.0 Apple Watch·Wear OS 컴패니언(페이스·적 거리 햅틱). 2.0 단독 모드. Apple Health/Health Connect 동기화 필수
9. 글래스: 공간 오디오+AI 성우 실시간 대사("적이 왼쪽 뒤 30m"). HUD 지도 2027+
10. 규제: 위치·마이크·헬스 권한 목적 설명 UX. 정보통신망법. 위치정보사업 신고 검토
11. 진입 훅: 한강(여의도·뚝섬·반포·잠실)·탄천·올림픽공원·서울숲 코스 팩. 대형 펀런 연계 이벤트. 크루 대항 리더보드(떼 러닝 방지 규칙 포함)
12. KPI: 월 churn 상위 4~6% 목표. ZR MAU 30만/유료 5만(확인 필요)이 니치 스토리 러닝 앱의 천장
13. 톤: 2030은 기록보다 함께·재미·패션. 귀엽고 공유 가능한 동물 캐릭터. 결과 화면은 공유용 설계

### 확인 필요 항목

- ZR MAU 30만/유료 5만 원출처
- 런데이 프리미엄 가격·MAU, 트랭글 워치 지원, 모바일인덱스 순위
- Run An Empire 서비스 상태, Zombie Streets 다운로드 규모
- Pikmin Bloom 워치 앱 부재 여부
- ZR 2026 신규 시즌·워치 오디오 실제 출시 시점
- 국내 "지도 위 적 배치 추격" 앱 출시 사례

### 출처

- Zombies, Run!
  - https://zrx.app/news/Get-started-with-zr
  - https://zombiesrungame.com/news/loc-testing-ko
  - https://www.makeuseof.com/what-is-zombies-run-app/
  - https://support.zombiesrungame.com/hc/en-us/articles/203780596-How-do-Chases-work-I-keep-getting-caught
  - https://www.npr.org/2012/02/19/147008041/the-new-running-game-where-zombies-chase-you
  - https://play.google.com/store/apps/details?id=com.sixtostart.zombiesrunclient
  - https://support.sixtostart.com/hc/en-us/articles/4421552238481-Zombies-Run-Subscription-iPhone
  - https://www.motera.app/zombie-run-app
  - https://www.marvel.com/articles/culture-lifestyle/walk-jog-or-run-with-super-heroes-in-marvel-move-now-available
  - https://betanews.com/article/how-zombies-run-got-four-million-downloads/
  - https://mobilegamer.biz/author-naomi-alderman-buys-back-zombies-run-for-six-figure-sum/
  - https://www.pocketgamer.biz/redundancies-at-zombies-run-and-marvel-move-developer-six-to-start/
  - https://zombiesrungame.com/news/naomi-buying-zr
  - https://www.pocketgamer.com/zombies-run/naomi-alderman-return/
  - https://www.aivanet.com/2026/05/zombies-run-is-officially-back-from-the-dead/
  - https://yonifreedhoffmd.substack.com/p/need-running-motivation-try-zombies-run
  - https://apps.apple.com/us/app/zombies-run/id503519713
  - https://justuseapp.com/en/app/566596422/zombies-run-5k-training/reviews
  - https://apps.apple.com/gb/app/zombies-run/id503519713?see-all=reviews
  - https://grokipedia.com/page/Zombies,_Run!
  - https://justuseapp.com/en/app/503519713/zombies-run/reviews
- Niantic/Scopely
  - https://techcrunch.com/2025/03/12/pokemon-go-maker-niantic-is-selling-its-games-division-to-scopely-for-3-5b
  - https://pokemongohub.net/post/news/niantic-games-team-now-officially-called-scopely-explore/
  - https://en.wikipedia.org/wiki/Niantic_Spatial
  - https://www.scopely.com/en/news/scopely-to-acquire-niantic-games-business-which-includes-pokemon-go-one-of-the-most-successful-mobile-games-of-all-time
  - https://www.pocketgamer.biz/pokmon-go-has-20m-weekly-active-players-nearly-nine-years-after-its-global-launch/
  - https://playperidot.com/en/news/peridot-mobile-sunset
  - https://www.nianticspatial.com/blog/peridot-beyond-multiplayer
  - https://vr.org/articles/niantic-peridot-mobile-sunset-ar-pivot-glasses
  - https://petapixel.com/2026/03/16/pokemon-go-players-unknowingly-helped-build-a-30-billion-ar-image-map-of-the-world/
  - https://nianticlabs.com/news/nrwp-update
  - https://www.gamedeveloper.com/design/designing-a-planet-scale-real-world-ar-platform
  - https://www.sciencedirect.com/science/article/pii/S1875952123000307
  - https://hshlawyers.com/blog/pokemon-go-personal-injury-safety-issues-and-liability/
  - https://attorneycoalition.com/can-pokemon-go-get-sued-for-accidents-robberies-and-trespassing-incidents/
  - https://niantic.helpshift.com/hc/en/6-pokemon-go/faq/1812-discontinued-support-for-apple-watch/
  - https://www.researchgate.net/publication/360265825_Balancing_the_Augmented_Experience_Design_Tensions_in_the_Location-based_Game_Pikmin_Bloom
  - https://en.wikipedia.org/wiki/Pikmin_Bloom
  - https://en.wikipedia.org/wiki/Ingress_(video_game)
  - https://ingress.com/news/getting-ready-for-niantic-spatial
  - https://brunch.co.kr/@@zIH/489
- 피트니스 RPG/추격
  - https://www.runanempire.com/
  - https://www.runanempire.com/stride/
  - https://striderunning.run/
  - https://justuseapp.com/en/app/834805518/walkr-a-gamified-fitness-app/reviews
  - https://www.appbrain.com/app/fitness-rpg-walking-games/com.shikudo.fitrpg.google
  - https://runwithzombies.com/
  - https://news.ycombinator.com/item?id=49197889
  - https://apps.apple.com/us/app/zombie-streets-gps-ar-shooter/id1670656973
  - https://www.pelobuddy.com/peloton-ghost-pacer/
  - https://play.google.com/store/apps/details?id=kr.co.runpick
  - https://apps.apple.com/kr/app/id6739476561
  - https://www.threads.com/@genkino2024/post/DIGF-IKhLgP/
  - https://mistyway.app/blog/best-walking-games
- 한국 시장
  - https://www.iconsumer.or.kr/news/articleView.html?idxno=30276
  - https://v.daum.net/v/20250918070600267
  - https://koreafuture.co.kr/m/view.php?idx=23771&mcode=m6272m3
  - https://www.wednesdata.com/truth-about-10-million-runners/
  - https://fashionbiz.co.kr/article/212867
  - https://www.kakaocorp.com/page/detail/12095
  - https://press.strava.com/articles/strava-releases-12th-annual-year-in-sport-trend-report-2025
  - https://www.threads.com/@velinkeem/post/DOz8cbokrlU
  - https://www.nike.com/kr/nrc-app
  - https://www.runday.co.kr/
  - https://biz.heraldcorp.com/article/2470281
  - https://thebestfastnews.com/런데이-왜-논란일까/
  - https://www.asiae.co.kr/article/2025032416121224051
  - https://namu.wiki/w/STRAVA
  - https://www.strava.com/pricing
  - https://www.tranggle.com/
  - https://www.newspim.com/news/view/20260514000285
  - https://zdnet.co.kr/view/?no=20260514105149
  - https://www.fnnews.com/news/202607181301148256
  - https://biz.heraldcorp.com/article/10706046
  - https://news.nate.com/view/20250916n35840
  - https://www.fnnews.com/news/202608171102357058
  - https://www.newsis.com/view/NISX20241210_0002991130
- 가격/churn·워치/글래스
  - https://lifecyclearchitect.com/benchmarks/fitness-apps-churn-rate-benchmarks/
  - https://adapty.io/blog/health-fitness-app-subscription-benchmarks/
  - https://support.strava.com/en-us/articles/15401555-meta-glasses-and-strava
  - https://www.uploadvr.com/meta-smart-glasses-garmin-strava-integration/
  - https://9to5google.com/2026/05/19/google-samsung-android-xr-glasses-styles-release-date/
  - https://www.findyouredge.app/news/best-running-apps-samsung-galaxy-watch-uk-2026

<a id="tech"></a>
## 기술 타당성 리서치

### 한국 지도 SDK

- 구글맵: 2026-02-27 국토지리정보원 협의체가 1:5,000 고정밀 지도 반출 조건부 허가. 조건: 국내 서버 처리 후 기본도·교통망만 반출, 군사·보안시설 블러, 국내 컴플라이언스 담당자 고용
- 구글맵: 2026-04 시점 한국 도보/자동차 턴바이턴 미출시, 시점 미정. 대중교통만 정상. Street View 커버리지 사실상 없음(2012 서울·부산 일부)
- 네이버(NCP Maps): Mobile Dynamic Map은 SDK, 맵 뷰 생성 1회=1건. 2025-07-01부터 구 인증(client id) 무료량 중단, ncpKeyId 마이그레이션 필요. 무료 한도·초과 단가(Directions 5 월 6만 건 무료·초과 5원 등) (확인 필요). Directions 5/15는 자동차 전용. 커뮤니티: `flutter_naver_map`, `@mj-studio/react-native-naver-map`
- 카카오맵: 공식 Flutter `kakao_map_sdk`. 무료 쿼터 지도 일 30만 건, 좌표→주소 일 10만 건. 2026-07-21부터 계정당 첫 활성 앱만 무료, 초과·두 번째 앱은 종량(지도 0.1원/건, 좌표→주소 0.5원/건). 길찾기는 카카오모빌리티 소관
- Mapbox/OSM: 보행로·POI·건물 형상 네이버/카카오 대비 열세. 한국 OSM 추출본 약 261MB(2026-04). VWorld 참고 OSM 편집 불가(2017 차단 전례). Maps SDK 월 25,000 MAU 무료, 초과 1,000 MAU당 $4. Navigation SDK 무료 구간 100 MAU+1,000 trips → 부적합. 강점: 커스텀 스타일, 벡터 타일, 3D 빌딩, Unity/Flutter/RN 공식 SDK
- VWorld: 인증키 발급 후 무료(2D WMTS/TMS, 3D, 지오코더). 일일 호출 제한, SLA 없음. 국외 서버 타일 캐싱 금지 (확인 필요). 백업/오프라인 개발용
- 현실적 구성: 표시는 Mapbox 스타일 또는 카카오, 경로/스냅은 자체 OSM 라우팅

### 보행자 경로 API

| 제공자 | 보행자 | 가격/제한 | 비고 |
|---|---|---|---|
| TMAP(SK open API) | O | 건당 10원, 일 1,000건 무료 (확인 필요). 월 220만원(VAT 포함) 정액제 | 한국 유일 공개 보행자 API |
| 카카오모빌리티 | 제휴 파트너 전용 | 공개 API는 자동차만 | 초기 접근 불가 |
| 네이버 Directions 5/15 | X | - | 자동차 전용 |
| 구글 Directions | 한국 도보 미제공(2026-04) | - | 시점 미정 |
| Mapbox Directions | O(OSM) | 무료 구간 후 $2/1,000건 (확인 필요) | 품질 불균일 |
| 자체 호스팅 OSRM/Valhalla/GraphHopper | O(foot) | 4 vCPU/8~16GB VM 월 $40~100 | OSRM 5~10ms·8코어 5k~10k QPS. Valhalla 10~30ms·2~4k QPS·trace_route 맵매칭. GraphHopper 1~3k QPS |

- 게임에 필요한 것: 목표까지 대략 거리/시간, 위치 스냅용 그래프, 적 이동 공간. OSM+Valhalla(또는 OSRM foot)로 충분
- 1만 MAU 이전 자체 호스팅 전환 필수. TMAP은 MVP(월 3만 건 이하)만
- 안전 규칙(횡단 최소화, 대로 회피): Valhalla pedestrian costing `walkway_factor`, `driveway_factor`

### GPS 정확도/배터리

- 오차: 개활지 3~5m, 도심 협곡 10~30m 이상, 실내·지하 수십 초 신호 상실. 워치는 폰보다 나쁨(Apple Watch Ultra 듀얼밴드 예외)
- 듀얼밴드(L1+L5): Galaxy S25, Pixel 9, iPhone 16 Pro 이상, Apple Watch Ultra. 도심 95% 수평 오차 40~60% 감소, 개활지 sub-3m. Android Raw GNSS Measurements API로 위성 데이터 접근
- 권장 파이프라인
  1. 게이트 필터: accuracy > 25~30m, 타임스탬프 역행, 속도 > 8 m/s 폐기
  2. 칼만 필터(등속) 또는 가속도계 융합, 1Hz
  3. 경로 스냅: 코스 폴리라인 수직 투영(오프라인). 자유 러닝은 Valhalla trace_route/OSRM match
  4. 케이던스(150~190 spm) 정합, GPS 소실 시 데드레코닝
  5. 조우 판정 반경 15~25m 히스테리시스. 적은 클라이언트 시뮬레이션, 서버는 결과 검증
- iOS: CLLocationManager activityType .fitness, desiredAccuracy Best, pausesLocationUpdatesAutomatically=false, allowsBackgroundLocationUpdates=true, UIBackgroundModes location/audio. iOS 17+ CLLocationUpdate.liveUpdates + CLBackgroundActivitySession
- Android: Foreground Service(type location) 필수. 14+ FOREGROUND_SERVICE_LOCATION, 백그라운드에서 FGS 시작 불가. FusedLocationProvider PRIORITY_HIGH_ACCURACY 1초, 화면 꺼짐 시 setMaxUpdateDelayMillis 배칭. 플레이 백그라운드 위치 선언 폼·영상 심사
- 배터리: 1Hz GPS+화면 상시+지도 시간당 15~25%, 화면 끄고 오디오 5~10% (확인 필요). 카메라 AR 25~40%+ 및 발열
- 기본 UX: 화면 꺼짐+오디오/워치 HUD. 지도는 화면 켤 때만 렌더링

### AR 프레임워크와 실용성

- ARCore Geospatial(VPS): 무료, Android/iOS/Unity. VPS 정밀도는 Street View 커버리지 의존 → 한국은 GPS+나침반 저정밀만 (확인 필요: 한국 VPS 커버리지). Street View 재진입해도 2027 이후
- Niantic Spatial: 2026-04 Scaniverse+VPS 2.0, NSDK 4.0, 100만 VPS 로케이션. Lightship ARDK 무료, 멀티플레이어 5만 MAU 초과 유료(6개월 유예), VPS 단가 비공개. 러닝 코스 전체 커버 불가
- 8th Wall: 오픈소스 전환·호스팅 종료(2026-01). 신규 상용 비추천
- Unity AR Foundation: Personal 무료($200K 이하), Pro 연 $2,310/시트(2026-01), 런타임 요금 폐지
- 러닝 중 카메라 AR 문제: 안전(시야 차단, 횡단 사고), 트래킹 손실(팔 스윙), 20~30분 내 열 스로틀링, 시간당 25~40%
- 결론: 코어는 "지도 위 AR"(2.5D 틸트 맵+적 스프라이트, 레이더/방향 화살표, 공간음향). Zombies, Run!은 오디오만으로 10년 이상 성공
- 카메라 AR은 정지 이벤트(출발 게이트, 체크포인트 미니게임, 도착 후 포토 모드)만. ARKit/ARCore 기본 앵커로 구현 → Unity 의존 제거

### 크로스플랫폼 선택

| 관점 | Flutter | RN(Expo) | Unity | 네이티브(+KMP) |
|---|---|---|---|---|
| 한국 지도 | kakao_map_sdk 공식, flutter_naver_map | 커뮤니티 포팅, 카카오 미성숙 | 플러그인 없음, Mapbox Unity SDK 정체 (확인 필요) | 1급 |
| 백그라운드 위치 | Transistorsoft $500/앱 또는 네이티브 FGS | expo-location, Transistorsoft | 매우 어려움 | 최적 |
| 워치 | 네이티브 별도 필수 | 동일 | 불가 | 동일 툴체인 |
| AR | 미성숙 | 미성숙 | 최강 | ARKit/ARCore 직접 |
| 공간음향 | 제한 | 제한 | Steam Audio/Resonance | PHASE/Spatializer/Oboe |
| 배터리 | 양호 | 양호 | 불리(상시 렌더) | 최적 |

- 1순위: 네이티브 Swift+Kotlin, KMP로 시뮬레이션·부정행위 규칙·오디오 큐 로직 공유
- 2순위(2~3인, 속도 우선): Flutter + 네이티브 워치 앱 + 네이티브 위치 FGS 모듈
- Unity는 카메라 AR 중심 피벗 시만 재검토

### 워치

- watchOS: HKWorkoutSession으로 백그라운드 유지·심박 스트리밍. 위치는 Background Modes "Location updates" + allowsBackgroundLocationUpdates 별도 설정(watchOS 4+). 독립 워치 앱 가능(GPS/셀룰러, AirPods 오디오)
- 배터리: Series 11 GPS 워크아웃 8시간, Ultra 3 14시간(저전력 20시간). 듀얼밴드는 Ultra 계열 (확인 필요: Series 11 포함 여부)
- iOS 17+ 미러링 세션. watchOS 26 Workout Buddy
- 워치 단독 UX: 레이더+거리/방향+햅틱+오디오
- Wear OS: Health Services ExerciseClient, ExerciseConfig(isGpsEnabled=true), FGS type health|location(Wear OS 5+), 기기당 1개 앱만 운동 추적. 화면 꺼짐 시 배칭(예 150초) → batchingModeOverrides 또는 FusedLocationProvider 직접. 갤럭시 워치4 이상. GPS 시간당 10~15% (확인 필요)
- 가민 Connect IQ: Monkey C, Position API, Communications 모듈. 메모리 제한 엄격(fēnix 5 데이터필드 28KB), 서드파티 오디오 재생 불가 (확인 필요: 최신 기기 한도). 데이터필드 거리 표시+진동만. 우선순위 낮음
- MVP: 폰 필수 + 워치 컴패니언(HUD/심박/햅틱)

### 스마트 글래스 2026

| 기기 | 서드파티 접근 | 디스플레이 | 한국 | 적합성 |
|---|---|---|---|---|
| Meta Ray-Ban Display($799, Neural Band) | DAT 2026-05 Display 개발자 프리뷰(텍스트·이미지·버튼·비디오, 제스처, iOS/Android SDK) | 단안 풀컬러 | 미국 한정(국제 확장 2026-01 중단) | 높음(향후) |
| Ray-Ban Meta/Oakley Meta | DAT 카메라(720p30)·오디오 | 없음 | 2026-05-25 출시(69만원~) | 오디오 채널 |
| Even Realities G2(+R1 링) | SDK, Even Hub(2026-04) 50+ 앱, 개발자 2,000명, BLE 텍스트 | 640×350 녹색 단색, 27.5° FOV, 1,200nit, 36g, 2일+ | 직구 (확인 필요) | 매우 높음 |
| 삼성/구글 Android XR | Developer Catalyst(2026-05~07), Jetpack XR. 개발킷 미국/캐나다/일본/영국/EU | 1세대(2026 가을) 디스플레이 없음, 디스플레이 모델 2027 루머 | 국내 출시 유력 | 2027 이후 |
| Xreal One/Air, Project Aura | 유선(USB-C/컴퓨트 퍽) | 양안 풀컬러 | 국내 판매 | 낮음 |

- 2026 가능한 것: 오디오(전 기기), 텍스트/아이콘 HUD(Even G2, Ray-Ban Display 프리뷰), 카메라 스트림(Meta). 세계 정합 AR 오버레이 불가
- 설계: "HUD 출력 채널" 추상화(텍스트 3~4줄+방향 아이콘). 1차 Even G2, 2차 Ray-Ban Display, 3차 Android XR

### 한국어 TTS

| 서비스 | 가격 | 한국어 | 상업 |
|---|---|---|---|
| ElevenLabs | Free/Starter $5/Creator $22/Pro $99/Scale $299/Business $990. Flash v2.5 크레딧 절반 | v3·Multilingual v2 상위권, 감정 태그. Flash 75ms, 실측 TTFB ~255ms | Starter 이상 |
| Typecast | Free 30k 크레딧/월, Lite $15/200k, Plus $280/4M, 최저 1k당 $0.07 | 캐릭터·감정 다양 | 유료 플랜 |
| Supertone | 베타 분당 $0.1. Starter 2,000 크레딧(~30분)~Pro 50,000(~800분) | 감정·연기 강점 | 유료, 출처 표기 불요 |
| CLOVA Voice | Premium 1,000자 단위, 무료량 있음, 단가 (확인 필요) | 발음 안정, 감정 제한 | NCP 약관 |
| OpenAI | tts-1 $15/1M자, tts-1-hd $30/1M자, gpt-4o-mini-tts ≈ $0.015/분 | 억양 외국인풍 | 가능 |
| Google Cloud TTS | Standard/WaveNet $4/1M자, Neural2 $16, Chirp 3 HD $30, Studio $160 | Chirp 3 HD 준수 | 가능 |
| 온디바이스 | 무료 | AVSpeechSynthesizer, Android TextToSpeech. 품질 낮음, 지연 0, 오프라인 | 가능 |

- 사전 생성 뱅크: 캐릭터 5종 × 대사 300~500개 = 2,500클립 ≈ 15~25만 자 → 일회성 $30~300. 지연 0, 오프라인. 변수(거리·시간)는 숫자 클립 조합 또는 온디바이스 TTS
- 실시간 LLM+TTS: gpt-realtime-2.1 오디오 $64/1M 토큰 ≈ $0.077/분, mini ≈ $0.024/분. TTFB 300~600ms+LTE → <300ms 즉각 반응 부적합. 10만 MAU 월 수만 달러 → 이벤트·프리미엄 한정. LLM 배치 생성+사전 합성 "반동적 뱅크" 절충
- 공간음향: iOS AVAudioEnvironmentNode(HRTF)/PHASE. CMHeadphoneMotionManager는 러닝 중 요동 → 폰 heading 기준 패닝. Android 13+ Spatializer 또는 Oboe+Resonance Audio. 좌/우/후방 3구역 패닝+거리 감쇠+도플러+심박 연동 BGM 템포. 스피커 모노 폴백

### 백엔드/리더보드/부정행위

- Supabase: Free(500MB, 50K MAU), Pro $25/월(100K MAU 포함), Team $599. Postgres+PostGIS, Realtime, Edge Functions. 1만 DAU 기준 Firebase 대비 수 배 저렴
- Firebase: Firestore 무료 일 5만 읽기·2만 쓰기, Blaze 10만 건당 $0.06~0.18 (확인 필요), Functions 월 200만 호출 무료. 읽기 많은 리더보드 비용 급증
- PocketBase: SQLite 단일 바이너리, $5~20 VPS. 수평 확장 불가 → 프로토타입 전용
- 리더보드: 공식 코스(1/3/5km 고정) 타임어택 + 랜덤 코스 페이스 정규화. 축: 코스×난이도(치와와→시바→늑대→사자)×기간×범위. Postgres 머티리얼라이즈드 뷰, 10만 MAU 이상 Redis Sorted Set. 검증 통과 기록만 공개
- 부정행위 다층
  1. 클라이언트: Location.isMock(API 31+), 루팅/Magisk/Xposed, Play Integrity(SafetyNet 2025-01 종료), App Attest/DeviceCheck, 탈옥 탐지. 캐주얼 스푸핑 60~80% 차단
  2. 서버 물리: 속도 상한(지속 >7~8 m/s, 순간 >12 m/s), 순간이동, accuracy 분포, 고도 정합, 케이던스/심박 vs GPS 속도, IP/셀 타워 정합, Raw GNSS 존재 여부
  3. 리플레이: 트랙+세션 시드로 적 AI 재시뮬레이션(결정론적 → KMP 공유). nonce·서명 타임스탬프, 트랙 해시 재사용 탐지
  4. 제재: 경고 → 리더보드 제외 → 정지. 이의제기 채널

### 비용 시나리오

- 가정: 인당 월 8세션, 30분, 세션당 경로 3회·지도 1회, 트랙 ~50KB, 실시간 LLM 제외

| 항목 | 1천 MAU | 1만 MAU | 10만 MAU |
|---|---|---|---|
| 지도(카카오) | 0원 | 0원 | 0원 |
| Mapbox 대안 | $0 | $0 | $300 |
| 경로 TMAP | 0원 | ≈210만원 | ≈2,400만원 |
| 경로 자체 호스팅 | $0~40 | $40~100 | $150~300 |
| TTS 뱅크 | 일회성 $30~300 + 월 $10~50 | 동일 | 동일 |
| 실시간 LLM(옵션) | $384~1,232 | $3.8K~12.3K | $38K~123K |
| Supabase | $0 | $35~75 | $300~800(Firebase $500~1,500) |
| 검증 컴퓨트 | 포함 | ~$10 | $20~100 |
| 합계(권장) | ≈$0~50 | ≈$100~250 | ≈$800~1,800(+Mapbox $300) |

- 지배 변수: 경로 자체 호스팅 전환 시점(1만 MAU 이전), 실시간 음성 여부(프리미엄 전용), 트랙 저장 정책

### PRD 질문에 반영할 시사점

- 코어 루프: 지도 위 AR(2.5D 맵+레이더+공간음향). 카메라 AR은 정지 이벤트 한정
- 구글맵 한국 도보 경로 의존 배제
- 경로: TMAP으로 MVP → 1만 MAU 전 Valhalla/OSRM 자체 호스팅
- 기본 UX: 화면 꺼짐+오디오 전제. 배터리·안전 동시 해결
- 워치: 폰 필수+컴패니언(HUD/심박/햅틱). 단독 모드 후순위, 가민 최후순위
- 글래스: HUD 채널 추상화. 1차 Even G2
- 음성: 사전 생성 뱅크+온디바이스 TTS. 실시간 LLM은 프리미엄
- 부정행위: 결정론적 시뮬레이션+서버 리플레이 검증 → KMP 공유 코드
- 백엔드: Supabase(PostGIS)

### 출처

- https://www.khan.co.kr/article/202511111326001
- https://zdnet.co.kr/view/?no=20260227120235
- https://www.theinvestor.co.kr/article/10684278
- https://www.jurist.org/news/2026/02/south-korea-conditionally-approves-googles-high-precision-map-data-export/
- https://techcrunch.com/2026/02/27/south-korea-opens-the-door-to-let-google-maps-operate-fully
- https://beforekorea.com/does-google-maps-work-in-korea-2026/
- https://www.seoulz.com/google-maps-korea/
- https://virtualstreets.org/index.php/2026/03/13/google-street-view-may-soon-cover-moldova-and-south-korea/
- https://en.wikipedia.org/wiki/Google_Street_View_in_Asia
- https://www.ncloud.com/support/faq/prod/2828
- https://api.ncloud-docs.com/docs/application-maps-overview
- https://www.ncloud-forums.com/topic/99/
- https://guide.ncloud-docs.com/docs/en/maps-direction15-api
- https://api.ncloud-docs.com/docs/en/ai-naver-mapsdirections-driving
- https://pub.dev/packages/flutter_naver_map
- https://developers.kakao.com/docs/ko/kakaomap/common
- https://devtalk.kakao.com/t/api/151036
- https://devtalk.kakao.com/t/topic/149092
- https://pub.dev/packages/kakao_map_sdk
- https://developers.kakaomobility.com/affiliate/walking/directions
- https://devtalk.kakao.com/t/directions-api-navigation-api/147260
- https://openapi.sk.com/products/detail?linkMenuSeq=45
- https://openapi.sk.com/products/calc?svcSeq=4&menuSeq=5
- https://tmapapi.tmapmobility.com/
- https://docs.mapbox.com/accounts/guides/pricing/
- https://www.woosmap.com/blog/mapbox-pricing
- https://download.geofabrik.de/asia/south-korea.html
- https://lists.openstreetmap.org/pipermail/talk-ko/2017-February/000262.html
- https://www.vworld.kr/dev/v4dv_baseguide_s001.do
- https://vworld.kr/dev/v4dv_wmtsguide_s001.do
- https://github.com/valhalla/valhalla
- https://www.pistack.xyz/posts/2026-04-25-graphhopper-vs-osrm-vs-valhalla-self-hosted-routing-engines-guide-2026/
- https://mapsi.dev/developers/routing-engine-comparison
- https://developer.android.com/develop/sensors-and-location/location/battery
- https://developer.android.com/develop/background-work/services/fgs/service-types
- https://developer.apple.com/documentation/corelocation/cllocationupdate/liveupdates(_:)
- https://maddevs.io/blog/reduce-gps-data-error-on-android-with-kalman-filter-and-accelerometer/
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9788430/
- https://navi.ion.org/content/68/4/727
- https://developers.google.com/ar/develop/geospatial
- https://developers.google.com/ar/develop/unity-arf/geospatial/check-vps-availability
- https://www.auganix.org/ar-news-nianctic-scaniverse-vps-2-0/
- https://www.geekwire.com/2026/from-pokemon-go-to-physical-ai-niantic-spatial-unveils-its-global-3d-mapping-platform/
- https://community.nianticspatial.com/t/pricing-changes-of-lightship/5134
- https://roadtovr.com/niantic-webar-platform-8th-wall-open-source/
- https://unity.com/products/pricing-updates
- https://www.cgchannel.com/2024/09/unity-scraps-controversial-runtime-fee-but-raises-prices/
- https://pub.dev/packages/flutter_background_geolocation
- https://docs.transistorsoft.com/purchase/
- https://www.thedroidsonroids.com/blog/flutter-vs-react-native-comparison
- https://developer.apple.com/documentation/HealthKit/running-workout-sessions
- https://asciiwwdc.com/2017/sessions/713
- https://developer.apple.com/forums/thread/726402
- https://developer.android.com/health-and-fitness/health-services/active-data
- https://developer.android.com/training/wearables/apps/location-detection
- https://support.apple.com/en-us/125093
- https://www.apple.com/newsroom/2025/09/introducing-apple-watch-ultra-3/
- https://developer.garmin.com/connect-iq/connect-iq-basics/app-types/
- https://www.garmin.com/en-US/blog/developer/improve-your-app-performance/
- https://developers.meta.com/blog/build-for-display-glasses/
- https://www.ghacks.net/2026/05/18/meta-opens-ray-ban-display-glasses-to-third-party-developers-through-wearables-toolkit/
- https://www.uploadvr.com/meta-wearables-device-access-toolkit-public-preview/
- https://techcrunch.com/2026/01/06/meta-pauses-international-expansion-of-its-ray-ban-display-glasses/
- https://about.fb.com/news/2026/05/ray-ban-meta-and-oakley-meta-officially-launch-in-korea/
- https://9to5google.com/2026/03/26/even-realities-even-hub-apps-and-better-conversate-mode/
- https://www.heise.de/en/news/Even-Realities-G2-New-smart-glasses-with-larger-display-and-smart-ring-11076939.html
- https://developer.android.com/develop/xr/catalyst
- https://9to5google.com/2026/05/19/google-samsung-android-xr-glasses-styles-release-date/
- https://roadtovr.com/google-android-xr-developer-program-free-ar-glasses/
- https://www.xreal.com/us/blog/project-aura-google-io-2026
- https://elevenlabs.io/pricing
- https://bigvu.tv/blog/elevenlabs-pricing-2026-plans-credits-commercial-rights-api-costs/
- https://elevenlabs.io/blog/meet-flash
- https://typecast.ai/pricing/api/
- https://www.supertone.ai/en/api
- https://www.supertone.ai/en/work/supertone-play-ai-voice-faq-eng
- https://www.ncloud.com/product/aiService/clovaVoice
- https://texttolab.com/blog/google-cloud-tts-pricing
- https://texttolab.com/blog/openai-tts-pricing
- https://www.layer3labs.io/guides/openai-realtime-api-pricing
- https://picovoice.ai/blog/text-to-speech-latency/
- https://www.gamesforchange.org/games/zombies-run/
- https://toolradar.com/blog/supabase-pricing-2026
- https://leaper.dev/blog/supabase-vs-firebase-2026
- https://blog.back4app.com/firebase-pricing/
- https://forestvpn.com/en/blog/gaming/how-does-niantic-detect-spoofing/
- https://theappninjas.com/blog/gps-spoofing-detection-2026/
- https://wappblaster.com/blog/anti-fake-gps-tech-explained/

<a id="legal_safety"></a>
## 법률 · 안전 · 정책 리서치

### 위치정보법
- 법률 자문 아님. 출시 전 변호사·방미통위·게임물관리위원회 확인 필요
- 위치기반서비스사업: 방송미디어통신위원회(구 방송통신위원회) 신고제(제9조). 개인위치정보사업은 등록제(2021.10 시행), 사물위치정보사업은 신고제
- 소상공인·1인 창조기업: 사업 개시 후 1개월까지 신고 면제, 이후 "소상공인등의 위치기반서비스사업 신고" 필요(2018년 개정, 확인 필요). 스토어 공개 전후 신고 완료
- 미신고 영업: 3년 이하 징역 또는 3천만 원 이하 벌금(제40조, 확인 필요)
- 절차: 방미통위 전자민원센터(emsit.go.kr) 온라인. 서류는 사업계획서, 설비 확인 서류, 기술적·관리적 보호조치 계획(명칭·처리기간 확인 필요). 수수료 없음으로 안내(확인 필요), 준비 1~2주
- 변경신고: 상호·소재지·사업 종류·주요 설비 변경 시. 향후 기능을 사업계획서에 미리 기재(확인 필요)
- 운영 의무
  - 위치기반서비스 이용약관 별도 작성·동의(제12조·제18조·제19조)
  - 제3자 제공 시 제공받는 자·일시·목적 즉시 통보(제19조 제3항). 리더보드·친구 위치 공유 해당
  - 수집·이용·제공사실 확인자료 자동 기록·보존(제16조 제2항), 실무상 6개월 이상(확인 필요). 목적 달성 후 확인자료 외 즉시 파기
  - 기술적·관리적 보호조치(제16조 제1항), 위치정보 관리책임자 지정
  - 8세 이하 아동·피성년후견인·중증 장애인: 보호의무자 동의(제26조)
- 개정: 2024.4.23 시행령 개정. 2025.10.1 법 개정 시행(방미통위 명칭 변경, 확인 필요). 2026.2.10 시행령 개정(대통령령 제36084호) 세부 확인 필요. 2026.9 기준 신고 의무 유효

### 개인정보보호법
- 위치 이력: 개인위치정보 + 개인정보 이중 적용. 집·직장 노출 고위험(2018 Strava 히트맵 군 기지 노출)
- 심박수·체중: 제23조 건강정보(민감정보) 가능성 높음, 별도 분리 동의. 걸음수·거리는 견해 갈림(확인 필요)
- 제15조 동의: 항목·목적·보유기간·거부권 고지. 선택 항목은 분리 동의
- 1년 미이용자 유효기간제 2023.9.15 폐지, 자체 보유기간 명시. 원시 GPS 트랙 90일 후 요약치만, 확인자료 로그 12개월, 안전 고지 동의 로그 3~5년(확인 필요)
- 앱 접근권한(정보통신망법 제22조의2): 필수/선택 구분 고지, 선택 거부 시 기본 기능 제공
- 이동형 영상정보처리기기(제25조의2): 업무 목적 촬영 시 촬영 사실 표시. 사업자가 영상 수집·분석 시 의무(확인 필요). AR 카메라는 온디바이스 실시간 처리·미저장 원칙
- 2026.2.12 국회 통과 개정안: 유출 통지 확대, CPO 책임 강화, 매출액 10% 과징금 상한
- 만 14세 미만: 법정대리인 동의 + 확인 의무(제22조의2), 확인은 휴대전화 문자·신용카드·본인인증. 초기 버전 만 14세 이상만 가입, 생년월일 입력 + 위반 시 계정 삭제

### 게임산업법/등급분류
- 제2조 제1호 게임물 정의에 "운동 효과" 포함. 게임물 판단 가능성 매우 높음
- 등급분류 면제(제21조 제1항 단서): 교육·공익·시험용·비영리. 구독·광고·인앱결제 시 면제 아님
- 자체등급분류: Google Play·App Store·갤럭시스토어·원스토어가 자체등급분류사업자. IARC 설문으로 전체/12세/15세 유통, 게임물관리위원회 별도 신청 불필요(사후관리 권한 보유)
- 2025.10.9 시행 개정: 청소년이용불가도 민간(GCRB) 분류, 내용수정신고 간소화
- 표시 의무(제33조): 등급·내용정보·상호·제작자
- 확률형 아이템 확률 표시(제33조 제2항, 2024.3.22 시행). 제외: 3년 연평균 매출 1억 원 이하 중소기업(시행령 제19조의2). 2025.8.1 시행: 최대 3배 손해배상·입증책임 전환. 초기 미도입 권장
- 과몰입 예방조치(제12조의3): 실명·연령 확인, 청소년 법정대리인 동의, 게임시간 선택제, 주의문구. 소규모 사업자 일부 면제(확인 필요)
- 청소년보호책임자(정보통신망법 제42조의3): 일평균 이용자 10만 명 또는 매출 10억 원 이상 시

### 앱 마켓 정책
| 항목 | Apple | Google Play |
|---|---|---|
| 위치 | 2.5.4 백그라운드는 의도된 목적만, 5.1.1 purpose string 구체화, 5.1.5 | 2021.1부터 백그라운드 위치 사전 승인, prominent disclosure + 권한 분리, 포그라운드 서비스(type=location) 권장 |
| 최근 변경 | 연령등급 개편(2025.7) 13+/16+/18+, 2026.1.31까지 새 설문 | 2026.4.15: 정밀 위치 정당화 선언, 지오펜싱은 Geofence API, 광고·분석 목적 위치 금지 |
| 건강 | 5.1.3 HealthKit 광고·마케팅 금지, iCloud 저장 금지 | 건강 앱 선언서(2025.1.22 필수, 2025.3.5 집행). "피트니스 기반 게임" 승인 사례. Google Fit 2026년 말 종료, Health Connect |
| 데이터 공유 | 5.1.2 제3자 AI(TTS/LLM) 전송 시 명시 고지·허락 | 건강 데이터 무단 소셜 공유 금지 |
| 아동·UGC | 5.1.4 미성년 위치 수집 시 아동 프라이버시. 1.2 필터링·신고·차단·24시간 조치. 1.4 물리적 위해 유도 시 거절 | UGC 정책 동일 |
- 원스토어: 자체등급분류사업자, IARC 등급, 위치 사용 시 처리방침·약관 링크, 결제 SDK 별도 심사

### 러닝 안전 설계
- 보행 중 스마트폰 사용률 33%, 사고 77%가 40대 이하. 이어폰 경적 미인지 사고 빈번. Pokémon GO 절벽 추락 사망·사유지 침입 소송
- 지자체 러닝크루 규제(2024~2025): 서초구 5인 이상 금지·2m 간격, 송파구 3인 이상 자제, 성북구 한 줄 달리기
- Zombies, Run! 벤치마크: 오디오 퍼스트, 경로 비강제(직전 30초 평균 대비 +20%를 60초 유지 시 탈출), Chase 끄기 토글, 트레드밀 모드
- 우리 컨셉("지정 위치까지" + "적 회피") = Pokémon GO형 리스크. 설계 원칙
  - 목적지는 사전 승인 코스 경유지만, 실시간 재라우팅 없음. 회피는 방향 전환 아닌 페이스 상승만(기본값)
  - 화면 UI는 정지 상태에서만. 추격 중 화면 잠금, 시작 전 5초 음성 카운트다운 + 워치 햅틱
  - 차도·횡단보도·철도 근처 추격 자동 일시정지. 야간·우천·폭염 특보 시 강도 하향(기상청 API)
  - 속도 캡: 최근 최고 페이스 110% 초과 요구 금지. 심박 상한(예: 최대심박 90%) 초과 시 종료, "의료 조언 아님" 고지
- 약관·책임
  - 약관규제법 제7조: 고의·중과실 면책 조항 무효. 포괄 면책 실효성 낮음. 책임 조항에 "고의 또는 중대한 과실이 없는 한" 단서, 이용자 준수사항(교통법규·사유지·금지구역) 별도 조항
  - 민법 제750조, 제조물책임법(설계·표시상 결함) 청구 가능. 위험 장소 유도 입증 시 사업자 과실
  - 매 세션 안전 고지 + 동의 로그(일시·앱 버전·문안 버전 ID·기기 ID)
  - 야간 모드, 오픈이어 권장, 긴급전화(112/119) 버튼, 영업배상책임보험(연 수십만 원~, 확인 필요)

### 금지/위험 구역
| 구역 | 근거 | 대응 |
|---|---|---|
| 군사기지·군사시설 보호구역 | 군사기지 및 군사시설 보호법 제9조 촬영·묘사·녹취·측량 금지. 3년 이하 징역 또는 3천만 원 이하 벌금. 진해 드론 촬영 벌금 100만 원 판례 | 지오펜스, AR 카메라 비활성화, 적·목적지 미배치, 경로 마스킹, 300m 버퍼 |
| 국가보안·국가중요시설(공항·항만·발전소·정수장) | 보안업무규정 제32조, 통합방위법 제21조, 항공보안법 | 반경 지오펜스, 촬영 억제 |
| 학교·유치원 | 학교 출입 관리, 교육환경보호구역 | 부지 내 미배치, 등하교 시간대 억제 |
| 사유지 | 형법 제319조 주거·건조물 침입 | 공공 보행로·공원·하천변 화이트리스트 |
| 도시공원 야간 | 도시공원법·지자체 조례 | 야간 이벤트 축소 |
| 자연공원 | 자연공원법 시행령 제26조 야간 산행 금지, 과태료 | 주간에도 미배치 |
| 차도·횡단보도·철도 | 도로교통법 제8조·제10조, 철도안전법 | 건널목 반경 추격 자동 정지 |
| 접경지·민통선 | 군사기지법·민통선 출입 통제 | 완전 제외 |
- 데이터 소스: 토지이음, 국가공간정보포털·공공데이터포털, 학교알리미, OSM, 국토지리정보원, 국립공원공단. 군사시설보호구역 경계 공개 범위 확인 필요
- 판정은 온디바이스. 진입 시 추격 정지, AR 카메라 종료, 목적지 재배치, 경로 마스킹. 비저장 실시간 프리뷰의 "촬영" 해당 여부 확인 필요

### 접근성
- 장애인차별금지법 제21조·시행령(2023.1.28 시행). 모바일 앱 정당한 편의: 2024.1.28 공공·교육·의료·금융, 2024.7.28 문화·예술·100인 이상, 2025.1.28 관광·100인 미만(확인 필요). 2026년 현재 소규모 사업자도 대상
- 지침: 과기정통부 「모바일 애플리케이션 접근성 지침」, KS 표준. 대체 텍스트, 색 무관 인식(적/아군 아이콘·패턴·진동 병행), 색 대비, 자막, 컨트롤 크기
- 시각: 음성·햅틱 중복. 청각: 워치 진동·화면 플래시·자막. 고령자: 큰 글씨, 심박 상한 경고. "의료 목적 아님" 문구로 식약처 의료기기 해당성 논란 회피

### AI 음성 관련
- 부정경쟁방지법 제2조 제1호 타목(2022.6 시행): 널리 인식된 타인의 성명·초상·음성 무단 사용은 부정경쟁행위. 유명 성우·연예인 유사 합성 금지
- 저작권법 실연자 권리: 복제·전송권(AI 학습 포함), 성명표시·동일성유지권. 녹음 계약서에 AI 학습·합성 범위·기간·대가 명시. 문체부 2026년 성우 표준녹음계약서 추진
- 옵션: 상용 TTS(ElevenLabs·Typecast·Supertone) 상업 라이선스 + 실존 인물 복제 금지 정책 준수
- 인공지능기본법(2026.1.22 시행) 제31조: 생성형 AI 사실 사전 고지, 결과물 AI 생성 표시, 실제와 구분 어려운 음향·영상 명확 표시. 창작물 예외(제31조 제3항 단서, 확인 필요)
- 위반: 시정명령 후 불이행 시 3천만 원 이하 과태료. 시행 초기 1년 이상 계도기간
- 대응: 앱 소개·설정·크레딧에 "일부 음성은 AI로 생성되었습니다" 고지. 실제 사람(코치·아나운서) 모사 회피

### 리더보드/UGC 의무
- 닉네임 필터링 직접 의무 조항 없음. 정보통신망법 제44조의7·제44조의2 임시조치, 청소년보호법, Apple 1.2/Google Play UGC 정책이 사실상 의무. 금칙어 DB + 운영정책
- 위치 결합 리더보드 = 개인위치정보 제3자 제공. 위치정보법 제19조 동의·통보 + 개인정보보호법 공개 동의. 기본 비공개, opt-in, 집·직장 프라이버시 존 마스킹, GPS 원본 비공개
- 야간 기록 분리 또는 안전 인증 코스만 랭킹. 청소년 실명·위치 노출 최소화
- 신고, 24시간 내 검토, 삭제/제재, 이의신청. 운영정책 별도 공개
- 이용자 음성 UGC: 도용·딥페이크 위험, 초기 제외

### PRD 질문에 반영할 시사점
- 이동 지시·회피·화면: 목적지를 사전 확인 코스 경유지로 한정하는가, 페이스 상승만으로 판정하는가, Chase 끄기 토글 기본 제공, 오디오·햅틱만으로 플레이 가능한가
- 연령·건강: 만 14세 이상 가입 제한 여부, 심박수 수집 여부와 민감정보 분리 동의, Health Connect 설계
- 수익화: 확률형 아이템 배제 여부(정액 구매·도전과제 보상), 매출 1억 원 기준 모니터링
- 공포·폭력 수위: 12세 이용가 목표, 유혈 없는 연출 기준
- AR 카메라·지오펜스: 온디바이스 미저장, 금지 구역 자동 지도 모드 전환, 지오펜스 DB 범위·버퍼
- 일정·비용: 사업자 등록·통신판매업 신고 출시 1~2개월 전, 약관 3종 변호사 검토 수십~수백만 원, 스토어 심사 수일~2주, 보험 연 수십만 원~

### 출처
- https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=277359
- https://www.gov.kr/mw/AA020InfoCappView.do?HighCtgCD=A09001&CappBizCD=15701000085
- https://www.emsit.go.kr/cp/cv/Cp1440000_0182_01Reg.do
- https://www.catchsecu.com/archives/14060
- https://www.gov.kr/mw/AA020InfoCappView.do?HighCtgCD=A09001&CappBizCD=15701000086
- https://www.lbsc.kr/front/content/contentViewer.do?contentId=CONTENT_0000091
- https://www.kmcc.go.kr/user.do?mode=view&page=A02060600&dc=K02060600&boardId=1080&cp=1&boardSeq=31228
- https://www.gov.kr/portal/service/serviceInfo/157010000012
- https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=1702&ccfNo=2&cciNo=1&cnpClsNo=3
- https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=1702&ccfNo=2&cciNo=1&cnpClsNo=2
- https://www.kakao.com/policy/location?lang=ko
- https://www.kimchang.com/ko/insights/detail.kc?sch_section=4&idx=24893
- https://www.moleg.go.kr/mpbleg/mpblegInfo.mo?mid=a10402020000&mpb_leg_pst_seq=130879
- https://www.kmcc.go.kr/user.do?boardId=1113&boardSeq=47343&dc=K00000200&mode=view&page=A05030000
- https://www.engadget.com/2018-03-13-after-exposing-secret-military-bases-strava-restricts-data-visi.html
- https://moleg.go.kr/lawinfo/lawAnalysis/nwLwAnList?csSeq=418282&rowIdx=65
- https://www.skshieldus.com/blog-security/security-trend-idx-20
- https://www.lawtimes.co.kr/news/articleView.html?idxno=217245
- https://datalaw.kr/guides/pipa-2026-amendment/
- https://svwvs.com/blog/personal-data-protection-act-2026/
- https://www.privacy.go.kr/front/contents/cntntsView.do?contsNo=94
- https://eiec.kdi.re.kr/policy/materialView.do?num=189815
- https://www.law.go.kr/LSW/lsInfoP.do?lsId=010196
- https://www.moleg.go.kr/mpbleg/mpblegInfo.mo?mid=a10402020000&mpb_leg_pst_seq=131183
- https://casenote.kr/%EB%B2%95%EB%A0%B9/%EA%B2%8C%EC%9E%84%EC%82%B0%EC%97%85%EC%A7%84%ED%9D%A5%EC%97%90_%EA%B4%80%ED%95%9C_%EB%B2%95%EB%A5%A0/%EC%A0%9C21%EC%A1%B0
- https://www.gamemeca.com/view.php?gid=1760187
- https://www.inews24.com/view/1971581
- https://www.hwawoo.com/kor/insights/newsletter/12852?currentPage=1
- https://onestore-dev.gitbook.io/dev/docs/review/one-store-review-guideline
- https://toss.im/apps-in-toss/blog/self-rated_game_distribution
- https://m.korea.kr/multi/visualNewsView.do?newsId=148924522
- https://www.yulchon.com/ko/resources/publications/newsletter-view/41159/page.do
- https://www.digitaltoday.co.kr/news/articleView.html?idxno=580719
- https://www.lawtimes.co.kr/LawFirm-NewsLetter/210245
- https://www.law.go.kr/LSW//lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=1000924527&lsId=000030&print=print
- https://developer.apple.com/app-store/review/guidelines/
- https://developer.apple.com/news/?id=ks775ehf
- https://ptkd.com/journal/app-store-age-ratings-2025-update
- https://niantic.helpshift.com/hc/en/6-pokemon-go/faq/1797-niantic-player-guidelines/
- https://support.google.com/googleplay/android-developer/answer/9799150?hl=en
- https://developer.android.com/develop/sensors-and-location/location/background
- https://support.google.com/googleplay/android-developer/answer/16926792?hl=en
- https://support.google.com/googleplay/android-developer/answer/17033915?hl=en
- https://asoworld.com/blog/april-2026-google-play-policy-updates-key-changes-for-contacts-permissions-location-privacy-account-transfers/
- https://developer.android.com/health-and-fitness/health-connect/publish
- https://support.google.com/googleplay/android-developer/answer/12991134?hl=en
- https://asoworld.com/blog/google-play-health-connect-policy-update-march-2025/
- https://dev.onestore.net/
- https://www.mdpi.com/2076-3417/15/13/7430
- https://m.korea.kr/briefing/pressReleaseView.do?newsId=156168146
- https://kidd.co.kr/news/188521
- https://mbiz.heraldcorp.com/article/2197838
- https://www.jbyonhap.com/news/articleView.html?idxno=319617
- https://namu.wiki/w/Pok%C3%A9mon%20GO/%EC%82%AC%EA%B1%B4%20%EC%82%AC%EA%B3%A0
- https://www.newsis.com/view/NISX20241008_0002912290
- https://www.imaeil.com/page/view/2024100218532035891
- https://www.androidpolice.com/2012/06/26/review-zombies-run-is-a-fantastic-app-as-long-as-you-like-working-out-more-than-you-like-zombies/
- https://zombiesrun.fandom.com/wiki/Player%27s_Guide
- https://support.zombiesrungame.com/hc/en-us/articles/10447200523549-Zombies-Run-FAQ
- https://www.commonsensemedia.org/app-reviews/zombies-run
- https://www.strava.com/legal/terms
- https://www.bikeradar.com/news/strava-2026-policies
- https://www.tldrlegal.com/license/pokemon-go-terms-of-service
- https://www.law.go.kr/%EB%B2%95%EB%A0%B9/%EA%B5%B0%EC%82%AC%EA%B8%B0%EC%A7%80%20%EB%B0%8F%20%EA%B5%B0%EC%82%AC%EC%8B%9C%EC%84%A4%20%EB%B3%B4%ED%98%B8%EB%B2%95/%EC%A0%9C9%EC%A1%B0
- https://www.legaltimes.co.kr/news/articleView.html?idxno=63985
- https://www.sedaily.com/article/13450737
- https://www.law.go.kr/%EB%B2%95%EB%A0%B9/%EB%B3%B4%EC%95%88%EC%97%85%EB%AC%B4%EA%B7%9C%EC%A0%95
- https://www.pressian.com/pages/articles/2026021116582875927
- https://www.knps.or.kr/portal/main/contents.do?menuNo=8000377
- https://www.korea.kr/briefing/policyBriefingView.do?newsId=148718636
- https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027&act=view&list_no=375590&tag=&nPage=1
- https://theindigo.co.kr/archives/47241
- https://www.khan.co.kr/national/court-law/article/202212262109015
- https://blog.sugar.legal/ai-law-publicity-rights
- https://v.daum.net/v/pSyZsEd8lI?f=p
- https://www.nepla.ai/nest/@xxWIvIKZwKx7/insight/%EC%84%B1%EC%9A%B0-%EB%A7%A4%EC%A0%88%EA%B3%84%EC%95%BD-%EB%8F%85%EC%86%8C%EC%A1%B0%ED%95%AD%EA%B3%BC-ai-%EC%9D%8C%EC%84%B1-%EB%B3%B5%EC%A0%9C%EC%97%90-%EB%8C%80%EC%9D%91%ED%95%98%EB%8A%94-%EB%B2%95%EB%A5%A0-%EC%A0%84%EB%9E%B5-%EB%82%B4-%EB%AA%A9%EC%86%8C%EB%A6%AC%EA%B0%80-%EB%82%98%EB%A5%BC-%EC%8B%A4%EC%A7%81%EC%8B%9C%ED%82%A8%EB%8B%A4%EB%A9%B4-7g6w93pvnojp
- https://view.asiae.co.kr/article/2026080814280231461
- https://www.daeryunlaw.com/trend/10341
- https://bh-law.kr/ko/news/column/ai-content-labeling-obligation-guide
- https://peekaboolabs.ai/blog/ai-basic-law-guide
- https://buddyboss.com/docs/app-store-guideline-1-2-safety-user-generated-content/
- https://www.plaync.com/policy/operation/bns2
- https://www.kakao.com/ko/location
- https://toss.im/apps-in-toss/blog/game_rating_classification

