"""괴물런 목소리 모델 테스트. TTS 세 개를 Modal GPU에서 같은 대사로 돌린다(docs/prd/19-monster-sound.md 11·12장)

- 엔진: qwen(Qwen3-TTS, Apache-2.0), cosy(Fun-CosyVoice3-0.5B, Apache-2.0), cbox(Chatterbox Multilingual, MIT)
- 대사: 역할 6 × 5줄(아래 LINES). 역할마다 참조 목소리를 Qwen3 VoiceDesign으로 한 번 만든다
  - 참조를 cosy·cbox 복제에도 넣는다. 음색을 맞추고 연기만 비교한다
- 테이크(엔진마다 2개)
  - qwen: 1 = 줄마다 VoiceDesign(역할 묘사 + 연기 지시), 2 = Base 복제(역할 참조)
  - cosy: 1 = instruct2(연기 지시를 지원 목록에 맞춤), 2 = zero-shot(참조 말투)
  - cbox: 1 = 감정 과장 0.5(cfg 0.5), 2 = 0.85(cfg 0.3)
- 결과: web/voice/model_test/<엔진>/<역할>__<줄>__<테이크>.wav (커밋하지 않는다)
- 앱은 임시 앱이라 끝나면 멈춘다. 끝에 한 번 더 확인한다

실행
  python3 web/voice/model_test.py --refs          # 역할 참조 후보 3개씩 → ASR로 고르고 Volume에 올린다
  python3 web/voice/model_test.py --engine qwen   # cosy, cbox도 같은 방식
"""
import os, sys, io, json, time, argparse, subprocess

import modal

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'model_test')
APP_NAME = 'runaway-model-test'
GPU = os.environ.get('LAB_GPU', 'L4')

app = modal.App(APP_NAME)
qvol = modal.Volume.from_name('runaway-qwen-tts', create_if_missing=True)   # Qwen 모델(qwen_modal.py가 받아 둠)
lab = modal.Volume.from_name('runaway-tts-lab', create_if_missing=True)     # 참조 목소리, cosy·cbox 모델

QWEN = {'design': '/models/Qwen3-TTS-12Hz-1.7B-VoiceDesign', 'base': '/models/Qwen3-TTS-12Hz-1.7B-Base'}
ENV = {'HF_HOME': '/lab/hf', 'HF_HUB_ENABLE_HF_TRANSFER': '1', 'TOKENIZERS_PARALLELISM': 'false'}
qwen_image = (modal.Image.debian_slim(python_version='3.12')
              .apt_install('sox', 'libsox-fmt-all', 'ffmpeg')
              .pip_install('torch==2.8.0', 'torchaudio==2.8.0', 'qwen-tts==0.1.1', 'hf_transfer==0.1.9')
              .env(ENV))
cosy_image = (modal.Image.debian_slim(python_version='3.10')
              .apt_install('git', 'sox', 'libsox-dev', 'ffmpeg', 'build-essential')
              .pip_install('torch==2.3.1', 'torchaudio==2.3.1', index_url='https://download.pytorch.org/whl/cu121')
              .pip_install('Cython', 'numpy==1.26.4', 'setuptools<70')
              .pip_install('conformer==0.3.2', 'diffusers==0.29.0', 'hydra-core==1.3.2', 'HyperPyYAML==1.2.3', 'inflect==7.3.1', 'librosa==0.10.2',
                           'lightning==2.2.4', 'matplotlib==3.7.5', 'modelscope==1.20.0', 'networkx==3.1', 'omegaconf==2.3.0', 'onnx==1.16.0',
                           'onnxruntime==1.18.0', 'openai-whisper==20231117', 'protobuf==4.25.3', 'pyarrow==18.1.0', 'pydantic==2.7.0', 'pyworld==0.3.4',
                           'rich==13.7.1', 'soundfile==0.12.1', 'transformers==4.51.3', 'x-transformers==2.11.24', 'wetext==0.0.4', 'wget==3.2',
                           'gdown==5.1.0', 'huggingface_hub==0.30.2', 'hf_transfer==0.1.9',
                           extra_options='--no-build-isolation')   # openai-whisper 옛 판의 setup.py가 pkg_resources를 쓴다(setuptools<70)
              .run_commands('git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git /opt/CosyVoice',
                            'cd /opt/CosyVoice && git submodule update --init --recursive')
              .env(ENV))
