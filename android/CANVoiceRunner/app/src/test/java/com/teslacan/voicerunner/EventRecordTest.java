package com.teslacan.voicerunner;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

import org.junit.Test;

/** V2优化-任务03-验证 triggered/skipped 状态和审计时间不会被覆盖。 */
public class EventRecordTest {
    @Test public void triggerRecordsContinuousScriptTime() {
        EventRecord event = event();
        event.trigger(12_345_678L);
        assertEquals(EventRecord.Status.TRIGGERED, event.getStatus());
        assertEquals(Long.valueOf(12_345_678L), event.getTriggerScriptTimeUs());
        assertNull(event.getSkipScriptTimeUs());
    }

    @Test public void cannotSkipBeforeTrigger() {
        EventRecord event = event();
        assertEquals(false, event.skip(9_000_000L));
        assertEquals(EventRecord.Status.PENDING, event.getStatus());
        assertNull(event.getTriggerScriptTimeUs());
        assertNull(event.getSkipScriptTimeUs());
    }

    @Test public void correctionAfterTriggerPreservesBothAuditTimes() {
        EventRecord event = event();
        event.trigger(10_000_000L);
        assertEquals(true, event.skip(11_500_000L));
        assertEquals(EventRecord.Status.SKIPPED, event.getStatus());
        assertEquals(Long.valueOf(10_000_000L), event.getTriggerScriptTimeUs());
        assertEquals(Long.valueOf(11_500_000L), event.getSkipScriptTimeUs());
    }

    @Test public void repeatedOperationsDoNotOverwriteFirstTimes() {
        EventRecord event = event();
        event.trigger(10L);
        event.trigger(20L);
        event.skip(30L);
        event.skip(40L);
        assertEquals(Long.valueOf(10L), event.getTriggerScriptTimeUs());
        assertEquals(Long.valueOf(30L), event.getSkipScriptTimeUs());
    }

    private EventRecord event() {
        return new EventRecord(0, new ScriptStep(10, "A", ""));
    }
}
