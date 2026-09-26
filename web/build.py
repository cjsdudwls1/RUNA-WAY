"""app.html + core.js + animals.js + replays.js → dist/runaway.html, docs/app/ (Pages)
실제 동물 소리: web/sounds/<동물id 또는 동물군>_<roam|sprint|tired>[_n].(mp3|m4a|ogg|wav)
  페이지에는 목록만 넣고 파일은 docs/app/sounds/로 복사한다. 앱은 고른 동물 것만 받는다. 규격은 web/sounds/README.md"""
import os, json, re, hashlib, html as H
# 배포 주소. Pages 주소가 바뀌면 여기 한 줄만 고치면 된다 (공유 카드·OG·매니페스트가 모두 이걸 쓴다)
SITE = 'https://cjsdudwls1.github.io/RUNA-WAY/'   # Pages 경로는 대소문자를 구분한다. 소문자는 404
# 방문자 수 확인용. goatcounter.com 무료 계정을 만들고 코드만 넣으면 켜진다. 비우면 아무것도 안 붙는다
COUNTER = ''

here = os.path.dirname(os.path.abspath(__file__))
r = lambda n: open(os.path.join(here, n), encoding='utf-8').read()
sd = os.path.join(here, 'sounds')
sidx, sfiles = {}, []
if os.path.isdir(sd):
    for f in sorted(os.listdir(sd)):
        k, ext = os.path.splitext(f)
        if ext.lower() not in ('.mp3', '.ogg', '.m4a', '.wav'):
            continue
        m = re.match(r'^([a-z]+)_(roam|sprint|tired|step|line_(?:spot|sprint|near|hit|escape|taunt))(?:_\d+)?$', k)
        if not m:
            print('소리 파일 이름 규칙 위반, 건너뜀:', f); continue
        sidx.setdefault(m.group(1) + '_' + m.group(2), []).append(f); sfiles.append(f)
sver = hashlib.sha1(b''.join(open(os.path.join(sd, f), 'rb').read() for f in sfiles)).hexdigest()[:10] if sfiles else ''
# 배경음악: web/music/<animal|monster>_<home|run>.mp3
md = os.path.join(here, 'music')
midx = {}
if os.path.isdir(md):
    for f in sorted(os.listdir(md)):
        k, ext = os.path.splitext(f)
        if ext.lower() in ('.mp3', '.m4a', '.ogg') and re.match(r'^(animal|monster)_(home|run)$', k):
            midx[k] = f
mver = hashlib.sha1(b''.join(open(os.path.join(md, f), 'rb').read() for f in midx.values())).hexdigest()[:10] if midx else ''
sounds_js = ('const SOUND_INDEX = ' + json.dumps(sidx) + ', SOUND_VER = ' + json.dumps(sver) + ';\n'
             'const MUSIC_INDEX = ' + json.dumps(midx) + ', MUSIC_VER = ' + json.dumps(mver) + ';\n')
# 음성 팩 목차(web/voice/bake.py 산출물). 조각 파일은 static/voice/에 있고 런타임에 받는다
vm = r('voice_manifest.js') if os.path.exists(os.path.join(here, 'voice_manifest.js')) else ''
has_credits = os.path.exists(os.path.join(here, 'sounds', 'credits.json'))
credits_link = '<p class="sub"><a href="credits.html" target="_blank" rel="noopener" style="color:var(--green)">동물 소리 출처</a></p>' if has_credits else ''
html = r('app.html').replace('<!--SITE-->', SITE.replace('https://', '').rstrip('/')).replace('<!--CORE-->', r('core.js')).replace('<!--ANIMALS-->', r('animals.js')).replace('<!--REPLAYS-->', r('replays.js')).replace('<!--SOUNDS-->', sounds_js).replace('<!--VOICE-->', vm).replace('<!--CREDITS-->', credits_link)
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
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="러너웨이">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
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
# 녹음 파일과 출처 페이지. 라이선스(CC-BY 등)는 출처 표시를 요구한다
sp = os.path.join(pages, 'sounds'); shutil.rmtree(sp, ignore_errors=True)
if sfiles:
    os.makedirs(sp)
    for f in sfiles:
        shutil.copy2(os.path.join(sd, f), os.path.join(sp, f))
mp = os.path.join(pages, 'music'); shutil.rmtree(mp, ignore_errors=True)
if midx:
    os.makedirs(mp)
    for f in midx.values():
        shutil.copy2(os.path.join(md, f), os.path.join(mp, f))
cj = os.path.join(sd, 'credits.json')
if os.path.exists(cj):
    rows = [r for r in json.load(open(cj, encoding='utf-8')) if r.get('file') in set(sfiles)]   # 빼낸 파일(교체 대기 등)의 출처는 싣지 않는다
    mc = os.path.join(md, 'credits.json')
    if os.path.exists(mc):
        rows += json.load(open(mc, encoding='utf-8'))
    tr = ''.join('<tr><td>%s</td><td><a href="%s">%s</a></td><td>%s</td><td>%s</td></tr>' % tuple(H.escape(str(x)) for x in (
        r.get('file', ''), r.get('source_url', ''), r.get('title') or r.get('source_url', ''), r.get('author', ''), r.get('license', ''))) for r in rows)
    open(os.path.join(pages, 'credits.html'), 'w', encoding='utf-8').write(
        '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>러너웨이 · 소리 출처</title><style>body{background:#0a0f0d;color:#dfe9e4;font:14px/1.5 system-ui,sans-serif;margin:16px}'
        'a{color:#3ff2a5;word-break:break-all}table{border-collapse:collapse;width:100%}td{border-bottom:1px solid #1f2b27;padding:6px 4px;vertical-align:top}</style></head>'
        '<body><h1>소리·음악 출처</h1><table>' + tr + '</table></body></html>')
elif os.path.exists(os.path.join(pages, 'credits.html')):
    os.remove(os.path.join(pages, 'credits.html'))
print('wrote', out, len(html.encode()) // 1024, 'KB, sounds:', len(sfiles), 'files', sorted(sidx) or '', '; pages: docs/app/index.html +', copied)
