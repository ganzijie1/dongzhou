package com.deepsignal.dongzhou;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.webkit.MimeTypeMap;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.IOException;
import java.io.InputStream;

public final class MainActivity extends Activity {
    private WebView webView;
    private HappoBridge happoBridge;
    private PcgrlBridge pcgrlBridge;

    @SuppressLint({"SetJavaScriptEnabled", "JavascriptInterface"})
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);

        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(false);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        webView.setWebViewClient(new AssetWebViewClient(this));
        webView.setWebChromeClient(new WebChromeClient());
        happoBridge = new HappoBridge(getApplicationContext());
        webView.addJavascriptInterface(happoBridge, "DongzhouHappo");
        pcgrlBridge = new PcgrlBridge(getApplicationContext());
        webView.addJavascriptInterface(pcgrlBridge, "DongzhouPcgrl");
        setContentView(webView);
        webView.loadUrl("https://appassets.androidplatform.net/index.html");
        if (Build.VERSION.SDK_INT >= 33) Api33Back.register(this);
    }

    @SuppressLint("GestureBackNavigation")
    @SuppressWarnings("deprecation")
    @Override
    public void onBackPressed() {
        handleBack();
    }

    private void handleBack() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else finish();
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.removeJavascriptInterface("DongzhouHappo");
            webView.removeJavascriptInterface("DongzhouPcgrl");
            webView.destroy();
        }
        if (happoBridge != null) happoBridge.close();
        if (pcgrlBridge != null) pcgrlBridge.close();
        super.onDestroy();
    }

    @SuppressLint("NewApi")
    private static final class Api33Back {
        static void register(MainActivity activity) {
            activity.getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT, activity::handleBack);
        }
    }

    private static final class AssetWebViewClient extends WebViewClient {
        private static final String ASSET_HOST = "appassets.androidplatform.net";
        private final Context context;

        AssetWebViewClient(Context context) {
            this.context = context.getApplicationContext();
        }

        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
            Uri uri = request.getUrl();
            if (!"https".equals(uri.getScheme()) || !ASSET_HOST.equals(uri.getHost()))
                return super.shouldInterceptRequest(view, request);
            String path = uri.getPath();
            if (path == null || path.contains("..")) return null;
            path = path.startsWith("/") ? path.substring(1) : path;
            if (path.isEmpty()) path = "index.html";
            try {
                InputStream stream = context.getAssets().open(path);
                return new WebResourceResponse(mimeType(path), isText(path) ? "UTF-8" : null, stream);
            } catch (IOException ignored) {
                return null;
            }
        }

        private static String mimeType(String path) {
            if (path.endsWith(".lua")) return "text/plain";
            if (path.endsWith(".json")) return "application/json";
            String extension = MimeTypeMap.getFileExtensionFromUrl(path);
            String detected = MimeTypeMap.getSingleton().getMimeTypeFromExtension(extension);
            return detected == null ? "application/octet-stream" : detected;
        }

        private static boolean isText(String path) {
            return path.endsWith(".html") || path.endsWith(".css") || path.endsWith(".js")
                || path.endsWith(".json") || path.endsWith(".lua") || path.endsWith(".txt");
        }
    }
}
