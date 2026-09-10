package com.teslacan.voicerunner;

import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.net.Uri;
import android.os.Environment;
import android.provider.MediaStore;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/** V2优化-任务08-用户可见的 Session 目录、持续落盘和 ZIP 打包。 */
final class SessionStorage {
    static final String ROOT = Environment.DIRECTORY_DOWNLOADS + "/CANVoiceRunner/";

    static final class Files {
        final String relativePath;
        final Uri jsonUri;
        final Uri csvUri;

        Files(String relativePath, Uri jsonUri, Uri csvUri) {
            this.relativePath = relativePath;
            this.jsonUri = jsonUri;
            this.csvUri = csvUri;
        }
    }

    private final Context context;
    private final ContentResolver resolver;

    SessionStorage(Context context) {
        this.context = context.getApplicationContext();
        resolver = context.getContentResolver();
    }

    String nextSessionId() {
        android.content.SharedPreferences preferences =
                context.getSharedPreferences("v2_session_sequence", Context.MODE_PRIVATE);
        int next = preferences.getInt("next", 1);
        preferences.edit().putInt("next", next + 1).apply();
        return String.format(Locale.US, "S%04d", next);
    }

    static String directoryName(String scriptName, long startEpochMs, String sessionId) {
        String base = scriptName == null ? "采集脚本" : scriptName;
        int dot = base.lastIndexOf('.');
        if (dot > 0) base = base.substring(0, dot);
        String stamp = new SimpleDateFormat("yyyyMMdd_HHmmss_SSS", Locale.US)
                .format(new Date(startEpochMs));
        return safeName(base) + "__" + stamp + "__" + sessionId;
    }

    static String safeName(String value) {
        String cleaned = value == null ? "" : value.trim()
                .replaceAll("[\\\\/:*?\"<>|\\p{Cntrl}]", "_")
                .replaceAll("\\s+", "_")
                .replaceAll("_+", "_");
        while (cleaned.startsWith(".")) cleaned = cleaned.substring(1);
        return cleaned.isEmpty() ? "未命名" : cleaned;
    }

    Files createSessionFiles(String directoryName) throws IOException {
        String path = ROOT + directoryName + "/";
        return new Files(path,
                create("session.json", "application/json", path),
                create("event_timeline.csv", "text/csv", path));
    }

    Uri create(String name, String mimeType, String relativePath) throws IOException {
        ContentValues values = new ContentValues();
        values.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
        values.put(MediaStore.MediaColumns.MIME_TYPE, mimeType);
        values.put(MediaStore.MediaColumns.RELATIVE_PATH, relativePath);
        Uri uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
        if (uri == null) throw new IOException("无法创建 " + name);
        return uri;
    }

    void writeText(Uri uri, String value) throws IOException {
        try (OutputStream output = resolver.openOutputStream(uri, "wt")) {
            if (output == null) throw new IOException("无法写入 " + uri);
            output.write(value.getBytes(StandardCharsets.UTF_8));
            output.flush();
        }
    }

    void persist(SessionRecord session, Files files, String appVersion) throws IOException {
        writeText(files.jsonUri, SessionJsonExporter.export(session, appVersion));
        List<String> csv = SessionCsvExporter.export(
                session.events, session.startClockEpochMs, session.startClock);
        writeText(files.csvUri, String.join("\n", csv) + "\n");
    }

    void copy(Uri source, OutputStream destination) throws IOException {
        try (InputStream raw = resolver.openInputStream(source)) {
            if (raw == null) throw new IOException("无法读取 " + source);
            try (BufferedInputStream input = new BufferedInputStream(raw)) {
                byte[] buffer = new byte[16 * 1024];
                int count;
                while ((count = input.read(buffer)) >= 0) {
                    if (count > 0) destination.write(buffer, 0, count);
                }
            }
        }
    }

    Uri saveFile(File source, String name, String mimeType, String relativePath)
            throws IOException {
        Uri destination = create(name, mimeType, relativePath);
        try (InputStream input = new FileInputStream(source);
             OutputStream output = resolver.openOutputStream(destination, "wt")) {
            if (output == null) throw new IOException("无法写入 " + name);
            byte[] buffer = new byte[16 * 1024];
            int count;
            while ((count = input.read(buffer)) >= 0) {
                if (count > 0) output.write(buffer, 0, count);
            }
        } catch (IOException error) {
            resolver.delete(destination, null, null);
            throw error;
        }
        return destination;
    }

    void exportZip(SessionRecord session, Files files, Uri destination) throws IOException {
        try (OutputStream raw = resolver.openOutputStream(destination, "wt")) {
            if (raw == null) throw new IOException("无法创建 ZIP");
            try (ZipOutputStream zip = new ZipOutputStream(new BufferedOutputStream(raw))) {
                String root = session.directoryName + "/";
                add(zip, root + "session.json", files.jsonUri);
                add(zip, root + "event_timeline.csv", files.csvUri);
                for (PhotoRecord photo : session.photos) {
                    if ("AVAILABLE".equals(photo.fileStatus)) {
                        add(zip, root + "photos/" + photo.fileName,
                                Uri.parse(photo.contentUri));
                    }
                }
                if (session.audio.contentUri != null && session.audio.fileName != null) {
                    add(zip, root + "audio/" + session.audio.fileName,
                            Uri.parse(session.audio.contentUri));
                }
            }
        }
    }

    private void add(ZipOutputStream zip, String name, Uri source) throws IOException {
        zip.putNextEntry(new ZipEntry(name));
        copy(source, zip);
        zip.closeEntry();
    }

    boolean canRead(Uri uri) {
        try (android.content.res.AssetFileDescriptor ignored =
                     resolver.openAssetFileDescriptor(uri, "r")) {
            return ignored != null;
        } catch (Exception error) {
            return false;
        }
    }
}
