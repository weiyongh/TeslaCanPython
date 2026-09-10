package com.teslacan.voicerunner;

import android.annotation.SuppressLint;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.AudioTimestamp;
import android.media.MediaCodec;
import android.media.MediaCodecInfo;
import android.media.MediaFormat;
import android.media.MediaMuxer;
import android.media.MediaRecorder;
import android.os.SystemClock;

import java.io.File;
import java.nio.ByteBuffer;

/** V2优化-任务06-AudioRecord + AAC/MediaMuxer 的单 Session 连续录音。 */
final class SessionAudioRecorder {
    interface Listener {
        void onStopped(Result result);
        void onFailure(String reason);
    }

    static final class Result {
        final File file;
        final long requestRealtimeNs;
        final long requestClockEpochMs;
        final Long streamStartRealtimeNs;
        final long frameCount;
        final int sampleRate;

        Result(File file, long requestRealtimeNs, long requestClockEpochMs,
               Long streamStartRealtimeNs, long frameCount, int sampleRate) {
            this.file = file;
            this.requestRealtimeNs = requestRealtimeNs;
            this.requestClockEpochMs = requestClockEpochMs;
            this.streamStartRealtimeNs = streamStartRealtimeNs;
            this.frameCount = frameCount;
            this.sampleRate = sampleRate;
        }
    }

    private static final int SAMPLE_RATE = 48_000;
    private static final int BIT_RATE = 96_000;
    private final File outputFile;
    private final Listener listener;
    private volatile boolean stopping;
    private Thread worker;
    private long requestRealtimeNs;
    private long requestClockEpochMs;

    SessionAudioRecorder(File outputFile, Listener listener) {
        this.outputFile = outputFile;
        this.listener = listener;
    }

    void start() {
        requestRealtimeNs = SystemClock.elapsedRealtimeNanos();
        requestClockEpochMs = System.currentTimeMillis();
        worker = new Thread(this::record, "CANVoiceRunner-Audio");
        worker.start();
    }

    void stop() {
        stopping = true;
    }

    long requestRealtimeNs() {
        return requestRealtimeNs;
    }

    long requestClockEpochMs() {
        return requestClockEpochMs;
    }

    @SuppressLint("MissingPermission")
    private void record() {
        AudioRecord audio = null;
        MediaCodec codec = null;
        MediaMuxer muxer = null;
        try {
            int minimum = AudioRecord.getMinBufferSize(SAMPLE_RATE,
                    AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT);
            if (minimum <= 0) throw new IllegalStateException("UNSUPPORTED_AUDIO_FORMAT");
            audio = new AudioRecord(MediaRecorder.AudioSource.DEFAULT, SAMPLE_RATE,
                    AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT,
                    Math.max(minimum * 2, 16_384));
            if (audio.getState() != AudioRecord.STATE_INITIALIZED) {
                throw new IllegalStateException("AUDIO_RECORD_INIT_FAILED");
            }
            MediaFormat format = MediaFormat.createAudioFormat(
                    MediaFormat.MIMETYPE_AUDIO_AAC, SAMPLE_RATE, 1);
            format.setInteger(MediaFormat.KEY_AAC_PROFILE,
                    MediaCodecInfo.CodecProfileLevel.AACObjectLC);
            format.setInteger(MediaFormat.KEY_BIT_RATE, BIT_RATE);
            format.setInteger(MediaFormat.KEY_MAX_INPUT_SIZE, Math.max(minimum, 8192));
            codec = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_AUDIO_AAC);
            codec.configure(format, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE);
            muxer = new MediaMuxer(outputFile.getAbsolutePath(),
                    MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4);
            codec.start();
            audio.startRecording();

            MediaCodec.BufferInfo info = new MediaCodec.BufferInfo();
            AudioTimestamp timestamp = new AudioTimestamp();
            Long streamStartNs = null;
            long frames = 0L;
            int track = -1;
            boolean muxerStarted = false;
            boolean eosQueued = false;
            boolean eosSeen = false;

            while (!eosSeen) {
                if (!eosQueued) {
                    int inputIndex = codec.dequeueInputBuffer(10_000);
                    if (inputIndex >= 0) {
                        ByteBuffer input = codec.getInputBuffer(inputIndex);
                        if (input == null) throw new IllegalStateException("ENCODER_INPUT_MISSING");
                        input.clear();
                        int read = stopping ? 0 : audio.read(input, input.remaining(),
                                AudioRecord.READ_BLOCKING);
                        if (read < 0) throw new IllegalStateException("AUDIO_READ_" + read);
                        long ptsUs = frames * 1_000_000L / SAMPLE_RATE;
                        if (stopping) {
                            codec.queueInputBuffer(inputIndex, 0, 0, ptsUs,
                                    MediaCodec.BUFFER_FLAG_END_OF_STREAM);
                            eosQueued = true;
                        } else {
                            codec.queueInputBuffer(inputIndex, 0, read, ptsUs, 0);
                            frames += read / 2L;
                            if (streamStartNs == null
                                    && audio.getTimestamp(timestamp,
                                    AudioTimestamp.TIMEBASE_BOOTTIME) == AudioRecord.SUCCESS) {
                                streamStartNs = timestamp.nanoTime
                                        - timestamp.framePosition * 1_000_000_000L / SAMPLE_RATE;
                            }
                        }
                    }
                }

                int outputIndex;
                while ((outputIndex = codec.dequeueOutputBuffer(info, 0)) >= 0) {
                    ByteBuffer output = codec.getOutputBuffer(outputIndex);
                    if (output != null && info.size > 0 && muxerStarted) {
                        output.position(info.offset);
                        output.limit(info.offset + info.size);
                        muxer.writeSampleData(track, output, info);
                    }
                    eosSeen = (info.flags & MediaCodec.BUFFER_FLAG_END_OF_STREAM) != 0;
                    codec.releaseOutputBuffer(outputIndex, false);
                }
                if (outputIndex == MediaCodec.INFO_OUTPUT_FORMAT_CHANGED) {
                    track = muxer.addTrack(codec.getOutputFormat());
                    muxer.start();
                    muxerStarted = true;
                }
            }
            audio.stop();
            codec.stop();
            if (muxerStarted) muxer.stop();
            listener.onStopped(new Result(outputFile, requestRealtimeNs,
                    requestClockEpochMs, streamStartNs, frames, SAMPLE_RATE));
        } catch (Exception error) {
            outputFile.delete();
            listener.onFailure(error.getClass().getSimpleName() + ": " + error.getMessage());
        } finally {
            try { if (audio != null) audio.release(); } catch (Exception ignored) { }
            try { if (codec != null) codec.release(); } catch (Exception ignored) { }
            try { if (muxer != null) muxer.release(); } catch (Exception ignored) { }
        }
    }
}
