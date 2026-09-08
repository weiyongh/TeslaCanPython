package com.teslacan.voicerunner;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

import java.util.Arrays;
import java.util.List;

/** V2优化-任务02-验证后台延迟时仍遵循真实采集时间轴。 */
public class SessionTimelineRunnerTest {
    @Test public void firesEachStepOnceAtItsPlannedSecond() {
        RecordingListener listener = new RecordingListener();
        SessionTimelineRunner runner = new SessionTimelineRunner(steps(), listener);

        runner.update(5_000L);
        runner.update(7_000L);
        runner.update(8_000L);
        runner.update(9_000L);
        runner.update(10_000L);
        runner.update(10_900L);
        runner.update(20_000L);
        runner.update(30_000L);

        assertEquals(Arrays.asList("A", "B", "C"), listener.fired);
        assertEquals(Arrays.asList(3, 2, 1), listener.countdowns.subList(0, 3));
        assertEquals(1, listener.completeCount);
    }

    @Test public void skipsPastStepsAndKeepsFutureStepOnOriginalTimeline() {
        RecordingListener listener = new RecordingListener();
        SessionTimelineRunner runner = new SessionTimelineRunner(steps(), listener);

        runner.update(27_000L);
        runner.update(30_000L);

        assertEquals(Arrays.asList("A", "B"), listener.skipped);
        assertEquals(Arrays.asList("C"), listener.fired);
        assertEquals(1, listener.completeCount);
    }

    @Test public void doesNotSpeakAfterCompletion() {
        RecordingListener listener = new RecordingListener();
        SessionTimelineRunner runner = new SessionTimelineRunner(steps(), listener);

        runner.update(10_000L);
        runner.update(20_000L);
        runner.update(30_000L);
        runner.update(40_000L);

        assertEquals(Arrays.asList("A", "B", "C"), listener.fired);
        assertEquals(1, listener.completeCount);
    }

    private List<ScriptStep> steps() {
        return Arrays.asList(
                new ScriptStep(10, "A", ""),
                new ScriptStep(20, "B", ""),
                new ScriptStep(30, "C", ""));
    }

    private static final class RecordingListener implements SessionTimelineRunner.Listener {
        final java.util.ArrayList<String> fired = new java.util.ArrayList<>();
        final java.util.ArrayList<String> skipped = new java.util.ArrayList<>();
        final java.util.ArrayList<Integer> countdowns = new java.util.ArrayList<>();
        int completeCount;

        @Override public void onPrepareStep(int index, ScriptStep step) { }
        @Override public void onCountdown(int value) { countdowns.add(value); }
        @Override public void onFireStep(int index, ScriptStep step, long elapsedMs) { fired.add(step.title); }
        @Override public void onSkipStep(int index, ScriptStep step) { skipped.add(step.title); }
        @Override public void onComplete() { completeCount++; }
    }
}
