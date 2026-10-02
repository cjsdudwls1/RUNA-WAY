"""괴물런 목소리 모델 비교 2회차: Step-Audio-EditX(stepfun-ai/Step-Audio-EditX, StepFun, 3B, Apache-2.0). 엔진 이름 stepedit

- 핵심 질문: 사람이 녹음한 목소리에 감정·말투(속삭임 등)·숨소리를 편집으로 입히는 기능이 한국어에서 되는가
- 대사: web/voice/model_test.py의 LINES(역할 6 × 5줄). 참조: model_test/refs/<역할>.wav + refs.json
- 테이크
  - 1 = 역할 참조 wav + 참조 문장으로 제로샷 복제(clone). 대사 앞에 [Korean] 태그(README 방식)
  - 2 = 테이크 1 결과를 편집 모드로 한 번 고친다(EDITS: 줄마다 연기 지시에 맞는 감정·말투·준언어 태그)
- 추론 경로: vLLM 없이
  - LLM(Step1 3B, bf16): safetensors를 GPU에 바로 올리고 직접 짠 배치 디코더로 샘플링
    - 모델 코드(modeling_step1.py)와 같은 계산: ALiBi(-sqrt 거리), GQA 48/4, RMSNorm, SwiGLU
    - temperature 0.7(저장소 vLLM 경로와 같음). 오디오 토큰만 허용(vq02 2개 + vq06 3개 묶음 순서, 65536 + 0~5119)
  - 오디오 토크나이저(funasr_detach, ONNX)·보코더(stepvocoder, bf16): 저장소 코드 그대로
    - raw.githubusercontent.com에서 import를 따라 필요한 파일만 받는다(SRC). GitHub API·git 없음
- 예산: 실패 포함 0.1달러. 누적 추정이 STOP_USD에 닿으면 앱을 멈춘다
  - 단가(modal.com/pricing): L4 $0.000222/s, CPU $0.0000131/core/s, 메모리 $0.00000222/GiB/s
  - 가중치는 GPU 없는 함수(prep)가 Volume runaway-tts-lab:/lab/stepedit에 받는다
  - GPU는 한 세션: 로딩 한 번 → 스모크 2줄(이 컴퓨터에서 ASR) → 테이크 1 나머지 → 테이크 2(역할마다 2줄 먼저)
  - 조각은 만들 때마다 Volume(/lab/stepedit/out)에 저장하고 이 컴퓨터로 보낸다
  - 비용 기록: model_test/stepedit/_cost.jsonl(실행마다 추정). runs.jsonl의 usd_est는 그 합
- 결과: model_test/stepedit/<역할>__<번호>__<테이크>.wav, model_test/stepedit/edits.json(쓴 태그·CER)

실행(프록시 때문에 PYTHONPATH에 pyfix)
  python3 web/voice/lab/stepedit_test.py            # 가중치 준비(처음 한 번) + GPU 생성
  python3 web/voice/lab/stepedit_test.py --prep     # 가중치만(CPU)
"""
import os, sys, io, re, json, time, math, argparse, subprocess, threading

import modal

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = os.path.dirname(HERE)
OUT_ROOT = os.path.join(VOICE, 'model_test')
OUT = os.path.join(OUT_ROOT, 'stepedit')
APP_NAME = 'runaway-lab-stepedit'
GPU = 'L4'
SRC = os.environ.get('STEPEDIT_SRC', os.path.expanduser('~/.cache/runaway/stepedit_src'))
RAW = 'https://raw.githubusercontent.com/stepfun-ai/Step-Audio-EditX/main/'

# 예산(달러)
RATE_GPU, RATE_CPU, RATE_MEM = 0.000222, 0.0000131, 0.00000222
GPU_RATE_EST = RATE_GPU + 2 * RATE_CPU + 12 * RATE_MEM    # GPU 컨테이너 1초 추정(코어 2, 메모리 12GiB로 넉넉히)
CPU_RATE_EST = 1 * RATE_CPU + 4 * RATE_MEM                # prep 컨테이너 1초 추정
CAP_USD = 0.10
STOP_USD = 0.08
GPU_TIMEOUT = int(os.environ.get('STEPEDIT_GPU_TIMEOUT', '240'))   # 남은 예산 시간에 맞춘 상한(시작 대기 제외)

ROOT = '/lab/stepedit'                        # Volume 안
EDITX = ROOT + '/Step-Audio-EditX'
ATOK = ROOT + '/Step-Audio-Tokenizer'
TOKDIR = ROOT + '/tok_fast'                   # 미리 변환해 둔 fast 토크나이저
FUNASR_ID = 'dengcunqin/speech_paraformer-large_asr_nat-zh-cantonese-en-16k-vocab8501-online'
LANG_TAG = '[Korean]'

