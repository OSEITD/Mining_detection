package com.mining.detector;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebSettings;
import android.webkit.WebChromeClient;
import android.webkit.ValueCallback;
import android.webkit.GeolocationPermissions;
import android.content.Intent;
import android.net.Uri;
import android.widget.Toast;
import android.view.KeyEvent;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

/**
 * Mining Detection System - Android WebView App
 * Loads the Streamlit dashboard in a native Android app
 */
public class MainActivity extends Activity {
    
    private WebView webView;
    private SwipeRefreshLayout swipeRefreshLayout;
    private ValueCallback<Uri[]> filePathCallback;
    private static final int FILE_CHOOSER_REQUEST_CODE = 1;
    
    // IMPORTANT: Update this URL with your computer's IP address
    // Get your IP by running: ipconfig (Windows) or ifconfig (Mac/Linux)
    private static final String APP_URL = "http://192.168.43.27:8501";
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Initialize SwipeRefreshLayout for pull-to-refresh
        swipeRefreshLayout = findViewById(R.id.swipeRefresh);
        
        // Disable swipe-to-refresh to prevent accidental page reloads while scrolling
        swipeRefreshLayout.setEnabled(false);
        
        // Alternative: If you want pull-to-refresh but less sensitive, uncomment below:
        // swipeRefreshLayout.setOnRefreshListener(() -> {
        //     webView.reload();
        // });
        
        // Initialize WebView
        webView = findViewById(R.id.webview);
        setupWebView();
        
        // Load the Streamlit app
        loadApp();
    }
    
    private void setupWebView() {
        WebSettings webSettings = webView.getSettings();
        
        // Enable JavaScript (required for Streamlit)
        webSettings.setJavaScriptEnabled(true);
        
        // Enable DOM storage (required for modern web apps)
        webSettings.setDomStorageEnabled(true);
        
        // Enable database storage
        webSettings.setDatabaseEnabled(true);
        
        // Enable file access
        webSettings.setAllowFileAccess(true);
        webSettings.setAllowContentAccess(true);
        
        // Enable caching for better performance
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);
        
        // Enable zooming
        webSettings.setSupportZoom(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);
        
        // Better rendering
        webSettings.setUseWideViewPort(true);
        webSettings.setLoadWithOverviewMode(true);
        
        // Modern rendering engine
        webSettings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        
        // Geolocation support
        webSettings.setGeolocationEnabled(true);
        
        // Set WebViewClient to handle navigation
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                // Load all URLs within the WebView
                view.loadUrl(url);
                return true;
            }
            
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                // Stop refresh animation when page loads
                swipeRefreshLayout.setRefreshing(false);
            }
            
            @Override
            public void onReceivedError(WebView view, int errorCode, 
                                       String description, String failingUrl) {
                super.onReceivedError(view, errorCode, description, failingUrl);
                swipeRefreshLayout.setRefreshing(false);
                Toast.makeText(MainActivity.this, 
                    "Connection error. Make sure:\n" +
                    "1. Your PC is running Streamlit\n" +
                    "2. Both devices are on same WiFi\n" +
                    "3. IP address is correct: " + APP_URL,
                    Toast.LENGTH_LONG).show();
            }
        });
        
        // Set WebChromeClient for advanced features
        webView.setWebChromeClient(new WebChromeClient() {
            // Geolocation permission
            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, 
                    GeolocationPermissions.Callback callback) {
                callback.invoke(origin, true, false);
            }
            
            // File upload support
            @Override
            public boolean onShowFileChooser(WebView webView, 
                    ValueCallback<Uri[]> filePathCallback,
                    FileChooserParams fileChooserParams) {
                if (MainActivity.this.filePathCallback != null) {
                    MainActivity.this.filePathCallback.onReceiveValue(null);
                }
                MainActivity.this.filePathCallback = filePathCallback;
                
                Intent intent = fileChooserParams.createIntent();
                try {
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST_CODE);
                } catch (Exception e) {
                    MainActivity.this.filePathCallback = null;
                    Toast.makeText(MainActivity.this, 
                        "Cannot open file chooser", Toast.LENGTH_SHORT).show();
                    return false;
                }
                return true;
            }
        });
    }
    
    private void loadApp() {
        swipeRefreshLayout.setRefreshing(true);
        webView.loadUrl(APP_URL);
    }
    
    // Handle file upload result
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        
        if (requestCode == FILE_CHOOSER_REQUEST_CODE) {
            if (filePathCallback == null) return;
            
            Uri[] results = null;
            if (resultCode == Activity.RESULT_OK && data != null) {
                String dataString = data.getDataString();
                if (dataString != null) {
                    results = new Uri[]{Uri.parse(dataString)};
                }
            }
            filePathCallback.onReceiveValue(results);
            filePathCallback = null;
        }
    }
    
    // Handle back button - navigate back in WebView history
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
    
    // Save WebView state
    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        webView.saveState(outState);
    }
    
    // Restore WebView state
    @Override
    protected void onRestoreInstanceState(Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        webView.restoreState(savedInstanceState);
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        webView.onResume();
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        webView.onPause();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (webView != null) {
            webView.destroy();
        }
    }
}
