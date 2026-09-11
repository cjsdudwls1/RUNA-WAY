"""app.html + core.js + animals.js + replays.js + sounds/ → dist/runaway.html (단일 파일).
sounds/<animalId 또는 동물군>_<roam|sprint|tired>.(mp3|ogg|m4a|wav) 를 base64로 포함. 동물군: bird canine feline reptile hoof small"""
import os, base64, json
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
html = r('app.html').replace('<!--CORE-->', r('core.js')).replace('<!--ANIMALS-->', r('animals.js')).replace('<!--REPLAYS-->', r('replays.js')).replace('<!--SOUNDS-->', sounds_js)
os.makedirs(os.path.join(here, 'dist'), exist_ok=True)
out = os.path.join(here, 'dist', 'runaway.html')
open(out, 'w', encoding='utf-8').write(html)
pages = os.path.join(here, '..', 'docs', 'app'); os.makedirs(pages, exist_ok=True)
open(os.path.join(pages, 'index.html'), 'w', encoding='utf-8').write('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' + html + '</body></html>')
print('wrote', out, len(html.encode()) // 1024, 'KB, sounds:', list(snd) or 'none', '; pages copy docs/app/index.html')
