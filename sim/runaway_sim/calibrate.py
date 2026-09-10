"""각 동물의 30분 평균 속도를 실측 목표(target30_kmh)에 ±10%로 맞춘다.
방법: 영구 추격 모드(감지 항상 참, 포획 없음)로 1800틱 진행. 회복 시간을 이분 탐색, 안 되면 순항 속도를 이분 탐색."""
import json
import sys
from .animals import load_all, Animal, DATA
from .enemy import Enemy

TICKS = 1800
TOL = 0.10


def avg_kmh(animal):
    e = Enemy(animal, 10 ** 9)
    for _ in range(TICKS):
        e.tick(0, 8.0, force_chase=True)
    return e.moved_total / TICKS * 0.036


def _with(d, **kw):
    x = dict(d)
    x.update(kw)
    return Animal(x)


def _tune_recover(d, target):
    lo, hi = 2, 7200
    for _ in range(40):
        mid = (lo + hi) // 2
        if avg_kmh(_with(d, recover_s=mid)) > target:
            lo = mid
        else:
            hi = mid
    nd = _with(d, recover_s=hi).raw
    return nd, avg_kmh(Animal(nd)), 'recover_s→%d' % hi


def _tune_cruise(d, target):
    lo, hi = 0.0, max(d['sprint_kmh'], target * 2)
    for _ in range(60):
        mid = (lo + hi) / 2
        if avg_kmh(_with(d, cruise_kmh=mid)) < target:
            lo = mid
        else:
            hi = mid
    nd = _with(d, cruise_kmh=round(hi, 2)).raw
    return nd, avg_kmh(Animal(nd)), 'cruise_kmh→%.2f' % hi


def calibrate_one(d):
    """tune 필드가 지정한 값을 먼저 조정, 실패 시 나머지 값으로. 스프린트 속도·지속은 실측이라 건드리지 않는다."""
    a = Animal(d)
    if a.constant:
        return d, avg_kmh(a), 'constant'
    target = a.target30_kmh
    cur = avg_kmh(a)
    if abs(cur - target) / target <= TOL:
        return d, cur, 'ok'
    order = [_tune_recover, _tune_cruise] if d.get('tune') == 'recover' else [_tune_cruise, _tune_recover]
    for fn in order:
        nd, v, note = fn(d, target)
        if abs(v - target) / target <= TOL:
            return nd, v, note
    return nd, v, note + ' (실패)'


def main(argv):
    write = '--write' in argv
    with open(DATA, encoding='utf-8') as f:
        doc = json.load(f)
    out = []
    print(f"{'동물':<10}{'목표':>8}{'보정전':>8}{'보정후':>8}  조치")
    all_ok = True
    for d in doc['animals']:
        before = avg_kmh(Animal(d))
        nd, after, note = calibrate_one(d)
        ok = abs(after - d['target30_kmh']) / d['target30_kmh'] <= TOL if not d.get('constant') else True
        all_ok &= ok
        print(f"{d['name_ko']:<10}{d['target30_kmh']:>8.2f}{before:>8.2f}{after:>8.2f}  {note}{'' if ok else '  !! 범위 밖'}")
        out.append(nd)
    if write:
        doc['animals'] = out
        with open(DATA, 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print('animals.json 갱신')
    print('전체 ±10% 통과' if all_ok else '통과 실패 있음')
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
