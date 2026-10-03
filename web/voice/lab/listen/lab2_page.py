#!/usr/bin/env python3
"""목소리 모델 테스트 2회차 검수 페이지: model_test/<엔진>/ → out2/(mp3, index.html, files.json)
- 1회차 1등 Qwen3를 기준으로 섞고, 새 엔진은 폴더가 있는 것만 넣는다
- 엔진마다 테이크 두 개까지. 예산 안에서 못 만든 줄은 빈 채로 둔다
- 음량 맞춤·mp3·ASR은 1회차(lab_page.py)와 같다
"""
import os, json, random, hashlib
import numpy as np
import lab_page as L

OUT = f'{L.MT}/_page2'
ENGINES = {  # 이름, 테이크 설명, 라이선스
    'qwen': ('Qwen3-TTS 1.7B', {1: '줄마다 목소리 설계', 2: '기준 목소리 복제'}, 'Apache-2.0'),
    'voxcpm': ('VoxCPM2 2B', {1: '목소리 설계', 2: '지시 붙인 복제'}, 'Apache-2.0'),
    'stepedit': ('Step-Audio-EditX 3B', {1: '복제', 2: '복제 뒤 감정·말투 편집'}, 'Apache-2.0'),
    'gemini': ('Gemini 3.8 Flash TTS', {1: '설계한 목소리 + 연기 지시', 2: '기본 목소리 + 묘사·지시'}, '구글 API(유료 등급은 상업 사용)'),
}


def main(takes_override=None):
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(20261002)
    T, MT = L.T, L.MT
    eng = {e: v for e, v in ENGINES.items() if os.path.isdir(f'{MT}/{e}') and any(f.endswith('.wav') for f in os.listdir(f'{MT}/{e}'))}
    if takes_override:
        for e, t in takes_override.items():
            if e in eng: eng[e] = (eng[e][0], {**eng[e][1], **t}, eng[e][2])
    files, roles = {}, []
    refs = json.load(open(f'{MT}/refs/refs.json', encoding='utf-8'))
    stats = {e: {'cer': [], 'made': 0} for e in eng}
    for role in T.ROLES:
        ko, sub = L.ROLE_KO[role]
        rf = f'ref/{role}.mp3'; L.mp3(L.load(f'{MT}/refs/{role}.wav'), f'{OUT}/{rf}'); files[rf] = f'{OUT}/{rf}'
        lines = []
        for _, n, text, dko, _, _ in [l for l in T.LINES if l[0] == role]:
            clips = []
            for e in eng:
                for take in (1, 2):
                    p = f'{MT}/{e}/{role}__{n}__{take}.wav'
                    if not os.path.exists(p): continue
                    y = L.load(p)
                    if len(y) < L.SR * 0.2 or not np.isfinite(y).all() or np.sqrt(np.mean(y ** 2)) < 1e-3: continue   # -60dBFS 아래는 사실상 무음
                    hyp = L.bake.transcribe(y, L.SR); cer = L.bake.cer(L.bake.norm(text), L.bake.norm(hyp))
                    stats[e]['cer'].append(cer); stats[e]['made'] += 1
                    cid = hashlib.sha1(f'r2{role}{n}{e}{take}'.encode()).hexdigest()[:8]
                    f = f'a/{cid}.mp3'; L.mp3(y, f'{OUT}/{f}'); files[f] = f'{OUT}/{f}'
                    clips.append({'id': cid, 'engine': e, 'take': take, 'file': f, 'dur': round(len(y) / L.SR, 1), 'cer': round(cer, 2), 'asr': hyp})
            rng.shuffle(clips)
            lines.append({'id': f'{role}{n}', 'n': n, 'text': text, 'dir': dko, 'clips': clips})
        roles.append({'id': role, 'ko': ko, 'sub': sub, 'ref': rf, 'ref_text': refs[role]['text'], 'dsp': False, 'lines': lines})
    runs = [json.loads(l) for l in open(f'{MT}/runs.jsonl', encoding='utf-8')] if os.path.exists(f'{MT}/runs.jsonl') else []
    runs = [r for r in runs if r.get('what') in eng]
    D = {'engines': {e: {'name': v[0], 'takes': v[1], 'lic': v[2], 'ran': True, 'made': stats[e]['made'],
                         'cer': round(float(np.mean(stats[e]['cer'])), 3) if stats[e]['cer'] else None,
                         'over': int(sum(c > 0.3 for c in stats[e]['cer'])), 'miss': 60 - stats[e]['made']} for e, v in eng.items()},
         'roles': roles, 'sfx': [],
         'runs': [{'what': r['what'], 'gpu': r.get('gpu'), 'clips': r.get('clips', '-'), 'wall_s': r.get('wall_s'), 'usd': r.get('usd_est')} for r in runs]}
    tpl = open(f'{L.HERE}/lab2_page.html', encoding='utf-8').read()
    open(f'{OUT}/index.html', 'w', encoding='utf-8').write(tpl.replace('/*DATA*/null', json.dumps(D, ensure_ascii=False).replace('</', '<\\/')))
    json.dump(files, open(f'{OUT}/files.json', 'w'), ensure_ascii=False, indent=1)
    print('파일', len(files), {e: (D['engines'][e]['made'], D['engines'][e]['cer'], D['engines'][e]['over']) for e in eng})


if __name__ == '__main__':
    main()
