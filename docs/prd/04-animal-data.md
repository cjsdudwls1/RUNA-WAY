# 추격자 동물 실측 데이터

- 조사일: 2026-09-09
- 목적: 티어별 적 파라미터를 실제 측정치에 근거해 설정
- 원칙: 수치는 앱 안에서 사용자에게 그대로 노출한다. 근거 없는 수치는 쓰지 않는다

## 1. 핵심 발견

- 인간은 스프린트에서 거의 모든 동물에 진다
- 인간은 지구력에서 거의 모든 동물을 이긴다
- 이유: 땀에 의한 체온 조절, 적은 체모, 긴 아킬레스건, 아치형 발
- 이것이 게임의 현실성 축이 되어야 함. 빠른 적을 속도로 이기는 게임이 아니라, 적의 스프린트를 버텨내는 게임

### 근거

- 지구력 사냥(persistence hunting): 칼라하리 수렵민이 쿠두를 잡는 데 2~5시간, 추격 거리 20~40km
- 실측 사례: 한 사냥꾼이 총 25.1km를 달려 쿠두를 잡았고, 최종 지점은 출발점에서 1.5km 거리
- Man versus Horse Marathon(웨일스, 34km): 2004년 Huw Lobb가 2시간 5분 19초로 말을 이김. 2007년 Florian Holzinger도 승리
- 치타는 최고 속도를 20~30초, 약 500m만 유지. 원인은 체온 상승보다 젖산 축적으로 보는 연구가 우세

## 2. 인간 기준값

| 구분 | 속도 | 비고 |
|---|---|---|
| 비운동 성인 조깅 | 8~10 km/h | |
| 취미 러너 지속 | 9~12 km/h | 우리 앱 기본 사용자 |
| 엘리트 마라톤 | 약 20 km/h | 42.2km 유지 |
| 훈련된 일반인 스프린트 | 약 32 km/h | 짧은 구간 |
| 우사인 볼트 순간 최고 | 44.72 km/h | 2009 세계선수권 100m, 60~80m 구간 |
| 우사인 볼트 100m 평균 | 37.58 km/h | 9.58초 기록 |
| 인간 이론적 한계 | 56~64 km/h | 근수축 속도 기반 추정 |

## 3. 동물 실측치

### 인간이 속도로 이길 수 있는 구간

| 동물 | 최고 속도 | 지속 | 비고 |
|---|---|---|---|
| 시추 | 약 9.6 km/h | 매우 짧음 | 가장 느린 견종 |
| 바셋하운드 | 약 8 km/h | 매우 짧음 | |
| 닭 | 14 km/h | 수 초 | |
| 치와와 | 8~16 km/h | 짧음 | 단두종은 호흡 제약 |
| 퍼그 | 8~16 km/h | 짧음 | 단두종 |

### 스프린트는 지지만 지구력으로 이기는 구간

| 동물 | 최고 속도 | 지속 | 비고 |
|---|---|---|---|
| 돼지 | 24 km/h | 짧음 | |
| 다람쥐 | 24 km/h | 매우 짧음 | |
| 일반 중형견 | 24~32 km/h | 중간 | |
| 불도그 | 최대 24 km/h | 짧음 | |
| 그레이하운드 | 최고 69 km/h, 경주 58~61 km/h | 300~500m | 순수 스프린터 |
| 유럽 산토끼 | 72 km/h | 짧은 반복 스프린트 | 지그재그 회피 |
| 치타 | 114 km/h | 20~30초 / 약 500m | 젖산 축적으로 정지 |

### 지구력까지 갖춰 인간이 고전하는 구간

| 동물 | 최고 속도 | 지속 | 비고 |
|---|---|---|---|
| 붉은캥거루 | 순간 70 km/h | 40 km/h로 약 2km, 순항 20~25 km/h | 18km/h 이상에서 에너지 효율이 동체급 최고 |
| 진돗개 | 약 40 km/h (확인 필요) | 2~3시간 (확인 필요) | 국내 출처가 블로그 수준. 1차 자료 필요 |
| 말 | 34km 코스에서 인간에게 패배 사례 있음 | 장거리 | Man vs Horse Marathon |

### 인간이 이길 수 없는 구간

