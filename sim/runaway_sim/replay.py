"""GPX 리플레이 CLI.
python -m runaway_sim.replay samples/steady10.gpx --animal cheetah --course 5000 [--csv out.csv]"""
import argparse
import csv
import sys
from .animals import get
from .gpx import load_track
from .session import run


def chart(rows, every=30, width=50):
    mx = max(r[4] for r in rows) or 1
    lines = []
    for r in rows[::every]:
        t, ps, st, es, gap, gauge, hits, paused, acc = r
        bar = '#' * int(gap / mx * width)
        flag = 'P' if paused else (' ' if st != 'lost' else 'L')
        lines.append(f"{t:5d}s {flag} {st:<7} 적{es*0.036:5.1f}km/h 나{ps*0.036:5.1f} gap{gap//100:4d}m 게이지{gauge//10:3d}% 피격{hits} |{bar}")
    return '\n'.join(lines)


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument('gpx')
    p.add_argument('--animal', default='cheetah')
    p.add_argument('--course', type=int, default=5000, help='m')
    p.add_argument('--csv')
    p.add_argument('--quiet', action='store_true')
    a = p.parse_args(argv)
    animal = get(a.animal)
    track = load_track(a.gpx)
    res = run(track, animal, a.course * 100)
    s = res.summary()
    print(f"[{animal.name_ko}] 목표 30분 {animal.target30_kmh} km/h")
    for k, v in s.items():
        print(f"  {k}: {v}")
    if not a.quiet:
        print(chart(res.rows))
    if a.csv:
        with open(a.csv, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['t', 'player_cms', 'enemy_state', 'enemy_cms', 'gap_cm', 'gauge_pm', 'hits', 'paused', 'acc_m'])
            w.writerows(res.rows)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
