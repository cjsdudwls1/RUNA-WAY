# android/ · 네이티브 앱 스캐폴드 (미빌드)

- 이 환경에는 Android SDK가 없고 Google Maven이 차단되어 컴파일하지 못했다. Android Studio에서 열어 빌드할 것
- `:core`(../core)를 의존. 코어는 Python 시뮬과 골든 테스트로 검증됨
- 현재 포함: Gradle 설정, 매니페스트(위치 포그라운드 서비스), LocationSource(GPS/리플레이), RunEngine(틱 단위 세션)
- 미포함: UI(Compose 화면), RunService 본문, 오디오. 빠른 반복은 web/ 프로토타입에서 먼저 진행
