package com.deepsignal.dongzhou;

import android.content.Context;
import android.webkit.JavascriptInterface;
import ai.onnxruntime.OnnxTensor;
import ai.onnxruntime.OrtEnvironment;
import ai.onnxruntime.OrtSession;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.FloatBuffer;
import java.security.MessageDigest;
import java.util.Collections;
import org.json.JSONArray;
import org.json.JSONObject;

public final class PcgrlBridge implements AutoCloseable {
    private static final int WIDTH = 19;
    private static final int HEIGHT = 14;
    private static final int CELL_COUNT = WIDTH * HEIGHT;
    private static final int FEATURE_COUNT = 9;
    private static final int TILE_COUNT = 4;
    private static final long INFERENCE_BUDGET_NANOS = 35_000_000L;
    private static final String MODEL_VERSION = "pcgrl-masui-2026-11-02";
    private static final String EXPECTED_MODEL_SHA256 =
        "ded525499ec83e9d3b58d1bf14b89cf621b8cd962726238367482b958b070ada";
    private static final int[][] SPAWNS = {
        {2, 6}, {3, 4}, {3, 6}, {3, 8}, {4, 3}, {4, 9}, {5, 5},
        {16, 6}, {15, 5}, {15, 7}, {14, 4}, {14, 8}, {13, 6}
    };

    private final OrtEnvironment environment;
    private OrtSession session;

    PcgrlBridge(Context context) {
        environment = OrtEnvironment.getEnvironment();
        try (InputStream input = context.getAssets().open("PcgrlMasui.onnx");
             ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192];
            int count;
            while ((count = input.read(buffer)) >= 0) output.write(buffer, 0, count);
            byte[] model = output.toByteArray();
            if (!EXPECTED_MODEL_SHA256.equals(sha256(model)))
                throw new IllegalStateException("model hash mismatch");
            session = environment.createSession(model, new OrtSession.SessionOptions());
        } catch (Exception ignored) {
            session = null;
        }
    }

    @JavascriptInterface
    public boolean isReady() {
        return session != null;
    }

    @JavascriptInterface
    public synchronized String generate(double requestedDifficulty, int seed) {
        if (session == null) return error("policy-unavailable");
        float difficulty = (float) Math.max(0.0, Math.min(1.0, requestedDifficulty));
        float[] features = buildFeatures(difficulty, seed);
        try (OnnxTensor cells = OnnxTensor.createTensor(
                 environment, FloatBuffer.wrap(features), new long[] {1, CELL_COUNT, FEATURE_COUNT})) {
            long started = System.nanoTime();
            try (OrtSession.Result result = session.run(Collections.singletonMap("cells", cells))) {
                long elapsed = System.nanoTime() - started;
                if (elapsed > INFERENCE_BUDGET_NANOS) return error("inference-budget-exceeded");
                float[][] logits = ((float[][][]) result.get(0).getValue())[0];
                JSONArray tiles = new JSONArray();
                for (int index = 0; index < CELL_COUNT; index++) {
                    int best = 0;
                    double bestScore = Double.NEGATIVE_INFINITY;
                    for (int tile = 0; tile < TILE_COUNT; tile++) {
                        double probability = Math.max(1e-7, Math.min(1.0 - 1e-7,
                            (hashUnit(seed ^ (tile * 0x45D9F3B), index, 0x27D4EB2D) + 1.0) * 0.5));
                        double gumbel = -Math.log(-Math.log(probability));
                        double score = logits[index][tile] + gumbel * 0.85;
                        if (Double.isFinite(score) && score > bestScore) {
                            bestScore = score;
                            best = tile;
                        }
                    }
                    tiles.put(best);
                }
                JSONObject payload = new JSONObject();
                payload.put("ready", true);
                payload.put("tiles", tiles);
                payload.put("inference_ms", elapsed / 1_000_000.0);
                payload.put("model_version", MODEL_VERSION);
                payload.put("model_sha256", EXPECTED_MODEL_SHA256);
                payload.put("seed", seed);
                payload.put("difficulty", difficulty);
                return payload.toString();
            }
        } catch (Exception ignored) {
            return error("inference-error");
        }
    }

    private static float[] buildFeatures(float difficulty, int seed) {
        float[] features = new float[CELL_COUNT * FEATURE_COUNT];
        for (int index = 0; index < CELL_COUNT; index++) {
            int y = index / WIDTH;
            int x = index % WIDTH;
            int edge = Math.min(Math.min(x, WIDTH - 1 - x), Math.min(y, HEIGHT - 1 - y));
            int offset = index * FEATURE_COUNT;
            features[offset] = x / (float) (WIDTH - 1) * 2f - 1f;
            features[offset + 1] = y / (float) (HEIGHT - 1) * 2f - 1f;
            features[offset + 2] = Math.min(edge, 4) / 4f;
            features[offset + 3] = x <= 5 ? 1f : 0f;
            features[offset + 4] = x >= WIDTH - 6 ? 1f : 0f;
            features[offset + 5] = Math.abs(y - (HEIGHT - 1) / 2f) <= 2f ? 1f : 0f;
            features[offset + 6] = difficulty;
            features[offset + 7] = hashUnit(seed, index, 0xA341316C);
            features[offset + 8] = hashUnit(seed, index, 0xC8013EA4);
            if (isSpawn(x, y)) features[offset + 5] = 1.5f;
        }
        return features;
    }

    private static boolean isSpawn(int x, int y) {
        for (int[] point : SPAWNS) if (point[0] == x && point[1] == y) return true;
        return false;
    }

    private static float hashUnit(int seed, int index, int salt) {
        int value = seed ^ index * 0x9E3779B9 ^ salt;
        value = (value ^ (value >>> 16)) * 0x7FEB352D;
        value = (value ^ (value >>> 15)) * 0x846CA68B;
        value ^= value >>> 16;
        return ((value >>> 8) & 0xFFFFFF) / 16777215f * 2f - 1f;
    }

    private static String error(String reason) {
        try {
            JSONObject payload = new JSONObject();
            payload.put("ready", false);
            payload.put("reason", reason);
            payload.put("model_version", MODEL_VERSION);
            return payload.toString();
        } catch (Exception ignored) {
            return "{\"ready\":false}";
        }
    }

    private static String sha256(byte[] values) throws Exception {
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(values);
        StringBuilder result = new StringBuilder(digest.length * 2);
        for (byte value : digest) result.append(String.format("%02x", value & 0xff));
        return result.toString();
    }

    @Override
    public synchronized void close() {
        if (session == null) return;
        try {
            session.close();
        } catch (Exception ignored) {
        }
        session = null;
    }
}
