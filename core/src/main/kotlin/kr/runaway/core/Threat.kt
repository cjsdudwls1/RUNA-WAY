package kr.runaway.core

/** 위협 게이지. 퍼밀(0~1000). 진입 30m / 이탈 50m 히스테리시스, 4초 충전, 2배속 감소, 정확도 보정. */
class Threat {
    companion object {
        const val ENTER_CM = 3000
        const val EXIT_CM = 5000
        const val FILL_PER_S = 1000 / 4
        const val DECAY_PER_S = FILL_PER_S * 2
        const val ACC_SLOW_M = 25.0
        const val ACC_FREEZE_M = 40.0
        const val INVULN_S = 3
        const val HIT_PENALTY_S = 30
        const val RESPAWN_GAP_CM = 20000
        const val MAX_HITS = 3
    }

    var inside = false
        private set
    var gauge = 0
        private set
    var hits = 0
        private set
    var invuln = 0
        private set
    var lowAccTicks = 0
        private set

    /** true면 이번 틱에 피격. */
    fun tick(gapCm: Int, accM: Double, active: Boolean = true): Boolean {
        if (gapCm <= ENTER_CM) inside = true else if (gapCm >= EXIT_CM) inside = false
        if (invuln > 0) invuln -= 1
        if (accM > ACC_FREEZE_M) {
            lowAccTicks += 1
            return false
        }
        val rate = if (accM <= ACC_SLOW_M) FILL_PER_S else FILL_PER_S / 2
        gauge = if (inside && active && invuln == 0) minOf(1000, gauge + rate) else maxOf(0, gauge - DECAY_PER_S)
        if (gauge >= 1000) {
            gauge = 0
            hits += 1
            invuln = INVULN_S
            return true
        }
        return false
    }
}