# 테이크 2 편집: (역할, 번호) → (편집 종류, 정보). paralinguistic은 정보 자리에 태그를 넣은 새 문장
EDITS = {
    ('caster', 1): ('emotion', 'excited'),
    ('caster', 2): ('style', 'shout'),
    ('caster', 3): ('style', 'exaggerated'),
    ('caster', 4): ('emotion', 'humour'),
    ('caster', 5): ('emotion', 'surprised'),
    ('narrator', 1): ('style', 'deeply'),
    ('narrator', 2): ('style', 'whisper'),
    ('narrator', 3): ('emotion', 'coldness'),
    ('narrator', 4): ('style', 'whisper'),
    ('narrator', 5): ('paralinguistic', '닭이 울었다. [sigh] 그것은 어둠 속으로 사라졌다.'),
    ('dokkaebi', 1): ('paralinguistic', '헉, 헉… [breath] 형님! 방망이 좀 들어 주실 분?'),
    ('dokkaebi', 2): ('paralinguistic', '뒤에 누구 있나~? [laugh] 아무도 없네~?'),
    ('dokkaebi', 3): ('style', 'arrogant'),
    ('dokkaebi', 4): ('emotion', 'confusion'),
    ('dokkaebi', 5): ('paralinguistic', '어디 숨었냐~ [chuckle] 도깨비불 켠다~'),
    ('halmae', 1): ('paralinguistic', '아이고 허리야… [sigh] 할매 버리고 가나?'),
    ('halmae', 2): ('paralinguistic', '호호호, [laugh] 할매한테 지면 우짜노~'),
    ('halmae', 3): ('style', 'shout'),
    ('halmae', 4): ('emotion', 'fear'),
    ('halmae', 5): ('paralinguistic', '[Dissatisfaction-hnn] 요즘 젊은 것들은 인정도 없데이…'),
    ('cheonyeo', 1): ('emotion', 'sad'),
    ('cheonyeo', 2): ('emotion', 'fear'),
    ('cheonyeo', 3): ('style', 'whisper'),
    ('cheonyeo', 4): ('paralinguistic', '어디 숨었어… [breath] 나 혼자 두지 마…'),
    ('cheonyeo', 5): ('emotion', 'angry'),
    ('jeoseung', 1): ('style', 'serious'),
    ('jeoseung', 2): ('emotion', 'coldness'),
    ('jeoseung', 3): ('style', 'murmur'),
    ('jeoseung', 4): ('style', 'whisper'),
    ('jeoseung', 5): ('emotion', 'angry'),
}
EDIT_FIRST = [('caster', 1), ('caster', 2), ('narrator', 2), ('narrator', 5), ('dokkaebi', 1), ('dokkaebi', 2),
              ('halmae', 4), ('halmae', 5), ('cheonyeo', 1), ('cheonyeo', 5), ('jeoseung', 2), ('jeoseung', 4)]   # 예산이 모자라도 역할마다 2줄
SMOKE = [('caster', 2), ('jeoseung', 1)]

app = modal.App(APP_NAME)
lab = modal.Volume.from_name('runaway-tts-lab', create_if_missing=True)
image = (modal.Image.debian_slim(python_version='3.12')
         .pip_install('torch==2.9.1', 'torchaudio==2.9.1', 'numpy<2.3', 'transformers==4.57.6', 'sentencepiece==0.2.1', 'protobuf',
                      'safetensors', 'einops==0.8.1', 'onnxruntime-gpu==1.23.2', 'openai-whisper==20250625', 'hyperpyyaml==1.2.3',
                      'librosa==0.11.0', 'soundfile', 'scipy', 'sox==1.5.0', 'omegaconf==2.3.0', 'tqdm', 'requests', 'six', 'pyyaml',
                      'huggingface_hub==0.36.0', 'hf_transfer==0.1.9')
         .env({'HF_HUB_ENABLE_HF_TRANSFER': '1', 'TOKENIZERS_PARALLELISM': 'false', 'PYTHONUNBUFFERED': '1'})
         .add_local_dir(SRC, '/opt/stepedit'))


# ---------------- 엔진(컨테이너 안, 이 컴퓨터 CPU 시험에서도 같은 코드) ----------------
def wav_bytes(x, sr):
    import numpy as np, soundfile as sf
    b = io.BytesIO(); sf.write(b, np.asarray(x, dtype='float32').reshape(-1), sr, format='WAV', subtype='PCM_16'); return b.getvalue()


def read_wav(b):
    import numpy as np, soundfile as sf
    x, sr = sf.read(io.BytesIO(b) if isinstance(b, (bytes, bytearray)) else b, dtype='float32', always_2d=True)
    return x.mean(1).astype(np.float32), sr


def n_syll(text):
    return len(re.findall(r'[가-힣A-Za-z0-9]', text))


def cap_clone(text):
    """복제 출력 토큰 상한(41.67 토큰/초). 느린 역할·말줄임표까지 넉넉히"""
    sec = 2.0 + 0.45 * n_syll(text) + 0.6 * text.count('…')
    return int(min(15.0, sec) * 41.67) // 5 * 5 + 5


def edit_instruction(audio_text, edit_type, edit_info=None, text=None):
    """tts.py StepAudioTTS._build_audio_edit_instruction 그대로"""
    audio_text = audio_text.strip() if audio_text else ''
    if edit_type in {'emotion', 'speed'}:
        if edit_info == 'remove':
            return f'Remove any emotion in the following audio and the reference text is: {audio_text}\n'
        return f'Make the following audio more {edit_info}. The text corresponding to the audio is: {audio_text}\n'
    if edit_type == 'style':
        if edit_info == 'remove':
            return f'Remove any speaking styles in the following audio and the reference text is: {audio_text}\n'
        return f'Make the following audio more {edit_info} style. The text corresponding to the audio is: {audio_text}\n'
    if edit_type == 'paralinguistic':
        return f'Add some non-verbal sounds to make the audio more natural, the new text is : {text}\n  The text corresponding to the audio is: {audio_text}\n'
    raise ValueError(edit_type)


