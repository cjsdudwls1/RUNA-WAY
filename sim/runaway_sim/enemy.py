"""적 상태 머신 + 피로 모델. 1D 궤적 추종: gap_cm = 플레이어 궤적상 뒤처진 거리."""

ROAM, SPRINT, TIRED, RECOVER, LOST, FROZEN = 'roam', 'sprint', 'tired', 'recover', 'lost', 'frozen'

ROAM_PM = 800      # 배회 속도 = 순항 x 0.8
TIRED_PM = 500     # 지침 속도 = 순항 x 0.5
LOST_ACC_M = 40    # 정확도 40m 초과 → 냄새 잃음


class Enemy:
    def __init__(self, animal, start_gap_cm):
        self.a = animal
        self.gap = int(start_gap_cm)
        self.state = ROAM
        self.cycle = 0
        self.timer = 0
        self.speed = 0
        self.sprints = 0
        self.moved_total = 0
        self._sp, self._du, self._rc = animal.cycle_params(0)

    def _start_sprint(self):
        self._sp, self._du, self._rc = self.a.cycle_params(self.cycle)
        self.state = SPRINT
        self.timer = self._du
        self.sprints += 1

    def reposition(self, gap_cm, after_hit=False):
        """재배치. after_hit이면 사냥 직후 지침 상태로 들어가 정상적으로 회복·피로 누적."""
        self.gap = int(gap_cm)
        if after_hit and not self.a.constant:
            self.state = TIRED
            self.timer = self._rc // 2
        else:
            self.state = ROAM
            self.timer = 0

    def tick(self, player_adv_cm, acc_m, frozen=False, force_chase=False, stalk_cms=None, can_detect=True):
        """1초 진행. frozen: 쿨다운·일시정지. force_chase: 캘리브레이션용(감지 항상 참). stalk_cms: 배회 중 추적 속도(워밍업)."""
        a = self.a
        if frozen:
            self.speed = 0
            self.gap = max(0, self.gap + player_adv_cm)
            return self.state
        if acc_m > LOST_ACC_M and not force_chase:
            self.speed = 0
            self.gap = max(0, self.gap + player_adv_cm)
            return LOST
        if a.constant:
            self.speed = a.cruise_cms
            self.state = ROAM
        else:
            detected = force_chase or (can_detect and self.gap <= a.detect_cm)
            if self.state == ROAM:
                self.speed = stalk_cms if stalk_cms is not None else a.cruise_cms * ROAM_PM // 1000
                if detected:
                    self._start_sprint()
                    self.speed = self._sp
            elif self.state == SPRINT:
                self.speed = self._sp
                self.timer -= 1
                if self.timer <= 0:
                    self.state = TIRED
                    self.timer = self._rc // 2
            elif self.state == TIRED:
                self.speed = a.cruise_cms * TIRED_PM // 1000
                self.timer -= 1
                if self.timer <= 0:
                    self.state = RECOVER
                    self.timer = self._rc - self._rc // 2
            elif self.state == RECOVER:
                self.speed = a.cruise_cms
                self.timer -= 1
                if self.timer <= 0:
                    self.cycle += 1
                    if detected:
                        self._start_sprint()
                        self.speed = self._sp
                    else:
                        self.state = ROAM
        self.moved_total += self.speed
        self.gap = max(0, self.gap + player_adv_cm - self.speed)
        return self.state
