package com.teslacan.voicerunner;

import android.content.Intent;
import android.graphics.Color;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraManager;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageCapture;
import androidx.camera.core.ImageCaptureException;
import androidx.camera.core.ImageProxy;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;

import com.google.common.util.concurrent.ListenableFuture;

import java.nio.ByteBuffer;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** V2优化-任务04-内嵌 CameraX 后置主摄单张拍摄页。 */
public final class CameraCaptureActivity extends androidx.activity.ComponentActivity {
    static final String EXTRA_EVENT_ID = "event_id";
    static final String EXTRA_ACTION = "action";
    static final String EXTRA_SEQUENCE = "sequence";
    static final String EXTRA_SESSION_START_NS = "session_start_ns";
    static final String EXTRA_SESSION_START_EPOCH_MS = "session_start_epoch_ms";
    static final String EXTRA_RELATIVE_PATH = "relative_path";
    static final String RESULT_CAPTURED_US = "captured_us";
    static final String RESULT_FILE_NAME = "file_name";
    static final String RESULT_CONTENT_URI = "content_uri";

    private final ExecutorService cameraExecutor = Executors.newSingleThreadExecutor();
    private ImageCapture imageCapture;
    private Button capture;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        buildUi();
        bindCamera();
    }

    private void buildUi() {
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        PreviewView preview = new PreviewView(this);
        preview.setId(android.R.id.primary);
        root.addView(preview, new FrameLayout.LayoutParams(-1, -1));

        Button close = new Button(this);
        close.setText("关闭");
        close.setOnClickListener(v -> finish());
        FrameLayout.LayoutParams closeLp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT,
                Gravity.TOP | Gravity.END);
        closeLp.setMargins(16, 24, 16, 0);
        root.addView(close, closeLp);

        capture = new Button(this);
        capture.setText("拍照");
        capture.setEnabled(false);
        capture.setOnClickListener(v -> capture());
        FrameLayout.LayoutParams captureLp = new FrameLayout.LayoutParams(
                220, 120, Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        captureLp.setMargins(0, 0, 0, 36);
        root.addView(capture, captureLp);
        setContentView(root);
    }

    private void bindCamera() {
        if (!hasRealtimeBackCamera()) {
            fail("后置相机时间戳不能与 Session 时间轴可靠映射");
            return;
        }
        PreviewView previewView = findViewById(android.R.id.primary);
        ListenableFuture<ProcessCameraProvider> future =
                ProcessCameraProvider.getInstance(this);
        future.addListener(() -> {
            try {
                ProcessCameraProvider provider = future.get();
                Preview preview = new Preview.Builder().build();
                preview.setSurfaceProvider(previewView.getSurfaceProvider());
                imageCapture = new ImageCapture.Builder()
                        .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                        .build();
                provider.unbindAll();
                provider.bindToLifecycle(this, CameraSelector.DEFAULT_BACK_CAMERA,
                        preview, imageCapture);
                capture.setEnabled(true);
            } catch (Exception error) {
                fail("相机启动失败：" + error.getMessage());
            }
        }, getMainExecutor());
    }

    private boolean hasRealtimeBackCamera() {
        try {
            CameraManager manager = getSystemService(CameraManager.class);
            for (String id : manager.getCameraIdList()) {
                CameraCharacteristics c = manager.getCameraCharacteristics(id);
                Integer facing = c.get(CameraCharacteristics.LENS_FACING);
                Integer source = c.get(CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE);
                if (facing != null && facing == CameraCharacteristics.LENS_FACING_BACK
                        && source != null
                        && source == CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE_REALTIME) {
                    return true;
                }
            }
        } catch (Exception ignored) { }
        return false;
    }

    private void capture() {
        if (imageCapture == null) return;
        capture.setEnabled(false);
        long requestedNs = android.os.SystemClock.elapsedRealtimeNanos();
        imageCapture.takePicture(cameraExecutor, new ImageCapture.OnImageCapturedCallback() {
            @Override public void onCaptureSuccess(@NonNull ImageProxy image) {
                try {
                    long timestampNs = image.getImageInfo().getTimestamp();
                    long sessionStartNs = getIntent().getLongExtra(EXTRA_SESSION_START_NS, 0L);
                    if (timestampNs <= 0L || sessionStartNs <= 0L
                            || timestampNs < requestedNs - 2_000_000_000L
                            || timestampNs > android.os.SystemClock.elapsedRealtimeNanos()
                            + 1_000_000_000L) {
                        throw new IllegalStateException("INVALID_CAMERA_TIMESTAMP");
                    }
                    long capturedUs = (timestampNs - sessionStartNs) / 1_000L;
                    if (capturedUs < 0L) {
                        throw new IllegalStateException("CAPTURE_BEFORE_SESSION_START");
                    }
                    ByteBuffer buffer = image.getPlanes()[0].getBuffer();
                    byte[] jpeg = new byte[buffer.remaining()];
                    buffer.get(jpeg);
                    save(jpeg, capturedUs);
                } catch (Exception error) {
                    runOnUiThread(() -> fail("拍摄失败：" + error.getMessage()));
                } finally {
                    image.close();
                }
            }

            @Override public void onError(@NonNull ImageCaptureException error) {
                runOnUiThread(() -> fail("拍摄失败：" + error.getMessage()));
            }
        });
    }

    private void save(byte[] jpeg, long capturedUs) throws Exception {
        String eventId = getIntent().getStringExtra(EXTRA_EVENT_ID);
        String action = getIntent().getStringExtra(EXTRA_ACTION);
        int sequence = getIntent().getIntExtra(EXTRA_SEQUENCE, 1);
        long captureEpochMs = getIntent().getLongExtra(EXTRA_SESSION_START_EPOCH_MS, 0L)
                + Math.round(capturedUs / 1000.0d);
        String stamp = new java.text.SimpleDateFormat(
                "yyyyMMdd_HHmmss_SSS", java.util.Locale.US)
                .format(new java.util.Date(captureEpochMs));
        String photoId = eventId + "-P"
                + String.format(java.util.Locale.US, "%02d", sequence);
        String name = photoId + "_" + SessionStorage.safeName(action)
                + "_" + stamp + ".jpg";
        SessionStorage storage = new SessionStorage(this);
        android.net.Uri uri = storage.create(name, "image/jpeg",
                getIntent().getStringExtra(EXTRA_RELATIVE_PATH) + "photos/");
        try (java.io.OutputStream output =
                     getContentResolver().openOutputStream(uri, "wt")) {
            if (output == null) throw new java.io.IOException("无法写入照片");
            output.write(jpeg);
        } catch (Exception error) {
            getContentResolver().delete(uri, null, null);
            throw error;
        }
        Intent result = new Intent()
                .putExtra(RESULT_CAPTURED_US, capturedUs)
                .putExtra(RESULT_FILE_NAME, name)
                .putExtra(RESULT_CONTENT_URI, uri.toString());
        setResult(RESULT_OK, result);
        finish();
    }

    private void fail(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
        setResult(RESULT_CANCELED);
        finish();
    }

    @Override protected void onDestroy() {
        cameraExecutor.shutdown();
        super.onDestroy();
    }
}
