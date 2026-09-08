package com.teslacan.voicerunner;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.pm.ServiceInfo;
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

/** V2优化-任务02-在界面退到后台后继续计时和语音播报。 */
public final class CollectionRunnerService extends Service
        implements TextToSpeech.OnInitListener, SessionTimelineRunner.Listener {
    static final String ACTION_START = "com.teslacan.voicerunner.START";
    static final String ACTION_STOP = "com.teslacan.voicerunner.STOP";
    static final String EXTRA_SCRIPT = "script";

    interface SnapshotListener {
        void onSnapshot(RunnerSnapshot snapshot);
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
    private final List<String> events = new ArrayList<>();
    private List<ScriptStep> steps = Collections.emptyList();
    private SessionTimelineRunner timelineRunner;
    private SnapshotListener snapshotListener;
    private TextToSpeech textToSpeech;
    private ToneGenerator toneGenerator;
    private boolean ttsReady;
    private boolean preRollStarted;
    private boolean completionClaimed;
    private long sessionStartMs;
    private long completedElapsedMs;
    private String lastNotificationText;
    private RunnerSnapshot.State state = RunnerSnapshot.State.IDLE;
    private String currentTitle = "尚未开始";
    private String countdownText = "—";

    private final Runnable tick = new Runnable() {
        @Override public void run() {
            if (state != RunnerSnapshot.State.RUNNING) return;
            long elapsedMs = SystemClock.elapsedRealtime() - sessionStartMs;
            timelineRunner.update(elapsedMs);
            publish(elapsedMs);
            if (state == RunnerSnapshot.State.RUNNING) handler.postDelayed(this, TICK_MS);
        }
    };

    @Override public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        textToSpeech = new TextToSpeech(this, this);
        toneGenerator = new ToneGenerator(AudioManager.STREAM_MUSIC, 90);
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null) return START_NOT_STICKY;
        String action = intent.getAction();
        if (ACTION_STOP.equals(action)) {
            stopSession();
            return START_NOT_STICKY;
        }
        if (ACTION_START.equals(action)) {
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
        return new ArrayList<>(events);
    }

    boolean claimCompletion() {
        if (state != RunnerSnapshot.State.COMPLETED || completionClaimed) return false;
        completionClaimed = true;
        stopForeground(STOP_FOREGROUND_REMOVE);
        stopSelf();
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
        events.clear();
        events.add("planned_s,actual_s,event");
        preRollStarted = false;
        completionClaimed = false;
        completedElapsedMs = 0L;
        lastNotificationText = null;
        timelineRunner = new SessionTimelineRunner(steps, this);
        state = RunnerSnapshot.State.PREPARING;
        currentTitle = "准备开始采集";
        countdownText = "—";
        publish(0L);
        if (ttsReady) speak("准备开始采集", "pre_start");
        else handler.postDelayed(this::beginPreRoll, 1800L);
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
        sessionStartMs = SystemClock.elapsedRealtime();
        currentTitle = "开始采集";
        countdownText = "开始";
        speak("开始采集");
        timelineRunner.update(0L);
        publish(0L);
        handler.post(tick);
    }

    void stopSession() {
        handler.removeCallbacksAndMessages(null);
        if (textToSpeech != null) textToSpeech.stop();
        state = RunnerSnapshot.State.IDLE;
        currentTitle = "尚未开始";
        countdownText = "—";
        publish(0L);
        stopForeground(STOP_FOREGROUND_REMOVE);
        stopSelf();
    }

    @Override public void onPrepareStep(int index, ScriptStep step) {
        speak("准备，" + step.title);
    }

    @Override public void onCountdown(int value) {
        countdownText = String.valueOf(value);
        toneGenerator.startTone(ToneGenerator.TONE_PROP_BEEP, 120);
    }

    @Override public void onFireStep(int index, ScriptStep step, long elapsedMs) {
        currentTitle = step.title;
        countdownText = "执行";
        toneGenerator.startTone(ToneGenerator.TONE_PROP_ACK, 260);
        events.add(step.second + "," + String.format(Locale.US, "%.3f", elapsedMs / 1000d)
                + ",\"" + step.title.replace("\"", "\"\"") + "\"");
    }

    @Override public void onSkipStep(int index, ScriptStep step) {
        // 已过去的计划节点不补播，保持采集时间流逝的真实性。
    }

    @Override public void onComplete() {
        completedElapsedMs = Math.max(0L, SystemClock.elapsedRealtime() - sessionStartMs);
        state = RunnerSnapshot.State.COMPLETED;
        countdownText = "—";
        speak("采集完成");
        publish(completedElapsedMs);
    }

    private long currentElapsedMs() {
        if (state == RunnerSnapshot.State.COMPLETED) return completedElapsedMs;
        return state == RunnerSnapshot.State.RUNNING
                ? Math.max(0L, SystemClock.elapsedRealtime() - sessionStartMs) : 0L;
    }

    private RunnerSnapshot createSnapshot(long elapsedMs) {
        int nextIndex = timelineRunner == null ? 0 : timelineRunner.getNextStepIndex();
        String nextTitle = nextIndex < steps.size() ? steps.get(nextIndex).title : "已完成";
        int nextSecond = nextIndex < steps.size() ? steps.get(nextIndex).second : -1;
        return new RunnerSnapshot(state, elapsedMs, currentTitle, nextTitle,
                nextSecond, countdownText);
    }

    private void publish(long elapsedMs) {
        RunnerSnapshot snapshot = createSnapshot(elapsedMs);
        if (state == RunnerSnapshot.State.PREPARING || state == RunnerSnapshot.State.RUNNING
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
        String elapsed = formatClock((int) (snapshot.elapsedMs / 1000L));
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
            startForeground(NOTIFICATION_ID, notification,
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
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
        if (textToSpeech != null) textToSpeech.shutdown();
        if (toneGenerator != null) toneGenerator.release();
        super.onDestroy();
    }
}
