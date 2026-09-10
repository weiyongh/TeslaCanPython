package com.teslacan.voicerunner;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

import java.util.Arrays;
import java.util.List;

/** V2优化-任务03-验证导出保留 Clock、原始 plan_time 和两类审计时间。 */
public class SessionCsvExporterTest {
    @Test public void exportsSessionAnchorsAndEventTimeDomains() {
        EventRecord event = new EventRecord(0,
                new ScriptStep(30, "插入\"充电枪\"", ""));
        event.trigger(34_827_000L);
        event.skip(36_000_000L);

        List<String> lines = SessionCsvExporter.export(Arrays.asList(event),
                1_788_926_400_000L, "2026-09-09T12:00:00.000+08:00");

        assertEquals(2, lines.size());
        assertEquals("event_id,action,plan_time_s,status,session_script_time_us,"
                + "skip_script_time_us,clock_iso,clock_epoch_ms", lines.get(0));
        assertTrue(lines.get(1).contains(
                "E01,\"插入\"\"充电枪\"\"\",30,skipped,34827000,36000000"));
        assertTrue(lines.get(1).endsWith(
                "\"2026-09-09T12:00:34.827+08:00\",1788926434827"));
    }

    @Test public void pendingEventDoesNotInventObservedTime() {
        EventRecord event = new EventRecord(0, new ScriptStep(10, "未触发动作", ""));
        List<String> lines = SessionCsvExporter.export(Arrays.asList(event),
                1_788_926_400_000L, "2026-09-09T12:00:00.000+08:00");
        assertEquals("E01,\"未触发动作\",10,pending,,,\"\",", lines.get(1));
    }
}
