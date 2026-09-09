package com.teslacan.voicerunner;

/** V2优化-任务03-向界面提供连续 script_time 与当前 Event 状态。 */
final class RunnerSnapshot {
    enum State { IDLE, PREPARING, RUNNING, PAUSED, COMPLETED }

    final State state;
    final long elapsedMs;
    final String currentTitle;
    final String nextTitle;
    final int nextSecond;
    final String countdownText;
    final String currentEventStatus;

    RunnerSnapshot(State state, long elapsedMs, String currentTitle,
                   String nextTitle, int nextSecond, String countdownText,
                   String currentEventStatus) {
        this.state = state;
        this.elapsedMs = elapsedMs;
        this.currentTitle = currentTitle;
        this.nextTitle = nextTitle;
        this.nextSecond = nextSecond;
        this.countdownText = countdownText;
        this.currentEventStatus = currentEventStatus;
    }
}
