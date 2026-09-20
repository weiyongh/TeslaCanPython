package com.teslacan.voicerunner;

import android.os.SystemClock;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

/** 冻结的 Rogue App START/STOP JSON API 客户端；不重试。 */
final class RogueApiClient {
    static final String START_URL = "http://picanlog.local:8080/cgi-bin/app/start";
    static final String STOP_URL = "http://picanlog.local:8080/cgi-bin/app/stop";

    static final class Result {
        final int httpStatus;
        final String rawJson;
        final long responseRealtimeNs;
        final boolean ok;
        final String scriptName;
        final String sessionId;
        final String logFilename;
        final Long requestReceivedEpochMs;
        final Long dumpEpochMs;
        final String errorCode;
        final String message;

        Result(int httpStatus, String rawJson, long responseRealtimeNs, boolean ok,
               String scriptName, String sessionId, String logFilename,
               Long requestReceivedEpochMs, Long dumpEpochMs,
               String errorCode, String message) {
            this.httpStatus = httpStatus;
            this.rawJson = rawJson;
            this.responseRealtimeNs = responseRealtimeNs;
            this.ok = ok;
            this.scriptName = scriptName;
            this.sessionId = sessionId;
            this.logFilename = logFilename;
            this.requestReceivedEpochMs = requestReceivedEpochMs;
            this.dumpEpochMs = dumpEpochMs;
            this.errorCode = errorCode;
            this.message = message;
        }
    }

    Result start(String scriptName, String sessionId, long requestEpochMs) throws IOException {
        JSONObject request = new JSONObject();
        try {
            request.put("script_name", scriptName);
            request.put("session_id", sessionId);
            request.put("benji_start_request_epoch_ms", requestEpochMs);
        } catch (JSONException error) {
            throw new IOException("无法生成 START JSON", error);
        }
        return post(START_URL, request, true);
    }

    Result stop(String scriptName, String sessionId, long requestEpochMs) throws IOException {
        JSONObject request = new JSONObject();
        try {
            request.put("script_name", scriptName);
            request.put("session_id", sessionId);
            request.put("benji_stop_request_epoch_ms", requestEpochMs);
        } catch (JSONException error) {
            throw new IOException("无法生成 STOP JSON", error);
        }
        return post(STOP_URL, request, false);
    }

    private Result post(String endpoint, JSONObject request, boolean start) throws IOException {
        HttpURLConnection connection = (HttpURLConnection) new URL(endpoint).openConnection();
        connection.setRequestMethod("POST");
        connection.setDoOutput(true);
        connection.setConnectTimeout(10_000);
        connection.setReadTimeout(30_000);
        connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
        connection.setRequestProperty("Accept", "application/json");
        byte[] body = request.toString().getBytes(StandardCharsets.UTF_8);
        connection.setFixedLengthStreamingMode(body.length);
        try {
            try (OutputStream output = connection.getOutputStream()) {
                output.write(body);
            }
            int status = connection.getResponseCode();
            InputStream responseStream = status >= 400
                    ? connection.getErrorStream() : connection.getInputStream();
            String raw = readUtf8(responseStream);
            long responseRealtimeNs = SystemClock.elapsedRealtimeNanos();
            return parse(status, raw, responseRealtimeNs, start);
        } finally {
            connection.disconnect();
        }
    }

    private Result parse(int status, String raw, long responseRealtimeNs, boolean start)
            throws IOException {
        final JSONObject response;
        try {
            response = new JSONObject(raw);
            boolean ok = response.getBoolean("ok");
            if (!ok) {
                return new Result(status, raw, responseRealtimeNs, false,
                        null, null, null, null, null,
                        response.getString("error_code"), response.getString("message"));
            }
            return new Result(status, raw, responseRealtimeNs, true,
                    response.getString("script_name"), response.getString("session_id"),
                    response.getString("log_filename"),
                    response.getLong(start
                            ? "rogue_start_request_received_epoch_ms"
                            : "rogue_stop_request_received_epoch_ms"),
                    response.getLong(start
                            ? "rogue_dump_start_epoch_ms" : "rogue_dump_stop_epoch_ms"),
                    null, null);
        } catch (JSONException error) {
            throw new ResponseException(status, raw, responseRealtimeNs,
                    "INVALID_RESPONSE", "Rogue response JSON 无效", error);
        }
    }

    static final class ResponseException extends IOException {
        final int httpStatus;
        final String rawJson;
        final long responseRealtimeNs;
        final String errorCode;

        ResponseException(int httpStatus, String rawJson, long responseRealtimeNs,
                          String errorCode, String message, Throwable cause) {
            super(message, cause);
            this.httpStatus = httpStatus;
            this.rawJson = rawJson;
            this.responseRealtimeNs = responseRealtimeNs;
            this.errorCode = errorCode;
        }
    }

    private static String readUtf8(InputStream input) throws IOException {
        if (input == null) return "";
        try (InputStream stream = input; ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[4096];
            int count;
            while ((count = stream.read(buffer)) >= 0) {
                if (count > 0) output.write(buffer, 0, count);
            }
            return new String(output.toByteArray(), StandardCharsets.UTF_8);
        }
    }
}