class Engine:
    """Step-Audio-EditX 추론. LLM은 직접 짠 배치 디코더, 오디오 토크나이저·보코더는 저장소 코드"""
    H, NH, NG, HD, NL = 3072, 48, 4, 64, 32
    A0, A1, EOS = 65536, 65536 + 5120, 3   # 오디오 토큰 범위(vq02 1024개 + vq06 4096개), <|EOT|>

    def __init__(self, root=ROOT, src='/opt/stepedit', device=None, log=print, cosy_dtype='bfloat16'):
        import types
        t0 = time.time()
        self.log = log
        if src not in sys.path: sys.path.insert(0, src)
        for name in ('vllm', 'funasr'):     # model_loader.py의 vllm import, funasr_detach/register.py의 'import funasr'(쓰지 않음)
            if name not in sys.modules:
                m = types.ModuleType(name); m.LLM = m.SamplingParams = None; sys.modules[name] = m
        import torch, torchaudio
        import soundfile as sf
        self.torch = torch
        self.dev = torch.device(device or ('cuda' if torch.cuda.is_available() else 'cpu'))

        def ta_load(f, *a, **k):        # torchaudio 2.9 load는 torchcodec(ffmpeg)이 필요하다. soundfile로 바꾼다
            x, sr = sf.read(f, dtype='float32', always_2d=True)
            return torch.from_numpy(x.T.copy()), sr
        torchaudio.load = ta_load
        if self.dev.type == 'cpu':      # funasr_detach가 .cuda()를 부른다(이 컴퓨터 CPU 시험용)
            torch.nn.Module.cuda = lambda self_, *a, **k: self_
            torch.Tensor.cuda = lambda self_, *a, **k: self_
        editx = os.path.join(root, 'Step-Audio-EditX')
        # LLM 가중치는 스레드로 올리고 그동안 나머지를 준비한다
        self._err = None
        th = threading.Thread(target=self._load_llm, args=(os.path.join(editx, 'model-00001.safetensors'),)); th.start()
        try:
            import onnxruntime
            if self.dev.type == 'cuda' and hasattr(onnxruntime, 'preload_dlls'):
                try: onnxruntime.preload_dlls()
                except Exception as e: log('  preload_dlls 실패:', repr(e)[:200])
            from transformers import AutoTokenizer
            tokdir = os.path.join(root, 'tok_fast')
            self.tok = AutoTokenizer.from_pretrained(tokdir if os.path.exists(os.path.join(tokdir, 'tokenizer.json')) else editx, trust_remote_code=True)
            from config.prompts import AUDIO_EDIT_CLONE_SYSTEM_PROMPT_TPL, AUDIO_EDIT_SYSTEM_PROMPT
            self.clone_tpl, self.edit_sys = AUDIO_EDIT_CLONE_SYSTEM_PROMPT_TPL, AUDIO_EDIT_SYSTEM_PROMPT
            from tokenizer import StepAudioTokenizer
            self.atok = StepAudioTokenizer(os.path.join(root, 'Step-Audio-Tokenizer'), model_source='local',
                                           funasr_model_id=FUNASR_ID)
            fm, orig = self.atok.funasr_model, self.atok.funasr_model.infer_encoder
            dev = 'cpu' if self.dev.type == 'cpu' else 0

            def infer_encoder(*a, **k):
                k['device'] = dev
                return orig(*a, **k)
            fm.infer_encoder = infer_encoder
            log('  onnx providers:', self.atok.ort_session.get_providers())
            if self.dev.type == 'cuda' and 'CUDAExecutionProvider' not in self.atok.ort_session.get_providers():
                so = onnxruntime.SessionOptions(); so.intra_op_num_threads = 2     # CUDA가 안 되면 CPU 스레드라도 늘린다
                self.atok.ort_session = onnxruntime.InferenceSession(os.path.join(root, 'Step-Audio-Tokenizer', 'speech_tokenizer_v1.onnx'),
                                                                     sess_options=so, providers=['CPUExecutionProvider'])
                log('  경고: speech tokenizer ONNX가 CPU로 돈다')
            from stepvocoder.cosyvoice2.cli.cosyvoice import CosyVoice
            self.cosy_dtype = getattr(torch, cosy_dtype)
            self.cosy = CosyVoice(os.path.join(editx, 'CosyVoice-300M-25Hz'), dtype=self.cosy_dtype, enable_cuda_graph=False)
        finally:
            th.join()
        if self._err: raise self._err
        self.load_s = time.time() - t0
        log(f'  엔진 준비 {self.load_s:.1f}초, 장치 {self.dev}')

    # ---- LLM ----
    def _load_llm(self, path):
        try:
            torch = self.torch
            from safetensors.torch import load_file
            t0 = time.time()
            sd = load_file(path, device=str(self.dev))
            g = lambda k: sd.pop(k)
            self.emb, self.norm, self.lm_head = g('model.embed_tokens.weight'), g('model.norm.weight'), g('lm_head.weight')
            self.layers = []
            for i in range(self.NL):
                p = f'model.layers.{i}.'
                self.layers.append({k: g(p + n) for k, n in (('q', 'self_attn.q_proj.weight'), ('k', 'self_attn.k_proj.weight'),
                                                             ('v', 'self_attn.v_proj.weight'), ('o', 'self_attn.o_proj.weight'),
                                                             ('g', 'mlp.gate_proj.weight'), ('u', 'mlp.up_proj.weight'),
                                                             ('d', 'mlp.down_proj.weight'), ('n1', 'input_layernorm.weight'),
                                                             ('n2', 'post_attention_layernorm.weight'))})
            assert not sd, list(sd)[:5]
            n, m = self.NH, 2 ** math.floor(math.log2(self.NH))      # modeling_step1.build_alibi_cache와 같은 기울기
            slopes = torch.pow(2.0 ** (-8.0 / m), torch.arange(1, m + 1))
            if m < n:
                slopes = torch.cat([slopes, torch.pow(2.0 ** (-4.0 / m), torch.arange(1, 1 + 2 * (n - m), 2))])
            self.slopes = slopes.to(self.dev, torch.float32)
            self.llm_s = time.time() - t0
        except Exception as e:
            self._err = e

    def _rms(self, x, w, eps=1e-5):
        var = x.float().pow(2).mean(-1, keepdim=True)
        return x * self.torch.rsqrt(var + eps).to(x.dtype) * w

    def _layers(self, x, attn):
        F = self.torch.nn.functional
        for i, w in enumerate(self.layers):
            h = self._rms(x, w['n1'])
            x = x + F.linear(attn(F.linear(h, w['q']), F.linear(h, w['k']), F.linear(h, w['v']), i), w['o'])
            h = self._rms(x, w['n2'])
            x = x + F.linear(F.silu(F.linear(h, w['g'])) * F.linear(h, w['u']), w['d'])
        return x

    def _logits(self, x):
        return self.torch.nn.functional.linear(self._rms(x[:, -1:], self.norm), self.lm_head)[:, -1].float()

    def _prefill(self, ids, b, start, K, V):
        """한 줄씩 미리 채운다(패딩 없음). 캐시 행 b의 [start, start+S)에 k, v를 쓴다"""
        torch, F = self.torch, self.torch.nn.functional
        S, G, R, D = len(ids), self.NG, self.NH // self.NG, self.HD
        x = F.embedding(torch.tensor([ids], device=self.dev), self.emb)
        i = torch.arange(S, device=self.dev)
        d = (i[:, None] - i[None, :]).float()
        bias = torch.where(d >= 0, -torch.sqrt(d.clamp(min=0))[None] * self.slopes[:, None, None], float('-inf')).to(x.dtype)
        mask = bias.view(G, R * S, S)[None]

        def attn(q, k, v, li):
            K[li][b, start:start + S] = k[0]; V[li][b, start:start + S] = v[0]
            qh = q.view(1, S, G, R, D).permute(0, 2, 3, 1, 4).reshape(1, G, R * S, D)
            o = F.scaled_dot_product_attention(qh, k.view(1, S, G, D).transpose(1, 2), v.view(1, S, G, D).transpose(1, 2), attn_mask=mask)
            return o.view(1, G, R, S, D).permute(0, 3, 1, 2, 4).reshape(1, S, self.H)
        return self._logits(self._layers(x, attn))

    def _decode(self, tok, p, K, V, pad):
        """모든 줄이 같은 위치 p의 토큰 하나씩. pad: (B, Ltot) True = 앞쪽 패딩"""
        torch, F = self.torch, self.torch.nn.functional
        B, G, R, D, L = tok.shape[0], self.NG, self.NH // self.NG, self.HD, p + 1
        x = F.embedding(tok[:, None], self.emb)
        row = -self.sqrt_rev[-L:][None] * self.slopes[:, None]                        # (48, L): -sqrt(p - j) * 기울기
        mask = row[None].expand(B, -1, -1).masked_fill(pad[:, None, :L], float('-inf')).to(x.dtype).view(B, G, R, L)

        def attn(q, k, v, li):
            K[li][:, p] = k[:, 0]; V[li][:, p] = v[:, 0]
            o = F.scaled_dot_product_attention(q.view(B, G, R, D), K[li][:, :L].view(B, L, G, D).transpose(1, 2),
                                               V[li][:, :L].view(B, L, G, D).transpose(1, 2), attn_mask=mask)
            return o.reshape(B, 1, self.H)
        return self._logits(self._layers(x, attn))

    def generate(self, prompts, caps, temperature=0.7, seed=0, greedy=False):
        """prompts: 토큰 id 목록들, caps: 줄마다 최대 출력 토큰. 출력: 오디오 토큰 목록들(EOS 제외)"""
        torch = self.torch
        with torch.inference_mode():
            B, P, T = len(prompts), max(len(x) for x in prompts), max(caps)
            Ltot = P + T + 1
            dt = self.emb.dtype
            K = [torch.zeros(B, Ltot, self.NG * self.HD, dtype=dt, device=self.dev) for _ in range(self.NL)]
            V = [torch.zeros_like(K[0]) for _ in range(self.NL)]
            pad = torch.ones(B, Ltot, dtype=torch.bool, device=self.dev)
            self.sqrt_rev = torch.sqrt(torch.arange(Ltot, device=self.dev, dtype=torch.float32)).flip(0)
            logits = []
            for b, ids in enumerate(prompts):
                logits.append(self._prefill(ids, b, P - len(ids), K, V))
                pad[b, P - len(ids):] = False
            logits = torch.cat(logits, 0)
            gen = torch.Generator(device=self.dev); gen.manual_seed(seed)
            capt = torch.tensor(caps, device=self.dev)
            done = torch.zeros(B, dtype=torch.bool, device=self.dev)
            out = torch.full((B, T), self.EOS, dtype=torch.long, device=self.dev)
            v02, v06 = (self.A0, self.A0 + 1024), (self.A0 + 1024, self.A1)
            for t in range(T):
                lo, hi = v02 if t % 5 < 2 else v06            # [02, 02, 06, 06, 06] 묶음
                cand = torch.cat([logits[:, lo:hi], logits[:, self.EOS:self.EOS + 1]], 1)
                if greedy:
                    idx = cand.argmax(-1)
                else:
                    idx = torch.multinomial(torch.softmax(cand / temperature, -1), 1, generator=gen)[:, 0]
                tok = torch.where(idx == hi - lo, self.EOS, idx + lo)
                tok = torch.where(done, self.EOS, tok)
                out[:, t] = tok
                done |= (tok == self.EOS) | (t + 1 >= capt)
                if t % 8 == 7 and bool(done.all()): break
                if t + 1 < T: logits = self._decode(tok, P + t, K, V, pad)
            res = []
            for b in range(B):
                r = out[b].tolist()
                res.append(r[:r.index(self.EOS)] if self.EOS in r else r)
            del K, V
            if self.dev.type == 'cuda': torch.cuda.empty_cache()
            return res

    # ---- 오디오 ----
    def audio_prompt(self, x, sr):
        """tts.py preprocess_prompt_wav와 같은 처리(파일 대신 배열)"""
        torch = self.torch
        with torch.inference_mode():
            wav = torch.from_numpy(x).float()[None]
            norm = wav.abs().max()
            if norm > 0.6: wav = wav / norm * 0.6
            feat, _ = self.cosy.frontend.extract_speech_feat(wav, sr)
            spk = self.cosy.frontend.extract_spk_embedding(wav, sr)
            vq0206, vq02, vq06 = self.atok.wav2token(wav, sr)
        return {'vq0206': vq0206, 'vq02': vq02, 'vq06': vq06, 'feat': feat, 'spk': spk,
                'tokens': self.atok.merge_vq0206_to_token_str(vq02, vq06)}

    def clone_ids(self, ref, ref_text, text):
        sys_prompt = self.clone_tpl.format(speaker='debug', prompt_text=ref_text, prompt_wav_tokens=ref['tokens'])
        return list(self.tok.apply_chat_template([{'role': 'system', 'content': sys_prompt}, {'role': 'user', 'content': text}],
                                                 tokenize=True, add_generation_prompt=True))

    def edit_ids(self, src, audio_text, edit_type, edit_info=None, text=None):
        ins = edit_instruction(audio_text, edit_type, edit_info, text)
        return list(self.tok.apply_chat_template([{'role': 'system', 'content': self.edit_sys},
                                                  {'role': 'user', 'content': f"{ins}\n{src['tokens']}\n"}],
                                                 tokenize=True, add_generation_prompt=True))

    def vocode(self, out, prompt):
        torch = self.torch
        with torch.inference_mode():
            w = self.cosy.token2wav_nonstream(torch.tensor(out, dtype=torch.long) - self.A0,
                                              torch.tensor([prompt['vq0206']], dtype=torch.long) - self.A0,
                                              prompt['feat'].to(torch.bfloat16), prompt['spk'].to(torch.bfloat16))
        return w.reshape(-1).float().numpy(), 24000


