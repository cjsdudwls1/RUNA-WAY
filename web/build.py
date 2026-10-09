"""app.html + core.js + game.js + sound.js + replays.js → dist/runaway.html, docs/app/ (Pages)
녹음 후보: web/sounds/<소리id>/<후보>[-번호].(mp3|m4a|ogg|wav). 앱의 소리 검수에서 고른다. 규격은 web/sounds/README.md"""
import os, json, re, hashlib, shutil
# 배포 주소. Pages 주소가 바뀌면 여기 한 줄만 고치면 된다 (공유 카드·OG·매니페스트가 모두 이걸 쓴다)
SITE = 'https://cjsdudwls1.github.io/RUNA-WAY/'   # Pages 경로는 대소문자를 구분한다. 소문자는 404
# 방문자 수 확인용. goatcounter.com 무료 계정을 만들고 코드만 넣으면 켜진다. 비우면 아무것도 안 붙는다
COUNTER = ''

here = os.path.dirname(os.path.abspath(__file__))
r = lambda n: open(os.path.join(here, n), encoding='utf-8').read()


ids = re.findall(r"\{ id: '([a-z_]+)'", r('sound.js'))
# 녹음 후보: web/sounds/<소리id>/<후보>.mp3, 여러 개로 한 벌이면 <후보>-<번호>.mp3 (발소리처럼). 앱에서 후보를 골라 쓴다
sd = os.path.join(here, 'sounds')
sidx, sfiles, sinfo = {}, [], {}
credits = {c['file']: c for c in json.load(open(os.path.join(sd, 'credits.json'), encoding='utf-8'))} if os.path.exists(os.path.join(sd, 'credits.json')) else {}
for sid in sorted(os.listdir(sd)) if os.path.isdir(sd) else []:
    if not os.path.isdir(os.path.join(sd, sid)): continue
    if sid not in ids:
        print('소리 폴더가 목록에 없음, 건너뜀:', sid); continue
    for f in sorted(os.listdir(os.path.join(sd, sid))):
        k, ext = os.path.splitext(f)
        if ext.lower() not in ('.mp3', '.ogg', '.m4a', '.wav'): continue
        cand, rel = re.sub(r'-\d+$', '', k), sid + '/' + f
        sidx.setdefault(sid, {}).setdefault(cand, []).append(rel); sfiles.append(rel)
        c = credits.get(rel)
        if c and sid + '/' + cand not in sinfo: sinfo[sid + '/' + cand] = c.get('title', '')[:60] + (' · ' + c['author'][:24] if c.get('author') and c['author'] != '러너웨이' else '')
sver = hashlib.sha1(b''.join(open(os.path.join(sd, f), 'rb').read() for f in sfiles)).hexdigest()[:10] if sfiles else ''
sounds_js = 'const SOUND_INDEX = ' + json.dumps(sidx) + ', SOUND_INFO = ' + json.dumps(sinfo, ensure_ascii=False) + ', SOUND_VER = ' + json.dumps(sver) + ';\n'

html = (r('app.html').replace('<!--SITE-->', SITE.replace('https://', '').rstrip('/')).replace('<!--CORE-->', r('core.js')).replace('<!--GAME-->', r('game.js'))
        .replace('<!--SOUND-->', r('sound.js')).replace('<!--REPLAYS-->', r('replays.js')).replace('<!--SOUNDS-->', sounds_js))
os.makedirs(os.path.join(here, 'dist'), exist_ok=True)
out = os.path.join(here, 'dist', 'runaway.html')
open(out, 'w', encoding='utf-8').write(html)
HEAD = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>러너웨이 · 뒤에서 쫓아오는 추격자</title>
<meta name="description" content="추격자가 내가 정한 페이스로 뒤에서 쫓아온다. 발소리, 숨소리, 으르렁. 잡히지 마라. 설치 없이 브라우저에서 바로.">
<meta name="theme-color" content="#0c0c0c">
<meta property="og:type" content="website">
<meta property="og:title" content="러너웨이 · 뒤에서 쫓아오는 추격자">
<meta property="og:description" content="일반런, 빌드업, 인터벌. 추격자는 내가 정한 페이스 그대로 쫓아온다. 잡히지 마라.">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-512.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="러너웨이">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
{COUNTER}</head><body>"""

pages = os.path.join(here, '..', 'docs', 'app'); os.makedirs(pages, exist_ok=True)
cjs = ('<script data-goatcounter="https://%s.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>\n' % COUNTER) if COUNTER else ''
head = HEAD.replace('{SITE}', SITE).replace('{COUNTER}', cjs)
open(os.path.join(pages, 'index.html'), 'w', encoding='utf-8').write(head + html + '</body></html>')
# 예전 빌드 산출물(음성 팩, 동물 녹음 출처)이 남지 않게
for old in ('voice', 'credits.html'):
    p = os.path.join(pages, old)
    if os.path.isdir(p): shutil.rmtree(p)
    elif os.path.exists(p): os.remove(p)
static = os.path.join(here, 'static'); copied = []
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
sp = os.path.join(pages, 'sounds'); shutil.rmtree(sp, ignore_errors=True)
for f in sfiles:
    os.makedirs(os.path.dirname(os.path.join(sp, f)), exist_ok=True)
    shutil.copy2(os.path.join(sd, f), os.path.join(sp, f))
print('wrote', out, len(html.encode()) // 1024, 'KB; 녹음', len(sfiles), '개, 후보', sum(len(v) for v in sidx.values()), '개', {k: len(v) for k, v in sorted(sidx.items())}, '; pages: docs/app/index.html +', copied)
