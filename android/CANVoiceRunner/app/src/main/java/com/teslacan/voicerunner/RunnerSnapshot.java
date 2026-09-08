package com.teslacan.voicerunner;

/** V2优化-任务02-向界面提供前台服务运行状态。 */
final class RunnerSnapshot {
    enum State { IDLE, PREPARING, RUNNING, COMPLETED }

    final State state;
    final long elapsedMs;
    final String currentTitle;
    final String nextTitle;
    final int nextSecond;
    final String countdownText;

    RunnerSnapshot(State state, long elapsedMs, String currentTitle,
                   String nextTitle, int nextSecond, String countdownText) {
        this.state = state;
        this.elapsedMs = elapsedMs;
        this.currentTitle = currentTitle;
        this.nextTitle = nextTitle;
        this.nextSecond = nextSecond;
        this.countdownText = countdownText;
    }
}
