package com.teslacan.voicerunner;

/** Rogue START/STOP API 的单次 Session 时间证据。 */
final class RogueApiRecord {
    String scriptName;

    String startStatus = "NOT_REQUESTED";
    Long benjiStartRequestEpochMs;
    Long rogueStartRequestReceivedEpochMs;
    Long rogueDumpStartEpochMs;
    Long benjiStartResponseEpochMs;
    String startLogFilename;
    Integer startHttpStatus;
    String startErrorCode;
    String startMessage;
    String startResponseFile;

    String stopStatus = "NOT_REQUESTED";
    Long benjiStopRequestEpochMs;
    Long rogueStopRequestReceivedEpochMs;
    Long rogueDumpStopEpochMs;
    Long benjiStopResponseEpochMs;
    String stopLogFilename;
    Integer stopHttpStatus;
    String stopErrorCode;
    String stopMessage;
    String stopResponseFile;
}
