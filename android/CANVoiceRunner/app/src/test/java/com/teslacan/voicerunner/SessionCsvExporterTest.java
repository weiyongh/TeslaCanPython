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
                1_000L, "2026-09-09T12:00:00.000+08:00",
                91_000L, "2026-09-09T12:01:30.000+08:00", 90_000_000L);

        assertEquals(4, lines.size());
        assertTrue(lines.get(1).contains("session_start"));
        assertTrue(lines.get(1).contains("2026-09-09T12:00:00.000+08:00"));
        assertTrue(lines.get(2).contains(
                "E01,\"插入\"\"充电枪\"\"\",30,skipped,34827000,36000000"));
        assertTrue(lines.get(3).endsWith(",90000000"));
    }
}