cbox_image = (modal.Image.debian_slim(python_version='3.11')
              .apt_install('ffmpeg', 'git')
              .pip_install('chatterbox-tts', 'hf_transfer==0.1.9')
              .env(ENV))

# 역할: 참조 목소리 묘사(Qwen VoiceDesign instruct)와 참조 문장(5~8초, 그 역할 말투)
ROLES = {
    'caster': ('Korean. An energetic Korean male sports commentator in his thirties calling a live race: fast, excited, big dynamic range, broadcast voice.',
               '자, 드디어 경기가 시작됩니다! 오늘 이 경기, 정말 기대가 되는데요!'),
    'narrator': ('Korean. A Korean male horror radio storyteller in his fifties: low, slow, breathy and ominous, very close to the microphone.',
                 '그날 밤은 유난히 조용했다. 아무도 그 길로는 가지 않았다.'),
    'dokkaebi': ('Korean. A playful, boastful Korean goblin (dokkaebi): a boisterous middle-aged man with a big hearty laugh, comedic and exaggerated like a cartoon.',
                 '으하하하! 이 방망이로 말할 것 같으면, 금 나와라 뚝딱 하면 금이 나오는 방망이란 말이다!'),
    'halmae': ('Korean. A chatty, feisty Korean grandmother in her seventies with a raspy voice and a strong Gyeongsang-do dialect, comedic and nagging.',
               '아이고 얘야, 할매 말 좀 들어 봐라. 요즘 젊은 것들은 할매를 못 따라온다 안 카나.'),
    'cheonyeo': ('Korean. A young Korean female ghost: a fragile, trembling voice that sobs and whispers, eerie and heartbroken.',
                 '여기는 너무 추워… 아무도 나를 찾으러 오지 않았어…'),
    'jeoseung': ('Korean. The Korean grim reaper: a deep, slow, emotionless male voice, cold and authoritative, like a judge passing sentence.',
                 '명부에 적힌 이름은 지워지지 않는다. 때가 되면 누구든 데려간다.'),
}
# (역할, 번호, 대사, 연기 지시, 영어 지시(qwen), cosy 지시 이름)
LINES = [
    ('caster', 1, '자, 오늘의 상대! 방망이 하나로 천하를 주름잡은, 도깨비 선수입니다!', '흥분, 소개 톤', 'excited, announcing a contestant', 'happy'),
    ('caster', 2, '출발했습니다!', '짧고 크게', 'short and loud, very excited', 'loud'),
    ('caster', 3, '역전! 역전입니다! 도깨비 선수, 방망이를 떨어뜨렸어요!', '최고조 흥분', 'screaming with excitement at the peak moment', 'loud'),
    ('caster', 4, '격차가 벌어집니다. 도깨비 선수, 표정이 좋지 않네요.', '중계 톤, 살짝 비꼼', 'calm commentary with a hint of sarcasm', 'fast'),
    ('caster', 5, '선수가 사라졌습니다! 어디로 간 걸까요?', '당황한 척', 'pretending to be flustered, comedic', 'fast'),
    ('narrator', 1, '오늘 밤, 그것이 깨어났다.', '낮고 느리게', 'low and slow, ominous', 'slow'),
    ('narrator', 2, '뒤를 돌아보지 마.', '속삭이듯', 'whispering a warning', 'soft'),
    ('narrator', 3, '발견.', '짧고 차갑게', 'one cold word, short and sharp', 'slow'),
    ('narrator', 4, '숨죽여. 소리 내지 마.', '속삭임', 'tense whisper', 'soft'),
    ('narrator', 5, '닭이 울었다. 그것은 어둠 속으로 사라졌다.', '낮게, 안도', 'low, with quiet relief', 'slow'),
    ('dokkaebi', 1, '헉, 헉… 형님! 방망이 좀 들어 주실 분?', '비굴, 숨참', 'groveling and out of breath, comedic', 'sad'),
    ('dokkaebi', 2, '뒤에 누구 있나~? 아무도 없네~?', '놀림, 노래하듯', 'teasing in a sing-song voice', 'happy'),
    ('dokkaebi', 3, '비켜라 비켜~ 도깨비 나가신다!', '으스댐', 'cocky and triumphant', 'loud'),
    ('dokkaebi', 4, '어? 어어? 방금 뭐가 지나갔냐?', '당황', 'confused and flustered', 'fast'),
    ('dokkaebi', 5, '어디 숨었냐~ 도깨비불 켠다~', '장난스럽게', 'playful, searching around', 'happy'),
    ('halmae', 1, '아이고 허리야… 할매 버리고 가나?', '서운한 척', 'pretending to be hurt, whiny', 'sad'),
    ('halmae', 2, '호호호, 할매한테 지면 우짜노~', '놀림', 'cackling and teasing', 'happy'),
    ('halmae', 3, '인자 할매 본실력 나온다!', '기세', 'fired up, shouting', 'loud'),
    ('halmae', 4, '잠깐! 틀니 떨어졌다! 기다리라!', '다급', 'panicked and urgent', 'fast'),
    ('halmae', 5, '요즘 젊은 것들은 인정도 없데이…', '삐짐', 'sulking', 'sad'),
    ('cheonyeo', 1, '어디 가…', '멀리서, 흐느끼듯', 'sobbing from far away', 'sad'),
    ('cheonyeo', 2, '같이 가…', '떨리게', 'trembling, pleading', 'soft'),
    ('cheonyeo', 3, '거기 있구나…', '귀에 속삭임', 'whispering right into your ear', 'soft'),
    ('cheonyeo', 4, '어디 숨었어… 나 혼자 두지 마…', '속삭임, 울먹', 'whispering, on the verge of tears', 'sad'),
    ('cheonyeo', 5, '왜… 왜 또 나만 두고 가…', '울먹이다 분노', 'tearful, turning into rage', 'angry'),
    ('jeoseung', 1, '명부에 네 이름이 있다.', '낮고 느리게', 'deep, slow, final', 'slow'),
    ('jeoseung', 2, '때가 되었다.', '감정 없이', 'emotionless and cold', 'slow'),
    ('jeoseung', 3, '도망쳐도… 소용없다.', '낮게, 가까이', 'low and close, menacing', 'soft'),
    ('jeoseung', 4, '숨어도 명부는 거짓말을 안 한다.', '속삭임', 'cold whisper', 'soft'),
    ('jeoseung', 5, '…오늘은 여기까지다.', '분노를 누르며', 'suppressed anger', 'angry'),
]
# CosyVoice3가 지원하는 지시문(cosyvoice/utils/common.py instruct_list에서 고름)
COSY = {
    'loud': 'You are a helpful assistant. Please say a sentence as loudly as possible.<|endofprompt|>',
    'soft': 'You are a helpful assistant. Please say a sentence in a very soft voice.<|endofprompt|>',
    'slow': 'You are a helpful assistant. 请用尽可能慢地语速说一句话。<|endofprompt|>',
    'fast': 'You are a helpful assistant. 请用尽可能快地语速说一句话。<|endofprompt|>',
    'happy': 'You are a helpful assistant. 请非常开心地说一句话。<|endofprompt|>',
    'sad': 'You are a helpful assistant. 请非常伤心地说一句话。<|endofprompt|>',
    'angry': 'You are a helpful assistant. 请非常生气地说一句话。<|endofprompt|>',
}


