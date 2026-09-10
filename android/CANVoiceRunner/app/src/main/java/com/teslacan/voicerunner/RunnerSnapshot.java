package com.teslacan.voicerunner;

/** V2优化-任务03-向界面提供连续 script_time 与当前 Event 状态。 */
final class RunnerSnapshot {
    enum State { IDLE, PREPARING, RUNNING, PAUSED, COMPLETED }

    final State state;
    final long elapsedMs;
    final long scheduleElapsedMs;
    final String currentTitle;
    final String nextTitle;
    final int nextSecond;
    final String countdownText;
    final String currentEventStatus;
    final int photoCount;
    final int eventNoteCount;
    final String recordingStatus;

    RunnerSnapshot(State state, long elapsedMs, long scheduleElapsedMs, String currentTitle,
                   String nextTitle, int nextSecond, String countdownText,
                   String currentEventStatus, int photoCount, int eventNoteCount,
                   String recordingStatus) {
        this.state = state;
        this.elapsedMs = elapsedMs;
        this.scheduleElapsedMs = scheduleElapsedMs;
        this.currentTitle = currentTitle;
        this.nextTitle = nextTitle;
        this.nextSecond = nextSecond;
        this.countdownText = countdownText;
        this.currentEventStatus = currentEventStatus;
        this.photoCount = photoCount;
        this.eventNoteCount = eventNoteCount;
        this.recordingStatus = recordingStatus;
    }
}
