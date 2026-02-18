# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to flags specified
# in [sdk]/tools/proguard/proguard-android.txt

# Keep WebView JavaScript interface
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# Keep WebView
-keepclassmembers class android.webkit.WebView {
    public *;
}

# Keep attributes
-keepattributes *Annotation*
-keepattributes Signature
-keepattributes Exceptions

# Don't warn about missing classes
-dontwarn android.webkit.**
