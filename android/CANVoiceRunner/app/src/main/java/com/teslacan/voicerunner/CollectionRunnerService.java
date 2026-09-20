package com.teslacan.voicerunner;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.content.pm.PackageManager;
import android.Manifest;
import android.media.AudioManager;
import android.media.ToneGenerator;
import android.os.Binder;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.SystemClock;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** V2优化-任务03-维护连续 script_time、可暂停播报和 Event 记录。 */
public final class CollectionRunnerService extends Service
        implements TextToSpeech.OnInitListener, SessionTimelineRunner.Listener {
    static final String ACTION_START = "com.teslacan.voicerunner.START";
    static final String ACTION_STOP = "com.teslacan.voicerunner.STOP";
    static final String EXTRA_SCRIPT = "script";
    static final String EXTRA_SCRIPT_NAME = "script_name";
    static final String EXTRA_RECORDING_ENABLED = "recording_enabled";
    static final String EXTRA_MANUAL_TRIGGER_MODE = "manual_trigger_mode";

    interface SnapshotListener {
        void onSnapshot(RunnerSnapshot snapshot);
    }

    interface ExportListener {
        void onExported();
        void onError(String message);
    }

    final class LocalBinder extends Binder {
        CollectionRunnerService getService() {
            return CollectionRunnerService.this;
        }
    }

    private static final String CHANNEL_ID = "collection_runner";
    private static final int NOTIFICATION_ID = 2001;
    private static final long TICK_MS = 100L;

    private final IBinder binder = new LocalBinder();
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final SessionTimebase timebase = new SessionTimebase();
    private final List<EventRecord> eventRecords = new ArrayList<>();
    private final ExecutorService persistenceExecutor = Executors.newSingleThreadExecutor();
    private final ExecutorService rogueApiExecutor = Executors.newSingleThreadExecutor();
    private final RogueApiClient rogueApiClient = new RogueApiClient();
    private List<ScriptStep> steps = Collections.emptyList();
    private SessionTimelineRunner timelineRunner;
    private SnapshotListener snapshotListener;
    private TextToSpeech textToSpeech;
    private ToneGenerator toneGenerator;
    private boolean ttsReady;
    private boolean preRollStarted;
    private boolean completionClaimed;
    private long completedScriptTimeUs;
    private long completedScheduleTimeMs;
    private long startClockEpochMs;
    private long endClockEpochMs;
    private String startClock = "";
    private String endClock = "";
    private int currentEventIndex = -1;
    private String lastNotificationText;
    private RunnerSnapshot.State state = RunnerSnapshot.State.IDLE;
    private String currentTitle = "尚未开始";
    private String countdownText = "—";
    private String sourceScriptName = "采集脚本.txt";
    private boolean recordingEnabled;
    private boolean manualTriggerMode;
    private int manualNextStepIndex;
    private SessionRecord sessionRecord;
    private SessionStorage sessionStorage;
    private SessionStorage.Files sessionFiles;
    private SessionAudioRecorder audioRecorder;
    private String audioStartFailure;
    private boolean rogueStartRequested;
    private boolean rogueStartSucceeded;
    private boolean rogueStopRequested;
    private boolean pendingCompletionAnnounce;

    private final Runnable tick = new Runnable() {
        @Override public void run() {
            if (!isActive()) return;
            long nowNanos = SystemClock.elapsedRealtimeNanos();
            if (state == RunnerSnapshot.State.RUNNING && !manualTriggerMode) {
                timelineRunner.update(timebase.scheduleTimeMs(nowNanos));
            }
            publish(timebase.scriptTimeUs(nowNanos) / 1_000L);
            if (isActive()) handler.postDelayed(this, TICK_MS);
        }
    };

    @Override public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        textToSpeech = new TextToSpeech(this, this);
        toneGenerator = new ToneGenerator(AudioManager.STREAM_MUSIC, 90);
        sessionStorage = new SessionStorage(this);
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null) return START_NOT_STICKY;
        String action = intent.getAction();
        if (ACTION_STOP.equals(action)) {
            finishSession();
            return START_NOT_STICKY;
        }
        if (ACTION_START.equals(action)) {
            sourceScriptName = intent.getStringExtra(EXTRA_SCRIPT_NAME);
            if (sourceScriptName == null || sourceScriptName.trim().isEmpty()) {
                sourceScriptName = "采集脚本.txt";
            }
            recordingEnabled = intent.getBooleanExtra(EXTRA_RECORDING_ENABLED, false);
            manualTriggerMode = intent.getBooleanExtra(EXTRA_MANUAL_TRIGGER_MODE, false);
            startInForeground(buildNotification("准备开始采集"));
            startSession(intent.getStringExtra(EXTRA_SCRIPT));
        }
        return START_NOT_STICKY;
    }

    @Override public IBinder onBind(Intent intent) {
        return binder;
    }

    void setSnapshotListener(SnapshotListener listener) {
        snapshotListener = listener;
        publish(currentElapsedMs());
    }

    RunnerSnapshot getSnapshot() {
        return createSnapshot(currentElapsedMs());
    }

    List<String> getEvents() {
        return SessionCsvExporter.export(eventRecords,
                startClockEpochMs, startClock);
    }

    SessionRecord getSessionRecord() {
        return sessionRecord;
    }

    SessionStorage.Files getSessionFiles() {
        return sessionFiles;
    }

    boolean claimCompletion() {
        if (state != RunnerSnapshot.State.COMPLETED || completionClaimed
                || !isAudioTerminal()) return false;
        completionClaimed = true;
        stopForeground(STOP_FOREGROUND_REMOVE);
        return true;
    }

    private void startSession(String scriptText) {
        try {
            steps = ScriptParser.parse(scriptText == null ? "" : scriptText);
        } catch (RuntimeException error) {
            stopSession();
            return;
        }
        handler.removeCallbacksAndMessages(null);
        eventRecords.clear();
        for (int i = 0; i < steps.size(); i++) {
            eventRecords.add(new EventRecord(i, steps.get(i)));
        }
        preRollStarted = false;
        completionClaimed = false;
        completedScriptTimeUs = 0L;
        completedScheduleTimeMs = 0L;
        startClockEpochMs = 0L;
        endClockEpochMs = 0L;
        startClock = "";
        endClock = "";
        currentEventIndex = -1;
        manualNextStepIndex = 0;
        sessionRecord = null;
        sessionFiles = null;
        audioRecorder = null;
        audioStartFailure = null;
        rogueStartRequested = false;
        rogueStartSucceeded = false;
        rogueStopRequested = false;
        pendingCompletionAnnounce = false;
        lastNotificationText = null;
        timelineRunner = manualTriggerMode ? null : new SessionTimelineRunner(steps, this);
        state = RunnerSnapshot.State.PREPARING;
        currentTitle = "准备开始采集";
        countdownText = "—";
        publish(0L);
        if (recordingEnabled) startAudioPreRoll();
        createSessionAndStartRogue();
    }

    private void createSessionAndStartRogue() {
        long nowNanos = SystemClock.elapsedRealtimeNanos();
        timebase.start(nowNanos);
        timebase.pause(nowNanos);
        startClockEpochMs = System.currentTimeMillis();
        startClock = formatWallClock(startClockEpochMs);
        String sessionId = sessionStorage.nextSessionId();
        String directoryName = SessionStorage.directoryName(
                sourceScriptName, startClockEpochMs, sessionId);
        sessionRecord = new SessionRecord(
                sessionId, sourceScriptName, directoryName, eventRecords);
        sessionRecord.startClockEpochMs = startClockEpochMs;
        sessionRecord.startClock = startClock;
        sessionRecord.startRealtimeNs = nowNanos;
        sessionRecord.status = "STARTING";
        sessionRecord.rogueApi.scriptName = rogueScriptName(sourceScriptName);
        sessionRecord.audio.enabled = recordingEnabled;
        if (!recordingEnabled) {
            sessionRecord.audio.status = "DISABLED";
        } else if (audioStartFailure != null) {
            markAudioFailure(audioStartFailure, 0L);
        } else {
            sessionRecord.audio.status = "RECORDING";
            sessionRecord.audio.requestClock = formatWallClock(audioRecorder.requestClockEpochMs());
            sessionRecord.audio.requestOffsetUs =
                    (audioRecorder.requestRealtimeNs() - nowNanos) / 1_000L;
            sessionRecord.audio.sampleRateHz = 48_000;
            sessionRecord.audio.channelCount = 1;
            sessionRecord.audio.mimeType = "audio/mp4";
            sessionRecord.audio.bitRate = 96_000;
        }
        try {
            sessionFiles = sessionStorage.createSessionFiles(directoryName);
            persistAsync();
        } catch (IOException error) {
            sessionFiles = null;
        }
        sendRogueStart();
    }

    private void beginPreRoll() {
        if (state != RunnerSnapshot.State.PREPARING || preRollStarted) return;
        preRollStarted = true;
        preRoll(3, "三", 0L);
        preRoll(2, "二", 1000L);
        preRoll(1, "一", 2000L);
        handler.postDelayed(this::beginTimedRun, 3000L);
    }

    private void preRoll(int value, String voice, long delayMs) {
        handler.postDelayed(() -> {
            if (state != RunnerSnapshot.State.PREPARING) return;
            countdownText = String.valueOf(value);
            speak(voice);
            toneGenerator.startTone(ToneGenerator.TONE_PROP_BEEP, 120);
            publish(0L);
        }, delayMs);
    }

    private void beginTimedRun() {
        if (state != RunnerSnapshot.State.PREPARING) return;
        state = RunnerSnapshot.State.RUNNING;
        long nowNanos = SystemClock.elapsedRealtimeNanos();
        timebase.resume(nowNanos);
        sessionRecord.status = "ACTIVE";
        currentTitle = "开始采集";
        countdownText = "开始";
        if (manualTriggerMode) {
            triggerManualStep(0);
            manualNextStepIndex = Math.min(1, steps.size());
        } else {
            speak("开始采集");
            timelineRunner.update(timebase.scheduleTimeMs(nowNanos));
        }
        publish(0L);
        handler.post(tick);
    }

    void stopSession() {
        if (rogueStartRequested && sessionRecord != null
                && "REQUESTED".equals(sessionRecord.rogueApi.startStatus)) return;
        handler.removeCallbacksAndMessages(null);
        if (textToSpeech != null) textToSpeech.stop();
        if (audioRecorder != null) audioRecorder.stop();
        state = RunnerSnapshot.State.IDLE;
        currentTitle = "尚未开始";
        countdownText = "—";
        publish(0L);
        stopForeground(STOP_FOREGROUND_REMOVE);
        stopSelf();
    }

    void finishSession() {
        if (!isActive()) return;
        completeSession(true);
    }

    void togglePause() {
        if (state == RunnerSnapshot.State.RUNNING) {
            timebase.pause(SystemClock.elapsedRealtimeNanos());
            state = RunnerSnapshot.State.PAUSED;
            if (textToSpeech != null) textToSpeech.stop();
            publish(currentElapsedMs());
        } else if (state == RunnerSnapshot.State.PAUSED) {
            timebase.resume(SystemClock.elapsedRealtimeNanos());
            state = RunnerSnapshot.State.RUNNING;
            publish(currentElapsedMs());
        }
    }

    boolean skipCurrentEvent() {
        if (!isActive() || eventRecords.isEmpty() || currentEventIndex < 0) return false;
        int targetIndex = currentEventIndex;
        if (targetIndex < 0 || targetIndex >= eventRecords.size()) return false;
        EventRecord target = eventRecords.get(targetIndex);
        if (!target.skip(currentScriptTimeUs())) return false;
        currentEventIndex = targetIndex;
        currentTitle = target.step.title;
        countdownText = "跳过";
        publish(currentElapsedMs());
        persistAsync();
        return true;
    }

    boolean triggerNextManualEvent() {
        if (!manualTriggerMode || state != RunnerSnapshot.State.RUNNING
                || manualNextStepIndex < 0 || manualNextStepIndex >= steps.size()) {
            return false;
        }
        triggerManualStep(manualNextStepIndex);
        manualNextStepIndex++;
        publish(currentElapsedMs());
        return true;
    }

    private void triggerManualStep(int index) {
        if (index < 0 || index >= eventRecords.size()) return;
        EventRecord event = eventRecords.get(index);
        if (event.getStatus() != EventRecord.Status.PENDING) return;
        event.trigger(currentScriptTimeUs());
        currentEventIndex = index;
        currentTitle = event.step.title;
        countdownText = "执行";
        speak(event.step.title);
        persistAsync();
    }

    @Override public void onPrepareStep(int index, ScriptStep step) {
        if (eventRecords.get(index).getStatus() == EventRecord.Status.SKIPPED) return;
        speak("准备，" + step.title);
    }

    @Override public void onCountdown(int index, int value) {
        if (eventRecords.get(index).getStatus() == EventRecord.Status.SKIPPED) return;
        countdownText = String.valueOf(value);
        toneGenerator.startTone(ToneGenerator.TONE_PROP_BEEP, 120);
    }

    @Override public void onFireStep(int index, ScriptStep step, long elapsedMs) {
        EventRecord event = eventRecords.get(index);
        if (event.getStatus() == EventRecord.Status.SKIPPED) return;
        event.trigger(currentScriptTimeUs());
        currentEventIndex = index;
        currentTitle = step.title;
        countdownText = "执行";
        toneGenerator.startTone(ToneGenerator.TONE_PROP_ACK, 260);
        persistAsync();
    }

    @Override public void onSkipStep(int index, ScriptStep step) {
        // 已过去的计划节点不补播，保持采集时间流逝的真实性。
    }

    @Override public void onComplete() {
        completeSession(true);
    }

    private long currentElapsedMs() {
        if (state == RunnerSnapshot.State.COMPLETED) return completedScriptTimeUs / 1_000L;
        if (state == RunnerSnapshot.State.STOPPING) return completedScriptTimeUs / 1_000L;
        return isActive() ? currentScriptTimeUs() / 1_000L : 0L;
    }

    private RunnerSnapshot createSnapshot(long elapsedMs) {
        int nextIndex = manualTriggerMode
                ? manualNextStepIndex
                : (timelineRunner == null ? 0 : timelineRunner.getNextStepIndex());
        while (nextIndex < eventRecords.size()
                && eventRecords.get(nextIndex).getStatus() == EventRecord.Status.SKIPPED) {
            nextIndex++;
        }
        String nextTitle = nextIndex < steps.size() ? steps.get(nextIndex).title : "已完成";
        int nextSecond = nextIndex < steps.size() ? steps.get(nextIndex).second : -1;
        String eventStatus = currentEventIndex >= 0 && currentEventIndex < eventRecords.size()
                ? eventRecords.get(currentEventIndex).getStatus().csvValue : "pending";
        long scheduleMs;
        if (state == RunnerSnapshot.State.COMPLETED) {
            scheduleMs = completedScheduleTimeMs;
        } else if (state == RunnerSnapshot.State.STOPPING) {
            scheduleMs = completedScheduleTimeMs;
        } else {
            scheduleMs = isActive() && timebase.isStarted()
                    ? timebase.scheduleTimeMs(SystemClock.elapsedRealtimeNanos()) : elapsedMs;
        }
        int photos = sessionRecord == null ? 0 : sessionRecord.photos.size();
        int notes = 0;
        if (sessionRecord != null) {
            for (NoteRecord note : sessionRecord.notes) {
                if (!note.deleted && note.targetType == NoteRecord.TargetType.EVENT) notes++;
            }
        }
        String audioStatus = sessionRecord == null
                ? (recordingEnabled ? "PREPARING" : "DISABLED")
                : sessionRecord.audio.status;
        return new RunnerSnapshot(state, elapsedMs, scheduleMs, currentTitle, nextTitle,
                nextSecond, countdownText, eventStatus, photos, notes, audioStatus,
                manualTriggerMode);
    }

    private void publish(long elapsedMs) {
        RunnerSnapshot snapshot = createSnapshot(elapsedMs);
        if (state == RunnerSnapshot.State.PREPARING || state == RunnerSnapshot.State.RUNNING
                || state == RunnerSnapshot.State.PAUSED
                || state == RunnerSnapshot.State.STOPPING
                || state == RunnerSnapshot.State.COMPLETED) {
            String notificationText = notificationText(snapshot);
            if (!notificationText.equals(lastNotificationText)) {
                lastNotificationText = notificationText;
                getSystemService(NotificationManager.class).notify(
                        NOTIFICATION_ID, buildNotification(notificationText));
            }
        }
        if (snapshotListener != null) snapshotListener.onSnapshot(snapshot);
    }

    private String notificationText(RunnerSnapshot snapshot) {
        if (snapshot.state == RunnerSnapshot.State.PREPARING) return "准备开始采集";
        if (snapshot.state == RunnerSnapshot.State.STOPPING) return "正在停止罗格采集";
        String elapsed = formatClock((int) (snapshot.elapsedMs / 1000L));
        if (snapshot.state == RunnerSnapshot.State.PAUSED) {
            return elapsed + " · 播报暂停，采集时间继续";
        }
        return snapshot.nextSecond >= 0
                ? elapsed + " · 下一操作 " + formatClock(snapshot.nextSecond) + " " + snapshot.nextTitle
                : elapsed + " · 已完成";
    }

    private void createNotificationChannel() {
        NotificationChannel channel = new NotificationChannel(CHANNEL_ID,
                "采集播报运行状态", NotificationManager.IMPORTANCE_LOW);
        channel.setDescription("采集期间保持计时和语音播报");
        getSystemService(NotificationManager.class).createNotificationChannel(channel);
    }

    private Notification buildNotification(String text) {
        Intent openIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, openIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        return new Notification.Builder(this, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_lock_silent_mode_off)
                .setContentTitle("CAN 采集播报正在运行")
                .setContentText(text)
                .setContentIntent(pendingIntent)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .build();
    }

    private void startInForeground(Notification notification) {
        if (Build.VERSION.SDK_INT >= 34) {
            int types = ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE;
            if (recordingEnabled && checkSelfPermission(Manifest.permission.RECORD_AUDIO)
                    == PackageManager.PERMISSION_GRANTED) {
                types |= ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE;
            }
            startForeground(NOTIFICATION_ID, notification,
                    types);
        } else {
            startForeground(NOTIFICATION_ID, notification);
        }
    }

    private void speak(String text) {
        speak(text, "step_" + SystemClock.uptimeMillis());
    }

    private void speak(String text, String id) {
        if (ttsReady) textToSpeech.speak(text, TextToSpeech.QUEUE_FLUSH, null, id);
    }

    private String formatClock(int seconds) {
        int value = Math.floorMod(seconds, 3600);
        return String.format(Locale.CHINA, "%02d:%02d", value / 60, value % 60);
    }

    private boolean isActive() {
        return state == RunnerSnapshot.State.RUNNING || state == RunnerSnapshot.State.PAUSED;
    }

    private long mappedEpochMs(long realtimeNs) {
        return startClockEpochMs
                + Math.round(timebase.scriptTimeUs(realtimeNs) / 1000.0d);
    }

    private static String rogueScriptName(String name) {
        return name == null ? "采集脚本" : name.replaceFirst("\\.[^.]+$", "");
    }

    private void sendRogueStart() {
        if (rogueStartRequested || sessionRecord == null) return;
        rogueStartRequested = true;
        sessionRecord.rogueApi.startStatus = "REQUESTED";
        rogueApiExecutor.execute(() -> {
            long requestRealtimeNs = SystemClock.elapsedRealtimeNanos();
            long requestEpochMs = mappedEpochMs(requestRealtimeNs);
            sessionRecord.rogueApi.benjiStartRequestEpochMs = requestEpochMs;
            try {
                RogueApiClient.Result result = rogueApiClient.start(
                        sessionRecord.rogueApi.scriptName, sessionRecord.sessionId,
                        requestEpochMs);
                saveRawRogueResponse(true, result.rawJson);
                handler.post(() -> handleRogueStartResult(result));
            } catch (RogueApiClient.ResponseException error) {
                saveRawRogueResponse(true, error.rawJson);
                handler.post(() -> failRogueStart(error.httpStatus, error.errorCode,
                        error.getMessage(), mappedEpochMs(error.responseRealtimeNs)));
            } catch (IOException error) {
                handler.post(() -> failRogueStart(null, "NETWORK_ERROR",
                        error.getMessage(), null));
            }
        });
    }

    private void handleRogueStartResult(RogueApiClient.Result result) {
        RogueApiRecord api = sessionRecord.rogueApi;
        api.startHttpStatus = result.httpStatus;
        api.benjiStartResponseEpochMs = mappedEpochMs(result.responseRealtimeNs);
        if (!result.ok) {
            failRogueStart(result.httpStatus, result.errorCode, result.message,
                    api.benjiStartResponseEpochMs);
            return;
        }
        api.rogueStartRequestReceivedEpochMs = result.requestReceivedEpochMs;
        api.rogueDumpStartEpochMs = result.dumpEpochMs;
        api.startLogFilename = result.logFilename;
        if (result.httpStatus != 200
                || !api.scriptName.equals(result.scriptName)
                || !sessionRecord.sessionId.equals(result.sessionId)
                || result.logFilename == null || result.logFilename.isEmpty()) {
            failRogueStart(result.httpStatus, "RESPONSE_MISMATCH",
                    "Rogue START response 与当前 Session 不一致",
                    api.benjiStartResponseEpochMs);
            return;
        }
        api.startStatus = "SUCCEEDED";
        rogueStartSucceeded = true;
        persistAsync();
        currentTitle = "准备开始采集";
        countdownText = "—";
        publish(currentElapsedMs());
        if (ttsReady) speak("准备开始采集", "pre_start");
        else handler.postDelayed(this::beginPreRoll, 1800L);
    }

    private void failRogueStart(Integer httpStatus, String errorCode,
                                String message, Long responseEpochMs) {
        if (sessionRecord == null || rogueStartSucceeded) return;
        RogueApiRecord api = sessionRecord.rogueApi;
        api.startStatus = "FAILED";
        api.startHttpStatus = httpStatus;
        api.startErrorCode = errorCode;
        api.startMessage = message;
        api.benjiStartResponseEpochMs = responseEpochMs;
        long nowNs = SystemClock.elapsedRealtimeNanos();
        completedScriptTimeUs = timebase.scriptTimeUs(nowNs);
        completedScheduleTimeMs = 0L;
        sessionRecord.endScriptTimeUs = completedScriptTimeUs;
        endClockEpochMs = mappedEpochMs(nowNs);
        endClock = formatWallClock(endClockEpochMs);
        sessionRecord.endClockEpochMs = endClockEpochMs;
        sessionRecord.endClock = endClock;
        sessionRecord.status = "START_FAILED";
        sessionRecord.endReason = "ROGUE_START_FAILED";
        if (audioRecorder != null) audioRecorder.stop();
        state = RunnerSnapshot.State.COMPLETED;
        currentTitle = "罗格启动失败";
        countdownText = "—";
        persistAsync();
        publish(completedScriptTimeUs / 1_000L);
    }

    private void sendRogueStop() {
        if (rogueStopRequested || !rogueStartSucceeded || sessionRecord == null) return;
        rogueStopRequested = true;
        sessionRecord.rogueApi.stopStatus = "REQUESTED";
        rogueApiExecutor.execute(() -> {
            long requestRealtimeNs = SystemClock.elapsedRealtimeNanos();
            long requestEpochMs = mappedEpochMs(requestRealtimeNs);
            sessionRecord.rogueApi.benjiStopRequestEpochMs = requestEpochMs;
            try {
                RogueApiClient.Result result = rogueApiClient.stop(
                        sessionRecord.rogueApi.scriptName, sessionRecord.sessionId,
                        requestEpochMs);
                saveRawRogueResponse(false, result.rawJson);
                handler.post(() -> handleRogueStopResult(result));
            } catch (RogueApiClient.ResponseException error) {
                saveRawRogueResponse(false, error.rawJson);
                handler.post(() -> failRogueStop(error.httpStatus, error.errorCode,
                        error.getMessage(), mappedEpochMs(error.responseRealtimeNs)));
            } catch (IOException error) {
                handler.post(() -> failRogueStop(null, "NETWORK_ERROR",
                        error.getMessage(), null));
            }
        });
    }

    private void handleRogueStopResult(RogueApiClient.Result result) {
        RogueApiRecord api = sessionRecord.rogueApi;
        api.stopHttpStatus = result.httpStatus;
        api.benjiStopResponseEpochMs = mappedEpochMs(result.responseRealtimeNs);
        if (!result.ok) {
            failRogueStop(result.httpStatus, result.errorCode, result.message,
                    api.benjiStopResponseEpochMs);
            return;
        }
        api.rogueStopRequestReceivedEpochMs = result.requestReceivedEpochMs;
        api.rogueDumpStopEpochMs = result.dumpEpochMs;
        api.stopLogFilename = result.logFilename;
        if (result.httpStatus != 200
                || !api.scriptName.equals(result.scriptName)
                || !sessionRecord.sessionId.equals(result.sessionId)
                || !api.startLogFilename.equals(result.logFilename)) {
            failRogueStop(result.httpStatus, "RESPONSE_MISMATCH",
                    "Rogue STOP response 与当前 Session 不一致",
                    api.benjiStopResponseEpochMs);
            return;
        }
        api.stopStatus = "SUCCEEDED";
        finishAfterRogueStop(true);
    }

    private void failRogueStop(Integer httpStatus, String errorCode,
                               String message, Long responseEpochMs) {
        RogueApiRecord api = sessionRecord.rogueApi;
        api.stopStatus = "FAILED";
        api.stopHttpStatus = httpStatus;
        api.stopErrorCode = errorCode;
        api.stopMessage = message;
        api.benjiStopResponseEpochMs = responseEpochMs;
        finishAfterRogueStop(false);
    }

    private void finishAfterRogueStop(boolean succeeded) {
        sessionRecord.status = succeeded ? "COMPLETED" : "STOP_FAILED";
        sessionRecord.endReason = succeeded
                ? (pendingCompletionAnnounce
                ? "NATURAL_OR_USER_COMPLETION" : "ABORTED")
                : "ROGUE_STOP_FAILED";
        state = RunnerSnapshot.State.COMPLETED;
        currentTitle = succeeded ? "采集完成" : "罗格停止失败";
        countdownText = "—";
        if (succeeded && pendingCompletionAnnounce) speak("采集完成");
        persistAsync();
        publish(completedScriptTimeUs / 1_000L);
    }

    private void saveRawRogueResponse(boolean start, String rawJson) {
        if (sessionFiles == null || rawJson == null) return;
        try {
            sessionStorage.saveRogueResponse(sessionFiles, start, rawJson);
            if (start) {
                sessionRecord.rogueApi.startResponseFile = "rogue_start_response.json";
            } else {
                sessionRecord.rogueApi.stopResponseFile = "rogue_stop_response.json";
            }
        } catch (IOException ignored) {
            // session.json 中仍保留 HTTP 状态和错误信息。
        }
    }

    private long currentScriptTimeUs() {
        return timebase.scriptTimeUs(SystemClock.elapsedRealtimeNanos());
    }

    boolean canAttachEvidence() {
        return isActive() && currentEventIndex >= 0
                && eventRecords.get(currentEventIndex).getTriggerScriptTimeUs() != null;
    }

    EventRecord currentEvent() {
        return canAttachEvidence() ? eventRecords.get(currentEventIndex) : null;
    }

    List<PhotoRecord> getPhotos() {
        return sessionRecord == null ? Collections.emptyList()
                : new ArrayList<>(sessionRecord.photos);
    }

    List<NoteRecord> getNotes() {
        return sessionRecord == null ? Collections.emptyList()
                : new ArrayList<>(sessionRecord.notes);
    }

    int nextPhotoSequence(String eventId) {
        int count = 0;
        if (sessionRecord != null) {
            for (PhotoRecord photo : sessionRecord.photos) {
                if (eventId.equals(photo.eventId)) count++;
            }
        }
        return count + 1;
    }

    boolean addPhoto(String eventId, String action, int sequence, long capturedScriptTimeUs,
                     String fileName, String contentUri) {
        if (sessionRecord == null || !isActive() || eventId == null || action == null
                || sequence < 1 || capturedScriptTimeUs < 0L
                || fileName == null || contentUri == null) return false;
        String photoId = eventId + "-P" + String.format(Locale.US, "%02d", sequence);
        sessionRecord.photos.add(new PhotoRecord(photoId, eventId, sequence, action,
                sessionRecord.clockAt(capturedScriptTimeUs), capturedScriptTimeUs,
                fileName, contentUri));
        persistAsync();
        publish(currentElapsedMs());
        return true;
    }

    NoteRecord addNote(NoteRecord.TargetType type, String targetId, String text,
                       long anchoredScriptTimeUs) {
        if (sessionRecord == null || !isActive() || text == null
                || text.trim().isEmpty()) return null;
        if (type == NoteRecord.TargetType.PHOTO) {
            for (NoteRecord note : sessionRecord.notes) {
                if (!note.deleted && type == note.targetType && targetId.equals(note.targetId)) {
                    return null;
                }
            }
        }
        String noteId = String.format(Locale.US, "N%04d", sessionRecord.notes.size() + 1);
        NoteRecord note = new NoteRecord(noteId, type, targetId, text.trim(),
                sessionRecord.clockAt(anchoredScriptTimeUs), anchoredScriptTimeUs);
        sessionRecord.notes.add(note);
        persistAsync();
        publish(currentElapsedMs());
        return note;
    }

    boolean updateNote(String noteId, String text) {
        NoteRecord note = findNote(noteId);
        if (note == null || note.deleted || !isActive() || text == null
                || text.trim().isEmpty()) return false;
        long nowUs = currentScriptTimeUs();
        note.text = text.trim();
        note.updatedScriptTimeUs = nowUs;
        note.updatedClock = sessionRecord.clockAt(nowUs);
        persistAsync();
        publish(currentElapsedMs());
        return true;
    }

    boolean deleteNote(String noteId) {
        NoteRecord note = findNote(noteId);
        if (note == null || note.deleted || !isActive()) return false;
        long nowUs = currentScriptTimeUs();
        note.deleted = true;
        note.deletedScriptTimeUs = nowUs;
        note.deletedClock = sessionRecord.clockAt(nowUs);
        persistAsync();
        publish(currentElapsedMs());
        return true;
    }

    long captureEvidenceTimeUs() {
        return isActive() ? currentScriptTimeUs() : -1L;
    }

    private NoteRecord findNote(String noteId) {
        if (sessionRecord != null) {
            for (NoteRecord note : sessionRecord.notes) {
                if (note.noteId.equals(noteId)) return note;
            }
        }
        return null;
    }

    void exportZip(android.net.Uri destination, ExportListener listener) {
        if (state != RunnerSnapshot.State.COMPLETED || sessionRecord == null
                || sessionFiles == null) {
            listener.onError("当前没有已完成的 Session");
            return;
        }
        SessionRecord record = sessionRecord;
        SessionStorage.Files files = sessionFiles;
        persistenceExecutor.execute(() -> {
            try {
                for (PhotoRecord photo : record.photos) {
                    photo.fileStatus = sessionStorage.canRead(
                            android.net.Uri.parse(photo.contentUri))
                            ? "AVAILABLE" : "UNAVAILABLE";
                }
                sessionStorage.persist(record, files, "0.2.1");
                sessionStorage.exportZip(record, files, destination);
                handler.post(listener::onExported);
            } catch (IOException error) {
                handler.post(() -> listener.onError(error.getMessage()));
            }
        });
    }

    boolean isExportReady() {
        return state == RunnerSnapshot.State.COMPLETED && isAudioTerminal()
                && sessionRecord != null && sessionFiles != null;
    }

    private void persistAsync() {
        if (sessionRecord == null || sessionFiles == null) return;
        String json = SessionJsonExporter.export(sessionRecord, "0.2.1");
        String csv = String.join("\n", SessionCsvExporter.export(
                sessionRecord.events, sessionRecord.startClockEpochMs,
                sessionRecord.startClock)) + "\n";
        SessionStorage.Files files = sessionFiles;
        persistenceExecutor.execute(() -> {
            try {
                sessionStorage.writeText(files.jsonUri, json);
                sessionStorage.writeText(files.csvUri, csv);
            } catch (IOException ignored) {
                // UI 通过最终保存/导出失败明确提示；正常写入路径不阻塞采集时序。
            }
        });
    }

    private void startAudioPreRoll() {
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO)
                != PackageManager.PERMISSION_GRANTED) {
            audioStartFailure = "PERMISSION_NOT_GRANTED";
            return;
        }
        java.io.File file = new java.io.File(getCacheDir(),
                "recording_" + SystemClock.elapsedRealtimeNanos() + ".m4a");
        audioRecorder = new SessionAudioRecorder(file, new SessionAudioRecorder.Listener() {
            @Override public void onStopped(SessionAudioRecorder.Result result) {
                handler.post(() -> finishAudio(result));
            }

            @Override public void onFailure(String reason) {
                handler.post(() -> {
                    audioStartFailure = reason;
                    if (sessionRecord != null) {
                        markAudioFailure(reason, currentElapsedMs() * 1_000L);
                        persistAsync();
                        publish(currentElapsedMs());
                    }
                });
            }
        });
        try {
            audioRecorder.start();
        } catch (RuntimeException error) {
            audioStartFailure = "AUDIO_START_FAILED: " + error.getMessage();
            audioRecorder = null;
        }
    }

    private void finishAudio(SessionAudioRecorder.Result result) {
        if (sessionRecord == null) {
            result.file.delete();
            return;
        }
        AudioRecordingRecord audio = sessionRecord.audio;
        try {
            if (sessionFiles == null) {
                throw new IOException("SESSION_STORAGE_UNAVAILABLE");
            }
            long streamStartEpochMs = result.streamStartRealtimeNs == null
                    ? result.requestClockEpochMs
                    : result.requestClockEpochMs
                    + Math.round((result.streamStartRealtimeNs - result.requestRealtimeNs)
                    / 1_000_000.0d);
            String scriptBase = SessionStorage.safeName(sourceScriptName
                    .replaceFirst("\\.[^.]+$", ""));
            String stamp = new SimpleDateFormat("yyyyMMdd_HHmmss_SSS", Locale.US)
                    .format(new Date(streamStartEpochMs));
            String name = scriptBase + "_录音_" + stamp + ".m4a";
            android.net.Uri uri = sessionStorage.saveFile(result.file, name, "audio/mp4",
                    sessionFiles.relativePath + "audio/");
            audio.fileName = name;
            audio.contentUri = uri.toString();
            audio.startClock = formatWallClock(streamStartEpochMs);
            if (result.streamStartRealtimeNs == null) {
                audio.startOffsetUs = null;
                audio.startMethod = "TIMESTAMP_UNAVAILABLE";
                audio.startAccuracyUs = null;
            } else {
                audio.startOffsetUs =
                        (result.streamStartRealtimeNs - sessionRecord.startRealtimeNs) / 1_000L;
                audio.startMethod = "AUDIO_TIMESTAMP_BOOTTIME";
                audio.startAccuracyUs = 20_000L;
            }
            audio.endClock = sessionRecord.endClock;
            audio.endScriptTimeUs = sessionRecord.endScriptTimeUs;
            audio.durationUs = result.frameCount * 1_000_000L / result.sampleRate;
            audio.sampleRateHz = result.sampleRate;
            audio.channelCount = 1;
            audio.mimeType = "audio/mp4";
            audio.bitRate = 96_000;
            audio.endReason = "COMPLETED";
            audio.status = "SAVED";
            result.file.delete();
        } catch (IOException error) {
            markAudioFailure("SAVE_FAILED: " + error.getMessage(),
                    sessionRecord.endScriptTimeUs == null ? 0L : sessionRecord.endScriptTimeUs);
            audio.status = "SAVE_FAILED";
            result.file.delete();
        }
        persistAsync();
        publish(currentElapsedMs());
    }

    private void markAudioFailure(String reason, long scriptTimeUs) {
        if (sessionRecord == null) return;
        AudioRecordingRecord audio = sessionRecord.audio;
        audio.enabled = true;
        audio.status = "FAILED";
        audio.failureReason = reason;
        audio.failureScriptTimeUs = scriptTimeUs;
        audio.failureClock = sessionRecord.clockAt(scriptTimeUs);
    }

    private boolean isAudioTerminal() {
        if (sessionRecord == null || !sessionRecord.audio.enabled) return true;
        String status = sessionRecord.audio.status;
        return "SAVED".equals(status) || "FAILED".equals(status)
                || "SAVE_FAILED".equals(status);
    }

    private void completeSession(boolean announce) {
        if (!isActive()) return;
        handler.removeCallbacks(tick);
        long completedAtNanos = SystemClock.elapsedRealtimeNanos();
        completedScriptTimeUs = timebase.scriptTimeUs(completedAtNanos);
        completedScheduleTimeMs = timebase.scheduleTimeMs(completedAtNanos);
        endClockEpochMs = mappedEpochMs(completedAtNanos);
        endClock = formatWallClock(endClockEpochMs);
        if (sessionRecord != null) {
            sessionRecord.endClockEpochMs = endClockEpochMs;
            sessionRecord.endClock = endClock;
            sessionRecord.endScriptTimeUs = completedScriptTimeUs;
            sessionRecord.status = "STOPPING";
        }
        if (audioRecorder != null && "RECORDING".equals(sessionRecord.audio.status)) {
            audioRecorder.stop();
        }
        pendingCompletionAnnounce = announce;
        state = RunnerSnapshot.State.STOPPING;
        currentTitle = "正在停止罗格采集";
        countdownText = "—";
        persistAsync();
        publish(completedScriptTimeUs / 1_000L);
        sendRogueStop();
    }

    private String formatWallClock(long epochMs) {
        return new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSXXX", Locale.US)
                .format(new Date(epochMs));
    }

    @Override public void onInit(int status) {
        if (status != TextToSpeech.SUCCESS) return;
        ttsReady = true;
        textToSpeech.setLanguage(Locale.SIMPLIFIED_CHINESE);
        textToSpeech.setSpeechRate(.92f);
        textToSpeech.setOnUtteranceProgressListener(new UtteranceProgressListener() {
            @Override public void onStart(String utteranceId) { }
            @Override public void onError(String utteranceId) {
                if ("pre_start".equals(utteranceId)) handler.post(CollectionRunnerService.this::beginPreRoll);
            }
            @Override public void onDone(String utteranceId) {
                if ("pre_start".equals(utteranceId)) handler.post(CollectionRunnerService.this::beginPreRoll);
            }
        });
    }

    @Override public void onDestroy() {
        handler.removeCallbacksAndMessages(null);
        if (audioRecorder != null) audioRecorder.stop();
        if (textToSpeech != null) textToSpeech.shutdown();
        if (toneGenerator != null) toneGenerator.release();
        persistenceExecutor.shutdown();
        rogueApiExecutor.shutdown();
        super.onDestroy();
    }
}
