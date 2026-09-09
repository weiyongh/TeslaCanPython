package com.teslacan.voicerunner;

/** V2优化-任务03-分离连续 script_time 与可暂停的计划播报进度。 */
final class SessionTimebase {
    private long startRealtimeNanos;
    private long accumulatedPauseNanos;
    private long pauseStartRealtimeNanos = -1L;
    private boolean started;

    void start(long nowRealtimeNanos) {
        startRealtimeNanos = nowRealtimeNanos;
        accumulatedPauseNanos = 0L;
        pauseStartRealtimeNanos = -1L;
        started = true;
    }

    void pause(long nowRealtimeNanos) {
        requireStarted();
        if (pauseStartRealtimeNanos < 0L) {
            pauseStartRealtimeNanos = clampedNow(nowRealtimeNanos);
        }
    }

    void resume(long nowRealtimeNanos) {
        requireStarted();
        if (pauseStartRealtimeNanos < 0L) return;
        accumulatedPauseNanos += clampedNow(nowRealtimeNanos) - pauseStartRealtimeNanos;
        pauseStartRealtimeNanos = -1L;
    }

    boolean isPaused() {
        return pauseStartRealtimeNanos >= 0L;
    }

    long scriptTimeUs(long nowRealtimeNanos) {
        requireStarted();
        return (clampedNow(nowRealtimeNanos) - startRealtimeNanos) / 1_000L;
    }

    long scheduleTimeMs(long nowRealtimeNanos) {
        requireStarted();
        long now = clampedNow(nowRealtimeNanos);
        long activePauseNanos = isPaused() ? now - pauseStartRealtimeNanos : 0L;
        long scheduleNanos = now - startRealtimeNanos
                - accumulatedPauseNanos - activePauseNanos;
        return Math.max(0L, scheduleNanos / 1_000_000L);
    }

    private long clampedNow(long nowRealtimeNanos) {
        return Math.max(startRealtimeNanos, nowRealtimeNanos);
    }

    private void requireStarted() {
        if (!started) throw new IllegalStateException("Session timebase has not started");
    }
}