def wav_bytes(x, sr):
    import numpy as np, soundfile as sf
    b = io.BytesIO(); sf.write(b, np.asarray(x, dtype='float32').reshape(-1), sr, format='WAV', subtype='PCM_16'); return b.getvalue()


def ref_of(role):
    """Volume의 역할 참조: (wav 경로, 참조 문장)"""
    meta = json.load(open('/lab/refs/refs.json', encoding='utf-8'))
    return f'/lab/refs/{role}.wav', meta[role]['text']


@app.cls(image=qwen_image, gpu=GPU, volumes={'/models': qvol, '/lab': lab}, timeout=3600, scaledown_window=20)
class Qwen:
    @modal.enter()
    def boot(self):
        self.m, self.prompts = {}, {}

    def model(self, name):
        if name not in self.m:
            import torch
            from qwen_tts import Qwen3TTSModel
            self.m[name] = Qwen3TTSModel.from_pretrained(QWEN[name], device_map='cuda:0', dtype=torch.bfloat16, attn_implementation='sdpa')
        return self.m[name]

    @modal.method()
    def refs(self, k, seed):
        """역할마다 참조 후보 k개(VoiceDesign)"""
        import torch
        out = []
        for role, (desc, text) in ROLES.items():
            for i in range(k):
                torch.manual_seed(seed + i); torch.cuda.manual_seed_all(seed + i)
                w, sr = self.model('design').generate_voice_design(text=text, language='Korean', instruct=desc)
                out.append({'role': role, 'i': i, 'text': text, 'wav': wav_bytes(w[0], sr)})
        return out

    def prompt(self, role):
        if role not in self.prompts:
            import soundfile as sf
            p, text = ref_of(role)
            x, sr = sf.read(p, dtype='float32')
            self.prompts[role] = self.model('base').create_voice_clone_prompt(ref_audio=(x, sr), ref_text=text, x_vector_only_mode=False)
        return self.prompts[role]

    @modal.method()
    def lines(self, seed):
        import torch
        t0, out = time.time(), []
        for role, n, text, _, en, _ in LINES:
            torch.manual_seed(seed + n); torch.cuda.manual_seed_all(seed + n)
            w, sr = self.model('design').generate_voice_design(text=text, language='Korean', instruct=f'{ROLES[role][0]} Speaking style: {en}.')
            out.append({'role': role, 'n': n, 'take': 1, 'wav': wav_bytes(w[0], sr)})
            w, sr = self.model('base').generate_voice_clone(text=[text], language=['Korean'], voice_clone_prompt=self.prompt(role))
            out.append({'role': role, 'n': n, 'take': 2, 'wav': wav_bytes(w[0], sr)})
        return {'out': out, 'gen_s': time.time() - t0}


