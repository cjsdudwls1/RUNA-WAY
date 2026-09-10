import unittest
from runaway_sim.animals import get
from runaway_sim.enemy import Enemy, SPRINT, TIRED, RECOVER, ROAM, LOST


class EnemyTest(unittest.TestCase):
    def test_cheetah_fatigue_params(self):
        a = get('cheetah')
        sp0, du0, rc0 = a.cycle_params(0)
        sp1, du1, rc1 = a.cycle_params(1)
        self.assertEqual(sp1, sp0 * 750 // 1000)
        self.assertEqual(du1, du0 * 700 // 1000)
        self.assertEqual(rc1, rc0 * 1600 // 1000)

    def test_state_sequence(self):
        a = get('cheetah')
        e = Enemy(a, 5000)
        states = [e.tick(0, 8.0) for _ in range(300)]
        self.assertEqual(states[0], SPRINT)
        self.assertIn(TIRED, states)
        self.assertIn(RECOVER, states)
        first_run = 0
        for st in states:
            if st == SPRINT:
                first_run += 1
            elif first_run:
                break
        self.assertEqual(first_run, 25)               # 사이클 0 지속 25초

    def test_lost_when_accuracy_bad(self):
        e = Enemy(get('cheetah'), 5000)
        self.assertEqual(e.tick(0, 50.0), LOST)
        self.assertEqual(e.speed, 0)

    def test_roam_when_out_of_detect(self):
        e = Enemy(get('cheetah'), 100000)
        self.assertEqual(e.tick(0, 8.0), ROAM)

    def test_constant_animal(self):
        e = Enemy(get('sloth'), 5000)
        e.tick(0, 8.0)
        self.assertEqual(e.speed, get('sloth').cruise_cms)


if __name__ == '__main__':
    unittest.main()
