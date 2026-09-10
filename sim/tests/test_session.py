import unittest
from runaway_sim.animals import get
from runaway_sim.synth import generate, write_gpx, pace_steady
from runaway_sim.gpx import load_track
from runaway_sim.session import run
import tempfile, os


def track_for(kmh, seed=1, **kw):
    pts, _ = generate(course_m=3000, pace=pace_steady(kmh), seed=seed, **kw)
    d = tempfile.mkdtemp()
    p = os.path.join(d, 't.gpx')
    write_gpx(p, pts)
    return load_track(p)


class SessionTest(unittest.TestCase):
    def test_deterministic(self):
        tr = track_for(10.0)
        r1 = run(tr, get('cheetah'), 300000).summary()
        r2 = run(tr, get('cheetah'), 300000).summary()
        self.assertEqual(r1, r2)

    def test_chicken_never_catches_runner(self):
        r = run(track_for(10.0, canyon=False, dropout=False, stop=False), get('chicken'), 300000)
        self.assertEqual(r.hits, 0)

    def test_cheetah_catches_recreational_runner(self):
        """물리적으로 치타는 감지 반경 안에서 한 번 스프린트하면 10km/h 러너를 잡는다. M0 회귀 기준."""
        r = run(track_for(10.0, canyon=False, dropout=False, stop=False), get('cheetah'), 300000)
        self.assertGreaterEqual(r.sprints, 3)
        self.assertGreaterEqual(r.hits, 1)          # 첫 스프린트(114km/h)는 반드시 잡는다
        self.assertLessEqual(r.hits, r.sprints)

    def test_autopause_on_stop(self):
        r = run(track_for(10.0, canyon=False, dropout=False, stop=True), get('chicken'), 300000)
        self.assertGreaterEqual(r.paused_s, 30)

    def test_distance_close_to_truth(self):
        pts, truth = generate(course_m=3000, pace=pace_steady(10.0), seed=7, canyon=False, dropout=False, stop=False, noise_m=2.0)
        d = tempfile.mkdtemp(); p = os.path.join(d, 't.gpx'); write_gpx(p, pts)
        tr = load_track(p)
        err = abs(tr[-1][1] / 100 - truth[-1][1]) / truth[-1][1]
        self.assertLess(err, 0.10)


if __name__ == '__main__':
    unittest.main()
