package kr.runaway.core

/** 1Hz 입력 행. dist는 누적 cm. */
data class TrackRow(val t: Int, val distCm: Int, val speedCms: Int, val accM: Double)

data class TickRow(
    val t: Int, val playerCms: Int, val enemyState: EnemyState, val enemyCms: Int,
    val gapCm: Int, val gaugePm: Int, val hits: Int, val paused: Boolean, val accM: Double,
)

class SessionResult(val courseCm: Int) {
    val rows = ArrayList<TickRow>()
    var hits = 0
    var failed = false
    var elapsedS = 0
    var movingS = 0
    var pausedS = 0
    var playerDistCm = 0
    var minGapCm: Int? = null
    var sprints = 0
    var enemyMovedCm: Long = 0
    var enemyActiveS = 0
    var lostS = 0
    var reengages = 0

    val penaltyS get() = hits * Threat.HIT_PENALTY_S
    val excessPauseS get() = maxOf(0, pausedS - Session.PAUSE_CAP_S)
    val finalTimeS get() = movingS + excessPauseS + penaltyS
    fun playerAvgKmh() = if (movingS == 0) 0.0 else playerDistCm.toDouble() / movingS * 0.036
    fun enemyAvgKmh() = if (enemyActiveS == 0) 0.0 else enemyMovedCm.toDouble() / enemyActiveS * 0.036
}

/** 세션 루프. sim/runaway_sim/session.py와 동일한 규칙·연산 순서. */
object Session {
    const val WARMUP_S = 180
    const val WARMUP_MIN_GAP_CM = 10000
    const val COOLDOWN_PCT = 87
    const val START_GAP_EXTRA_CM = 10000
    const val REENGAGE_INSIDE_CM = 2000
    const val PAUSE_SPEED_CMS = 100
    const val PAUSE_AFTER_S = 8
    const val PAUSE_CAP_S = 180

    fun run(track: List<TrackRow>, animal: Animal, courseCm: Int): SessionResult {
        val enemy = Enemy(animal, animal.detectCm + START_GAP_EXTRA_CM)
        val warmGap = minOf(WARMUP_MIN_GAP_CM, animal.detectCm - REENGAGE_INSIDE_CM)
        val threat = Threat()
        val res = SessionResult(courseCm)
        var prevDist = track[0].distCm
        var slowTicks = 0
        var lastCycle = 0
        val recent = ArrayDeque<Int>()
        for (row in track) {
            val adv = row.distCm - prevDist
            prevDist = row.distCm
            res.elapsedS += 1
            recent.addLast(row.speedCms)
            if (recent.size > 5) recent.removeFirst()
            if (recent.sum() / recent.size < PAUSE_SPEED_CMS) slowTicks += 1 else slowTicks = 0
            val paused = slowTicks >= PAUSE_AFTER_S
            if (paused) res.pausedS += 1 else res.movingS += 1
            val warmup = res.elapsedS <= WARMUP_S
            val cooldown = row.distCm >= courseCm.toLong() * COOLDOWN_PCT / 100
            val frozen = paused || cooldown
            var stalk: Int? = null
            if (warmup && enemy.gap > warmGap) {
                val remaining = maxOf(1, WARMUP_S - res.elapsedS + 1)
                stalk = adv + maxOf(20, (enemy.gap - warmGap) / remaining)
            }
            val state = enemy.tick(adv, row.accM, frozen = frozen, stalkCms = stalk, canDetect = !warmup)
            if (warmup) enemy.clampGapAtLeast(warmGap)
            if (enemy.cycle > lastCycle) {
                lastCycle = enemy.cycle
                if (!warmup && !frozen && enemy.gap > animal.detectCm) {
                    enemy.reposition(animal.detectCm - REENGAGE_INSIDE_CM)
                    res.reengages += 1
                }
            }
            if (!frozen) {
                res.enemyActiveS += 1
                res.enemyMovedCm += enemy.speed
            }
            if (state == EnemyState.LOST) res.lostS += 1
            val hit = threat.tick(enemy.gap, row.accM, active = (!warmup && !frozen))
            if (hit) {
                res.hits += 1
                enemy.reposition(Threat.RESPAWN_GAP_CM, afterHit = true)
                if (res.hits >= Threat.MAX_HITS) res.failed = true
            }
            val mg = res.minGapCm
            if (mg == null || enemy.gap < mg) res.minGapCm = enemy.gap
            res.rows.add(TickRow(row.t, row.speedCms, enemy.state, enemy.speed, enemy.gap, threat.gauge, res.hits, paused, row.accM))
            res.playerDistCm = row.distCm
            if (row.distCm >= courseCm) break
        }
        res.sprints = enemy.sprints
        return res
    }
}
