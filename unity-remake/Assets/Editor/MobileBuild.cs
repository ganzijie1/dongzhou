using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;

namespace DongZhou.UnityRemake.Editor
{
    public static class MobileBuild
    {
        private static readonly string[] Scenes = { "Assets/Scenes/DongJiao.unity" };

        public static void BuildAndroid()
        {
            if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.Android, BuildTarget.Android))
                throw new InvalidOperationException("Unity Android Build Support is not installed.");

            EditorUserBuildSettings.SwitchActiveBuildTarget(
                BuildTargetGroup.Android, BuildTarget.Android);
            PlayerSettings.SetScriptingBackend(
                BuildTargetGroup.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel26;
            PlayerSettings.Android.targetSdkVersion = AndroidSdkVersions.AndroidApiLevel36;
            PlayerSettings.productName = "Dongzhou";
            PlayerSettings.bundleVersion = "0.1.0";
            PlayerSettings.Android.bundleVersionCode = 1;
            PlayerSettings.SetApplicationIdentifier(
                BuildTargetGroup.Android, "com.deepsignal.dongzhou");

            var output = Environment.GetEnvironmentVariable("DONGZHOU_ANDROID_OUTPUT");
            if (string.IsNullOrWhiteSpace(output))
                output = Path.GetFullPath(Path.Combine("Builds", "Android", "Dongzhou.apk"));
            Directory.CreateDirectory(Path.GetDirectoryName(output));

            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = Scenes,
                locationPathName = output,
                target = BuildTarget.Android,
                options = BuildOptions.None
            });
            if (report.summary.result != BuildResult.Succeeded)
                throw new InvalidOperationException(
                    $"Android build failed: {report.summary.result}, {report.summary.totalErrors} errors");
        }
    }
}
