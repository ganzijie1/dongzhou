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
import java.util.HashMap;
import java.util.Map;
import org.json.JSONArray;

public final class HappoBridge implements AutoCloseable {
    private static final int LOCAL_FEATURES = 20;
    private static final int CANDIDATE_FEATURES = 34;
    private static final int MAX_CANDIDATES = 256;
    private static final int ROLE_COUNT = 11;
    private static final long INFERENCE_BUDGET_NANOS = 12_000_000L;
    private static final String EXPECTED_MODEL_SHA256 =
        "e7310bd63dc843970f6fe570ebf0924b76dbe21717c2d5db8c69068b5047b697";

    private final OrtEnvironment environment;
    private OrtSession session;

    HappoBridge(Context context) {
        environment = OrtEnvironment.getEnvironment();
        try (InputStream input = context.getAssets().open("HappoMobile.onnx");
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
    public synchronized int selectAction(
        String localJson, String candidatesJson, int candidateCount, int roleIndex) {
        if (session == null || candidateCount < 1 || candidateCount > MAX_CANDIDATES
            || roleIndex < 0 || roleIndex >= ROLE_COUNT) return -1;
        try {
            float[] local = readArray(localJson, LOCAL_FEATURES);
            float[] rawCandidates = readArray(
                candidatesJson, candidateCount * CANDIDATE_FEATURES);
            float[] candidates = new float[MAX_CANDIDATES * CANDIDATE_FEATURES];
            System.arraycopy(rawCandidates, 0, candidates, 0, rawCandidates.length);
            float[] legalMask = new float[MAX_CANDIDATES];
            for (int index = 0; index < candidateCount; index++) legalMask[index] = 1f;
            float[] role = new float[ROLE_COUNT];
            role[roleIndex] = 1f;

            try (OnnxTensor localTensor = OnnxTensor.createTensor(
                     environment, FloatBuffer.wrap(local), new long[] {1, LOCAL_FEATURES});
                 OnnxTensor candidateTensor = OnnxTensor.createTensor(
                     environment, FloatBuffer.wrap(candidates),
                     new long[] {1, MAX_CANDIDATES, CANDIDATE_FEATURES});
                 OnnxTensor maskTensor = OnnxTensor.createTensor(
                     environment, FloatBuffer.wrap(legalMask), new long[] {1, MAX_CANDIDATES});
                 OnnxTensor roleTensor = OnnxTensor.createTensor(
                     environment, FloatBuffer.wrap(role), new long[] {1, ROLE_COUNT})) {
                Map<String, OnnxTensor> inputs = new HashMap<>();
                inputs.put("local", localTensor);
                inputs.put("candidates", candidateTensor);
                inputs.put("legal_mask", maskTensor);
                inputs.put("role_one_hot", roleTensor);
                long started = System.nanoTime();
                try (OrtSession.Result result = session.run(inputs)) {
                    float[] logits = ((float[][]) result.get(0).getValue())[0];
                    if (System.nanoTime() - started > INFERENCE_BUDGET_NANOS) return -1;
                    int best = 0;
                    for (int index = 1; index < candidateCount; index++) {
                        if (Float.isFinite(logits[index]) && logits[index] > logits[best]) best = index;
                    }
                    return best;
                }
            }
        } catch (Exception ignored) {
            return -1;
        }
    }

    private static float[] readArray(String json, int expectedLength) throws Exception {
        JSONArray values = new JSONArray(json);
        if (values.length() != expectedLength) throw new IllegalArgumentException("feature length");
        float[] result = new float[expectedLength];
        for (int index = 0; index < expectedLength; index++) {
            result[index] = (float) values.getDouble(index);
            if (!Float.isFinite(result[index])) throw new IllegalArgumentException("non-finite feature");
        }
        return result;
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
