package kr.runaway.core

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/** Kotlin GPX 파이프라인이 Python(sim/runaway_sim/gpx.py)과 같은 트랙을 만드는지. */
class GpxGoldenTest {
    @Test fun sameTrackAsPython() {
        val xml = javaClass.getResourceAsStream("/golden_steady10.gpx")!!.bufferedReader().readText()
        val got = Gpx.loadTrack(xml)
        val exp = javaClass.getResourceAsStream("/golden_steady10_track.csv")!!.bufferedReader().readLines()
        assertEquals(exp.size, got.size, "row count")
        var maxDist = 0
        for ((i, line) in exp.withIndex()) {
            val c = line.split(',')
            assertEquals(c[0].toInt(), got[i].t)
            maxDist = maxOf(maxDist, kotlin.math.abs(c[1].toInt() - got[i].distCm))
            assertTrue(kotlin.math.abs(c[1].toInt() - got[i].distCm) <= 1, "dist row $i")
            assertTrue(kotlin.math.abs(c[2].toInt() - got[i].speedCms) <= 1, "speed row $i")
            assertTrue(kotlin.math.abs(c[3].toDouble() - got[i].accM) < 1e-3, "acc row $i")
        }
    }
}
