using System;
using System.Collections.Generic;
using System.Diagnostics;
using Unity.Sentis;
using UnityEngine;

namespace DongZhou.UnityRemake.Mobile
{
    public sealed class HappoSentisPolicy : MonoBehaviour
    {
        [SerializeField] private ModelAsset modelAsset;
        [SerializeField] private BackendType backend = BackendType.CPU;
        [SerializeField, Min(0.1f)] private float inferenceBudgetMilliseconds = 12f;

        private readonly float[] paddedCandidates = new float[
            HappoPolicyContract.MaxCandidates * HappoPolicyContract.CandidateFeatureCount];
        private readonly float[] legalMaskValues = new float[HappoPolicyContract.MaxCandidates];
        private readonly float[] roleOneHot = new float[HappoPolicyContract.RoleCount];
        private IWorker worker;

        public static HappoSentisPolicy Instance { get; private set; }
        public bool IsReady => worker != null;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Bootstrap()
        {
            if (Instance != null || FindObjectOfType<HappoSentisPolicy>() != null)
                return;
            var root = new GameObject("HAPPO Mobile Inference");
            DontDestroyOnLoad(root);
            root.AddComponent<HappoSentisPolicy>();
        }

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            if (modelAsset == null)
                modelAsset = Resources.Load<ModelAsset>("Models/HappoMobile");
            Initialize();
        }

        public void Initialize()
        {
            worker?.Dispose();
            worker = null;
            if (modelAsset == null)
                return;
            var runtimeModel = ModelLoader.Load(modelAsset);
            worker = WorkerFactory.CreateWorker(backend, runtimeModel);
        }

        public int SelectAction(
            float[] local,
            float[] candidates,
            bool[] legalMask,
            int roleIndex,
            out HappoSelectionDiagnostics diagnostics)
        {
            var fallback = HappoPolicyContract.FirstLegal(legalMask);
            if (!HappoPolicyContract.Validate(
                    local, candidates, legalMask, roleIndex, out var validationReason))
            {
                diagnostics = new HappoSelectionDiagnostics(validationReason, 0d);
                return fallback;
            }
            if (worker == null)
            {
                diagnostics = new HappoSelectionDiagnostics(
                    HappoFallbackReason.ModelUnavailable, 0d);
                return fallback;
            }

            Array.Clear(paddedCandidates, 0, paddedCandidates.Length);
            Array.Copy(candidates, paddedCandidates, candidates.Length);
            Array.Clear(legalMaskValues, 0, legalMaskValues.Length);
            for (var index = 0; index < legalMask.Length; index++)
                legalMaskValues[index] = legalMask[index] ? 1f : 0f;
            Array.Clear(roleOneHot, 0, roleOneHot.Length);
            roleOneHot[roleIndex] = 1f;

            var started = Stopwatch.GetTimestamp();
            try
            {
                using var localTensor = new TensorFloat(
                    new TensorShape(1, HappoPolicyContract.LocalFeatureCount), local);
                using var candidateTensor = new TensorFloat(
                    new TensorShape(
                        1,
                        HappoPolicyContract.MaxCandidates,
                        HappoPolicyContract.CandidateFeatureCount),
                    paddedCandidates);
                using var maskTensor = new TensorFloat(
                    new TensorShape(1, HappoPolicyContract.MaxCandidates), legalMaskValues);
                using var roleTensor = new TensorFloat(
                    new TensorShape(1, HappoPolicyContract.RoleCount), roleOneHot);
                var inputs = new Dictionary<string, Tensor>
                {
                    ["local"] = localTensor,
                    ["candidates"] = candidateTensor,
                    ["legal_mask"] = maskTensor,
                    ["role_one_hot"] = roleTensor
                };
                worker.Execute(inputs);
                var output = worker.PeekOutput("logits") as TensorFloat;
                if (output == null)
                    return FinishFallback(HappoFallbackReason.InvalidOutput, started, fallback, out diagnostics);

                var scores = output.ToReadOnlyArray();
                var bestIndex = -1;
                var bestScore = float.NegativeInfinity;
                for (var index = 0; index < legalMask.Length; index++)
                {
                    if (!legalMask[index] || !HappoPolicyContract.IsFinite(scores[index]))
                        continue;
                    if (bestIndex < 0 || scores[index] > bestScore)
                    {
                        bestIndex = index;
                        bestScore = scores[index];
                    }
                }

                var elapsed = ElapsedMilliseconds(started);
                if (elapsed > inferenceBudgetMilliseconds)
                {
                    diagnostics = new HappoSelectionDiagnostics(
                        HappoFallbackReason.InferenceTimedOut, elapsed);
                    return fallback;
                }
                if (bestIndex < 0)
                {
                    diagnostics = new HappoSelectionDiagnostics(
                        HappoFallbackReason.InvalidOutput, elapsed);
                    return fallback;
                }

                diagnostics = new HappoSelectionDiagnostics(HappoFallbackReason.None, elapsed);
                return bestIndex;
            }
            catch (Exception exception)
            {
                UnityEngine.Debug.LogWarning($"HAPPO inference fallback: {exception.Message}");
                return FinishFallback(
                    HappoFallbackReason.InferenceFailed, started, fallback, out diagnostics);
            }
        }

        private static int FinishFallback(
            HappoFallbackReason reason,
            long started,
            int fallback,
            out HappoSelectionDiagnostics diagnostics)
        {
            diagnostics = new HappoSelectionDiagnostics(reason, ElapsedMilliseconds(started));
            return fallback;
        }

        private static double ElapsedMilliseconds(long started) =>
            (Stopwatch.GetTimestamp() - started) * 1000d / Stopwatch.Frequency;

        private void OnDestroy()
        {
            worker?.Dispose();
            worker = null;
            if (Instance == this)
                Instance = null;
        }
    }
}
