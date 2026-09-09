package com.teslacan.voicerunner;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

/** V2优化-任务03-验证 script_time 永远连续且暂停只冻结播报进度。 */
public class SessionTimebaseTest {
    @Test public void pauseDoesNotStopScriptTime() {
        SessionTimebase timebase = new SessionTimebase();
        timebase.start(ns(10));
        timebase.pause(ns(14));

        assertTrue(timebase.isPaused());
        assertEquals(9_000_000L, timebase.scriptTimeUs(ns(19)));
        assertEquals(4_000L, timebase.scheduleTimeMs(ns(19)));
    }

    @Test public void resumeContinuesScheduleFromPausedPosition() {
        SessionTimebase timebase = new SessionTimebase();
        timebase.start(ns(10));
        timebase.pause(ns(14));
        timebase.resume(ns(19));

        assertFalse(timebase.isPaused());
        assertEquals(12_000_000L, timebase.scriptTimeUs(ns(22)));
        assertEquals(7_000L, timebase.scheduleTimeMs(ns(22)));
    }

    @Test public void multiplePausesAccumulateWithoutChangingScriptTime() {
        SessionTimebase timebase = new SessionTimebase();
        timebase.start(ns(0));
        timebase.pause(ns(2));
        timebase.resume(ns(5));
        timebase.pause(ns(8));
        timebase.resume(ns(10));

        assertEquals(15_000_000L, timebase.scriptTimeUs(ns(15)));
        assertEquals(10_000L, timebase.scheduleTimeMs(ns(15)));
    }

    private long ns(long seconds) {
        return seconds * 1_000_000_000L;
    }
}
