# 러너웨이 M0 · GPX 리플레이 시뮬레이터

- 밖에 나가지 않고 판정·상태 머신·피로 모델을 검증하는 도구
- 코어(enemy, threat, session)는 정수 연산, 고정 틱 1Hz, 결정론. Kotlin 이식 대상
- 입력: GPX(실주행 또는 합성). 출력: 타임라인, 요약, CSV

## 사용

```
cd sim
python3 -m runaway_sim.make_samples                     # 합성 GPX 5종 생성 → samples/
python3 -m runaway_sim.replay samples/steady10.gpx --animal cheetah --course 5000
python3 -m runaway_sim.replay samples/intervals.gpx --animal wolf --csv out.csv
python3 -m runaway_sim.calibrate                        # 30분 평균 vs 목표 확인
python3 -m runaway_sim.calibrate --write                # 보정값을 data/animals.json에 기록
./run_tests.sh
```

## 실주행 GPX

- 삼성헬스, 스트라바, 가민 등에서 GPX 내보내기
- `<extensions><accuracy>` 또는 `hdop`가 있으면 정확도 보정에 사용. 없으면 8m로 가정
- `samples/` 에 넣고 위 명령으로 재생

## 구조

| 파일 | 역할 |
|---|---|
| data/animals.json | 동물 25종 파라미터. 출처는 docs/prd/04-animal-data.md |
| runaway_sim/enemy.py | 상태 머신(배회/스프린트/지침/회복/냄새잃음) + 피로 모델 |
| runaway_sim/threat.py | 위협 게이지, 히스테리시스, 정확도 보정, 피격 |
| runaway_sim/session.py | 워밍업, 쿨다운, 자동 일시정지, 페널티, 결과 |
| runaway_sim/gpx.py | GPX 파싱, 1Hz 리샘플, 게이트 필터 |
| runaway_sim/synth.py | 합성 트랙(노이즈, 도심 협곡, 신호 소실, 신호등 정지) |
| runaway_sim/calibrate.py | 30분 평균 보정 |
| tests/ | 단위 테스트. M0 통과 기준 포함 |

## 모델 가정 (PRD 수치 합의와 동일)

- 위협 진입 30m / 이탈 50m, 4초 충전, 2배속 감소
- 정확도 25m 초과 반속, 40m 초과 동결 + 적 정지
- 피격 +30초, 적 200m 후방 재배치, 3초 무적, 3회 실패
- 워밍업 3분(적은 100m 안으로 못 들어옴), 쿨다운 코스 87% 이후
- 정지 8초 자동 일시정지, 누적 3분 초과분은 시간에 포함
- 적은 플레이어 궤적을 1차원으로 추종. gap = 뒤처진 호길이
