# TTS · 배경음 조사

- 2026-09-10
- 조건: 한국어, 상업 이용 가능, 감정 연기(어트랙션 톤), 비용 0에 가까움
- 전제: 대사는 사전 생성 뱅크. 300라인 x 40자 = 약 12,000자. 실시간 합성 없음

## 1. 후보 비교

### 무료 + 상업 이용 가능

| 후보 | 한국어 | 감정·연기 | 라이선스 | 비용 | 비고 |
|---|---|---|---|---|---|
| Google Cloud Chirp 3 HD | 지원 | 30종 스타일 음성, 속도·쉼 제어 | 생성물 소유권 사용자. 상업 OK | 월 100만 자 무료 | GCP 계정(카드 등록) 필요 |
| CosyVoice 2/3 (Alibaba) | 우수. 논문에서 일본어보다 한국어 성능 높음 | instruct 모드로 감정·말투 지시 | Apache 2.0 | 0. Colab 무료 GPU | 로컬 실행. 설정 난이도 중간 |
| MeloTTS (MyShell) | 지원 | 없음 | MIT | 0. CPU 실행 가능 | 시스템 안내용. 연기 불가 |
| Orpheus 3B | 목록에 있음. 품질 확인 필요 | 감정 태그 | Apache 2.0 | 0. GPU 필요 | 영어 중심 모델 |

### 무료지만 상업 불가 → 제외

| 후보 | 이유 |
|---|---|
| ElevenLabs Free | 월 10,000 크레딧. 비상업 + 출처 표기 의무 |
| Typecast Free | 월 5분. 출처 표기 의무 |
| Azure TTS Free | 월 50만 자지만 상업권은 유료 티어만 |
| Fish Speech 1.5 | 한국어 2만 시간 학습으로 품질 좋으나 가중치 CC-BY-NC-SA |
| XTTS v2 | CPML 비상업 |
| F5-TTS | CC-BY-NC |

### 저비용 유료 (감정 연기가 강함)

| 후보 | 한국어 | 감정·연기 | 비용 |
|---|---|---|---|
| Gemini-TTS (Google Cloud) | 지원 | 자연어 스타일 지시, [whispers] 등 오디오 태그 200개 이상 | 무료 티어 없음. 12,000자는 몇백 원 수준 |
| ElevenLabs Starter | 지원 | 업계 최상급 | 월 $5, 3만 크레딧, 상업권 포함. 1개월만 결제 |
| Typecast 유료 | 한국 회사. 한국어 감정 연기 강점 | 캐릭터 음성 다수 | 월 $8.99 |
| Supertone Play | 지원 | 한국 회사 | 분당 $0.10 (베타) |

## 2. 추천

- 1순위: Google Cloud Chirp 3 HD
  - 무료 한도가 우리 필요량의 80배. 상업 OK. 한국어 스타일 음성 다수
  - 오퍼레이터 일반 대사 200~250개를 여기서 생성
- 감정이 필요한 대사 30~50개(오프닝 브리핑, 점프 스케어 직후, 지친 적 조롱)만 별도
  - 1안 Gemini-TTS: 같은 GCP 안에서 오디오 태그로 연기 지시. 비용 몇백 원
  - 2안 ElevenLabs Starter 1개월 $5: 품질 최상. 생성 후 해지
- 완전 무료·로컬을 원하면 CosyVoice 2. 한국어 품질이 오픈소스 중 최상이고 감정 지시가 됨. Colab에서 배치 생성
- MeloTTS는 대체 수단. 감정 없는 시스템 음성("GPS 신호 약함")에만

## 3. 결정 절차

- 동일 대사 10개(브리핑 3, 추격 4, 지침 조롱 3)를 Chirp 3 HD, CosyVoice 2, ElevenLabs로 생성
- 5명 블라인드 청취. 긴박감·자연스러움·발음 3항목 5점 척도
- 대사 원문과 연출 지시는 공급자 독립 포맷(스프레드시트)으로 보관. 공급자 교체 시 재생성만

## 4. 배경음 · 앰비언스

### 필요한 것

- 서식지 앰비언스 5종: 열대우림(나무늘보·악어·코모도), 사바나(치타·프롱혼·타조), 침엽수림(늑대), 호주 관목지(캥거루·코알라), 한국 시골 밤(진돗개)
- 추격 드럼 레이어: 적 상태에 따라 템포 변화. 스프린트 시 최고, 지침 시 정지
- 동물 소리: 티어별 4상태 x 변형 3 = 12종 이하. 25종이면 최대 300개, 실제로는 공유 소리 많아 150개 내외

### 무료 상업 이용 가능 소재

| 출처 | 라이선스 | 용도 |
|---|---|---|
| Pixabay (music, sound-effects) | 상업 OK, 출처 표기 불필요 | 앰비언스, 동물 소리, BGM |
| Mixkit | 로열티프리, 상업 OK | 정글 효과음 |
| Zapsplat | 무료 상업 OK, 무료 회원은 출처 표기 필요 | 숲·정글 앰비언스 |
| freesound.org | CC0 필터로 검색 | 동물 울음 원본 |

- 부족한 동물 소리는 실제 녹음 소재를 피치·속도 변형해 지침·회복 상태 버전 제작
- AI 음악 생성(Suno, Udio)은 상업 라이선스가 유료 플랜 조건. MVP는 소재 조합으로 시작

## 5. 출처

- [Google Cloud, Chirp 3: HD voices](https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd)
- [Google Cloud, Gemini-TTS](https://docs.cloud.google.com/text-to-speech/docs/gemini-tts)
- [Google Cloud TTS free plan limits](https://costbench.com/software/ai-voice-tools/google-cloud-text-to-speech/free-plan/)
- [CosyVoice 2 논문](https://arxiv.org/pdf/2412.10117)
- [CosyVoice 3 논문](https://arxiv.org/html/2505.17589v2)
- [MeloTTS GitHub](https://github.com/myshell-ai/MeloTTS)
- [Fish Speech LICENSE](https://github.com/fishaudio/fish-speech/blob/main/LICENSE)
- [BentoML, Best Open-Source TTS 2026](https://www.bentoml.com/blog/exploring-the-world-of-open-source-text-to-speech-models)
- [ElevenLabs free commercial use](https://oakgen.ai/blog/elevenlabs-free-commercial-use)
- [ElevenLabs pricing 2026](https://bigvu.tv/blog/elevenlabs-pricing-2026-plans-credits-commercial-rights-api-costs/)
- [Typecast pricing](https://typecast.ai/pricing/)
- [Supertone Play](https://www.supertone.ai/en/play)
- [Azure free tier commercial use Q&A](https://learn.microsoft.com/en-us/answers/questions/5792674/can-the-audio-generated-by-azure-speech-studios-fr)
- [Pixabay savanna music](https://pixabay.com/music/search/savanna/)
- [Pixabay jungle sound effects](https://pixabay.com/sound-effects/search/jungle/)
- [Zapsplat forest and jungle ambiences](https://www.zapsplat.com/sound-effect-category/forest-and-jungle-ambiences/)

## 6. 확인 필요

- Orpheus 3B, Chatterbox 다국어판의 실제 한국어 품질. 직접 청취 필요
- CosyVoice 3 가중치 공개 여부와 라이선스
- Zapsplat 무료 회원의 출처 표기 조건 세부
