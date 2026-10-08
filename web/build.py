"""app.html + core.js + game.js + sound.js + race_lines.md + voice_manifest.js + replays.js → dist/runaway.html, docs/app/ (Pages)
대사: web/race_lines.md(web/linebook.py로 읽는다). 구운 음성은 web/voice/bake.py → static/voice/race.bin, 없는 줄은 기기 음성
녹음: web/sounds/<소리id>[_번호].(mp3|m4a|ogg|wav). 있으면 그 소리만 합성음 대신 녹음. 규격은 web/sounds/README.md"""
import os, json, re, hashlib, shutil
# 배포 주소. Pages 주소가 바뀌면 여기 한 줄만 고치면 된다 (공유 카드·OG·매니페스트가 모두 이걸 쓴다)
SITE = 'https://cjsdudwls1.github.io/RUNA-WAY/'   # Pages 경로는 대소문자를 구분한다. 소문자는 404
# 방문자 수 확인용. goatcounter.com 무료 계정을 만들고 코드만 넣으면 켜진다. 비우면 아무것도 안 붙는다
COUNTER = ''

here = os.path.dirname(os.path.abspath(__file__))
r = lambda n: open(os.path.join(here, n), encoding='utf-8').read()


import sys
sys.path.insert(0, here)
import linebook
race_lines, race_info = linebook.parse()
errs = linebook.check(race_lines)
if errs:   # 구울 수 없는 대사. 앱에 넣기 전에 막는다
    print('\n'.join(['대사표 오류 (web/race_lines.md):'] + errs)); sys.exit(1)
lines_js = 'const RACE_LINES = ' + json.dumps(race_lines, ensure_ascii=False) + ', RACE_LINE_INFO = ' + json.dumps(race_info, ensure_ascii=False) + ';\n'
# 해설 엔진이 쓰는 키가 대사표에 다 있는지. 오타 난 키는 조용히 안 나오므로 빌드에서 알린다
used = set(re.findall(r"say\('([a-z0-9_]+)'", r('game.js'))) | set(re.findall(r"'((?:lead|behind)_(?:small|big|huge)|tie|win(?:_close)?|lose(?:_close)?|overtake_me|overtaken|set_win|set_lose|last_set|set_start|interval_win|interval_lose|draw)'", r('game.js')))
missing = sorted(k for k in used if k not in race_lines)
if missing:
    print('대사표에 없는 상황:', missing)
# 구운 대사(web/voice/bake.py 산출물). 없거나 대사를 고친 뒤 안 구웠으면 그 줄만 기기 음성으로 읽는다
vm = r('voice_manifest.js') if os.path.exists(os.path.join(here, 'voice_manifest.js')) else ''
if vm:
    have = set(json.loads(vm[vm.index('{'):vm.rindex('}') + 1])['clips'])
    want = [c for c, _, _ in linebook.clips(race_lines)]
    stale = [c for c in want if c not in have]
    if stale:
        print(f'안 구운 대사 {len(stale)}조각 (python3 web/voice/bake.py). 예:', stale[:3])

ids = re.findall(r"\{ id: '([a-z_]+)'", r('sound.js'))
sd = os.path.join(here, 'sounds')
sidx, sfiles = {}, []
if os.path.isdir(sd):
    for f in sorted(os.listdir(sd)):
        k, ext = os.path.splitext(f)
        if ext.lower() not in ('.mp3', '.ogg', '.m4a', '.wav'):
            continue
        m = re.match(r'^([a-z_]+?)(?:_(\d+))?$', k)
        if not m or m.group(1) not in ids:
            print('소리 파일 이름이 목록에 없음, 건너뜀:', f); continue
        sidx.setdefault(m.group(1), []).append(f); sfiles.append(f)
sver = hashlib.sha1(b''.join(open(os.path.join(sd, f), 'rb').read() for f in sfiles)).hexdigest()[:10] if sfiles else ''
sounds_js = 'const SOUND_INDEX = ' + json.dumps(sidx) + ', SOUND_VER = ' + json.dumps(sver) + ';\n'

html = (r('app.html').replace('<!--SITE-->', SITE.replace('https://', '').rstrip('/')).replace('<!--CORE-->', r('core.js')).replace('<!--GAME-->', r('game.js'))
        .replace('<!--SOUND-->', r('sound.js')).replace('<!--LINES-->', lines_js).replace('<!--VOICE-->', vm).replace('<!--REPLAYS-->', r('replays.js')).replace('<!--SOUNDS-->', sounds_js))
os.makedirs(os.path.join(here, 'dist'), exist_ok=True)
out = os.path.join(here, 'dist', 'runaway.html')
open(out, 'w', encoding='utf-8').write(html)
HEAD = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>러너웨이 · 정한 페이스로 따라오는 상대</title>
<meta name="description" content="경주 모드: 긁는 상대와 경주. 공포 모드: 쫓아오는 아무개씨를 피해 도망. 상대는 내가 정한 페이스로 달린다. 설치 없이 브라우저에서 바로.">
<meta name="theme-color" content="#0a0f0d">
<meta property="og:type" content="website">
<meta property="og:title" content="러너웨이 · 정한 페이스로 따라오는 상대">
<meta property="og:description" content="일반런, 빌드업, 인터벌. 상대는 내가 정한 페이스 그대로 달린다. 이기거나, 도망치거나.">
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
for old in ('voice', 'credits.html'):   # voice/는 static/에 있으면 아래에서 다시 복사된다
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
if sfiles:
    os.makedirs(sp)
    for f in sfiles:
        shutil.copy2(os.path.join(sd, f), os.path.join(sp, f))
print('wrote', out, len(html.encode()) // 1024, 'KB; 대사', sum(len(v) for v in race_lines.values()), '줄 /', len(race_lines), '상황; 녹음', len(sfiles), '개', sorted(sidx) or '', '; pages: docs/app/index.html +', copied)
