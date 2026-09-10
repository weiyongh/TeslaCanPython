package com.teslacan.voicerunner;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.*;
import android.content.res.ColorStateList;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.*;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.*;
import android.provider.OpenableColumns;
import android.provider.Settings;
import android.view.*;
import android.widget.*;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.*;

/** V2优化-任务03-沿用既有执行区并增加 Clock、暂停与跳过操作。 */
public class MainActivity extends Activity implements CollectionRunnerService.SnapshotListener {
    private static final int OPEN = 10, ZIP = 11, NOTIFICATIONS = 12,
            CAMERA_PERMISSION = 13, AUDIO_PERMISSION = 14, PHOTO_CAPTURE = 15;
    private static final int BLUE = Color.rgb(61, 111, 198), ORANGE = Color.rgb(246, 126, 37);
    private TextView fileName, currentClock, timer, current, countdown, next, sessionStatus;
    private Button runButton, pauseButton, skipButton, exportButton;
    private Button photoButton, noteButton, recordingButton;
    private TextView photoSummary, noteSummary, recordingSummary;
    private String scriptText = "", scriptName = "内置示例脚本.txt";
    private List<ScriptStep> steps = new ArrayList<>();
    private CollectionRunnerService runnerService;
    private boolean serviceBound;
    private boolean recordingEnabled;
    private String pendingPhotoEventId;
    private String pendingPhotoAction;
    private int pendingPhotoSequence;
    private final Handler clockHandler = new Handler(Looper.getMainLooper());
    private final Runnable clockTick = new Runnable() {
        @Override public void run() {
            if (currentClock != null) {
                String value = new SimpleDateFormat("HH:mm:ss", Locale.CHINA)
                        .format(new Date());
                if (runnerService != null) {
                    RunnerSnapshot snapshot = runnerService.getSnapshot();
                    if (snapshot.state == RunnerSnapshot.State.RUNNING
                            || snapshot.state == RunnerSnapshot.State.PAUSED
                            || snapshot.state == RunnerSnapshot.State.COMPLETED) {
                        value += "  耗时 " + clock((int) (snapshot.elapsedMs / 1000L));
                    }
                }
                currentClock.setText(value);
            }
            clockHandler.postDelayed(this, 250L);
        }
    };

