using System;

namespace DongZhou.UnityRemake.Mobile
{
    public enum HappoFallbackReason
    {
        None,
        InvalidInput,
        NoLegalAction,
        ModelUnavailable,
        InferenceFailed,
        InferenceTimedOut,
        InvalidOutput
    }

    public readonly struct HappoSelectionDiagnostics
    {
        public HappoSelectionDiagnostics(
            HappoFallbackReason fallbackReason,
            double inferenceMilliseconds)
        {
            FallbackReason = fallbackReason;
            InferenceMilliseconds = inferenceMilliseconds;
        }

        public HappoFallbackReason FallbackReason { get; }
        public double InferenceMilliseconds { get; }
        public bool UsedFallback => FallbackReason != HappoFallbackReason.None;
    }

    public static class HappoPolicyContract
    {
        public const int LocalFeatureCount = 20;
        public const int CandidateFeatureCount = 34;
        public const int RoleCount = 11;
        public const int MaxCandidates = 256;

        public static bool Validate(
            float[] local,
            float[] candidates,
            bool[] legalMask,
            int roleIndex,
            out HappoFallbackReason reason)
        {
            reason = HappoFallbackReason.InvalidInput;
            if (local == null || local.Length != LocalFeatureCount)
                return false;
            if (legalMask == null || legalMask.Length == 0 || legalMask.Length > MaxCandidates)
                return false;
            if (candidates == null || candidates.Length != legalMask.Length * CandidateFeatureCount)
                return false;
            if (roleIndex < 0 || roleIndex >= RoleCount)
                return false;
            if (!AllFinite(local) || !AllFinite(candidates))
                return false;
            if (FirstLegal(legalMask) < 0)
            {
                reason = HappoFallbackReason.NoLegalAction;
                return false;
            }

            reason = HappoFallbackReason.None;
            return true;
        }

        public static int FirstLegal(bool[] legalMask)
        {
            if (legalMask == null)
                return -1;
            for (var index = 0; index < legalMask.Length; index++)
            {
                if (legalMask[index])
                    return index;
            }
            return -1;
        }

        public static bool IsFinite(float value) =>
            !float.IsNaN(value) && !float.IsInfinity(value);

        private static bool AllFinite(float[] values)
        {
            foreach (var value in values)
            {
                if (!IsFinite(value))
                    return false;
            }
            return true;
        }
    }
}
