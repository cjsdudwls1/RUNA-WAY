# web/ · 폰에서 바로 쓰는 프로토타입

- 단일 HTML. 설치 없이 링크로 실행. 수정하면 같은 링크에 즉시 반영
- 코어(core.js)는 Python 시뮬·Kotlin 코어와 골든 테스트로 일치 확인: `node test_golden.mjs`
- 빌드: `python3 gen_animals.py && python3 build.py` → `dist/runaway.html`
- 화면: 관제실 레이더(A안). 헤딩업, 궤적, 적 열원(상태별 색), 위협 반경 30m, 감지 반경
- 소리: Web Audio 합성(심박·으르렁·헐떡임·바람) + 브라우저 한국어 TTS 오퍼레이터 + 진동 + 점프 스케어
- 모드: 실주행 GPS(watchPosition, Wake Lock) / 리플레이 데모(합성 GPX 10배속, 실내 확인용)
- 제약: 화면 꺼지면 GPS 멈춤. 백그라운드 없음. 지도 타일 없음(카카오 키 후 추가)

## 배포

```
web/deploy.sh "커밋 메시지"
```

- `build.py`로 `docs/app/`을 만들고, 그 내용을 `gh-pages` 브랜치 루트에 올린다
- 주소: https://cjsdudwls1.github.io/RUNA-WAY/ (경로는 대소문자를 구분한다. 소문자는 404)
- 주소를 바꾸려면 `build.py`의 `SITE` 한 줄만 고친다. 공유 카드, OG, 매니페스트가 전부 따라간다
- 방문자 집계는 `build.py`의 `COUNTER`에 goatcounter 코드를 넣으면 켜진다
