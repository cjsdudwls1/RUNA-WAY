"""app.html + core.js + animals.js + replays.js + sounds/ → dist/runaway.html (단일 파일).
sounds/<animalId 또는 동물군>_<roam|sprint|tired>.(mp3|ogg|m4a|wav) 를 base64로 포함. 동물군: bird canine feline reptile hoof small"""
import os, base64, json
# 배포 주소. Pages 주소가 바뀌면 여기 한 줄만 고치면 된다 (공유 카드·OG·매니페스트가 모두 이걸 쓴다)
SITE = 'https://cjsdudwls1.github.io/RUNA-WAY/'   # Pages 경로는 대소문자를 구분한다. 소문자는 404
# 방문자 수 확인용. goatcounter.com 무료 계정을 만들고 코드만 넣으면 켜진다. 비우면 아무것도 안 붙는다
COUNTER = ''

here = os.path.dirname(os.path.abspath(__file__))
r = lambda n: open(os.path.join(here, n), encoding='utf-8').read()
snd = {}
sd = os.path.join(here, 'sounds')
if os.path.isdir(sd):
    for f in sorted(os.listdir(sd)):
        k, ext = os.path.splitext(f)
        if ext.lower() in ('.mp3', '.ogg', '.m4a', '.wav'):
            snd[k] = base64.b64encode(open(os.path.join(sd, f), 'rb').read()).decode()
sounds_js = 'const SOUNDS = ' + json.dumps(snd) + ';\n'
# 음성 팩 목차(web/voice/bake.py 산출물). 조각 파일은 static/voice/에 있고 런타임에 받는다
vm = r('voice_manifest.js') if os.path.exists(os.path.join(here, 'voice_manifest.js')) else ''
html = r('app.html').replace('<!--SITE-->', SITE.replace('https://', '').rstrip('/')).replace('<!--CORE-->', r('core.js')).replace('<!--ANIMALS-->', r('animals.js')).replace('<!--REPLAYS-->', r('replays.js')).replace('<!--SOUNDS-->', sounds_js).replace('<!--VOICE-->', vm)
os.makedirs(os.path.join(here, 'dist'), exist_ok=True)
out = os.path.join(here, 'dist', 'runaway.html')
open(out, 'w', encoding='utf-8').write(html)
HEAD = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>러너웨이 · 뒤에서 진짜 동물이 쫓아온다</title>
<meta name="description" content="실측 속도와 지구력 그대로의 동물 무리가 GPS로 당신을 쫓는다. 설치 없이 브라우저에서 바로.">
<meta name="theme-color" content="#0a0f0d">
<meta property="og:type" content="website">
<meta property="og:title" content="러너웨이 · 뒤에서 진짜 동물이 쫓아온다">
<meta property="og:description" content="닭한테서도 도망쳐 보면 안다. 실측 속도와 지구력 그대로의 동물이 GPS로 쫓아온다.">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-512.png">
{COUNTER}</head><body>"""

import shutil
pages = os.path.join(here, '..', 'docs', 'app'); os.makedirs(pages, exist_ok=True)
cjs = ('<script data-goatcounter="https://%s.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>\n' % COUNTER) if COUNTER else ''
head = HEAD.replace('{SITE}', SITE).replace('{COUNTER}', cjs)
open(os.path.join(pages, 'index.html'), 'w', encoding='utf-8').write(head + html + '</body></html>')
static = os.path.join(here, 'static'); copied = []
import hashlib
build_id = hashlib.sha1(html.encode()).hexdigest()[:10]
if os.path.isdir(static):
    for f in sorted(os.listdir(static)):
        if f.startswith('_'):
            continue
        src, dst = os.path.join(static, f), os.path.join(pages, f)
        if os.path.isdir(src):
            shutil.rmtree(dst, ignore_errors=True); shutil.copytree(src, dst)
        elif f == 'sw.js':   # 빌드마다 캐시 이름이 바뀌어야 옛 버전이 남지 않는다
            open(dst, 'w', encoding='utf-8').write(open(src, encoding='utf-8').read().replace('<!--BUILD-->', build_id))
        else:
            shutil.copy2(src, dst)
        copied.append(f)
print('wrote', out, len(html.encode()) // 1024, 'KB, sounds:', list(snd) or 'none', '; pages: docs/app/index.html +', copied)
