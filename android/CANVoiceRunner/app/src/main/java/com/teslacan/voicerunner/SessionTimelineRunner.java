package com.teslacan.voicerunner;

import java.util.List;

/** V2优化-任务02-按真实流逝时间调度脚本播报。 */
final class SessionTimelineRunner {
    interface Listener {
        void onPrepareStep(int index, ScriptStep step);
        void onCountdown(int value);
        void onFireStep(int index, ScriptStep step, long elapsedMs);
        void onSkipStep(int index, ScriptStep step);
        void onComplete();
    }

    private final List<ScriptStep> steps;
    private final Listener listener;
    private int nextStepIndex;
    private int announcedIndex = -1;
    private int countdownSecond = -1;
    private boolean complete;

    SessionTimelineRunner(List<ScriptStep> steps, Listener listener) {
        this.steps = steps;
        this.listener = listener;
    }

    void update(long elapsedMs) {
        if (complete) return;
        int elapsedSecond = (int) (elapsedMs / 1000L);

        while (nextStepIndex < steps.size()
                && steps.get(nextStepIndex).second < elapsedSecond) {
            listener.onSkipStep(nextStepIndex, steps.get(nextStepIndex));
            nextStepIndex++;
        }

        if (nextStepIndex >= steps.size()) {
            complete();
            return;
        }

        ScriptStep step = steps.get(nextStepIndex);
        int remaining = step.second - elapsedSecond;
        if (remaining <= 5 && nextStepIndex != announcedIndex) {
            announcedIndex = nextStepIndex;
            listener.onPrepareStep(nextStepIndex, step);
        }
        if (remaining >= 1 && remaining <= 3 && countdownSecond != remaining) {
            countdownSecond = remaining;
            listener.onCountdown(remaining);
        } else if (remaining > 3) {
            countdownSecond = -1;
        }

        if (remaining == 0) {
            listener.onFireStep(nextStepIndex, step, elapsedMs);
            nextStepIndex++;
            announcedIndex = -1;
            countdownSecond = -1;
            if (nextStepIndex >= steps.size()) complete();
        }
    }

    int getNextStepIndex() {
        return nextStepIndex;
    }

    private void complete() {
        if (complete) return;
        complete = true;
        listener.onComplete();
    }
}
