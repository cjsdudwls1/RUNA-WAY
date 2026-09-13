package kr.runaway.core

import kotlin.math.asin
import kotlin.math.cos
import kotlin.math.round
import kotlin.math.sin
import kotlin.math.sqrt

/** GPX 파싱, 1Hz 리샘플, 스무딩·게이트 필터. sim/runaway_sim/gpx.py와 동일 연산. */
object Gpx {
    const val GATE_ACC_M = 30.0
    const val GATE_SPEED_MS = 8.0
    const val DROPOUT_S = 20
    const val SMOOTH_ALPHA = 0.35
    const val JUMP_RESET_N = 3
    private const val EARTH_R = 6371000.0

    data class Pt(val t: Double, val lat: Double, val lon: Double, val acc: Double)

    fun haversineM(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val p1 = Math.toRadians(lat1); val p2 = Math.toRadians(lat2)
        val dp = p2 - p1; val dl = Math.toRadians(lon2 - lon1)
        val a = sin(dp / 2) * sin(dp / 2) + cos(p1) * cos(p2) * sin(dl / 2) * sin(dl / 2)
        return 2 * EARTH_R * asin(sqrt(a))
    }

    private val trkpt = Regex("""<trkpt[^>]*lat="([^"]+)"[^>]*lon="([^"]+)"[^>]*>(.*?)</trkpt>""", RegexOption.DOT_MATCHES_ALL)
    private val timeRe = Regex("""<time>([^<]+)</time>""")
    private val accRe = Regex("""<accuracy>([^<]+)</accuracy>""")
    private val hdopRe = Regex("""<hdop>([^<]+)</hdop>""")

    /** 원본 점. t는 첫 점 기준 초. acc는 accuracy 또는 hdop*5, 없으면 8. */
    fun parse(xml: String): List<Pt> {
        val out = ArrayList<Pt>()
        var t0: Long? = null
        for (m in trkpt.findAll(xml)) {
            val body = m.groupValues[3]
            val tm = timeRe.find(body) ?: continue
            val epochMs = java.time.Instant.parse(tm.groupValues[1].trim()).toEpochMilli()
            if (t0 == null) t0 = epochMs
            val acc = accRe.find(body)?.groupValues?.get(1)?.toDouble()
                ?: hdopRe.find(body)?.groupValues?.get(1)?.toDouble()?.times(5.0) ?: 8.0
            out.add(Pt((epochMs - t0) / 1000.0, m.groupValues[1].toDouble(), m.groupValues[2].toDouble(), acc))
        }
        require(out.isNotEmpty()) { "trkpt 없음" }
        return out
    }

    fun resample1Hz(raw: List<Pt>): List<Pt> {
        val out = ArrayList<Pt>()
        var i = 0
        val tEnd = raw.last().t.toInt()
        for (t in 0..tEnd) {
            while (i + 1 < raw.size && raw[i + 1].t <= t) i++
            val a = raw[i]
            if (i + 1 < raw.size) {
                val b = raw[i + 1]
                if (b.t - a.t > DROPOUT_S && t > a.t) { out.add(Pt(t.toDouble(), a.lat, a.lon, 99.0)); continue }
                var f = if (b.t == a.t) 0.0 else (t - a.t) / (b.t - a.t)
                f = f.coerceIn(0.0, 1.0)
                out.add(Pt(t.toDouble(), a.lat + (b.lat - a.lat) * f, a.lon + (b.lon - a.lon) * f, a.acc + (b.acc - a.acc) * f))
            } else out.add(Pt(t.toDouble(), a.lat, a.lon, a.acc))
        }
        return out
    }

    /** 스트리밍 트랙 빌더. 리플레이와 실시간 위치 모두 이걸 통해 코어 입력을 만든다. */
    class TrackBuilder {
        private var dist = 0.0
        private var slat = Double.NaN; private var slon = Double.NaN
        private var plat = Double.NaN; private var plon = Double.NaN
        private var ignored = 0
        var lastSmoothLat = Double.NaN; private set
        var lastSmoothLon = Double.NaN; private set

        fun push(t: Int, lat: Double, lon: Double, acc: Double): TrackRow {
            // 정확도 게이트를 먼저. 나쁜 점이 평활화 시드가 되면 좌표가 통째로 날아간다
            if (acc > GATE_ACC_M) return TrackRow(t, round(dist * 100).toInt(), 0, acc)
            if (slat.isNaN()) { slat = lat; slon = lon; plat = lat; plon = lon }
            slat = SMOOTH_ALPHA * lat + (1 - SMOOTH_ALPHA) * slat
            slon = SMOOTH_ALPHA * lon + (1 - SMOOTH_ALPHA) * slon
            lastSmoothLat = slat; lastSmoothLon = slon
            var step = haversineM(plat, plon, slat, slon)
            if (step > GATE_SPEED_MS) {
                ignored += 1
                if (ignored >= JUMP_RESET_N) { plat = slat; plon = slon; ignored = 0 }
                step = 0.0
            } else { ignored = 0; plat = slat; plon = slon }
            dist += step
            return TrackRow(t, round(dist * 100).toInt(), round(step * 100).toInt(), acc)
        }
    }

    fun toTrack(pts: List<Pt>): List<TrackRow> {
        val b = TrackBuilder()
        return pts.map { b.push(it.t.toInt(), it.lat, it.lon, it.acc) }
    }

    fun loadTrack(xml: String): List<TrackRow> = toTrack(resample1Hz(parse(xml)))
}
