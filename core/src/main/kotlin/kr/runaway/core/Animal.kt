package kr.runaway.core

/** 코어용 정수 파라미터. 속도 cm/s, 시간 s, 계수 퍼밀. sim/runaway_sim/animals.py와 동일. */
data class Animal(
    val id: String,
    val nameKo: String,
    val track: Char,
    val tier: Int,
    val constant: Boolean,
    val sprintCms: Int,
    val sprintS: Int,
    val cruiseCms: Int,
    val recoverS: Int,
    val dvPm: Int,
    val dtPm: Int,
    val gPm: Int,
    val detectCm: Int,
    val target30Kmh: Double,
) {
    /** n번째 사이클(0부터)의 (스프린트 cms, 지속 s, 회복 s). 반복 곱으로 결정론 유지. */
    fun cycleParams(n: Int): Triple<Int, Int, Int> {
        var sp = sprintCms
        var du = sprintS
        var rc = recoverS
        repeat(n) {
            sp = sp * dvPm / 1000
            du = du * dtPm / 1000
            rc = rc * gPm / 1000
        }
        return Triple(sp, maxOf(du, 1), maxOf(rc, 2))
    }
}
