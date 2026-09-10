"""sim/data/animals.json → core/src/main/kotlin/kr/runaway/core/Animals.kt. 단일 출처 유지. 변경 시 재실행."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'sim'))
from runaway_sim.animals import load_all
out = ['package kr.runaway.core', '', '// 자동 생성. 수정 금지. 출처: sim/data/animals.json (core/tools/gen_animals.py)', '',
       'object Animals {', '    val all: List<Animal> = listOf(']
for a in load_all():
    out.append(f'        Animal("{a.id}", "{a.name_ko}", \'{a.track}\', {a.tier}, {str(a.constant).lower()}, {a.sprint_cms}, {a.sprint_s}, {a.cruise_cms}, {a.recover_s}, {a.dv_pm}, {a.dt_pm}, {a.g_pm}, {a.detect_cm}, {a.target30_kmh}),')
out += ['    )', '    fun get(id: String): Animal = all.first { it.id == id }', '}', '']
path = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'kotlin', 'kr', 'runaway', 'core', 'Animals.kt')
open(path, 'w', encoding='utf-8').write('\n'.join(out))
print('wrote', path)
