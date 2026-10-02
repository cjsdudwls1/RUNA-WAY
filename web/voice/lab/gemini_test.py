#!/usr/bin/env python3
"""목소리 모델 테스트 2회차: Gemini 3.8 Flash TTS (Gemini API, 키는 환경 변수 GEMINI_API_KEY)

- 테이크 1: 역할마다 목소리 설계(Voices API, type=prompted)로 만든 목소리 + 줄마다 연기 지시(style)
- 테이크 2: 기본 목소리 30종 중 역할에 맞는 것 + 역할 묘사와 연기 지시를 합친 style
- 결과: model_test/gemini/<역할>__<번호>__<테이크>.wav, 설계한 목소리 아이디는 model_test/gemini/voices.json(다시 쓰기)
- 무료 등급은 분당 요청 수가 적다. 429면 기다렸다 다시 한다

  python3 web/voice/lab/gemini_test.py            # 60개
  python3 web/voice/lab/gemini_test.py --lines 2  # 역할마다 2줄만(스모크)
"""
import os, sys, io, json, time, base64, wave, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = os.path.dirname(HERE)
sys.path.insert(0, VOICE)
import model_test as T  # noqa: E402

MODEL = 'gemini-3.8-flash-tts'
OUT = f'{VOICE}/model_test/gemini'
RUNS = f'{VOICE}/model_test/runs.jsonl'
SR = 24000
GENDER = {'caster': 'male', 'narrator': 'male', 'dokkaebi': 'male', 'halmae': 'female', 'cheonyeo': 'female', 'jeoseung': 'male'}
# 기본 목소리(문서의 성격 표기): Fenrir 신남, Algenib 거침, Gacrux 노련, Enceladus 숨소리, Charon 차분
STOCK = {'caster': 'Fenrir', 'narrator': 'Algenib', 'dokkaebi': 'Algenib', 'halmae': 'Gacrux', 'cheonyeo': 'Enceladus', 'jeoseung': 'Charon'}
USD_PER_AUDIO_TOKEN, AUDIO_TOKENS_PER_S = 9.0 / 1e6, 25   # 2026년 유료 단가, 추정용


def client():
    if not os.environ.get('GEMINI_API_KEY'):
        sys.exit('GEMINI_API_KEY 환경 변수가 없다. 환경 설정에 넣고 새 세션에서 실행')
    from google import genai
    return genai.Client()


def retry(fn, tries=6):
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            msg = str(e)
            if i == tries - 1 or not any(k in msg for k in ('429', 'RESOURCE_EXHAUSTED', '503', 'UNAVAILABLE', '500')):
                raise
            time.sleep(min(60, 8 * 2 ** i))


def to_wav(data):
    b = base64.b64decode(data) if isinstance(data, str) else data
    if b[:4] == b'RIFF':
        return b
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(b)
    return buf.getvalue()


def seconds(wav_bytes):
    with wave.open(io.BytesIO(wav_bytes)) as w:
        return w.getnframes() / w.getframerate()


def design_voices(c):
    """역할마다 설계한 목소리. 이미 만든 건 voices.json에서 다시 쓴다"""
    path = f'{OUT}/voices.json'
    have = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
    for role, (desc, _) in T.ROLES.items():
        if role in have: continue
        v = retry(lambda: c.voices.create(store=True, voice={
            'model': MODEL, 'type': 'prompted', 'display_name': f'runaway-{role}',
            'gender': GENDER[role], 'language_code': 'ko-KR', 'prompted': {'input': desc}}))
        have[role] = v.id
        if getattr(v, 'sample_audio', None) and getattr(v.sample_audio, 'data', None):
            open(f'{OUT}/_sample_{role}.wav', 'wb').write(to_wav(v.sample_audio.data))
        json.dump(have, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return have


def speak(c, text, style, voice):
    r = retry(lambda: c.interactions.create(
        model=MODEL,
        input=[{'type': 'user_input', 'content': [{'type': 'text', 'text': text,
                                                   'annotations': [{'type': 'speech_metadata', 'style': style}]}]}],
        response_format={'type': 'audio'},
        generation_config={'speech_config': [{'voice': voice}]}))
    return to_wav(r.output_audio.data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lines', type=int, default=5, help='역할마다 줄 수(1~5)')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    c = client()
    t0 = time.time()
    voices = design_voices(c)
    made = errs = 0; audio_s = 0.0
    for role, n, text, _, en, _ in T.LINES:
        if n > a.lines: continue
        persona = T.ROLES[role][0].replace('Korean. ', '')
        for take, voice, style in ((1, voices[role], en), (2, STOCK[role], f'{persona} Delivery: {en}')):
            p = f'{OUT}/{role}__{n}__{take}.wav'
            if os.path.exists(p): continue
            try:
                w = speak(c, text, style, voice)
                open(p, 'wb').write(w); made += 1; audio_s += seconds(w)
                print(f'ok {role} {n} {take} {seconds(w):.1f}s', flush=True)
            except Exception as e:
                errs += 1; print(f'err {role} {n} {take} {str(e)[:200]}', flush=True)
            time.sleep(1)
    run = {'what': 'gemini', 'model': MODEL, 'clips': made, 'errs': errs, 'wall_s': round(time.time() - t0),
           'gpu': None, 'usd_est': round(audio_s * AUDIO_TOKENS_PER_S * USD_PER_AUDIO_TOKEN, 4)}
    open(RUNS, 'a', encoding='utf-8').write(json.dumps(run, ensure_ascii=False) + '\n')
    print(run)


if __name__ == '__main__':
    main()
