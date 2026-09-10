import json
import os
from .geo import kmh_to_cms

DATA = os.path.join(os.path.dirname(__file__), '..', 'data', 'animals.json')


class Animal:
    """코어용 정수 파라미터. 계수는 퍼밀(1000분율)."""

    def __init__(self, d):
        self.id = d['id']
        self.name_ko = d['name_ko']
        self.track = d['track']
        self.tier = d['tier']
        self.constant = bool(d.get('constant', False))
        self.sprint_cms = kmh_to_cms(d['sprint_kmh'])
        self.sprint_s = int(d['sprint_s'])
        self.cruise_cms = kmh_to_cms(d['cruise_kmh'])
        self.recover_s = int(d['recover_s'])
        self.dv_pm = int(round(d['dv'] * 1000))
        self.dt_pm = int(round(d['dt'] * 1000))
        self.g_pm = int(round(d['g'] * 1000))
        self.detect_cm = int(d['detect_m']) * 100
        self.target30_kmh = float(d['target30_kmh'])
        self.raw = d

    def cycle_params(self, n):
        """n번째 사이클(0부터)의 (스프린트 cms, 지속 s, 회복 s). 반복 곱으로 결정론 유지."""
        sp, du, rc = self.sprint_cms, self.sprint_s, self.recover_s
        for _ in range(n):
            sp = sp * self.dv_pm // 1000
            du = du * self.dt_pm // 1000
            rc = rc * self.g_pm // 1000
        return sp, max(du, 1), max(rc, 2)


def load_all(path=DATA):
    with open(path, encoding='utf-8') as f:
        return [Animal(d) for d in json.load(f)['animals']]


def get(animal_id, path=DATA):
    for a in load_all(path):
        if a.id == animal_id:
            return a
    raise KeyError(animal_id)
