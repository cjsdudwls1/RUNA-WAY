"""Python 시뮬의 결과를 골든으로 저장 → Kotlin 이식 검증. python3 core/tools/gen_golden.py"""
import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'sim'))
from runaway_sim.synth import generate, write_gpx, pace_steady
from runaway_sim.gpx import load_track
from runaway_sim.animals import get
from runaway_sim.session import run
res = os.path.join(os.path.dirname(__file__), '..', 'src', 'test', 'resources')
pts, _ = generate(course_m=5000, pace=pace_steady(10.0), seed=11, canyon=True, dropout=True, stop=True, noise_m=4.0)
d = tempfile.mkdtemp(); p = os.path.join(d, 't.gpx'); write_gpx(p, pts)
track = load_track(p)
with open(os.path.join(res, 'golden_track.csv'), 'w') as f:
    for (t, dist, speed, acc) in track:
        f.write(f'{t},{dist},{speed},{acc:.3f}\n')
with open(os.path.join(res, 'golden_expected.csv'), 'w') as f:
    for aid in ('cheetah', 'chicken', 'wolf', 'greyhound', 'sloth', 'pronghorn'):
        r = run(track, get(aid), 500000)
        f.write(f'{aid},{r.hits},{r.sprints},{int(r.failed)},{r.min_gap_cm},{r.final_time_s},{r.paused_s},{r.lost_s},{r.reengages},{r.enemy_moved_cm}\n')
print('golden written', len(track), 'rows')
