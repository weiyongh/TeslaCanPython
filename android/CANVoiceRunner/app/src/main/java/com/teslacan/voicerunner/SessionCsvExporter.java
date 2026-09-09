package com.teslacan.voicerunner;

import java.util.ArrayList;
import java.util.List;

/** V2优化-任务03-导出带明确时间域的临时 CSV 验证记录。 */
final class SessionCsvExporter {
    private SessionCsvExporter() { }

    static List<String> export(List<EventRecord> events,
                               long startClockEpochMs, String startClock,
                               long endClockEpochMs, String endClock,
                               long endScriptTimeUs) {
        List<String> lines = new ArrayList<>();
        lines.add("record_type,event_id,action,plan_time_s,status,"
                + "trigger_script_time_us,skip_script_time_us,clock_iso,"
                + "clock_epoch_ms,session_script_time_us");
        lines.add("session_start,,,,,,," + csv(startClock) + ","
                + startClockEpochMs + ",0");
        for (EventRecord event : events) {
            lines.add("event," + eventId(event.index) + "," + csv(event.step.title)
                    + "," + event.step.second + "," + event.getStatus().csvValue
                    + "," + nullable(event.getTriggerScriptTimeUs())
                    + "," + nullable(event.getSkipScriptTimeUs()) + ",,,");
        }
        lines.add("session_end,,,,,,," + csv(endClock) + ","
                + endClockEpochMs + "," + endScriptTimeUs);
        return lines;
    }

    private static String eventId(int index) {
        return String.format(java.util.Locale.US, "E%02d", index + 1);
    }

    private static String nullable(Long value) {
        return value == null ? "" : Long.toString(value);
    }

    private static String csv(String value) {
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }
}
