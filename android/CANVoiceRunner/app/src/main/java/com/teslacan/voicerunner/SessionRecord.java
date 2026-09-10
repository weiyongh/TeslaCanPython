package com.teslacan.voicerunner;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/** V2优化-任务04至08-单个采集 Session 的统一内存数据合同。 */
final class SessionRecord {
    final String sessionId;
    final String sourceScriptName;
    final String directoryName;
    final List<EventRecord> events;
    final List<PhotoRecord> photos = new ArrayList<>();
    final List<NoteRecord> notes = new ArrayList<>();
    final AudioRecordingRecord audio = new AudioRecordingRecord();
    long startClockEpochMs;
    String startClock;
    Long endClockEpochMs;
    String endClock;
    Long endScriptTimeUs;
    String status = "ACTIVE";
    String endReason;
    long startRealtimeNs;

    SessionRecord(String sessionId, String sourceScriptName, String directoryName,
                  List<EventRecord> events) {
        this.sessionId = sessionId;
        this.sourceScriptName = sourceScriptName;
        this.directoryName = directoryName;
        this.events = events;
    }

    String clockAt(long scriptTimeUs) {
        return formatClock(startClockEpochMs + Math.round(scriptTimeUs / 1000.0d));
    }

    static String formatClock(long epochMs) {
        return new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSXXX", Locale.US)
                .format(new Date(epochMs));
    }
}
