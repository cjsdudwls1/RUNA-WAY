# web/ · 폰에서 바로 쓰는 앱

- 단일 HTML. 설치 없이 링크로 실행
- 빌드: `python3 web/build.py` → `dist/runaway.html`, `docs/app/`
- 화면: 첫 화면(일반런/빌드업/인터벌과 값, 출발) → 주행 → 결과. 공포 모드 하나. 명세는 docs/prd/17-modes.md
- 규칙: game.js. `node web/test_game.mjs`
- 소리: sound.js. web/sounds/<id>_<번호>.mp3가 있으면 녹음, 없으면 합성. 검수표 docs/prd/18-horror-sounds.md
- 위치: 실주행 GPS(watchPosition, Wake Lock) / 실내 데모(녹화 주행 10배속). `?src=demo&demoMs=10`이면 100배속
- GPS 거리 계산(TrackBuilder)은 core.js. Python 시뮬·Kotlin 코어와 골든 테스트로 일치 확인: `node web/test_golden.mjs`
- 제약: 화면 꺼지면 GPS 멈춤. 백그라운드 없음

## QA

```
python3 web/build.py && NODE_PATH=$(npm root -g) node web/qa.mjs
```

- docs/app/을 로컬에 띄워 헤드리스 크롬으로 돈다. 일반런·빌드업·인터벌 실내 데모 완주, 말 없음, 녹음 재생, 검수 화면, GPS 모드(위치 에뮬레이션), 아이폰 에뮬레이션
- 규칙: `node web/test_game.mjs`, 골든 테스트: `node web/test_golden.mjs`
- 검수용 WAV: `NODE_PATH=$(npm root -g) node web/render_sounds.mjs` → web/dist/sounds/

## 배포

```
web/deploy.sh "커밋 메시지"
```

- `build.py`로 `docs/app/`을 만들고, 그 내용을 `gh-pages` 브랜치 루트에 올린다
- 주소: https://cjsdudwls1.github.io/RUNA-WAY/ (경로는 대소문자를 구분한다. 소문자는 404)
- 주소를 바꾸려면 `build.py`의 `SITE` 한 줄만 고친다. 공유 카드, OG, 매니페스트가 전부 따라간다
- 방문자 집계는 `build.py`의 `COUNTER`에 goatcounter 코드를 넣으면 켜진다
