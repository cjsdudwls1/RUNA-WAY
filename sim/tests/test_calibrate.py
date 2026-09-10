import unittest, json
from runaway_sim.calibrate import calibrate_one
from runaway_sim.animals import DATA


class CalibrateTest(unittest.TestCase):
    def test_all_within_10pct(self):
        with open(DATA, encoding='utf-8') as f:
            doc = json.load(f)
        bad = []
        for d in doc['animals']:
            nd, v, note = calibrate_one(d)
            if d.get('constant'):
                continue
            if abs(v - d['target30_kmh']) / d['target30_kmh'] > 0.10:
                bad.append((d['id'], v, d['target30_kmh']))
        self.assertEqual(bad, [])


if __name__ == '__main__':
    unittest.main()
