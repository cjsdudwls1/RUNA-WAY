"""app.html + core.js + animals.js + replays.js → dist/runaway.html (단일 파일)."""
import os
here = os.path.dirname(os.path.abspath(__file__))
r = lambda n: open(os.path.join(here, n), encoding='utf-8').read()
html = r('app.html').replace('<!--CORE-->', r('core.js')).replace('<!--ANIMALS-->', r('animals.js')).replace('<!--REPLAYS-->', r('replays.js'))
os.makedirs(os.path.join(here, 'dist'), exist_ok=True)
out = os.path.join(here, 'dist', 'runaway.html')
open(out, 'w', encoding='utf-8').write(html)
print('wrote', out, len(html.encode()) // 1024, 'KB')
