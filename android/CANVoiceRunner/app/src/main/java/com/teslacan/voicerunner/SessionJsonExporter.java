package com.teslacan.voicerunner;

import java.util.List;
import java.util.Locale;

/** V2优化-任务07-无第三方依赖生成稳定 JSON。 */
final class SessionJsonExporter {
    private SessionJsonExporter() { }

    static String export(SessionRecord session, String appVersion) {
        StringBuilder out = new StringBuilder(4096);
        out.append("{\n");
        field(out, 1, "schema_version", "1", true);
        field(out, 1, "exported_clock", quote(SessionRecord.formatClock(
                System.currentTimeMillis())), true);
        field(out, 1, "app_version", quote(appVersion), true);
        out.append("  \"session\": {\n");
        field(out, 2, "session_id", quote(session.sessionId), true);
        field(out, 2, "source_script_name", quote(session.sourceScriptName), true);
        field(out, 2, "start_clock", nullable(session.startClock), true);
        field(out, 2, "start_clock_epoch_ms", number(session.startClockEpochMs), true);
        field(out, 2, "end_clock", nullable(session.endClock), true);
        field(out, 2, "end_clock_epoch_ms", number(session.endClockEpochMs), true);
        field(out, 2, "end_script_time_us", number(session.endScriptTimeUs), true);
        field(out, 2, "status", quote(session.status), true);
        field(out, 2, "end_reason", nullable(session.endReason), true);
        field(out, 2, "script_time_source", quote("ELAPSED_REALTIME"), true);
        field(out, 2, "script_time_unit", quote("us"), true);
        field(out, 2, "clock_precision", quote("ms"), false);
        out.append("  },\n");
        events(out, session.events);
        out.append(",\n");
        photos(out, session.photos);
        out.append(",\n");
        notes(out, session.notes);
        out.append(",\n");
        audio(out, session.audio);
        out.append("\n}\n");
        return out.toString();
    }

    private static void events(StringBuilder out, List<EventRecord> records) {
        out.append("  \"events\": [");
        for (int i = 0; i < records.size(); i++) {
            EventRecord event = records.get(i);
            out.append(i == 0 ? "\n" : ",\n").append("    {\n");
            field(out, 3, "event_id", quote(event.eventId()), true);
            field(out, 3, "event_sequence", Integer.toString(event.index + 1), true);
            field(out, 3, "action", quote(event.step.title), true);
            field(out, 3, "action_detail", quote(event.step.detail), true);
            field(out, 3, "plan_time_s", Integer.toString(event.step.second), true);
            field(out, 3, "status", quote(event.getStatus().csvValue), true);
            field(out, 3, "trigger_script_time_us",
                    number(event.getTriggerScriptTimeUs()), true);
            field(out, 3, "skip_script_time_us",
                    number(event.getSkipScriptTimeUs()), false);
            out.append("    }");
        }
        out.append(records.isEmpty() ? "]" : "\n  ]");
    }

    private static void photos(StringBuilder out, List<PhotoRecord> records) {
        out.append("  \"photos\": [");
        for (int i = 0; i < records.size(); i++) {
            PhotoRecord photo = records.get(i);
            out.append(i == 0 ? "\n" : ",\n").append("    {\n");
            field(out, 3, "photo_id", quote(photo.photoId), true);
            field(out, 3, "event_id", quote(photo.eventId), true);
            field(out, 3, "photo_sequence", Integer.toString(photo.photoSequence), true);
            field(out, 3, "captured_clock", quote(photo.capturedClock), true);
            field(out, 3, "captured_script_time_us",
                    Long.toString(photo.capturedScriptTimeUs), true);
            field(out, 3, "file_name", quote(photo.fileName), true);
            field(out, 3, "content_uri", quote(photo.contentUri), true);
            field(out, 3, "file_status", quote(photo.fileStatus), false);
            out.append("    }");
        }
        out.append(records.isEmpty() ? "]" : "\n  ]");
    }

