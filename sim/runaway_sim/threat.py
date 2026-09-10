"""위협 게이지. 퍼밀(0~1000). 진입 30m / 이탈 50m 히스테리시스, 4초 충전, 2배속 감소, 정확도 보정."""

ENTER_CM = 3000
EXIT_CM = 5000
FILL_PER_S = 1000 // 4      # 4초에 100%
DECAY_PER_S = FILL_PER_S * 2
ACC_SLOW_M = 25             # 초과 시 충전 속도 50%
ACC_FREEZE_M = 40           # 초과 시 동결
INVULN_S = 3
HIT_PENALTY_S = 30
RESPAWN_GAP_CM = 20000
MAX_HITS = 3

HIT = 'hit'


class Threat:
    def __init__(self):
        self.inside = False
        self.gauge = 0
        self.hits = 0
        self.invuln = 0
        self.low_acc_ticks = 0

    def tick(self, gap_cm, acc_m, active=True):
        if gap_cm <= ENTER_CM:
            self.inside = True
        elif gap_cm >= EXIT_CM:
            self.inside = False
        if self.invuln > 0:
            self.invuln -= 1
        if acc_m > ACC_FREEZE_M:
            self.low_acc_ticks += 1
            return None                      # 동결
        rate = FILL_PER_S if acc_m <= ACC_SLOW_M else FILL_PER_S // 2
        if self.inside and active and self.invuln == 0:
            self.gauge = min(1000, self.gauge + rate)
        else:
            self.gauge = max(0, self.gauge - DECAY_PER_S)
        if self.gauge >= 1000:
            self.gauge = 0
            self.hits += 1
            self.invuln = INVULN_S
            return HIT
        return None
