package com.teslacan.voicerunner;

/** V2优化-任务04-一张成功保存且绑定 Event 的照片。 */
final class PhotoRecord {
    final String photoId;
    final String eventId;
    final int photoSequence;
    final String eventAction;
    final String capturedClock;
    final long capturedScriptTimeUs;
    final String fileName;
    final String contentUri;
    String fileStatus = "AVAILABLE";

    PhotoRecord(String photoId, String eventId, int photoSequence, String eventAction,
                String capturedClock, long capturedScriptTimeUs,
                String fileName, String contentUri) {
        this.photoId = photoId;
        this.eventId = eventId;
        this.photoSequence = photoSequence;
        this.eventAction = eventAction;
        this.capturedClock = capturedClock;
        this.capturedScriptTimeUs = capturedScriptTimeUs;
        this.fileName = fileName;
        this.contentUri = contentUri;
    }
}