    private final ServiceConnection serviceConnection = new ServiceConnection() {
        @Override public void onServiceConnected(ComponentName name, IBinder binder) {
            runnerService = ((CollectionRunnerService.LocalBinder) binder).getService();
            serviceBound = true;
            runnerService.setSnapshotListener(MainActivity.this);
            onSnapshot(runnerService.getSnapshot());
            if (runnerService.claimCompletion()) {
                showExportPrompt();
            }
        }
        @Override public void onServiceDisconnected(ComponentName name) {
            serviceBound = false;
            runnerService = null;
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().setStatusBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
        buildUi();
        loadSample();
        showBackgroundGuideOnce();
    }

    @Override protected void onStart() {
        super.onStart();
        clockHandler.removeCallbacks(clockTick);
        clockHandler.post(clockTick);
        bindService(new Intent(this, CollectionRunnerService.class), serviceConnection, Context.BIND_AUTO_CREATE);
    }

    @Override protected void onStop() {
        clockHandler.removeCallbacks(clockTick);
        if (serviceBound) {
            runnerService.setSnapshotListener(null);
            unbindService(serviceConnection);
            serviceBound = false;
        }
        super.onStop();
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18), dp(12), dp(18), dp(14)); root.setBackgroundColor(Color.WHITE); root.setFitsSystemWindows(true);
        LinearLayout top = new LinearLayout(this); top.setGravity(Gravity.CENTER);
        top.addView(button("导入脚本", view -> openScript()), buttonLp());
        top.addView(button("查看脚本", view -> showScript()), buttonLp());
        exportButton = button("导出", view -> exportEvents());
        exportButton.setEnabled(false);
        top.addView(exportButton, buttonLp()); root.addView(top, matchWrap());
        LinearLayout fileClockRow = new LinearLayout(this); fileClockRow.setGravity(Gravity.CENTER_VERTICAL);
        fileName = text("", 16, Color.DKGRAY); fileName.setSingleLine();
        fileName.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE);
        fileClockRow.addView(fileName, new LinearLayout.LayoutParams(0, -2, 1f));
        currentClock = text("--:--:--", 14, BLUE); currentClock.setGravity(Gravity.END);
        fileClockRow.addView(currentClock, new LinearLayout.LayoutParams(dp(190), -2));
        root.addView(fileClockRow, matchWrap());
        root.addView(new Space(this), space(0.65f));
        timer = text("00:00", 48, Color.rgb(15, 31, 47)); timer.setTypeface(Typeface.create("sans-serif-light", Typeface.NORMAL));
        timer.setGravity(Gravity.CENTER); root.addView(timer, matchWrap());
        current = text("尚未开始", 25, Color.rgb(25, 25, 25)); current.setGravity(Gravity.CENTER);
        current.setPadding(4, dp(10), 4, dp(10)); root.addView(current, matchWrap());
        FrameLayout circle = new FrameLayout(this); GradientDrawable background = new GradientDrawable();
        background.setShape(GradientDrawable.OVAL); background.setColor(ORANGE); circle.setBackground(background);
        countdown = text("—", 58, Color.WHITE); countdown.setGravity(Gravity.CENTER);
        circle.addView(countdown, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout.LayoutParams circleParams = new LinearLayout.LayoutParams(dp(190), dp(190));
        circleParams.gravity = Gravity.CENTER; circleParams.setMargins(0, dp(10), 0, dp(16)); root.addView(circle, circleParams);
        root.addView(new Space(this), space(.35f));
        next = text("下一操作：—", 20, Color.rgb(30, 30, 30)); next.setGravity(Gravity.CENTER);
        next.setPadding(4, dp(8), 4, dp(8)); root.addView(next, matchWrap());
        root.addView(new Space(this), space(.35f));
        LinearLayout summary = new LinearLayout(this); summary.setGravity(Gravity.CENTER);
        photoSummary = text("照片 0", 17, Color.GRAY); photoSummary.setGravity(Gravity.CENTER);
        noteSummary = text("备注 0", 17, Color.GRAY); noteSummary.setGravity(Gravity.CENTER);
        recordingSummary = text("本次未录音", 16, Color.GRAY); recordingSummary.setGravity(Gravity.CENTER);
        photoSummary.setOnClickListener(v -> showPhotos());
        noteSummary.setOnClickListener(v -> showEventNotes());
        summary.addView(photoSummary, buttonLp()); summary.addView(noteSummary, buttonLp());
        summary.addView(recordingSummary, buttonLp()); root.addView(summary, matchWrap());
        LinearLayout evidence = new LinearLayout(this); evidence.setGravity(Gravity.CENTER);
        photoButton = button("拍照", v -> preparePhoto());
        noteButton = button("备注", v -> addCurrentEventNote());
        recordingButton = button("录音：关", v -> toggleRecordingOption());
        evidence.addView(photoButton, buttonLp()); evidence.addView(noteButton, buttonLp());
        evidence.addView(recordingButton, buttonLp()); root.addView(evidence, matchWrap());
        root.addView(new Space(this), space(.45f));
        sessionStatus = text("尚未采集", 17, Color.DKGRAY); sessionStatus.setGravity(Gravity.CENTER);
        sessionStatus.setPadding(0, dp(6), 0, dp(6)); root.addView(sessionStatus, matchWrap());
        LinearLayout controls = new LinearLayout(this); controls.setGravity(Gravity.CENTER);
        pauseButton = button("暂停播报", view -> togglePause());
        tintButton(pauseButton, Color.rgb(80, 170, 90));
        skipButton = button("跳过", view -> skipCurrent());
        tintButton(skipButton, ORANGE);
        runButton = button("开始采集", view -> toggle());
        controls.addView(pauseButton, buttonLp()); controls.addView(skipButton, buttonLp());
        controls.addView(runButton, buttonLp()); root.addView(controls, matchWrap());
        pauseButton.setEnabled(false); skipButton.setEnabled(false);
        photoButton.setEnabled(false); noteButton.setEnabled(false);
        setContentView(root);
    }

    private void toggle() {
        RunnerSnapshot snapshot = serviceBound ? runnerService.getSnapshot() : null;
        if (snapshot != null && (snapshot.state == RunnerSnapshot.State.RUNNING
                || snapshot.state == RunnerSnapshot.State.PAUSED
                || snapshot.state == RunnerSnapshot.State.PREPARING)) {
            if (snapshot.state == RunnerSnapshot.State.PREPARING) {
                runnerService.stopSession();
                return;
            }
            runnerService.finishSession();
            return;
        }
        if (steps.isEmpty()) { toast("请先导入脚本"); return; }
        if (requestNotificationPermission()) return;
        startCollection();
    }

    private void startCollection() {
        exportButton.setEnabled(false);
        Intent intent = new Intent(this, CollectionRunnerService.class).setAction(CollectionRunnerService.ACTION_START)
                .putExtra(CollectionRunnerService.EXTRA_SCRIPT, scriptText)
                .putExtra(CollectionRunnerService.EXTRA_SCRIPT_NAME, scriptName)
                .putExtra(CollectionRunnerService.EXTRA_RECORDING_ENABLED, recordingEnabled);
        startForegroundService(intent);
        recordingEnabled = false;
    }

    @Override public void onSnapshot(RunnerSnapshot snapshot) { runOnUiThread(() -> render(snapshot)); }

    private void render(RunnerSnapshot snapshot) {
        if (snapshot.state == RunnerSnapshot.State.IDLE && !steps.isEmpty()) {
            timer.setText("00:00");
            current.setText(steps.get(0).title);
            countdown.setText("—");
            showNext(steps.size() > 1 ? 1 : 0);
            runButton.setText("开始采集");
            pauseButton.setEnabled(false); skipButton.setEnabled(false);
            photoButton.setEnabled(false); noteButton.setEnabled(false);
            recordingButton.setEnabled(true);
            recordingButton.setText(recordingEnabled ? "录音：开" : "录音：关");
            sessionStatus.setText("尚未采集");
            return;
        }
        timer.setText(clock((int) (snapshot.scheduleElapsedMs / 1000L))); current.setText(snapshot.currentTitle);
        countdown.setText(snapshot.countdownText);
        next.setText(snapshot.nextSecond >= 0 ? "下一操作： " + clock(snapshot.nextSecond) + "  " + snapshot.nextTitle : "下一操作： 已完成");
        boolean active = snapshot.state == RunnerSnapshot.State.RUNNING
                || snapshot.state == RunnerSnapshot.State.PAUSED
                || snapshot.state == RunnerSnapshot.State.PREPARING;
        runButton.setText(active ? "结束采集" : "开始采集");
        pauseButton.setEnabled(snapshot.state == RunnerSnapshot.State.RUNNING
                || snapshot.state == RunnerSnapshot.State.PAUSED);
        skipButton.setEnabled((snapshot.state == RunnerSnapshot.State.RUNNING
                || snapshot.state == RunnerSnapshot.State.PAUSED)
                && "triggered".equals(snapshot.currentEventStatus));
        boolean evidenceEnabled = runnerService != null && runnerService.canAttachEvidence();
        photoButton.setEnabled(evidenceEnabled);
        noteButton.setEnabled(evidenceEnabled);
        recordingButton.setEnabled(snapshot.state == RunnerSnapshot.State.COMPLETED);
        pauseButton.setText(snapshot.state == RunnerSnapshot.State.PAUSED ? "继续播报" : "暂停播报");
        if (snapshot.state == RunnerSnapshot.State.PAUSED) {
            sessionStatus.setText("播报暂停中 · script_time 继续");
        } else if (snapshot.state == RunnerSnapshot.State.RUNNING) {
            sessionStatus.setText("播报运行中 · " + snapshot.currentEventStatus);
        } else if (snapshot.state == RunnerSnapshot.State.PREPARING) {
            sessionStatus.setText("准备开始采集");
        } else if (snapshot.state == RunnerSnapshot.State.COMPLETED) {
            sessionStatus.setText("采集已结束");
        }
        photoSummary.setText("照片 " + snapshot.photoCount);
        photoSummary.setTextColor(snapshot.photoCount > 0 ? BLUE : Color.GRAY);
        noteSummary.setText("备注 " + snapshot.eventNoteCount);
        noteSummary.setTextColor(BLUE);
        renderRecording(snapshot.recordingStatus);
        if (snapshot.state == RunnerSnapshot.State.COMPLETED) {
            recordingButton.setText(recordingEnabled ? "录音：开" : "录音：关");
        }
        exportButton.setEnabled(runnerService != null && runnerService.isExportReady());
        if (snapshot.state == RunnerSnapshot.State.COMPLETED && runnerService != null
                && runnerService.claimCompletion()) {
            showExportPrompt();
        }
    }

    private void togglePause() {
        if (runnerService != null) runnerService.togglePause();
    }

    private void skipCurrent() {
        if (runnerService == null || !runnerService.skipCurrentEvent()) {
            toast("当前没有可跳过的操作");
        }
    }

    private void exportEvents() {
        if (runnerService == null || !runnerService.isExportReady()) {
            toast("当前没有可导出的采集记录");
            return;
        }
        saveEvents();
    }

    private void showExportPrompt() {
        new AlertDialog.Builder(this).setTitle("采集已结束").setMessage("是否导出本次 Session ZIP？")
                .setNegativeButton("暂不导出", null).setPositiveButton("导出记录", (dialog, which) -> saveEvents()).show();
    }

    private void showBackgroundGuideOnce() {
        String key = "v2_background_guide";
        if (getPreferences(MODE_PRIVATE).getBoolean(key, false)) return;
        getPreferences(MODE_PRIVATE).edit().putBoolean(key, true).apply();
        new AlertDialog.Builder(this).setTitle("允许后台采集播报")
                .setMessage("采集期间 App 会显示常驻通知。请允许通知，并在 ColorOS 的 App 管理中允许后台活动、将电池使用设为不受限制。")
                .setNegativeButton("稍后设置", null).setPositiveButton("打开 App 设置", (dialog, which) -> openAppSettings()).show();
    }

    private void openAppSettings() {
        startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + getPackageName())));
    }

    private boolean requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, NOTIFICATIONS);
            return true;
        }
        return false;
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        boolean granted = grantResults.length > 0
                && grantResults[0] == PackageManager.PERMISSION_GRANTED;
        if (requestCode == NOTIFICATIONS) {
            if (granted) {
                startCollection();
            } else {
                new AlertDialog.Builder(this).setTitle("需要通知权限")
                        .setMessage("后台采集必须显示常驻通知。请在 App 设置中允许通知后重新开始采集。")
                        .setNegativeButton("取消", null)
                        .setPositiveButton("打开 App 设置", (dialog, which) -> openAppSettings()).show();
            }
        } else if (requestCode == AUDIO_PERMISSION) {
            recordingEnabled = granted;
            recordingButton.setText(granted ? "录音：开" : "录音：关");
            if (!granted && !shouldShowRequestPermissionRationale(Manifest.permission.RECORD_AUDIO)) {
                showPermissionSettings("录音权限已被拒绝，请在系统设置中允许麦克风权限。");
            }
        } else if (requestCode == CAMERA_PERMISSION) {
            if (granted) launchCamera();
            else toast("没有相机权限，未生成照片记录");
        }
    }

    private void showPermissionSettings(String message) {
            new AlertDialog.Builder(this).setTitle("需要权限")
                    .setMessage(message)
                    .setNegativeButton("取消", null)
                    .setPositiveButton("打开 App 设置", (dialog, which) -> openAppSettings()).show();
    }

    private void renderRecording(String status) {
        if ("PREPARING".equals(status)) {
            recordingSummary.setText("录音准备中");
            recordingSummary.setTextColor(ORANGE);
            recordingButton.setText("录音准备中");
        } else if ("RECORDING".equals(status)) {
            recordingSummary.setText("● 录音中");
            recordingSummary.setTextColor(Color.rgb(205, 55, 45));
            recordingButton.setText("录音中");
        } else if ("SAVED".equals(status)) {
            recordingSummary.setText("录音已保存");
            recordingSummary.setTextColor(BLUE);
            recordingButton.setText("录音已保存");
        } else if ("FAILED".equals(status) || "SAVE_FAILED".equals(status)) {
            recordingSummary.setText("录音失败");
            recordingSummary.setTextColor(Color.rgb(205, 55, 45));
            recordingButton.setText("录音失败");
        } else {
            recordingSummary.setText("本次未录音");
            recordingSummary.setTextColor(Color.GRAY);
            recordingButton.setText("录音：关");
        }
    }

    private void toggleRecordingOption() {
        if (recordingEnabled) {
            recordingEnabled = false;
            recordingButton.setText("录音：关");
            return;
        }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO)
                == PackageManager.PERMISSION_GRANTED) {
            recordingEnabled = true;
            recordingButton.setText("录音：开");
        } else {
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, AUDIO_PERMISSION);
        }
    }

    private void preparePhoto() {
        if (runnerService == null || !runnerService.canAttachEvidence()) {
            toast("当前没有可绑定的 Event");
            return;
        }
        EventRecord event = runnerService.currentEvent();
        pendingPhotoEventId = event.eventId();
        pendingPhotoAction = event.step.title;
        pendingPhotoSequence = runnerService.nextPhotoSequence(pendingPhotoEventId);
        if (checkSelfPermission(Manifest.permission.CAMERA)
                == PackageManager.PERMISSION_GRANTED) {
            launchCamera();
        } else {
            requestPermissions(new String[]{Manifest.permission.CAMERA}, CAMERA_PERMISSION);
        }
    }

    private void launchCamera() {
        if (runnerService == null || runnerService.getSessionRecord() == null
                || runnerService.getSessionFiles() == null) return;
        SessionRecord session = runnerService.getSessionRecord();
        Intent intent = new Intent(this, CameraCaptureActivity.class)
                .putExtra(CameraCaptureActivity.EXTRA_EVENT_ID, pendingPhotoEventId)
                .putExtra(CameraCaptureActivity.EXTRA_ACTION, pendingPhotoAction)
                .putExtra(CameraCaptureActivity.EXTRA_SEQUENCE, pendingPhotoSequence)
                .putExtra(CameraCaptureActivity.EXTRA_SESSION_START_NS, session.startRealtimeNs)
                .putExtra(CameraCaptureActivity.EXTRA_SESSION_START_EPOCH_MS,
                        session.startClockEpochMs)
                .putExtra(CameraCaptureActivity.EXTRA_RELATIVE_PATH,
                        runnerService.getSessionFiles().relativePath);
        startActivityForResult(intent, PHOTO_CAPTURE);
    }

    private void addCurrentEventNote() {
        if (runnerService == null || !runnerService.canAttachEvidence()) {
            toast("当前没有可备注的 Event");
            return;
        }
        EventRecord event = runnerService.currentEvent();
        long anchoredUs = runnerService.captureEvidenceTimeUs();
        showNoteEditor("新增备注 · " + event.eventId(), "", text -> {
            boolean saved = runnerService.addNote(NoteRecord.TargetType.EVENT,
                    event.eventId(), text, anchoredUs) != null;
            if (!saved) toast("备注保存失败");
            return saved;
        });
    }

    private interface TextSave { boolean save(String text); }

    private void showNoteEditor(String title, String initial, TextSave save) {
        EditText input = new EditText(this);
        input.setMinLines(4);
        input.setGravity(Gravity.TOP);
        input.setText(initial);
        input.setPadding(dp(18), dp(12), dp(18), dp(12));
        AlertDialog dialog = new AlertDialog.Builder(this).setTitle(title)
                .setView(input).setNegativeButton("取消", null)
                .setPositiveButton("保存", null).create();
        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE)
                .setOnClickListener(v -> {
                    String value = input.getText().toString().trim();
                    if (value.isEmpty()) {
                        toast("备注不能为空");
                        return;
                    }
                    if (save.save(value)) dialog.dismiss();
                }));
        dialog.show();
    }

    private void showEventNotes() {
        if (runnerService == null) return;
        LinearLayout list = verticalList();
        boolean any = false;
        for (NoteRecord note : runnerService.getNotes()) {
            if (note.deleted || note.targetType != NoteRecord.TargetType.EVENT) continue;
            any = true;
            addNoteRow(list, note);
        }
        if (!any) list.addView(text("暂无事件备注", 17, Color.GRAY));
        new AlertDialog.Builder(this).setTitle("事件备注")
                .setView(scroll(list)).setPositiveButton("关闭", null).show();
    }

    private void addNoteRow(LinearLayout list, NoteRecord note) {
        TextView body = text(note.targetId + " · " + note.noteId + "\n"
                + note.text + "\n" + note.createdClock
                + "  耗时 " + clock((int) (note.createdScriptTimeUs / 1_000_000L)),
                16, Color.DKGRAY);
        body.setPadding(dp(8), dp(10), dp(8), dp(4));
        list.addView(body, matchWrap());
        LinearLayout actions = new LinearLayout(this);
        Button edit = button("修改", v -> showNoteEditor("修改备注", note.text,
                value -> {
                    boolean saved = runnerService.updateNote(note.noteId, value);
                    if (!saved) toast("备注修改失败");
                    return saved;
                }));
        Button delete = button("删除", v -> new AlertDialog.Builder(this)
                .setTitle("删除备注？")
                .setMessage("该备注将从有效列表移除，但保留删除审计记录。")
                .setNegativeButton("取消", null)
                .setPositiveButton("删除", (d, w) -> {
                    boolean deleted = runnerService.deleteNote(note.noteId);
                    toast(deleted ? "备注已删除" : "备注删除失败");
                }).show());
        boolean editable = runnerService.getSnapshot().state == RunnerSnapshot.State.RUNNING
                || runnerService.getSnapshot().state == RunnerSnapshot.State.PAUSED;
        edit.setEnabled(editable); delete.setEnabled(editable);
        actions.addView(edit, buttonLp()); actions.addView(delete, buttonLp());
        list.addView(actions, matchWrap());
    }

    private void showPhotos() {
        if (runnerService == null || runnerService.getPhotos().isEmpty()) return;
        LinearLayout list = verticalList();
        for (PhotoRecord photo : runnerService.getPhotos()) {
            boolean available = canRead(photo.contentUri);
            NoteRecord existing = photoNote(photo);
            LinearLayout photoRow = new LinearLayout(this);
            photoRow.setGravity(Gravity.CENTER_VERTICAL);
            ImageView thumbnail = new ImageView(this);
            thumbnail.setScaleType(ImageView.ScaleType.CENTER_CROP);
            if (available) thumbnail.setImageURI(Uri.parse(photo.contentUri));
            else thumbnail.setImageResource(android.R.drawable.ic_menu_report_image);
            photoRow.addView(thumbnail, new LinearLayout.LayoutParams(dp(82), dp(82)));
            TextView title = text(photo.photoId + " · " + photo.eventAction + "\n"
                    + photo.capturedClock + "  耗时 "
                    + clock((int) (photo.capturedScriptTimeUs / 1_000_000L))
                    + (existing == null ? "" : "\n备注：" + existing.text)
                    + (available ? "" : "\n照片文件不可用"),
                    16, Color.DKGRAY);
            title.setPadding(dp(10), dp(8), 0, dp(8));
            photoRow.addView(title, new LinearLayout.LayoutParams(0, -2, 1f));
            list.addView(photoRow, matchWrap());
            LinearLayout actions = new LinearLayout(this);
            Button view = button("查看", v -> previewPhoto(photo));
            view.setEnabled(available);
            actions.addView(view, buttonLp());
            Button noteAction = button(existing == null ? "添加备注" : "修改备注",
                    v -> editPhotoNote(photo));
            boolean editable = runnerService.getSnapshot().state == RunnerSnapshot.State.RUNNING
                    || runnerService.getSnapshot().state == RunnerSnapshot.State.PAUSED;
            noteAction.setEnabled(editable);
            actions.addView(noteAction, buttonLp());
            if (existing != null) {
                Button delete = button("删除备注", v -> new AlertDialog.Builder(this)
                        .setTitle("删除照片备注？")
                        .setMessage("备注将逻辑删除，照片本身保留。")
                        .setNegativeButton("取消", null)
                        .setPositiveButton("删除", (d, w) -> {
                            boolean deleted = runnerService.deleteNote(existing.noteId);
                            toast(deleted ? "照片备注已删除" : "照片备注删除失败");
                        }).show());
                delete.setEnabled(editable);
                actions.addView(delete, buttonLp());
            }
            list.addView(actions, matchWrap());
        }
        new AlertDialog.Builder(this).setTitle("照片")
                .setView(scroll(list)).setPositiveButton("关闭", null).show();
    }

    private NoteRecord photoNote(PhotoRecord photo) {
        for (NoteRecord note : runnerService.getNotes()) {
            if (!note.deleted && note.targetType == NoteRecord.TargetType.PHOTO
                    && photo.photoId.equals(note.targetId)) return note;
        }
        return null;
    }

    private void editPhotoNote(PhotoRecord photo) {
        NoteRecord existing = photoNote(photo);
        long anchoredUs = runnerService.captureEvidenceTimeUs();
        showNoteEditor((existing == null ? "添加" : "修改") + "照片备注 · " + photo.photoId,
                existing == null ? "" : existing.text, value -> {
                    if (existing == null) {
                        boolean saved = runnerService.addNote(NoteRecord.TargetType.PHOTO,
                                photo.photoId, value, anchoredUs) != null;
                        if (!saved) toast("照片备注保存失败");
                        return saved;
                    } else {
                        boolean saved = runnerService.updateNote(existing.noteId, value);
                        if (!saved) toast("照片备注修改失败");
                        return saved;
                    }
                });
    }

    private void previewPhoto(PhotoRecord photo) {
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        ImageView image = new ImageView(this);
        image.setScaleType(ImageView.ScaleType.FIT_CENTER);
        try {
            image.setImageURI(Uri.parse(photo.contentUri));
        } catch (RuntimeException error) {
            toast("照片文件不可用");
            return;
        }
        root.addView(image, new FrameLayout.LayoutParams(-1, -1));
        Button close = button("关闭", null);
        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(dp(90), dp(54),
                Gravity.TOP | Gravity.END);
        root.addView(close, lp);
        AlertDialog dialog = new AlertDialog.Builder(this).setView(root).create();
        close.setOnClickListener(v -> dialog.dismiss());
        dialog.setOnShowListener(v -> dialog.getWindow().setLayout(-1, -1));
        dialog.show();
    }

    private boolean canRead(String uriText) {
        try (android.content.res.AssetFileDescriptor ignored =
                     getContentResolver().openAssetFileDescriptor(Uri.parse(uriText), "r")) {
            return ignored != null;
        } catch (Exception error) {
            return false;
        }
    }

    private LinearLayout verticalList() {
        LinearLayout list = new LinearLayout(this);
        list.setOrientation(LinearLayout.VERTICAL);
        list.setPadding(dp(12), dp(8), dp(12), dp(8));
        return list;
    }

    private ScrollView scroll(LinearLayout content) {
        ScrollView scroll = new ScrollView(this);
        scroll.addView(content);
        return scroll;
    }

    private void openScript() {
        RunnerSnapshot snapshot = serviceBound ? runnerService.getSnapshot() : null;
        if (snapshot != null && (snapshot.state == RunnerSnapshot.State.RUNNING
                || snapshot.state == RunnerSnapshot.State.PAUSED
                || snapshot.state == RunnerSnapshot.State.PREPARING)) {
            toast("请先结束当前采集，再导入脚本");
            return;
        }
        startActivityForResult(new Intent(Intent.ACTION_OPEN_DOCUMENT).setType("text/*").addCategory(Intent.CATEGORY_OPENABLE), OPEN);
    }
    private void showScript() { new AlertDialog.Builder(this).setTitle(scriptName).setMessage(scriptText.isEmpty() ? "尚未载入脚本" : scriptText).setPositiveButton("关闭", null).show(); }
    private void saveEvents() {
        SessionRecord session = runnerService == null ? null : runnerService.getSessionRecord();
        String name = session == null ? "CANVoiceRunner_Session.zip"
                : session.directoryName + ".zip";
        startActivityForResult(new Intent(Intent.ACTION_CREATE_DOCUMENT)
                .setType("application/zip").putExtra(Intent.EXTRA_TITLE, name), ZIP);
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode != RESULT_OK || data == null) return;
        try {
            if (requestCode == OPEN) {
                Uri uri = data.getData();
                if (uri == null) return;
                scriptName = queryName(uri);
                load(read(uri));
            }
            else if (requestCode == ZIP) {
                if (data.getData() == null) return;
                if (runnerService == null) throw new IOException("采集服务不可用");
                exportButton.setEnabled(false);
                runnerService.exportZip(data.getData(), new CollectionRunnerService.ExportListener() {
                    @Override public void onExported() {
                        exportButton.setEnabled(true);
                        toast("Session ZIP 已导出");
                    }

                    @Override public void onError(String message) {
                        exportButton.setEnabled(true);
                        toast("导出失败：" + message);
                    }
                });
            } else if (requestCode == PHOTO_CAPTURE && runnerService != null) {
                String uriText = data.getStringExtra(
                        CameraCaptureActivity.RESULT_CONTENT_URI);
                boolean saved = runnerService.addPhoto(pendingPhotoEventId,
                        pendingPhotoAction, pendingPhotoSequence,
                        data.getLongExtra(CameraCaptureActivity.RESULT_CAPTURED_US, -1L),
                        data.getStringExtra(CameraCaptureActivity.RESULT_FILE_NAME),
                        uriText);
                if (!saved && uriText != null) {
                    getContentResolver().delete(Uri.parse(uriText), null, null);
                }
                toast(saved ? "照片已保存" : "照片记录失败");
            }
        } catch (Exception error) { toast("操作失败：" + error.getMessage()); }
    }

    private String queryName(Uri uri) {
        try (Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) { int index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME); if (index >= 0) return cursor.getString(index); }
        }
        return "采集脚本.txt";
    }

    private String read(Uri uri) throws IOException {
        try (InputStream input = getContentResolver().openInputStream(uri); ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            if (input == null) throw new IOException("无法读取文件"); byte[] buffer = new byte[4096]; int count;
            while ((count = input.read(buffer)) > 0) output.write(buffer, 0, count); return output.toString("UTF-8");
        }
    }

    private void load(String raw) {
        try { steps = ScriptParser.parse(raw); } catch (RuntimeException error) { toast(error.getMessage()); return; }
        scriptText = raw; fileName.setText(scriptName); timer.setText("00:00"); current.setText(steps.get(0).title);
        showNext(steps.size() > 1 ? 1 : 0); toast("已载入 " + steps.size() + " 个操作节点");
    }

    private void loadSample() {
        try (InputStream input = getAssets().open("sample_script.txt"); ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[4096]; int count; while ((count = input.read(buffer)) > 0) output.write(buffer, 0, count);
            load(output.toString("UTF-8"));
        } catch (Exception error) { toast("示例脚本载入失败：" + error.getMessage()); }
    }

    private void showNext(int index) { next.setText(index >= 0 && index < steps.size() ? "下一操作： " + clock(steps.get(index).second) + "  " + steps.get(index).title : "下一操作： 已完成"); }
    private String clock(int seconds) { int value = Math.floorMod(seconds, 3600); return String.format(Locale.CHINA, "%02d:%02d", value / 60, value % 60); }
    private Button button(String label, View.OnClickListener listener) {
        Button button = new Button(this);
        button.setText(label);
        button.setTextSize(18);
        button.setTextColor(Color.WHITE);
        button.setAllCaps(false);
        tintButton(button, BLUE);
        if (listener != null) button.setOnClickListener(listener);
        return button;
    }
    private void tintButton(Button button, int enabledColor) {
        button.setBackgroundTintList(new ColorStateList(
                new int[][]{new int[]{-android.R.attr.state_enabled}, new int[]{}},
                new int[]{Color.rgb(175, 175, 175), enabledColor}));
    }
    private TextView text(String value, int size, int color) { TextView view = new TextView(this); view.setText(value); view.setTextSize(size); view.setTextColor(color); return view; }
    private LinearLayout.LayoutParams buttonLp() { LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, dp(54), 1); params.setMargins(dp(5), 0, dp(5), 0); return params; }
    private LinearLayout.LayoutParams matchWrap() { return new LinearLayout.LayoutParams(-1, -2); }
    private LinearLayout.LayoutParams space(float weight) { return new LinearLayout.LayoutParams(1, 0, weight); }
    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    private void toast(String message) { Toast.makeText(this, message, Toast.LENGTH_LONG).show(); }
}
