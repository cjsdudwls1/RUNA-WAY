# 추격자 동물 데이터 · 30분 지속 속도 기준

- 조사일: 2026-09-09
- 기준: 세션 표준 길이 30분 동안 유지 가능한 평균 속도
- 최고 속도는 티어 산정에 쓰지 않는다. 화면 연출에만 쓴다
- 원칙: 실측과 추정을 구분해 표기한다

## 1. 왜 최고 속도를 버렸나

- 치타 114 km/h는 20~30초, 약 500m만 유지된다
- 그레이하운드 69 km/h는 300~500m만 유지된다
- 30분 세션에서 이 수치는 의미가 없다. 실제로 만나는 것은 "스프린트 한 번과 긴 회복"이다
- 30분 평균으로 환산하면 순위가 뒤집힌다. 치타는 취미 러너보다 느리다

## 2. 인간 기준선 (30분)

| 구분 | 30분 지속 속도 | 근거 |
|---|---|---|
| 비운동 성인 | 6~8 km/h | 걷기~가벼운 조깅 |
| 취미 러너 | 9~12 km/h | 5km를 25~33분 |
| 중급 러너 | 12~14 km/h | 5km를 21~25분 |
| 엘리트 | 약 21 km/h | 하프마라톤 페이스 |
| 참고: 우사인 볼트 순간 | 44.72 km/h | 9.58초 동안만 |

## 3. 30분 지속 속도 산출식

실측 지속 속도가 없는 동물은 아래 식으로 추정한다.

```
30분 평균 = (스프린트속도 x 스프린트지속 + 순항속도 x 회복시간) / (스프린트지속 + 회복시간)
```

- 스프린트 속도와 지속: 실측치
- 순항 속도: 실측치가 있으면 실측, 없으면 최고 속도의 20~35%
- 회복 시간: 실측치가 있으면 실측, 없으면 지속의 10~40배. 파충류는 무산소 대사 비중이 커서 회복이 김
- 이 식은 게임 내부 적 AI에도 그대로 쓴다. 표와 게임 동작이 같은 모델을 공유한다

## 4. 트랙 A · 정규 티어 (인간이 30분 기준으로 이길 수 있음)

순차 해금. 이전 티어를 클리어해야 다음 도전 가능.

| 티어 | 동물 | 30분 지속 | 최고 속도 | 스프린트 지속 | 구분 |
|---|---|---|---|---|---|
| 1 | 세발가락나무늘보 | 0.16 km/h | 0.16 km/h | 무한 | 실측 |
| 2 | 나일악어 | 약 1.3 km/h | 17~27 km/h | 약 10초 | 추정 |
| 3 | 아홉띠아르마딜로 | 약 1.7 km/h | 48 km/h | 약 15초 | 추정 |
| 4 | 늘보로리스 | 1.8 km/h | 1.8 km/h | 지속형 | 실측 |
| 5 | 코알라 | 약 1.9 km/h | 30 km/h | 약 20초 | 추정 |
| 6 | 코모도왕도마뱀 | 약 2.0 km/h | 20 km/h | 약 15초 | 추정 |
| 7 | 힐라몬스터 | 2.4 km/h | 2.4 km/h | 지속형 | 실측 |
| 8 | 닭 | 약 2.9 km/h | 14 km/h | 약 10초 | 추정 |
| 9 | 치타 | 약 4.5 km/h | 114 km/h | 20~30초 | 추정 |
| 10 | 집고양이 | 약 4.5 km/h | 48 km/h | 약 10초 | 추정 |
| 11 | 치와와 | 약 4.9 km/h | 8~16 km/h | 약 30초 | 추정 |
| 12 | 하마 | 약 5.2 km/h | 30 km/h | 약 30초 | 추정 |
| 13 | 돼지 | 약 5.8 km/h | 24 km/h | 약 30초 | 추정 |
| 14 | 다람쥐 | 약 6.0 km/h | 24 km/h | 약 10초 | 추정 |
| 15 | 회색늑대 | 8~9 km/h | 56~72 km/h | 짧음 | 실측(순항) |
| 16 | 코끼리 | 약 9.1 km/h | 40 km/h | 약 60초 | 추정 |
| 17 | 유럽 산토끼 | 약 9.2 km/h | 72 km/h | 약 20초 | 추정 |
| 18 | 그레이하운드 | 약 10.0 km/h | 69 km/h | 300~500m | 추정 |
| 19 | 진돗개 | 12~15 km/h | 약 40 km/h | 미검증 | 추정 |

- 티어 15부터가 취미 러너(9~12 km/h) 구간. 여기부터 실제로 어려워진다
- 티어 19 진돗개는 중형견 지구력으로 추정. 국내에서 인용되는 "40 km/h로 2~3시간"은 썰매개 기록(40km 구간 평균 32 km/h)보다 높아 신뢰하기 어렵다

## 5. 트랙 B · 어차피 못 깨는 것들 (상시 개방)

30분 기준으로도 인간을 이기는 동물. 전부 실측 지구력 데이터.

| 동물 | 30분 지속 | 근거 |
|---|---|---|
| 붉은캥거루 | 20~25 km/h | 순항 속도 실측. 40 km/h로 2km 가능 |
| 지구력 경주마 | 25~30 km/h | FEI 100~120km 경주 평균 14.1~24.8 km/h. 캔터 20 km/h를 8시간 |
| 알래스칸허스키(썰매개) | 약 32 km/h | 40km 구간 평균 32 km/h. 이디타로드 전체 평균은 12.9 km/h |
| 단봉낙타 | 약 40 km/h | 40 km/h를 수 시간. 장거리 평균 20 km/h를 18시간 |
| 타조 | 48~60 km/h | 48~61 km/h를 최대 40분. 40~45 km/h로 16~24km |
| 프롱혼 | 64 km/h | 64 km/h를 30분 이상. 30분 기준의 절대 강자 |