@app.function(image=qwen_image, volumes={'/lab': lab}, timeout=600)
def put_refs(files, meta):
    os.makedirs('/lab/refs', exist_ok=True)
    for n, b in files.items(): open(f'/lab/refs/{n}', 'wb').write(b)
    json.dump(meta, open('/lab/refs/refs.json', 'w', encoding='utf-8'), ensure_ascii=False)
    lab.commit()
    return sorted(os.listdir('/lab/refs'))


@app.cls(image=cosy_image, gpu=GPU, volumes={'/lab': lab}, timeout=3600, scaledown_window=20)
class Cosy:
    @modal.enter()
    def boot(self):
        sys.path[:0] = ['/opt/CosyVoice', '/opt/CosyVoice/third_party/Matcha-TTS']
        d = '/lab/cosy3'
        if not os.path.exists(os.path.join(d, '.done')):
            from huggingface_hub import snapshot_download
            snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B-2512', local_dir=d)
            open(os.path.join(d, '.done'), 'w').write('ok')
            lab.commit()
        from cosyvoice.cli.cosyvoice import AutoModel
        self.m = AutoModel(model_dir=d)

    @modal.method()
    def lines(self, seed):
        import torch
        t0, out = time.time(), []
        for role, n, text, _, _, ins in LINES:
            p, ref_text = ref_of(role)
            for take, run in ((1, lambda: self.m.inference_instruct2(text, COSY[ins], p, stream=False)),
                              (2, lambda: self.m.inference_zero_shot(text, 'You are a helpful assistant.<|endofprompt|>' + ref_text, p, stream=False))):
                torch.manual_seed(seed + n)
                try:
                    segs = [j['tts_speech'] for j in run()]
                    out.append({'role': role, 'n': n, 'take': take, 'wav': wav_bytes(torch.cat(segs, dim=1).cpu().numpy(), self.m.sample_rate)})
                except Exception as e:
                    out.append({'role': role, 'n': n, 'take': take, 'err': repr(e)[:300]})
        return {'out': out, 'gen_s': time.time() - t0}


@app.cls(image=cbox_image, gpu=GPU, volumes={'/lab': lab}, timeout=3600, scaledown_window=20)
class Cbox:
    @modal.enter()
    def boot(self):
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        self.m = ChatterboxMultilingualTTS.from_pretrained(device='cuda')
        lab.commit()

    @modal.method()
    def lines(self, seed):
        import torch
        t0, out = time.time(), []
        for role, n, text, _, _, _ in LINES:
            p, _ = ref_of(role)
            for take, ex, cfg in ((1, 0.5, 0.5), (2, 0.85, 0.3)):
                torch.manual_seed(seed + n)
                try:
                    w = self.m.generate(text, language_id='ko', audio_prompt_path=p, exaggeration=ex, cfg_weight=cfg)
                    out.append({'role': role, 'n': n, 'take': take, 'wav': wav_bytes(w.cpu().numpy(), self.m.sr)})
                except Exception as e:
                    out.append({'role': role, 'n': n, 'take': take, 'err': repr(e)[:300]})
        return {'out': out, 'gen_s': time.time() - t0}