    private static void notes(StringBuilder out, List<NoteRecord> records) {
        out.append("  \"notes\": [");
        for (int i = 0; i < records.size(); i++) {
            NoteRecord note = records.get(i);
            out.append(i == 0 ? "\n" : ",\n").append("    {\n");
            field(out, 3, "note_id", quote(note.noteId), true);
            field(out, 3, "target_type", quote(note.targetType.name()), true);
            field(out, 3, "target_id", quote(note.targetId), true);
            field(out, 3, "text", quote(note.text), true);
            field(out, 3, "created_clock", quote(note.createdClock), true);
            field(out, 3, "created_script_time_us",
                    Long.toString(note.createdScriptTimeUs), true);
            field(out, 3, "updated_clock", nullable(note.updatedClock), true);
            field(out, 3, "updated_script_time_us",
                    number(note.updatedScriptTimeUs), true);
            field(out, 3, "deleted", Boolean.toString(note.deleted), true);
            field(out, 3, "deleted_clock", nullable(note.deletedClock), true);
            field(out, 3, "deleted_script_time_us",
                    number(note.deletedScriptTimeUs), false);
            out.append("    }");
        }
        out.append(records.isEmpty() ? "]" : "\n  ]");
    }

    private static void audio(StringBuilder out, AudioRecordingRecord audio) {
        out.append("  \"audio_recording\": {\n");
        field(out, 2, "enabled", Boolean.toString(audio.enabled), true);
        field(out, 2, "status", quote(audio.status), true);
        field(out, 2, "file_name", nullable(audio.fileName), true);
        field(out, 2, "content_uri", nullable(audio.contentUri), true);
        field(out, 2, "request_clock", nullable(audio.requestClock), true);
        field(out, 2, "request_offset_us", number(audio.requestOffsetUs), true);
        field(out, 2, "start_clock", nullable(audio.startClock), true);
        field(out, 2, "start_offset_us", number(audio.startOffsetUs), true);
        field(out, 2, "start_method", nullable(audio.startMethod), true);
        field(out, 2, "start_accuracy_us", number(audio.startAccuracyUs), true);
        field(out, 2, "end_clock", nullable(audio.endClock), true);
        field(out, 2, "end_script_time_us", number(audio.endScriptTimeUs), true);
        field(out, 2, "duration_us", number(audio.durationUs), true);
        field(out, 2, "sample_rate_hz", number(audio.sampleRateHz), true);
        field(out, 2, "channel_count", number(audio.channelCount), true);
        field(out, 2, "mime_type", nullable(audio.mimeType), true);
        field(out, 2, "bit_rate", number(audio.bitRate), true);
        field(out, 2, "end_reason", nullable(audio.endReason), true);
        field(out, 2, "failure_clock", nullable(audio.failureClock), true);
        field(out, 2, "failure_script_time_us",
                number(audio.failureScriptTimeUs), true);
        field(out, 2, "failure_reason", nullable(audio.failureReason), false);
        out.append("  }");
    }

    private static void field(StringBuilder out, int indent, String name,
                              String value, boolean comma) {
        for (int i = 0; i < indent; i++) out.append("  ");
        out.append(quote(name)).append(": ").append(value);
        if (comma) out.append(',');
        out.append('\n');
    }

    private static String number(Number value) {
        return value == null ? "null" : value.toString();
    }

    private static String nullable(String value) {
        return value == null ? "null" : quote(value);
    }

    static String quote(String value) {
        if (value == null) return "null";
        StringBuilder out = new StringBuilder(value.length() + 8).append('"');
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            switch (c) {
                case '"': out.append("\\\""); break;
                case '\\': out.append("\\\\"); break;
                case '\b': out.append("\\b"); break;
                case '\f': out.append("\\f"); break;
                case '\n': out.append("\\n"); break;
                case '\r': out.append("\\r"); break;
                case '\t': out.append("\\t"); break;
                default:
                    if (c < 0x20) out.append(String.format(Locale.US, "\\u%04x", (int) c));
                    else out.append(c);
            }
        }
        return out.append('"').toString();
    }
}
