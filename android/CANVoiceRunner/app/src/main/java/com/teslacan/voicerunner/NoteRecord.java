package com.teslacan.voicerunner;

/** V2优化-任务05-Event 与 Photo 共用的可审计备注模型。 */
final class NoteRecord {
    enum TargetType { EVENT, PHOTO }

    final String noteId;
    final TargetType targetType;
    final String targetId;
    String text;
    final String createdClock;
    final long createdScriptTimeUs;
    String updatedClock;
    Long updatedScriptTimeUs;
    boolean deleted;
    String deletedClock;
    Long deletedScriptTimeUs;

    NoteRecord(String noteId, TargetType targetType, String targetId, String text,
               String createdClock, long createdScriptTimeUs) {
        this.noteId = noteId;
        this.targetType = targetType;
        this.targetId = targetId;
        this.text = text;
        this.createdClock = createdClock;
        this.createdScriptTimeUs = createdScriptTimeUs;
    }
}