# ---------------- 이 컴퓨터 쪽 ----------------
class _Null:
    def __enter__(self): return self
    def __exit__(self, *a): return False


def stop_app(app_id):
    """이번 실행의 앱이 아직 살아 있으면 멈춘다(다른 앱은 건드리지 않는다)"""
    if not app_id: return
    try:
        r = subprocess.run(['modal', 'app', 'list', '--json'], capture_output=True, text=True, timeout=60)
        for x in json.loads(r.stdout or '[]'):
            if x.get('app_id') == app_id and x.get('state') not in ('stopped', 'stopping'):
                subprocess.run(['modal', 'app', 'stop', '-y', app_id], timeout=60)
                print('  modal app stop', app_id, flush=True)
    except Exception as e:
        print(f'  앱 상태 확인 실패(수동 확인: modal app list, {app_id}):', e, flush=True)


def log_run(rec):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'runs.jsonl'), 'a', encoding='utf-8') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def do_refs(a):
    import numpy as np, soundfile as sf
    sys.path.insert(0, HERE)
    import bake
    d = os.path.join(OUT, 'refs'); os.makedirs(os.path.join(d, 'cands'), exist_ok=True)
    t0 = time.time()
    with modal.enable_output() if a.verbose else _Null(), app.run():
        app_id = app.app_id
        res = Qwen().refs.remote(a.k, a.seed)
        best = {}
        for r in res:
            p = os.path.join(d, 'cands', f"{r['role']}__{r['i']}.wav"); open(p, 'wb').write(r['wav'])
            x, sr = sf.read(p, dtype='float32', always_2d=True); x = x.mean(1)
            hyp = bake.transcribe(x, sr); c = bake.cer(bake.norm(r['text']), bake.norm(hyp))
            print(f"  {r['role']:9s} {r['i']} {len(x) / sr:4.1f}s CER {c:.2f}  {hyp}", flush=True)
            if r['role'] not in best or c < best[r['role']][0]: best[r['role']] = (c, r)
        files = {f'{role}.wav': r['wav'] for role, (c, r) in best.items()}
        meta = {role: {'text': r['text'], 'cand': r['i'], 'cer': round(c, 3)} for role, (c, r) in best.items()}
        for n, b in files.items(): open(os.path.join(d, n), 'wb').write(b)
        json.dump(meta, open(os.path.join(d, 'refs.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('  Volume:', put_refs.remote(files, meta), flush=True)
    log_run({'what': 'refs', 'app_id': app_id, 'wall_s': round(time.time() - t0), 'gpu': GPU})
    stop_app(app_id)


def do_engine(a):
    cls = {'qwen': Qwen, 'cosy': Cosy, 'cbox': Cbox}[a.engine]
    d = os.path.join(OUT, a.engine); os.makedirs(d, exist_ok=True)
    t0 = time.time()
    with modal.enable_output() if a.verbose else _Null(), app.run():
        app_id = app.app_id
        res = cls().lines.remote(a.seed)
    errs = 0
    for r in res['out']:
        if 'err' in r: errs += 1; print('  실패', r['role'], r['n'], r['take'], r['err'], flush=True); continue
        open(os.path.join(d, f"{r['role']}__{r['n']}__{r['take']}.wav"), 'wb').write(r['wav'])
    print(f"  {a.engine}: {len(res['out']) - errs}개, 실패 {errs}, 생성 {res['gen_s']:.0f}초, 전체 {time.time() - t0:.0f}초", flush=True)
    log_run({'what': a.engine, 'app_id': app_id, 'clips': len(res['out']) - errs, 'errs': errs, 'gen_s': round(res['gen_s']), 'wall_s': round(time.time() - t0), 'gpu': GPU})
    stop_app(app_id)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--refs', action='store_true')
    ap.add_argument('--engine', choices=['qwen', 'cosy', 'cbox'])
    ap.add_argument('--k', type=int, default=3)
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()
    if a.refs: do_refs(a)
    elif a.engine: do_engine(a)
    else: ap.print_help()


if __name__ == '__main__':
    main()