| 동물 | 최고 속도 | 지속 | 비고 |
|---|---|---|---|
| 프롱혼(가지뿔영양) | 88 km/h | 64 km/h를 30분 이상 (확인 필요) | 속도와 지구력을 모두 갖춤. 큰 폐와 심장 |

## 4. 게임 반영 방식

### 적 파라미터 4종

기존의 "속도 배율" 단일 파라미터를 4개로 확장한다. 모두 실측치에서 유도한다.

| 파라미터 | 의미 | 데이터 출처 |
|---|---|---|
| 스프린트 속도 | 추격 개시 후 최고 속도 | 실측 최고 속도 |
| 스프린트 지속 | 그 속도를 유지하는 시간 | 실측 지속 시간 |
| 순항 속도 | 스프린트 후 유지 속도 | 실측 순항치 또는 최고 속도의 35~50% |
| 회복 시간 | 다시 스프린트하기까지 | 실측 없으면 지속 시간의 2~3배 |

### 실감 장치

- 세션 시작 화면에 실제 수치를 그대로 표시. 예: "치타 · 최고 114 km/h · 단 20초"
- 적이 지쳤을 때 근거를 음성으로 알림. 예: "젖산이 찼다. 지금이 기회다"
- 결과 화면에 오늘의 대결 요약. 예: "치타의 스프린트 3회를 모두 버텼다"
- 데이터 출처를 앱 내 도감에 표기

### 밸런스 문제

- 실제 속도를 절대값으로 쓰면 게임이 성립하지 않음. 치와와 16 km/h도 취미 러너 상한(12 km/h)보다 빠름
- 해결 방향은 결정 필요. 3안을 아래 PRD 미결정 항목에 올림

## 5. 출처

- [Liebenberg 2006, Persistence Hunting by Modern Hunter-Gatherers](https://cybertracker.org/wp-content/uploads/2022/06/Liebenberg-2006-Persistence-Hunting-Modern-Hunter-Gatherers.pdf)
- [Britannica, Persistence hunting](https://britannica.com/topic/persistence-hunting)
- [Dehydration and persistence hunting in Homo erectus, ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0047248419300077)
- [Man versus Horse Marathon](https://en.wikipedia.org/wiki/Man_versus_Horse_Marathon)
- [CNN, The foot and hoof race that pits humans against horses](https://www.cnn.com/2016/07/22/health/man-versus-horse-race-fit-nation/index.html)
- [Marathon Handbook, How Fast Can Usain Bolt Run](https://marathonhandbook.com/how-fast-can-usain-bolt-run/)
- [Marathon Handbook, Average Human Running Speed](https://marathonhandbook.com/how-fast-can-the-average-human-run/)
- [Britannica, How Fast Is the World's Fastest Human](https://www.britannica.com/story/how-fast-is-the-worlds-fastest-human)
- [Animal Speed Comparison, gimmecalc](https://gimmecalc.com/animal-speed-comparison/)
- [Greyhound, Wikipedia](https://en.wikipedia.org/wiki/Greyhound)
- [Canine Bible, How Fast Can A Dog Run](https://www.caninebible.com/how-fast-can-dogs-run/)
- [Top Dog Tips, Slowest Dog Breeds](https://topdogtips.com/slowest-dog-breeds/)
- [Countryfile, Hare guide](https://www.countryfile.com/wildlife/mammals/hare-guide)
- [Biology Insights, How Fast Can a Kangaroo Run and Hop](https://biologyinsights.com/how-fast-can-a-kangaroo-run-and-hop/)
- [Biology Insights, How Long Can Cheetahs Run](https://biologyinsights.com/how-long-can-cheetahs-run-the-limits-of-their-speed/)
- [Kenya Wild Parks, Do Cheetahs Overheat During the Hunt](https://www.kenyawildparks.com/do-cheetahs-overheat-during-the-hunt/)
- [ESL Teachers, Fastest Land Animals](https://eslteacher.org/fastest-land-animal-vocabulary/)

## 6. 확인 필요 항목

- 진돗개 최고 속도 40 km/h와 지구력 2~3시간: 국내 블로그 출처뿐. 학술 자료 또는 견종 협회 자료 필요
- 프롱혼 64 km/h 30분 유지: 대중 매체 인용. 1차 논문 확인 필요
- 치와와 속도 범위: 출처마다 8~16 km/h로 편차. 개체차 큼
