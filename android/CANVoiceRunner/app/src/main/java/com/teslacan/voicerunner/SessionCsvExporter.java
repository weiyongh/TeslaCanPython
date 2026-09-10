package com.teslacan.voicerunner;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.TimeZone;

/** V2优化-任务03-导出带明确时间域的临时 CSV 验证记录。 */
final class SessionCsvExporter {
    private SessionCsvExporter() { }

    static List<String> export(List<EventRecord> events,
                               long startClockEpochMs, String startClock) {
        List<String> lines = new ArrayList<>();
        lines.add("event_id,action,plan_time_s,status,session_script_time_us,"
                + "skip_script_time_us,clock_iso,clock_epoch_ms");
        for (EventRecord event : events) {
            Long scriptUs = event.getTriggerScriptTimeUs();
            Long eventEpochMs = scriptUs == null ? null
                    : startClockEpochMs + Math.round(scriptUs / 1000.0d);
            String eventClock = eventEpochMs == null ? "" : formatClock(
                    eventEpochMs, timeZoneFrom(startClock));
            lines.add(event.eventId() + "," + csv(event.step.title)
                    + "," + event.step.second + "," + event.getStatus().csvValue
                    + "," + nullable(scriptUs)
                    + "," + nullable(event.getSkipScriptTimeUs())
                    + "," + csv(eventClock) + "," + nullable(eventEpochMs));
        }
        return lines;
    }

    private static TimeZone timeZoneFrom(String clock) {
        if (clock != null && clock.length() >= 6) {
            String suffix = clock.substring(clock.length() - 6);
            if (suffix.matches("[+-][0-9]{2}:[0-9]{2}")) {
                return TimeZone.getTimeZone("GMT" + suffix);
            }
        }
        return TimeZone.getDefault();
    }

    private static String formatClock(long epochMs, TimeZone zone) {
        SimpleDateFormat format = new SimpleDateFormat(
                "yyyy-MM-dd'T'HH:mm:ss.SSSXXX", Locale.US);
        format.setTimeZone(zone);
        return format.format(new Date(epochMs));
    }

    private static String nullable(Long value) {
        return value == null ? "" : Long.toString(value);
    }

    private static String csv(String value) {
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }
}
