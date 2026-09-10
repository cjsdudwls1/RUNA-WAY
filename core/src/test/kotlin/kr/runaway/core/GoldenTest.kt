package kr.runaway.core

import kotlin.test.Test
import kotlin.test.assertEquals

/** Python 시뮬(sim/)의 결과와 동일해야 한다. core/tools/gen_golden.py로 생성. */
class GoldenTest {
    private fun res(name: String) = javaClass.getResourceAsStream("/$name")!!.bufferedReader().readLines()

    private val track: List<TrackRow> = res("golden_track.csv").map {
        val c = it.split(',')
        TrackRow(c[0].toInt(), c[1].toInt(), c[2].toInt(), c[3].toDouble())
    }

    @Test fun matchesPython() {
        for (line in res("golden_expected.csv")) {
            val c = line.split(',')
            val r = Session.run(track, Animals.get(c[0]), 500000)
            assertEquals(c[1].toInt(), r.hits, "${c[0]} hits")
            assertEquals(c[2].toInt(), r.sprints, "${c[0]} sprints")
            assertEquals(c[3].toInt() == 1, r.failed, "${c[0]} failed")
            assertEquals(c[4].toInt(), r.minGapCm, "${c[0]} minGap")
            assertEquals(c[5].toInt(), r.finalTimeS, "${c[0]} finalTime")
            assertEquals(c[6].toInt(), r.pausedS, "${c[0]} paused")
            assertEquals(c[7].toInt(), r.lostS, "${c[0]} lost")
            assertEquals(c[8].toInt(), r.reengages, "${c[0]} reengages")
            assertEquals(c[9].toLong(), r.enemyMovedCm, "${c[0]} enemyMoved")
        }
    }
}
