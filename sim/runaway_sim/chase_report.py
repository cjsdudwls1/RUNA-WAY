"""동물 전체를 표준 러너(7/10/13 km/h, 5km, 잡음 없음)에 돌려 추격 결과를 표로. 티어 근거.
python -m runaway_sim.chase_report [--course 5000]"""
import argparse
import os
import sys
import tempfile
from .animals import load_all
from .synth import generate, write_gpx, pace_steady
from .gpx import load_track
from .session import run

SPEEDS = (7.0, 10.0, 13.0)


def tracks(course_m):
    out = {}
    d = tempfile.mkdtemp()
    for v in SPEEDS:
        pts, _ = generate(course_m=course_m, pace=pace_steady(v), seed=11, canyon=False, dropout=False, stop=False, noise_m=2.0)
        p = os.path.join(d, f'{v}.gpx')
        write_gpx(p, pts)
        out[v] = load_track(p)
    return out


def closing_m(a, runner_kmh):
    """한 번의 스프린트(사이클 0)로 좁힐 수 있는 거리(m). 감지 반경 - 40m보다 크면 따라잡음."""
    r = runner_kmh * 1000 / 36
    return (a.sprint_cms - r) * a.sprint_s / 100


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument('--course', type=int, default=5000)
    p.add_argument('--md', help='마크다운 표 저장 경로')
    a = p.parse_args(argv)
    trs = tracks(a.course)
    rows = []
    for an in load_all():
        cells = []
        for v in SPEEDS:
            r = run(trs[v], an, a.course * 100)
            cells.append((r.hits, r.sprints, r.failed))
        need = (an.detect_cm - 3000) / 100
        rows.append((an, cells, closing_m(an, 10.0), need))
    hdr = f"{'동물':<9}{'트랙':>3}{'스프린트':>8}{'감지':>5}{'10km/h닫힘':>10}{'필요':>5} | " + ' | '.join(f'{v:>4.0f}km/h 피격/스프' for v in SPEEDS)
    print(hdr)
    md = ['| 동물 | 트랙 | 스프린트 | 감지 | 스프린트 1회 닫힘(10km/h 기준) | 필요 | 7 km/h | 10 km/h | 13 km/h |', '|---|---|---|---|---|---|---|---|---|']
    for an, cells, close, need in rows:
        c = ' | '.join(f"{h:>2}/{s:<2}{'X' if f else ' '}" for h, s, f in cells)
        print(f"{an.name_ko:<9}{an.track:>3}{an.raw['sprint_kmh']:>6.0f}km{an.detect_cm//100:>5}{close:>10.0f}{need:>5.0f} | {c}")
        md.append(f"| {an.name_ko} | {an.track} | {an.raw['sprint_kmh']} km/h x {an.sprint_s}s | {an.detect_cm//100}m | {close:.0f}m | {need:.0f}m | " +
                  ' | '.join(f"피격 {h}, 스프린트 {s}{', 실패' if f else ''}" for h, s, f in cells) + ' |')
    print('X = 3회 피격 실패. 닫힘 > 필요 이면 물리적으로 따라잡힘')
    # 시뮬 기반 순위: 10km/h 피격 → 13km/h 피격 → 7km/h 피격 → 닫힘 거리
    ranked = sorted(rows, key=lambda r: (r[1][1][0], r[1][2][0], r[1][0][0], r[2]))
    print('\n시뮬 순위 (10km/h 러너 기준, 쉬운 순):')
    md.append('\n## 시뮬 순위 (10 km/h 러너 기준)\n')
    md.append('| 순위 | 동물 | 7 | 10 | 13 km/h 피격 |')
    md.append('|---|---|---|---|---|')
    for i, (an, cells, close, need) in enumerate(ranked, 1):
        print(f"{i:>2}. {an.name_ko:<9} 피격 {cells[0][0]}/{cells[1][0]}/{cells[2][0]}")
        md.append(f"| {i} | {an.name_ko} | {cells[0][0]} | {cells[1][0]} | {cells[2][0]} |")
    if a.md:
        with open(a.md, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