- 순위 없음. 생존 시간만 기록
- 프롱혼은 전설 티어. 전 세계 클리어 0명 카운터 노출

## 6. 반전 포인트 (앱 카피 소재)

| 동물 | 최고 | 30분 | 한 줄 |
|---|---|---|---|
| 치타 | 114 km/h | 약 4.5 km/h | 지구 최속. 30분 기준으로는 당신이 걷는 속도 |
| 그레이하운드 | 69 km/h | 약 10 km/h | 500m 챔피언. 501m부터는 당신 차례 |
| 아르마딜로 | 48 km/h | 약 1.7 km/h | 15초 튀고 끝. 그 다음은 어슬렁 |
| 집고양이 | 48 km/h | 약 4.5 km/h | 우사인 볼트보다 빠르다. 10초 동안만 |
| 코알라 | 30 km/h | 약 1.9 km/h | 하루 20시간 자는 데는 이유가 있다 |
| 늑대 | 72 km/h | 8~9 km/h | 시속 8km로 하루 80km. 당신 조깅 속도로 하루 종일 |
| 진돗개 | 약 40 km/h | 12~15 km/h | 우리의 영원한 귀염둥이. 근데 가까워서 몰랐지 |
| 프롱혼 | 88 km/h | 64 km/h | 치타보다 느리다. 근데 30분을 그 속도로 |

## 7. 게임 반영

- 세션 시작 화면: "치타 · 30분 기준 4.5 km/h · 단 스프린트는 114 km/h"
- 두 수치를 나란히 보여주는 것 자체가 이 앱의 교육적 재미
- 적이 지쳤을 때: "젖산이 찼다. 지금이 기회다"
- 결과 화면: "치타의 스프린트 3회를 모두 버텼다"
- 도감에 최고 속도, 30분 지속, 산출 근거, 출처를 함께 표기

## 8. 출처

- [Liebenberg 2006, Persistence Hunting by Modern Hunter-Gatherers](https://cybertracker.org/wp-content/uploads/2022/06/Liebenberg-2006-Persistence-Hunting-Modern-Hunter-Gatherers.pdf)
- [Britannica, Persistence hunting](https://britannica.com/topic/persistence-hunting)
- [Man versus Horse Marathon](https://en.wikipedia.org/wiki/Man_versus_Horse_Marathon)
- [Marathon Handbook, Average Human Running Speed](https://marathonhandbook.com/how-fast-can-the-average-human-run/)
- [Marathon Handbook, How Fast Can Usain Bolt Run](https://marathonhandbook.com/how-fast-can-usain-bolt-run/)
- [Biology Insights, How Long Can Cheetahs Run](https://biologyinsights.com/how-long-can-cheetahs-run-the-limits-of-their-speed/)
- [Biology Insights, How Fast Is a Wolf](https://biologyinsights.com/how-fast-is-a-wolf-top-speed-and-endurance-explained/)
- [Biology Insights, How Fast Can a Kangaroo Run and Hop](https://biologyinsights.com/how-fast-can-a-kangaroo-run-and-hop/)
- [Mushing, How Fast Can Sled Dogs Go](https://mushing.com/featured/how-fast-can-sled-dogs-go/)
- [Snowhook Adventures, How Fast Do Sled Dogs Go on the Trail](https://snowhookadventures.com/how-fast-do-sled-dogs-go-on-the-trail/)
- [Birdfact, How Fast Can an Ostrich Run](https://www.birdfact.com/articles/how-fast-can-an-ostrich-run)
- [Biology Insights, How Fast Can Camels Run](https://biologyinsights.com/how-fast-can-camels-run-sprinting-cruising-speeds/)
- [Tevis Cup, Facts and Figures](https://teviscup.org/the-ride/facts-and-figures/)
- [Endurance riding, Wikipedia](https://en.wikipedia.org/wiki/Endurance_riding)
- [Greyhound, Wikipedia](https://en.wikipedia.org/wiki/Greyhound)
- [Africa Freak, How Fast Can a Crocodile Run](https://africafreak.com/how-fast-can-a-crocodile-run)
- [CK-12, How fast can a Komodo dragon run](https://www.ck12.org/flexi/biology/reptile-evolution/how-fast-can-a-komodo-dragon-run/)
- [Florida Museum, Five facts nine-banded armadillo](https://www.floridamuseum.ufl.edu/science/five-facts-nine-banded-armadillo/)
- [Live Science, What is the world's slowest animal](https://www.livescience.com/animals/what-is-the-worlds-slowest-animal)
- [Countryfile, Hare guide](https://www.countryfile.com/wildlife/mammals/hare-guide)
- [Canine Bible, How Fast Can A Dog Run](https://www.caninebible.com/how-fast-can-dogs-run/)
- [gimmecalc, Animal Speed Comparison](https://gimmecalc.com/animal-speed-comparison/)

## 9. 확인 필요

- 트랙 A의 "추정" 15종: 회복 시간 실측치가 없어 산출식으로 계산. 종별 대사 연구 확인 필요
- 진돗개 40 km/h, 2~3시간: 국내 블로그 출처뿐. 견종 협회 또는 학술 자료 필요
- 집고양이 48 km/h, 아르마딜로 48 km/h: 위키 계열 출처. 1차 자료 필요
- 프롱혼 64 km/h 30분 유지: 대중 매체 인용. 원 논문 확인 필요
- 악어 육상 최고 27 km/h: 종별 편차 큼. 나일악어 기준 확정 필요
