import unittest
from runaway_sim.threat import Threat, HIT


class ThreatTest(unittest.TestCase):
    def test_fill_in_4s_then_hit(self):
        th = Threat()
        ev = [th.tick(2000, 8.0) for _ in range(4)]
        self.assertEqual(ev[-1], HIT)
        self.assertEqual(th.hits, 1)

    def test_hysteresis(self):
        th = Threat()
        th.tick(2000, 8.0)
        self.assertTrue(th.inside)
        th.tick(4000, 8.0)            # 30~50m 사이: 유지
        self.assertTrue(th.inside)
        th.tick(5000, 8.0)
        self.assertFalse(th.inside)

    def test_decay_twice_fast(self):
        th = Threat()
        for _ in range(3):
            th.tick(2000, 8.0)        # 750
        th.tick(7000, 8.0)            # -500 → 250
        self.assertEqual(th.gauge, 250)
        th.tick(7000, 8.0)
        self.assertEqual(th.gauge, 0)

    def test_accuracy_slow_and_freeze(self):
        th = Threat()
        th.tick(2000, 30.0)
        self.assertEqual(th.gauge, 125)   # 반속
        th.tick(2000, 45.0)
        self.assertEqual(th.gauge, 125)   # 동결

    def test_invuln_after_hit(self):
        th = Threat()
        for _ in range(4):
            th.tick(2000, 8.0)
        th.tick(2000, 8.0)
        self.assertEqual(th.gauge, 0)     # 무적 중 충전 없음


if __name__ == '__main__':
    unittest.main()
