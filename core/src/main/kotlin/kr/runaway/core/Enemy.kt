package kr.runaway.core

enum class EnemyState { ROAM, SPRINT, TIRED, RECOVER, LOST }

/** 적 상태 머신 + 피로 모델. 1D 궤적 추종: gap = 플레이어 궤적상 뒤처진 거리(cm). */
class Enemy(val animal: Animal, startGapCm: Int) {
    companion object {
        const val ROAM_PM = 800
        const val TIRED_PM = 500
        const val LOST_ACC_M = 40.0
    }

    var gap: Int = startGapCm
        private set
    var state: EnemyState = EnemyState.ROAM
        private set
    var cycle: Int = 0
        private set
    var timer: Int = 0
        private set
    var speed: Int = 0
        private set
    var sprints: Int = 0
        private set
    var movedTotal: Long = 0
        private set

    private var sp = 0
    private var du = 0
    private var rc = 0

    init {
        val p = animal.cycleParams(0)
        sp = p.first; du = p.second; rc = p.third
    }

    private fun startSprint() {
        val p = animal.cycleParams(cycle)
        sp = p.first; du = p.second; rc = p.third
        state = EnemyState.SPRINT
        timer = du
        sprints += 1
    }

    /** 재배치. afterHit이면 사냥 직후 지침 상태로 들어가 정상적으로 회복·피로 누적. */
    fun reposition(gapCm: Int, afterHit: Boolean = false) {
        gap = gapCm
        if (afterHit && !animal.constant) {
            state = EnemyState.TIRED
            timer = rc / 2
        } else {
            state = EnemyState.ROAM
            timer = 0
        }
    }

    /** 워밍업 접근 한계 클램프 등 외부에서 gap을 올릴 때. */
    fun clampGapAtLeast(minGap: Int) {
        if (gap < minGap) gap = minGap
    }

    /**
     * 1초 진행.
     * frozen: 쿨다운·일시정지. forceChase: 캘리브레이션용(감지 항상 참).
     * stalkCms: 배회 중 추적 속도(워밍업). canDetect: 워밍업 중 false.
     */
    fun tick(playerAdvCm: Int, accM: Double, frozen: Boolean = false, forceChase: Boolean = false,
             stalkCms: Int? = null, canDetect: Boolean = true): EnemyState {
        val a = animal
        if (frozen) {
            speed = 0
            gap = maxOf(0, gap + playerAdvCm)
            return state
        }
        if (accM > LOST_ACC_M && !forceChase) {
            speed = 0
            gap = maxOf(0, gap + playerAdvCm)
            return EnemyState.LOST
        }
        if (a.constant) {
            speed = a.cruiseCms
            state = EnemyState.ROAM
        } else {
            val detected = forceChase || (canDetect && gap <= a.detectCm)
            when (state) {
                EnemyState.ROAM -> {
                    speed = stalkCms ?: (a.cruiseCms * ROAM_PM / 1000)
                    if (detected) {
                        startSprint()
                        speed = sp
                    }
                }
                EnemyState.SPRINT -> {
                    speed = sp
                    timer -= 1
                    if (timer <= 0) {
                        state = EnemyState.TIRED
                        timer = rc / 2
                    }
                }
                EnemyState.TIRED -> {
                    speed = a.cruiseCms * TIRED_PM / 1000
                    timer -= 1
                    if (timer <= 0) {
                        state = EnemyState.RECOVER
                        timer = rc - rc / 2
                    }
                }
                EnemyState.RECOVER -> {
                    speed = a.cruiseCms
                    timer -= 1
                    if (timer <= 0) {
                        cycle += 1
                        if (detected) {
                            startSprint()
                            speed = sp
                        } else {
                            state = EnemyState.ROAM
                        }
                    }
                }
                EnemyState.LOST -> { /* python 코드와 동일: LOST는 반환값일 뿐 상태로 저장되지 않음 */ }
            }
        }
        movedTotal += speed
        gap = maxOf(0, gap + playerAdvCm - speed)
        return state
    }
}
