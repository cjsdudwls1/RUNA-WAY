"""세션 루프. 입력 트랙은 gpx.load_track 형식 [(t, dist_cm, speed_cms, acc_m)]."""
from .enemy import Enemy, LOST
from .threat import Threat, HIT, HIT_PENALTY_S, RESPAWN_GAP_CM, MAX_HITS

WARMUP_S = 180
WARMUP_MIN_GAP_CM = 10000      # 워밍업 중 접근 한계. 감지 반경이 더 작으면 감지 반경 - 20m
COOLDOWN_FRACTION = 0.87       # 코스 87% 이후 쿨다운, 적 정지
START_GAP_EXTRA_CM = 10000     # 스폰 = 감지 반경 + 100m
REENGAGE_INSIDE_CM = 2000      # 회복을 마쳤는데 감지 밖이면 따라잡아 감지 반경 안쪽 20m에 재배치
PAUSE_SPEED_CMS = 100          # 5초 평균 1.0 m/s 미만
PAUSE_AFTER_S = 8
PAUSE_CAP_S = 180


class Result:
    def __init__(self):
        self.rows = []
        self.hits = 0
        self.failed = False
        self.elapsed_s = 0
        self.moving_s = 0
        self.paused_s = 0
        self.player_dist_cm = 0
        self.min_gap_cm = None
        self.sprints = 0
        self.enemy_moved_cm = 0
        self.enemy_active_s = 0
        self.lost_s = 0
        self.course_cm = 0
        self.reengages = 0

    @property
    def penalty_s(self):
        return self.hits * HIT_PENALTY_S

    @property
    def excess_pause_s(self):
        return max(0, self.paused_s - PAUSE_CAP_S)

    @property
    def final_time_s(self):
        return self.moving_s + self.excess_pause_s + self.penalty_s

    def player_avg_kmh(self):
        return 0.0 if self.moving_s == 0 else self.player_dist_cm / self.moving_s * 0.036

    def enemy_avg_kmh(self):
        return 0.0 if self.enemy_active_s == 0 else self.enemy_moved_cm / self.enemy_active_s * 0.036

    def summary(self):
        return {
            'hits': self.hits, 'failed': self.failed,
            'elapsed_s': self.elapsed_s, 'moving_s': self.moving_s, 'paused_s': self.paused_s,
            'penalty_s': self.penalty_s, 'final_time_s': self.final_time_s,
            'player_km': round(self.player_dist_cm / 100000, 3),
            'player_avg_kmh': round(self.player_avg_kmh(), 2),
            'enemy_avg_kmh': round(self.enemy_avg_kmh(), 2),
            'sprints': self.sprints, 'min_gap_m': None if self.min_gap_cm is None else self.min_gap_cm // 100,
            'lost_s': self.lost_s, 'reengages': self.reengages,
        }


def run(track, animal, course_cm):
    """결정론. 같은 입력이면 같은 결과."""
    enemy = Enemy(animal, animal.detect_cm + START_GAP_EXTRA_CM)
    warm_gap = min(WARMUP_MIN_GAP_CM, animal.detect_cm - REENGAGE_INSIDE_CM)
    threat = Threat()
    res = Result()
    res.course_cm = course_cm
    prev_dist = track[0][1]
    slow_ticks = 0
    paused = False
    last_cycle = 0
    recent = []
    for (t, dist, speed, acc) in track:
        adv = dist - prev_dist
        prev_dist = dist
        res.elapsed_s += 1
        # 자동 일시정지 (5초 이동평균)
        recent.append(speed)
        if len(recent) > 5:
            recent.pop(0)
        if sum(recent) // len(recent) < PAUSE_SPEED_CMS:
            slow_ticks += 1
        else:
            slow_ticks = 0
        paused = slow_ticks >= PAUSE_AFTER_S
        if paused:
            res.paused_s += 1
        else:
            res.moving_s += 1
        warmup = res.elapsed_s <= WARMUP_S
        cooldown = dist >= int(course_cm * COOLDOWN_FRACTION)
        frozen = paused or cooldown
        stalk = None
        if warmup and enemy.gap > warm_gap:
            remaining = max(1, WARMUP_S - res.elapsed_s + 1)
            stalk = adv + max(20, (enemy.gap - warm_gap) // remaining)   # 워밍업 끝에 정확히 접근 한계까지
        state = enemy.tick(adv, acc, frozen=frozen, stalk_cms=stalk, can_detect=not warmup)
        if warmup and enemy.gap < warm_gap:
            enemy.gap = warm_gap
        if enemy.cycle > last_cycle:
            last_cycle = enemy.cycle
            if not warmup and not frozen and enemy.gap > animal.detect_cm:
                enemy.reposition(animal.detect_cm - REENGAGE_INSIDE_CM)
                res.reengages += 1
        if not frozen:
            res.enemy_active_s += 1
            res.enemy_moved_cm += enemy.speed
        if state == LOST:
            res.lost_s += 1
        ev = threat.tick(enemy.gap, acc, active=(not warmup and not frozen))
        if ev == HIT:
            res.hits += 1
            enemy.reposition(RESPAWN_GAP_CM, after_hit=True)
            if res.hits >= MAX_HITS:
                res.failed = True
        if res.min_gap_cm is None or enemy.gap < res.min_gap_cm:
            res.min_gap_cm = enemy.gap
        res.rows.append((t, speed, enemy.state, enemy.speed, enemy.gap, threat.gauge, res.hits, paused, acc))
        res.player_dist_cm = dist
        if dist >= course_cm:
            break
    res.sprints = enemy.sprints
    return res
