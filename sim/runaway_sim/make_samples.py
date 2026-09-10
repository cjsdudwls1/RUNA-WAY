"""합성 GPX 샘플 생성. python -m runaway_sim.make_samples"""
import os
from .synth import generate, write_gpx, pace_steady, pace_intervals

OUT = os.path.join(os.path.dirname(__file__), '..', 'samples')


def main():
    os.makedirs(OUT, exist_ok=True)
    specs = [
        ('steady10', pace_steady(10.0), dict(seed=1)),
        ('steady7', pace_steady(7.0), dict(seed=2)),
        ('steady13', pace_steady(13.0), dict(seed=3)),
        ('intervals', pace_intervals(9.0, 16.0), dict(seed=4)),
        ('clean10', pace_steady(10.0), dict(seed=5, canyon=False, dropout=False, stop=False, noise_m=2.0)),
    ]
    for name, pace, kw in specs:
        pts, _ = generate(course_m=5000, pace=pace, **kw)
        write_gpx(os.path.join(OUT, name + '.gpx'), pts, name)
        print('wrote', name)


if __name__ == '__main__':
    main()
