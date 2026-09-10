package kr.runaway.core

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ThreatTest {
    @Test fun fillIn4sThenHit() {
        val th = Threat()
        val ev = (1..4).map { th.tick(2000, 8.0) }
        assertTrue(ev.last()); assertEquals(1, th.hits)
    }
    @Test fun hysteresis() {
        val th = Threat()
        th.tick(2000, 8.0); assertTrue(th.inside)
        th.tick(4000, 8.0); assertTrue(th.inside)
        th.tick(5000, 8.0); assertFalse(th.inside)
    }
    @Test fun decayTwiceFast() {
        val th = Threat()
        repeat(3) { th.tick(2000, 8.0) }
        th.tick(7000, 8.0); assertEquals(250, th.gauge)
        th.tick(7000, 8.0); assertEquals(0, th.gauge)
    }
    @Test fun accuracySlowAndFreeze() {
        val th = Threat()
        th.tick(2000, 30.0); assertEquals(125, th.gauge)
        th.tick(2000, 45.0); assertEquals(125, th.gauge)
    }
}