def plan(lines, refs_text):
    """작업 목록: 스모크 → 테이크 1(길이순 두 묶음) → 테이크 2(역할마다 2줄 먼저, 나머지)"""
    by = {(r, n): (r, n, t, ko) for r, n, t, ko, *_ in lines}
    take1 = [dict(role=r, n=n, take=1, text=t, ko=ko) for (r, n, t, ko) in by.values()]
    smoke = [j for j in take1 if (j['role'], j['n']) in SMOKE]
    rest = sorted([j for j in take1 if (j['role'], j['n']) not in SMOKE], key=lambda j: n_syll(j['text']))
    half = (len(rest) + 1) // 2
    edits = []
    for key in EDIT_FIRST + [k for k in by if k not in EDIT_FIRST]:
        r, n, t, ko = by[key]
        et, info = EDITS[key]
        edits.append(dict(role=r, n=n, take=2, text=t, ko=ko, edit_type=et, edit_info=None if et == 'paralinguistic' else info,
                          new_text=info if et == 'paralinguistic' else None))
    return [('t1_smoke', smoke), ('t1_short', rest[:half]), ('t1_long', rest[half:]),
            ('t2_first', edits[:len(EDIT_FIRST)]), ('t2_rest', edits[len(EDIT_FIRST):])]


def run_batches(eng, batches, refs, refs_text, save, deadline=None, seed=2026, log=print):
    """batches: plan() 결과. refs: {역할: (x, sr)}. save(job, x, sr) 를 조각마다 부른다(제너레이터)"""
    prompts = {}
    t1_audio = {}
    for name, jobs in batches:
        if not jobs: continue
        t0 = time.time()
        if deadline and time.time() > deadline:
            log(f'  {name}: 시간 상한으로 건너뜀'); yield {'ev': 'skip', 'batch': name, 'n': len(jobs)}; continue
        ids, caps, srcs, ok = [], [], [], []
        for j in jobs:
            try:
                if j['take'] == 1:
                    if j['role'] not in prompts: prompts[j['role']] = eng.audio_prompt(*refs[j['role']])
                    src = prompts[j['role']]
                    ids.append(eng.clone_ids(src, refs_text[j['role']], LANG_TAG + j['text']))
                    caps.append(cap_clone(j['text']))
                else:
                    key = (j['role'], j['n'])
                    if key not in t1_audio: raise RuntimeError('테이크 1 없음')
                    src = eng.audio_prompt(*t1_audio[key])
                    new = LANG_TAG + j['new_text'] if j['new_text'] else None
                    ids.append(eng.edit_ids(src, LANG_TAG + j['text'], j['edit_type'], j['edit_info'], new))
                    caps.append(min(1200, int(len(src['vq0206']) * 1.6) // 5 * 5 + 125))
                srcs.append(src); ok.append(j)
            except Exception as e:
                yield {'ev': 'clip', **j, 'err': repr(e)[:300]}
        if not ok: continue
        t1 = time.time()
        outs = eng.generate(ids, caps, seed=seed + len(name))
        t2 = time.time()
        for j, o, src, cap in zip(ok, outs, srcs, caps):
            try:
                if len(o) < 10: raise RuntimeError(f'출력 토큰 {len(o)}개')
                x, sr = eng.vocode(o, src)
                if j['take'] == 1: t1_audio[(j['role'], j['n'])] = (x, sr)
                save(j, x, sr)
                yield {'ev': 'clip', **j, 'wav': wav_bytes(x, sr), 'tokens': len(o), 'cap': cap, 'hit_cap': len(o) >= cap,
                       'prompt_len': len(ids[ok.index(j)])}
            except Exception as e:
                yield {'ev': 'clip', **j, 'err': repr(e)[:300]}
        t3 = time.time()
        steps = max(len(o) for o in outs)
        log(f'  {name}: {len(ok)}줄, 준비 {t1 - t0:.1f}s, 생성 {t2 - t1:.1f}s({steps}스텝), 보코더 {t3 - t2:.1f}s')
        yield {'ev': 'batch', 'batch': name, 'n': len(ok), 'prep_s': t1 - t0, 'gen_s': t2 - t1, 'voc_s': t3 - t2, 'steps': steps}


@app.function(image=image, volumes={'/lab': lab}, timeout=1200, cpu=1.0, memory=4096)
def prep():
    """가중치를 Volume에 받는다(GPU 없음). 필요한 파일만"""
    from huggingface_hub import snapshot_download
    t0 = time.time()
    snapshot_download('stepfun-ai/Step-Audio-EditX', local_dir=EDITX,
                      allow_patterns=['config.json', 'configuration_step1.py', 'modeling_step1.py', 'tokenizer.model', 'tokenizer_config.json',
                                      'model.safetensors.index.json', 'model-00001.safetensors', 'CosyVoice-300M-25Hz/cosyvoice.yaml',
                                      'CosyVoice-300M-25Hz/flow.pt', 'CosyVoice-300M-25Hz/hift.pt', 'CosyVoice-300M-25Hz/campplus.onnx',
                                      'CosyVoice-300M-25Hz/FLOW_VERSION'])
    snapshot_download('stepfun-ai/Step-Audio-Tokenizer', local_dir=ATOK,
                      allow_patterns=['linguistic_tokenizer.npy', 'speech_tokenizer_v1.onnx'] +
                      [f'{FUNASR_ID}/{f}' for f in ('am.mvn', 'config.yaml', 'configuration.json', 'model.pt', 'seg_dict', 'tokens.json', 'tokens.txt')])
    t1 = time.time()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(EDITX, trust_remote_code=True)
    tok.save_pretrained(TOKDIR)
    open(ROOT + '/.done', 'w').write('ok')
    lab.commit()
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(ROOT) for f in fs)
    return {'dl_s': round(t1 - t0), 'tok_s': round(time.time() - t1), 'gb': round(size / 1e9, 2), 'tok_class': type(tok).__name__}


@app.function(image=image, gpu=GPU, cpu=2.0, volumes={'/lab': lab}, timeout=GPU_TIMEOUT, max_containers=1, scaledown_window=2)
def gpu_run(batches, refs_b, refs_text, seed=2026):
    """한 세션: 로딩 한 번 → 묶음 차례로. 조각마다 Volume에 저장하고 보낸다"""
    t_start = time.time()
    yield {'ev': 'start'}
    os.makedirs(ROOT + '/out', exist_ok=True)
    logs = []
    log = lambda *a: (print(*a, flush=True), logs.append(' '.join(str(x) for x in a)))
    eng = Engine(log=log)
    import torch
    yield {'ev': 'loaded', 'load_s': eng.load_s, 'llm_s': getattr(eng, 'llm_s', None), 'gpu': torch.cuda.get_device_name(0),
           'logs': logs[:]}
    refs = {r: read_wav(b) for r, b in refs_b.items()}

    def save(j, x, sr):
        open(f"{ROOT}/out/{j['role']}__{j['n']}__{j['take']}.wav", 'wb').write(wav_bytes(x, sr))
    deadline = t_start + GPU_TIMEOUT - 25
    for ev in run_batches(eng, batches, refs, refs_text, save, deadline=deadline, seed=seed, log=log):
        if ev['ev'] == 'batch':
            lab.commit()
            ev['t'] = time.time() - t_start
        yield ev
    yield {'ev': 'done', 't': time.time() - t_start, 'mem_gb': torch.cuda.max_memory_allocated() / 1e9}


# ---------------- 이 컴퓨터 쪽 ----------------
def fetch_src(dest=SRC):
    """raw.githubusercontent.com에서 필요한 모듈만 import를 따라 받는다"""
    import urllib.request, urllib.error
    if os.path.exists(os.path.join(dest, '.complete')): return dest
    seen, missing = {}, set()

    def get(path):
        if path in seen: return seen[path]
        if path in missing: return None
        try:
            with urllib.request.urlopen(RAW + path, timeout=60) as r: data = r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404: missing.add(path); return None
            raise
        seen[path] = data
        p = os.path.join(dest, path); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'wb').write(data)
        return data

    def fetch_module(mod, names=()):
        path, todo = mod.replace('.', '/'), []
        if get(path + '.py') is not None: todo.append(path + '.py')
        else:
            if get(path + '/__init__.py') is not None: todo.append(path + '/__init__.py')
            for n in names:
                if get(f'{path}/{n}.py') is not None: todo.append(f'{path}/{n}.py')
                elif get(f'{path}/{n}/__init__.py') is not None: todo.append(f'{path}/{n}/__init__.py')
        parts = mod.split('.')
        for i in range(1, len(parts)):          # 상위 패키지 __init__ (없으면 빈 파일)
            d = '/'.join(parts[:i])
            if get(d + '/__init__.py') is None:
                p = os.path.join(dest, d, '__init__.py'); os.makedirs(os.path.dirname(p), exist_ok=True)
                if not os.path.exists(p): open(p, 'w').close()
        return todo

    def parse(path, src):
        pkg = path[:-len('/__init__.py')].replace('/', '.') if path.endswith('__init__.py') else path.rsplit('/', 1)[0].replace('/', '.')
        text = re.sub(r'\(\s*([^)]*?)\s*\)', lambda m: m.group(1).replace('\n', ' '), src.decode('utf-8', 'ignore'))
        out = []
        for m in re.finditer(r'^\s*from\s+(\.*)([\w\.]*)\s+import\s+([^\n#]+)', text, re.M):
            dots, mod = m.group(1), m.group(2)
            names = [x.strip().split(' as ')[0].strip() for x in m.group(3).split(',') if x.strip() and x.strip() != '*']
            if dots:
                base = pkg.split('.')
                if len(dots) > 1: base = base[:len(base) - (len(dots) - 1)]
                mod = '.'.join([b for b in base if b] + ([mod] if mod else []))
            if mod.split('.')[0] in ('stepvocoder', 'funasr_detach'): out.append((mod, names))
        for m in re.finditer(r'^\s*import\s+([\w\.]+)', text, re.M):
            if m.group(1).split('.')[0] in ('stepvocoder', 'funasr_detach'): out.append((m.group(1), []))
        return out
    seeds = ['stepvocoder.cosyvoice2.cli.cosyvoice', 'stepvocoder.cosyvoice2.cli.frontend', 'stepvocoder.cosyvoice2.flow.flow',
             'stepvocoder.cosyvoice2.embedding.dual_codebook', 'stepvocoder.cosyvoice2.transformer.upsample_encoder_v2',
             'stepvocoder.cosyvoice2.flow.flow_matching', 'stepvocoder.cosyvoice2.flow.decoder_dit', 'stepvocoder.cosyvoice2.hifigan.generator',
             'stepvocoder.cosyvoice2.hifigan.f0_predictor', 'stepvocoder.cosyvoice2.bigvgan.bigvgan', 'stepvocoder.cosyvoice2.matcha.audio',
             'funasr_detach', 'funasr_detach.auto.auto_model', 'funasr_detach.auto.auto_frontend', 'funasr_detach.register',
             'funasr_detach.models.paraformer_streaming.model', 'funasr_detach.models.scama.encoder', 'funasr_detach.models.sanm.encoder',
             'funasr_detach.models.paraformer.decoder', 'funasr_detach.models.paraformer.cif_predictor', 'funasr_detach.frontends.wav_frontend',
             'funasr_detach.models.specaug.specaug', 'funasr_detach.tokenizer.char_tokenizer']
    queue, done = [], set()
    for s in seeds: queue += fetch_module(s)
    while queue:
        p = queue.pop()
        if p in done: continue
        done.add(p)
        for mod, names in parse(p, seen[p]): queue += [x for x in fetch_module(mod, names) if x not in done]
    for f in ('funasr_detach/version.txt', 'tokenizer.py', 'utils.py', 'model_loader.py', 'config/prompts.py', 'config/edit_config.py'):
        if get(f) is None: raise RuntimeError('원본 파일 없음: ' + f)
    if get('config/__init__.py') is None: open(os.path.join(dest, 'config', '__init__.py'), 'w').close()
    open(os.path.join(dest, '.complete'), 'w').write(f'{len(done)} modules\n')
    print(f'  소스 {len(done)}개 모듈 → {dest}', flush=True)
    return dest


