"""sim/data/animals.json → web/animals.js"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sim'))
from runaway_sim.animals import load_all
rows = []
for a in load_all():
    r = a.raw
    rows.append(dict(id=a.id, nameKo=a.name_ko, track=a.track, tier=a.tier, constant=a.constant, sprintCms=a.sprint_cms, sprintS=a.sprint_s,
                     cruiseCms=a.cruise_cms, recoverS=a.recover_s, dvPm=a.dv_pm, dtPm=a.dt_pm, gPm=a.g_pm, detectCm=a.detect_cm,
                     target30Kmh=a.target30_kmh, sprintKmh=r['sprint_kmh'], hits=r.get('sim_hits_7_10_13')))
out = os.path.join(os.path.dirname(__file__), 'animals.js')
open(out, 'w', encoding='utf-8').write('// 자동 생성. 출처 sim/data/animals.json (web/gen_animals.py)\nconst ANIMALS = ' + json.dumps(rows, ensure_ascii=False) + ';\nif (typeof module !== "undefined") module.exports = ANIMALS;\n')
print('wrote', out, len(rows))
