package kr.runaway.app

import kr.runaway.core.Animal
import kr.runaway.core.Enemy
import kr.runaway.core.EnemyState
import kr.runaway.core.Gpx
import kr.runaway.core.Session
import kr.runaway.core.Threat
import kr.runaway.core.TrackRow

/** 한 틱의 화면·소리용 스냅샷. */
data class Snapshot(
    val t: Int,
    val playerCms: Int,
    val distCm: Int,
    val enemyState: EnemyState,
    val enemyCms: Int,
    val gapCm: Int,
    val gaugePm: Int,
    val hits: Int,
    val failed: Boolean,
    val paused: Boolean,
    val warmup: Boolean,
    val cooldown: Boolean,
    val accM: Double,
    val cycle: Int,
    val done: Boolean,
    // 화면용 좌표(미터, 첫 위치 기준 동·북)
    val trail: List<Pair<Float, Float>>,
    val enemyXY: Pair<Float, Float>?,
)

/**
 * 실시간 스트리밍 세션. Session.run()과 같은 규칙을 틱 단위로 진행한다.
 * 규칙이 바뀌면 core/Session.kt와 이 파일을 함께 고친다(골든 테스트가 Session을 지킨다).
 */
class RunEngine(private val animal: Animal, private val courseCm: Int) {
    private val builder = Gpx.TrackBuilder()
    private val enemy = Enemy(animal, animal.detectCm + Session.START_GAP_EXTRA_CM)
    private val warmGap = minOf(Session.WARMUP_MIN_GAP_CM, animal.detectCm - Session.REENGAGE_INSIDE_CM)
    private val threat = Threat()
    private var prevDist = 0
    private var elapsed = 0
    private var slowTicks = 0
    private var lastCycle = 0
    private val recent = ArrayDeque<Int>()
    private var hits = 0
    private var failed = false
    private var done = false
    private var lat0 = Double.NaN
    private var lon0 = Double.NaN
    // 궤적: 누적거리(cm)와 화면 좌표
    private val trailDist = ArrayList<Int>()
    private val trailXY = ArrayList<Pair<Float, Float>>()

    var lastRow: TrackRow? = null; private set

    fun push(f: Fix): Snapshot {
        val row = builder.push(f.t, f.lat, f.lon, f.accM)
        lastRow = row
        if (lat0.isNaN()) { lat0 = f.lat; lon0 = f.lon }
        val sl = if (builder.lastSmoothLat.isNaN()) f.lat else builder.lastSmoothLat
        val so = if (builder.lastSmoothLon.isNaN()) f.lon else builder.lastSmoothLon
        val north = Gpx.haversineM(lat0, lon0, sl, lon0) * (if (sl >= lat0) 1 else -1)
        val east = Gpx.haversineM(lat0, lon0, lat0, so) * (if (so >= lon0) 1 else -1)
        if (trailDist.isEmpty() || row.distCm > trailDist.last()) {
            trailDist.add(row.distCm); trailXY.add(Pair(east.toFloat(), north.toFloat()))
        }

        val adv = row.distCm - prevDist
        prevDist = row.distCm
        elapsed += 1
        recent.addLast(row.speedCms); if (recent.size > 5) recent.removeFirst()
        if (recent.sum() / recent.size < Session.PAUSE_SPEED_CMS) slowTicks += 1 else slowTicks = 0
        val paused = slowTicks >= Session.PAUSE_AFTER_S
        val warmup = elapsed <= Session.WARMUP_S
        val cooldown = row.distCm >= courseCm.toLong() * Session.COOLDOWN_PCT / 100
        val frozen = paused || cooldown
        var stalk: Int? = null
        if (warmup && enemy.gap > warmGap) {
            val remaining = maxOf(1, Session.WARMUP_S - elapsed + 1)
            stalk = adv + maxOf(20, (enemy.gap - warmGap) / remaining)
        }
        enemy.tick(adv, row.accM, frozen = frozen, stalkCms = stalk, canDetect = !warmup)
        if (warmup) enemy.clampGapAtLeast(warmGap)
        if (enemy.cycle > lastCycle) {
            lastCycle = enemy.cycle
            if (!warmup && !frozen && enemy.gap > animal.detectCm) enemy.reposition(animal.detectCm - Session.REENGAGE_INSIDE_CM)
        }
        val hit = threat.tick(enemy.gap, row.accM, active = (!warmup && !frozen))
        if (hit) {
            hits += 1
            enemy.reposition(Threat.RESPAWN_GAP_CM, afterHit = true)
            if (hits >= Threat.MAX_HITS) failed = true
        }
        if (row.distCm >= courseCm) done = true

        return Snapshot(
            t = row.t, playerCms = row.speedCms, distCm = row.distCm,
            enemyState = enemy.state, enemyCms = enemy.speed, gapCm = enemy.gap,
            gaugePm = threat.gauge, hits = hits, failed = failed, paused = paused,
            warmup = warmup, cooldown = cooldown, accM = row.accM, cycle = enemy.cycle, done = done,
            trail = trailXY.takeLast(600), enemyXY = pointBehind(enemy.gap),
        )
    }

    /** 궤적을 gap만큼 거슬러 올라간 지점. 궤적이 짧으면 출발점 뒤로 직선 외삽. */
    private fun pointBehind(gapCm: Int): Pair<Float, Float>? {
        if (trailDist.isEmpty()) return null
        val target = trailDist.last() - gapCm
        if (target <= trailDist.first()) {
            val (x, y) = trailXY.first()
            val (x2, y2) = if (trailXY.size > 1) trailXY[1] else Pair(x, y + 1f)
            val dx = x - x2; val dy = y - y2
            val len = kotlin.math.sqrt(dx * dx + dy * dy).coerceAtLeast(0.01f)
            val back = (trailDist.first() - target) / 100f
            return Pair(x + dx / len * back, y + dy / len * back)
        }
        var i = trailDist.size - 1
        while (i > 0 && trailDist[i - 1] > target) i--
        val d0 = trailDist[i - 1]; val d1 = trailDist[i]
        val f = if (d1 == d0) 0f else (target - d0).toFloat() / (d1 - d0)
        val (x0, y0) = trailXY[i - 1]; val (x1, y1) = trailXY[i]
        return Pair(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)
    }
}
