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

### 트랙 A · 정규 티어 (인간이 이길 수 있음, 순차 해금)

| 티어 | 동물 | 실측 속도 | 지속 | 비고 |
|---|---|---|---|---|
| 1 | 세발가락나무늘보 | 0.1~0.16 km/h (지상) | 무한 | 튜토리얼. 걸어도 이김 |
| 2 | 힐라몬스터(독도마뱀) | 2.4 km/h | 짧음 | 빠른 걸음 |
| 3 | 늘보로리스 | 1.8 km/h | 짧음 | 야간 티어 후보 |
| 4 | 닭 | 14 km/h | 수 초 | 첫 달리기 요구 |
| 5 | 치와와 | 8~16 km/h | 짧음 | 단두종 호흡 제약 |
| 6 | 나일악어(육상) | 평균 13~17 km/h, 최고 27 km/h | 짧은 폭발 | 갤럽 가능, 장거리 불가 |
| 7 | 코모도왕도마뱀 | 20 km/h | 짧은 폭발 | 장거리 추격 불가 |
| 8 | 돼지 | 24 km/h | 짧음 | 아마추어 스프린트 한계선 |
| 9 | 다람쥐 | 24 km/h | 매우 짧음 | 8티어와 동급, 회피 패턴 다름 |

- 기준선: 취미 러너 지속 9~12 km/h, 평균인 스프린트 12~15 km/h, 아마추어 경쟁 스프린트 약 24 km/h
- 티어 8~9는 실제로 아마추어 스프린트 상한과 같음. 여기가 정규 티어의 끝

### 트랙 B · 어차피 못 깨는 것들 (상시 개방)

인간이 실측상 이길 수 없는 동물. 체험용으로 언제든 도전 가능하되 클리어는 사실상 불가.

| 동물 | 실측 속도 | 지속 | 반전 포인트 |
|---|---|---|---|
| 코알라 | 30 km/h | 짧음 | 하루 20시간 자는 동물 |
| 집고양이 | 48 km/h (확인 필요) | 매우 짧음 | 우사인 볼트보다 빠름 |
| 아홉띠아르마딜로 | 48 km/h (확인 필요) | 짧음 | 평소 시속 0.5km로 어슬렁거림 |
| 하마 | 30 km/h | 짧음 | 3톤 체중 |
| 코끼리 | 40 km/h | 짧음 | 체중 대비 |
| 진돗개 | 약 40 km/h (확인 필요) | 2~3시간 (확인 필요) | 속도와 지구력을 모두 갖춤 |
| 그레이하운드 | 최고 69 km/h, 경주 58~61 km/h | 300~500m | 순수 스프린터 |
| 유럽 산토끼 | 72 km/h | 짧은 반복 | 지그재그 회피 |
| 붉은캥거루 | 순간 70 km/h | 40 km/h로 2km | 18km/h 이상에서 에너지 효율 최고 |
| 타조 | 약 70 km/h | 장거리 | 조류 최속 |
| 치타 | 114 km/h | 20~30초 / 약 500m | 젖산 축적으로 정지 |
| 프롱혼 | 88 km/h | 64 km/h를 30분 이상 (확인 필요) | 속도와 지구력 모두. 전설 티어 |

- 트랙 B는 순위 없음. "몇 초 버텼는가"만 기록
- 프롱혼은 전설 티어. 전 세계 클리어 0명 카운터를 앱에 노출

### 참고 · 게임에 쓰지 않는 극단값

| 동물 | 속도 |
|---|---|
| 갈라파고스땅거북 | 0.26 km/h |
| 정원달팽이 | 0.001 km/h |
| 바나나민달팽이 | 0.0096 km/h |

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

### 속도 모델 (확정)

- 실측 절대값 그대로 사용. 배율 보정 없음
- 성립 근거: 정규 티어를 "인간이 실제로 이길 수 있는 동물"로만 구성했기 때문
- 치와와 16 km/h는 취미 러너 지속 속도보다 빠르지만, 치와와의 스프린트 지속이 짧아 버티면 이김
- 이것이 이 앱의 핵심 재미. 속도로 이기는 게임이 아니라 지속 시간으로 이기는 게임

### 진행 규칙

- 트랙 A는 순차 해금. 이전 티어를 깨야 다음 티어 도전 가능
- 트랙 B는 상시 개방. 클리어 불가를 전제로 하되 "몇 초 버텼는가"를 기록
- 트랙 B의 목적은 체감. 사용자가 실제 동물 속도를 몸으로 느끼게 하는 것

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

- [CK-12, How fast can a Komodo dragon run](https://www.ck12.org/flexi/biology/reptile-evolution/how-fast-can-a-komodo-dragon-run/)
- [Africa Freak, How Fast Can a Crocodile Run](https://africafreak.com/how-fast-can-a-crocodile-run)
- [Florida Museum, Five facts nine-banded armadillo](https://www.floridamuseum.ufl.edu/science/five-facts-nine-banded-armadillo/)
- [Live Science, What is the world's slowest animal](https://www.livescience.com/animals/what-is-the-worlds-slowest-animal)
- [A-Z Animals, The Top 8 Slowest Animals](https://a-z-animals.com/animals/lists/slowest-animals/)
- [phys.org, Animals are better sprinters than humans](https://phys.org/news/2021-07-animals-sprinters-humans.html)

## 6. 확인 필요 항목

- 진돗개 최고 속도 40 km/h와 지구력 2~3시간: 국내 블로그 출처뿐. 학술 자료 또는 견종 협회 자료 필요
- 프롱혼 64 km/h 30분 유지: 대중 매체 인용. 1차 논문 확인 필요
- 치와와 속도 범위: 출처마다 8~16 km/h로 편차. 개체차 큼
- 집고양이 48 km/h: 널리 인용되나 1차 자료 미확인
- 아홉띠아르마딜로 30 mph(48 km/h): 위키 계열 출처. 학술 자료 필요
- 악어 육상 최고 27 km/h: 종별 편차 큼. 나일악어 기준으로 확정 필요