def stop_app(app_id):
    """이번 실행의 앱만 멈춘다"""
    if not app_id: return
    try:
        r = subprocess.run(['modal', 'app', 'list', '--json'], capture_output=True, text=True, timeout=60)
        for x in json.loads(r.stdout or '[]'):
            if x.get('app_id') == app_id and x.get('state') not in ('stopped', 'stopping'):
                subprocess.run(['modal', 'app', 'stop', '-y', app_id], timeout=60)
                print('  modal app stop', app_id, flush=True)
    except Exception as e:
        print(f'  앱 상태 확인 실패(수동 확인: modal app list, {app_id}):', e, flush=True)


def cost_so_far():
    p = os.path.join(OUT, '_cost.jsonl')
    if not os.path.exists(p): return 0.0
    return sum(json.loads(l).get('usd', 0) for l in open(p, encoding='utf-8') if l.strip())


def add_cost(rec):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, '_cost.jsonl'), 'a', encoding='utf-8') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')


class _Null:
    def __enter__(self): return self
    def __exit__(self, *a): return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prep', action='store_true', help='가중치만 받는다')
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()
    sys.path.insert(0, VOICE)
    import model_test as T
    import bake
    import numpy as np
    fetch_src()
    os.makedirs(OUT, exist_ok=True)
    spent0 = cost_so_far()
    print(f'  지금까지 추정 {spent0:.4f}달러 / 멈춤 {STOP_USD} / 상한 {CAP_USD}', flush=True)
    if spent0 >= STOP_USD: print('  예산 소진. 실행하지 않는다'); return
    refs_meta = json.load(open(os.path.join(OUT_ROOT, 'refs', 'refs.json'), encoding='utf-8'))
    refs_text = {r: refs_meta[r]['text'] for r in T.ROLES}
    refs_b = {r: open(os.path.join(OUT_ROOT, 'refs', f'{r}.wav'), 'rb').read() for r in T.ROLES}
    batches = plan(T.LINES, refs_text)
    need_prep = '.done' not in [os.path.basename(e.path) for e in lab.listdir('/stepedit')] if _vol_has_dir() else True

    t_wall, app_id, stop_flag = time.time(), None, {'stop': False, 'why': ''}
    clips, errs, cers, meta, gpu_info = 0, 0, [], {}, {}
    t_gpu0 = t_gpu1 = None
    prep_s = 0.0
    try:
        with modal.enable_output() if a.verbose else _Null(), app.run():
            app_id = app.app_id
            print('  app', app_id, flush=True)
            if need_prep or a.prep:
                t0 = time.time()
                try:
                    print('  prep:', prep.remote(), flush=True)
                finally:
                    prep_s = time.time() - t0
                    add_cost({'app_id': app_id, 'what': 'prep', 'secs': round(prep_s), 'usd': round(prep_s * CPU_RATE_EST, 5)})
            if a.prep: return
            spent = cost_so_far()
            budget_s = (STOP_USD - spent) / GPU_RATE_EST
            print(f'  GPU 예산 {budget_s:.0f}초(추정 단가 {GPU_RATE_EST:.6f}$/s), 함수 timeout {GPU_TIMEOUT}초', flush=True)
            if budget_s < 90: print('  GPU 예산 부족. 멈춘다'); return

            def watchdog():
                while not stop_flag.get('end'):
                    time.sleep(2)
                    if t_gpu0 and (time.time() - t_gpu0) >= budget_s and not stop_flag['stop']:
                        stop_flag.update(stop=True, why='예산(누적 추정 %.3f달러)' % STOP_USD)
                        print('  예산 도달: 앱을 멈춘다', flush=True)
                        subprocess.run(['modal', 'app', 'stop', '-y', app_id], timeout=60)
            threading.Thread(target=watchdog, daemon=True).start()
            t_gpu0 = time.time()
            smoke_bad = False
            try:
                for ev in gpu_run.remote_gen(batches, refs_b, refs_text, a.seed):
                    k = ev['ev']
                    if k == 'start': print(f'  GPU 시작(대기 {time.time() - t_gpu0:.0f}초)', flush=True)
                    elif k == 'loaded':
                        gpu_info = ev; print(f"  로딩 {ev['load_s']:.1f}s(LLM {ev['llm_s'] or 0:.1f}s), {ev['gpu']}", flush=True)
                        for l in ev.get('logs', []): print('   ', l, flush=True)
                    elif k == 'clip':
                        key = f"{ev['role']}__{ev['n']}__{ev['take']}"
                        if 'err' in ev:
                            errs += 1; meta[key] = {'err': ev['err']}; print('  실패', key, ev['err'], flush=True); continue
                        open(os.path.join(OUT, key + '.wav'), 'wb').write(ev['wav'])
                        clips += 1
                        meta[key] = {'take': ev['take'], 'text': ev['text'], 'tokens': ev['tokens'], 'cap': ev['cap'], 'hit_cap': ev['hit_cap']}
                        if ev['take'] == 2: meta[key].update(edit_type=ev['edit_type'], edit_info=ev['edit_info'], new_text=ev['new_text'])
                        try:            # 이 컴퓨터 쪽 검사가 실패해도 GPU 흐름은 계속
                            x, sr = read_wav(ev['wav'])
                            ref = re.sub(r'\[[^\]]*\]', '', ev['new_text'] if ev.get('new_text') else ev['text'])
                            hyp = bake.transcribe(x, sr); c = bake.cer(bake.norm(ref), bake.norm(hyp))
                            cers.append(c); meta[key].update(dur=round(len(x) / sr, 2), cer=round(c, 3), hyp=hyp)
                            print(f"  {key:16s} {len(x) / sr:4.1f}s CER {c:.2f}{' 상한' if ev['hit_cap'] else ''}  {hyp}", flush=True)
                        except Exception as e:
                            print('  ASR 실패', key, repr(e)[:200], flush=True)
                    elif k == 'batch':
                        print(f"  묶음 {ev['batch']}: {ev['n']}줄 생성 {ev['gen_s']:.1f}s({ev['steps']}스텝) 보코더 {ev['voc_s']:.1f}s 준비 {ev['prep_s']:.1f}s, GPU {ev['t']:.0f}s", flush=True)
                        if ev['batch'] == 't1_smoke':
                            sc = [meta[f'{r}__{n}__1']['cer'] for r, n in SMOKE if 'cer' in meta.get(f'{r}__{n}__1', {})]
                            if not sc or sum(sc) / len(sc) > 0.6:
                                smoke_bad = True; stop_flag.update(stop=True, why=f'스모크 실패(CER {sc})')
                                print('  스모크 실패: 한국어를 못 읽는다. 멈춘다', flush=True)
                                break
                    elif k == 'skip': print('  건너뜀', ev, flush=True)
                    elif k == 'done': print(f"  GPU 끝 {ev['t']:.0f}s, 최대 메모리 {ev['mem_gb']:.1f}GB", flush=True)
            except Exception as e:
                print('  GPU 호출 중단:', repr(e)[:300], flush=True)
            finally:
                t_gpu1 = time.time()
                stop_flag['end'] = True
    finally:
        gpu_s = (t_gpu1 - t_gpu0) if (t_gpu0 and t_gpu1) else 0
        if gpu_s: add_cost({'app_id': app_id, 'what': 'gpu', 'gpu': GPU, 'secs': round(gpu_s), 'usd': round(gpu_s * GPU_RATE_EST, 5)})
        total = cost_so_far()
        if meta:
            prev = {}
            p = os.path.join(OUT, 'edits.json')
            if os.path.exists(p): prev = json.load(open(p, encoding='utf-8'))
            prev.update(meta)
            json.dump(prev, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        if app_id and gpu_s:            # prep만 한 실행은 _cost.jsonl에만 남긴다
            rec = {'what': 'stepedit', 'app_id': app_id, 'clips': clips, 'errs': errs, 'gen_s': round(gpu_s), 'wall_s': round(time.time() - t_wall),
                   'gpu': GPU, 'usd_est': round(total, 4)}
            if cers: rec.update(cer=round(sum(cers) / len(cers), 3), cer_over_03=sum(c > 0.3 for c in cers))
            if stop_flag.get('why'): rec['note'] = stop_flag['why']
            with open(os.path.join(OUT_ROOT, 'runs.jsonl'), 'a', encoding='utf-8') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            print('  runs.jsonl:', rec, flush=True)
        stop_app(app_id)


def _vol_has_dir():
    try:
        return any(os.path.basename(e.path.rstrip('/')) == 'stepedit' for e in lab.listdir('/'))
    except Exception:
        return False


if __name__ == '__main__':
    main()
