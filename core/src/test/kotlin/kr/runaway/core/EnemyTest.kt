package kr.runaway.core

import kotlin.test.Test
import kotlin.test.assertEquals

class EnemyTest {
    @Test fun cheetahFatigueParams() {
        val a = Animals.get("cheetah")
        val (sp0, du0, rc0) = a.cycleParams(0)
        val (sp1, du1, rc1) = a.cycleParams(1)
        assertEquals(sp0 * 750 / 1000, sp1)
        assertEquals(du0 * 700 / 1000, du1)
        assertEquals(rc0 * 1600 / 1000, rc1)
    }
    @Test fun firstSprintLasts25s() {
        val e = Enemy(Animals.get("cheetah"), 5000)
        val states = (1..300).map { e.tick(0, 8.0) }
        var run = 0
        for (s in states) { if (s == EnemyState.SPRINT) run++ else if (run > 0) break }
        assertEquals(25, run)
    }
    @Test fun lostWhenAccuracyBad() {
        val e = Enemy(Animals.get("cheetah"), 5000)
        assertEquals(EnemyState.LOST, e.tick(0, 50.0)); assertEquals(0, e.speed)
    }
}
