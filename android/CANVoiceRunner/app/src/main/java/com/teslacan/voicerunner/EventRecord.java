package com.teslacan.voicerunner;

/** V2优化-任务03-保存脚本事实与现场触发/跳过记录。 */
final class EventRecord {
    enum Status {
        PENDING("pending"),
        TRIGGERED("triggered"),
        SKIPPED("skipped");

        final String csvValue;

        Status(String csvValue) {
            this.csvValue = csvValue;
        }
    }

    final int index;
    final ScriptStep step;
    private Status status = Status.PENDING;
    private Long triggerScriptTimeUs;
    private Long skipScriptTimeUs;

    EventRecord(int index, ScriptStep step) {
        this.index = index;
        this.step = step;
    }

    void trigger(long scriptTimeUs) {
        if (status == Status.SKIPPED || triggerScriptTimeUs != null) return;
        triggerScriptTimeUs = scriptTimeUs;
        status = Status.TRIGGERED;
    }

    void skip(long scriptTimeUs) {
        if (skipScriptTimeUs != null) return;
        skipScriptTimeUs = scriptTimeUs;
        status = Status.SKIPPED;
    }

    Status getStatus() {
        return status;
    }

    Long getTriggerScriptTimeUs() {
        return triggerScriptTimeUs;
    }

    Long getSkipScriptTimeUs() {
        return skipScriptTimeUs;
    }
}
