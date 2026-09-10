package com.teslacan.voicerunner;

/** V2优化-任务06-Session 级录音结果。 */
final class AudioRecordingRecord {
    boolean enabled;
    String status = "DISABLED";
    String fileName;
    String contentUri;
    String requestClock;
    Long requestOffsetUs;
    String startClock;
    Long startOffsetUs;
    String startMethod;
    Long startAccuracyUs;
    String endClock;
    Long endScriptTimeUs;
    Long durationUs;
    Integer sampleRateHz;
    Integer channelCount;
    String mimeType;
    Integer bitRate;
    String endReason;
    String failureClock;
    Long failureScriptTimeUs;
    String failureReason;
}
