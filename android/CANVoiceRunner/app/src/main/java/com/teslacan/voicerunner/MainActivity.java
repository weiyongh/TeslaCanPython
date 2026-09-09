package com.teslacan.voicerunner;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.*;
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
    private static final int OPEN = 10, SAVE = 11, NOTIFICATIONS = 12;
    private static final int BLUE = Color.rgb(61, 111, 198), ORANGE = Color.rgb(246, 126, 37);
    private TextView fileName, currentClock, timer, current, countdown, next, sessionStatus;
    private Button runButton, pauseButton, skipButton, exportButton;
    private String scriptText = "", scriptName = "内置示例脚本.txt";
    private List<ScriptStep> steps = new ArrayList<>();
    private List<String> completedEvents = new ArrayList<>();
    private CollectionRunnerService runnerService;
    private boolean serviceBound;
    private final Handler clockHandler = new Handler(Looper.getMainLooper());
    private final Runnable clockTick = new Runnable() {
        @Override public void run() {
            if (currentClock != null) {
                currentClock.setText(new SimpleDateFormat("HH:mm:ss", Locale.CHINA)
                        .format(new Date()));
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
                completedEvents = runnerService.getEvents();
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
        currentClock = text("--:--:--", 16, Color.DKGRAY); currentClock.setGravity(Gravity.END);
        fileClockRow.addView(currentClock, new LinearLayout.LayoutParams(dp(88), -2));
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
        next.setPadding(4, dp(8), 4, dp(8)); root.addView(next, matchWrap()); root.addView(new Space(this), space(1f));
        sessionStatus = text("尚未采集", 17, Color.DKGRAY); sessionStatus.setGravity(Gravity.CENTER);
        sessionStatus.setPadding(0, dp(6), 0, dp(6)); root.addView(sessionStatus, matchWrap());
        LinearLayout controls = new LinearLayout(this); controls.setGravity(Gravity.CENTER);
        pauseButton = button("暂停播报", view -> togglePause()); pauseButton.setBackgroundColor(Color.rgb(80, 170, 90));
        skipButton = button("跳过", view -> skipCurrent()); skipButton.setBackgroundColor(ORANGE);
        runButton = button("开始采集", view -> toggle());
        controls.addView(pauseButton, buttonLp()); controls.addView(skipButton, buttonLp());
        controls.addView(runButton, buttonLp()); root.addView(controls, matchWrap());
        pauseButton.setEnabled(false); skipButton.setEnabled(false); setContentView(root);
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
        completedEvents.clear();
        exportButton.setEnabled(false);
        Intent intent = new Intent(this, CollectionRunnerService.class).setAction(CollectionRunnerService.ACTION_START)
                .putExtra(CollectionRunnerService.EXTRA_SCRIPT, scriptText);
        startForegroundService(intent);
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
            sessionStatus.setText("尚未采集");
            return;
        }
        timer.setText(clock((int) (snapshot.elapsedMs / 1000L))); current.setText(snapshot.currentTitle);
        countdown.setText(snapshot.countdownText);
        next.setText(snapshot.nextSecond >= 0 ? "下一操作： " + clock(snapshot.nextSecond) + "  " + snapshot.nextTitle : "下一操作： 已完成");
        boolean active = snapshot.state == RunnerSnapshot.State.RUNNING
                || snapshot.state == RunnerSnapshot.State.PAUSED
                || snapshot.state == RunnerSnapshot.State.PREPARING;
        runButton.setText(active ? "结束采集" : "开始采集");
        pauseButton.setEnabled(snapshot.state == RunnerSnapshot.State.RUNNING
                || snapshot.state == RunnerSnapshot.State.PAUSED);
        skipButton.setEnabled(snapshot.state == RunnerSnapshot.State.RUNNING
                || snapshot.state == RunnerSnapshot.State.PAUSED);
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
        if (snapshot.state == RunnerSnapshot.State.COMPLETED && runnerService != null
                && runnerService.claimCompletion()) {
            completedEvents = runnerService.getEvents();
            exportButton.setEnabled(true);
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
        if (completedEvents.isEmpty()) {
            toast("当前没有可导出的采集记录");
            return;
        }
        saveEvents();
    }

    private void showExportPrompt() {
        new AlertDialog.Builder(this).setTitle("采集已结束").setMessage("是否导出本次实际事件时间？")
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
        if (requestCode != NOTIFICATIONS) return;
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            startCollection();
        } else {
            new AlertDialog.Builder(this).setTitle("需要通知权限")
                    .setMessage("后台采集必须显示常驻通知。请在 App 设置中允许通知后重新开始采集。")
                    .setNegativeButton("取消", null)
                    .setPositiveButton("打开 App 设置", (dialog, which) -> openAppSettings()).show();
        }
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
    private void saveEvents() { startActivityForResult(new Intent(Intent.ACTION_CREATE_DOCUMENT).setType("text/csv").putExtra(Intent.EXTRA_TITLE,
            "CAN事件_" + new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.CHINA).format(new Date()) + ".csv"), SAVE); }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode != RESULT_OK || data == null || data.getData() == null) return;
        try {
            if (requestCode == OPEN) { Uri uri = data.getData(); scriptName = queryName(uri); load(read(uri)); }
            else if (requestCode == SAVE) { write(data.getData(), String.join("\n", completedEvents)); toast("记录已导出"); }
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

    private void write(Uri uri, String value) throws IOException {
        try (OutputStream output = getContentResolver().openOutputStream(uri)) {
            if (output == null) throw new IOException("无法创建文件"); output.write(value.getBytes(StandardCharsets.UTF_8));
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
    private Button button(String label, View.OnClickListener listener) { Button button = new Button(this); button.setText(label); button.setTextSize(18); button.setTextColor(Color.WHITE); button.setAllCaps(false); button.setBackgroundColor(BLUE); button.setOnClickListener(listener); return button; }
    private TextView text(String value, int size, int color) { TextView view = new TextView(this); view.setText(value); view.setTextSize(size); view.setTextColor(color); return view; }
    private LinearLayout.LayoutParams buttonLp() { LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, dp(54), 1); params.setMargins(dp(5), 0, dp(5), 0); return params; }
    private LinearLayout.LayoutParams matchWrap() { return new LinearLayout.LayoutParams(-1, -2); }
    private LinearLayout.LayoutParams space(float weight) { return new LinearLayout.LayoutParams(1, 0, weight); }
    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    private void toast(String message) { Toast.makeText(this, message, Toast.LENGTH_LONG).show(); }
}
