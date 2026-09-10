package com.teslacan.voicerunner;

import static org.junit.Assert.assertTrue;

import org.junit.Test;

import java.util.ArrayList;
import java.util.List;

/** V2优化-任务07-验证完整 JSON 的关键合同字段。 */
public class SessionJsonExporterTest {
    @Test public void exportsEventsPhotosNotesAndDisabledAudio() {
        List<EventRecord> events = new ArrayList<>();
        EventRecord event = new EventRecord(0,
                new ScriptStep(0, "开始\"采集", "保持 P 挡"));
        event.trigger(125_000L);
        events.add(event);
        SessionRecord session = new SessionRecord("S0001", "脚本.txt",
                "脚本__20260910_093000_000__S0001", events);
        session.startClockEpochMs = 1_788_930_000_000L;
        session.startClock = "2026-09-09T12:00:00.000+08:00";
        session.endClockEpochMs = 1_788_930_001_000L;
        session.endClock = "2026-09-09T12:00:01.000+08:00";
        session.endScriptTimeUs = 1_000_000L;
        session.status = "COMPLETED";
        session.endReason = "NATURAL_COMPLETION";
        session.photos.add(new PhotoRecord("E01-P01", "E01", 1,
                "开始采集", session.clockAt(200_000L), 200_000L,
                "E01-P01_开始采集.jpg", "content://photo/1"));
        session.notes.add(new NoteRecord("N0001", NoteRecord.TargetType.EVENT,
                "E01", "现场正常", session.clockAt(300_000L), 300_000L));

        String json = SessionJsonExporter.export(session, "0.2.0");

        assertTrue(json.contains("\"session_id\": \"S0001\""));
        assertTrue(json.contains("\"action\": \"开始\\\"采集\""));
        assertTrue(json.contains("\"photo_id\": \"E01-P01\""));
        assertTrue(json.contains("\"note_id\": \"N0001\""));
        assertTrue(json.contains("\"status\": \"DISABLED\""));
    }
}
