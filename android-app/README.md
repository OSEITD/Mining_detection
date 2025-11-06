# 📱 Mining Detector - Android App

Native Android WebView wrapper for the Illegal Mining Detection System.

## 🎯 What This Does

This Android app wraps your Streamlit Mining Detection dashboard in a native Android application that:
- ✅ Loads your Streamlit app from your computer
- ✅ Works like a native app (no browser UI)
- ✅ Supports file uploads (for photos)
- ✅ Supports geolocation (for field reports)
- ✅ Pull-to-refresh functionality
- ✅ Back button navigation
- ✅ Offline state preservation

## 📋 Prerequisites

Before building, you need:

### Option 1: Android Studio (Easiest)
1. **Download Android Studio**: https://developer.android.com/studio
2. **Install Android Studio** (default settings are fine)
3. During setup, it will install:
   - Android SDK
   - Android SDK Platform
   - Android Virtual Device (optional)

### Option 2: Command Line Only
1. **Install Java JDK 17 or higher**
   - Download from: https://adoptium.net/
2. **Install Android SDK Command-line Tools**
   - Download from: https://developer.android.com/studio#command-tools

## 🔧 Configuration

### IMPORTANT: Update Your IP Address

Before building, you MUST update the server URL in the code:

1. **Get your computer's IP address:**
   ```powershell
   # On Windows (PowerShell)
   Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}
   
   # Or simple command
   ipconfig
   ```
   
   Look for something like: `192.168.1.XXX` or `169.254.XX.XX`

2. **Edit MainActivity.java:**
   
   Open: `app/src/main/java/com/mining/detector/MainActivity.java`
   
   Find line ~24:
   ```java
   private static final String APP_URL = "http://169.254.49.183:8501";
   ```
   
   Replace with YOUR IP address:
   ```java
   private static final String APP_URL = "http://YOUR_IP_HERE:8501";
   ```

## 🏗️ Building the APK

### Method 1: Using Android Studio (Recommended)

1. **Open the Project:**
   - Launch Android Studio
   - Click "Open an Existing Project"
   - Navigate to: `[Your Project Path]/android-app`
   - Click "OK"

2. **Wait for Gradle Sync:**
   - Android Studio will automatically sync Gradle (first time takes 5-10 minutes)
   - Wait for "Gradle sync finished" message at the bottom

3. **Build APK:**
   - Click **Build** menu → **Build Bundle(s) / APK(s)** → **Build APK(s)**
   - Wait for build to complete (1-3 minutes)
   - Click "locate" in the popup notification

4. **Find Your APK:**
   ```
   android-app/app/build/outputs/apk/debug/app-debug.apk
   ```

### Method 2: Using Command Line

1. **Open PowerShell/Terminal** in the `android-app` folder:
   ```powershell
   cd "c:\Users\oseim\OneDrive\School\Final Year Project\Project\android-app"
   ```

2. **Windows - Build APK:**
   ```powershell
   .\gradlew.bat assembleDebug
   ```

3. **Find Your APK:**
   ```
   android-app\app\build\outputs\apk\debug\app-debug.apk
   ```

### Build Signed APK (For Distribution)

If you want to distribute the app or install on multiple devices:

1. **In Android Studio:**
   - Build → Generate Signed Bundle / APK
   - Select APK → Next
   - Create new keystore (follow prompts)
   - Build release APK

2. **Your signed APK will be at:**
   ```
   android-app/app/build/outputs/apk/release/app-release.apk
   ```

## 📲 Installing on Your Phone

### Method 1: Direct USB Connection

1. **Enable Developer Options on your phone:**
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times
   - Go back → Developer Options
   - Enable "USB Debugging"

2. **Connect phone to computer via USB**

3. **Install APK:**
   ```powershell
   # Navigate to the APK location
   cd "android-app\app\build\outputs\apk\debug"
   
   # Install (if you have adb in PATH)
   adb install app-debug.apk
   ```

4. **From Android Studio:**
   - Connect phone via USB
   - Click Run (▶️) button
   - Select your device
   - App installs automatically

### Method 2: Transfer APK File

1. **Copy APK to your phone:**
   - Connect phone via USB
   - Copy `app-debug.apk` to your phone's Downloads folder
   - Or email it to yourself
   - Or use Google Drive / OneDrive

2. **On your phone:**
   - Open Files / My Files app
   - Navigate to Downloads
   - Tap `app-debug.apk`
   - Allow "Install from unknown sources" if prompted
   - Tap Install
   - Tap Open when done

## 🚀 Using the App

### Before You Start

1. **Start Streamlit on your computer:**
   ```powershell
   streamlit run "app_enhanced.py" --server.address 0.0.0.0 --server.port 8501
   ```

2. **Make sure both devices are on the same WiFi network**

3. **Open the app on your phone**
   - It should connect automatically
   - If you see an error, check:
     - Is Streamlit running?
     - Are both on same WiFi?
     - Is the IP address correct in MainActivity.java?

### Features

- **Pull to Refresh**: Swipe down from the top to reload
- **Back Button**: Navigate back through pages
- **File Upload**: Take photos or select from gallery
- **Geolocation**: Allow location access for field reports
- **Full Screen**: No browser UI clutter

## 🔧 Troubleshooting

### "Connection Error" in the app

**Problem**: App shows connection error
**Solution**:
1. Check Streamlit is running: Open `http://localhost:8501` on your PC
2. Verify IP address in MainActivity.java matches your computer's IP
3. Ensure both devices on same WiFi
4. Windows Firewall: Allow port 8501
   ```powershell
   # Add firewall rule (run as Administrator)
   netsh advfirewall firewall add rule name="Streamlit" dir=in action=allow protocol=TCP localport=8501
   ```

### "Failed to install" on Android

**Problem**: APK won't install
**Solution**:
1. Enable "Install from unknown sources":
   - Settings → Security → Unknown Sources (enable)
   - Or Settings → Apps → Special Access → Install unknown apps
2. Check phone has enough storage (at least 50MB)
3. Try uninstalling old version first

### Build fails with "SDK not found"

**Problem**: Gradle can't find Android SDK
**Solution**:
1. Open Android Studio
2. Tools → SDK Manager
3. Install "Android SDK Build-Tools" and "Android SDK Platform 34"
4. File → Project Structure → SDK Location
5. Note the path and create `local.properties`:
   ```
   sdk.dir=C\:\\Users\\YourName\\AppData\\Local\\Android\\Sdk
   ```

### App is slow or laggy

**Problem**: App feels slower than browser
**Solution**:
1. On Android 10+, this is normal due to WebView restrictions
2. Try enabling hardware acceleration in AndroidManifest.xml (already enabled)
3. Clear app data: Settings → Apps → Mining Detector → Storage → Clear Data

### Location/Camera not working

**Problem**: Camera or GPS features don't work
**Solution**:
1. Check app permissions: Settings → Apps → Mining Detector → Permissions
2. Enable Camera and Location
3. Restart the app

## 📁 Project Structure

```
android-app/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/mining/detector/
│   │       │   └── MainActivity.java          ← Main app code
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   │   └── activity_main.xml      ← UI layout
│   │       │   ├── values/
│   │       │   │   ├── strings.xml
│   │       │   │   ├── colors.xml
│   │       │   │   └── styles.xml
│   │       │   └── mipmap-*/                  ← App icons
│   │       └── AndroidManifest.xml            ← App config & permissions
│   └── build.gradle                           ← App dependencies
├── build.gradle                               ← Project config
├── settings.gradle
└── gradle.properties
```

## 🎨 Customization

### Change App Name
Edit `app/src/main/res/values/strings.xml`:
```xml
<string name="app_name">Your App Name</string>
```

### Change App Icon
Replace icons in:
- `app/src/main/res/mipmap-hdpi/`
- `app/src/main/res/mipmap-mdpi/`
- `app/src/main/res/mipmap-xhdpi/`
- `app/src/main/res/mipmap-xxhdpi/`
- `app/src/main/res/mipmap-xxxhdpi/`

Or use Android Studio: Right-click `res` → New → Image Asset

### Change App Colors
Edit `app/src/main/res/values/colors.xml`:
```xml
<color name="colorPrimary">#YOUR_COLOR</color>
```

### Change Server URL
Edit `MainActivity.java` line ~24:
```java
private static final String APP_URL = "http://YOUR_SERVER:PORT";
```

## 🌐 Remote Access (Optional)

Want to access the app from anywhere, not just local WiFi?

### Using ngrok (Free)

1. **Download ngrok**: https://ngrok.com/download
2. **Run ngrok:**
   ```powershell
   ngrok http 8501
   ```
3. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)
4. **Update MainActivity.java** with this URL
5. **Rebuild APK**

Now your app works from anywhere with internet!

## 📦 App Size

- **APK Size**: ~2-5 MB
- **Installed Size**: ~10-15 MB
- **Minimum Android**: 7.0 (API 24)
- **Target Android**: 14 (API 34)

## 🔐 Security Notes

- This is a **debug APK** - don't distribute publicly
- The app uses HTTP (not HTTPS) - only for local network use
- For production: Use HTTPS, signed APK, and proper authentication
- The cleartext traffic is allowed in AndroidManifest for local development

## 📝 License

This Android wrapper is part of your Final Year Project.

## 🆘 Need Help?

1. **Check Streamlit is running**: Open `http://localhost:8501` on your PC
2. **Verify IP address**: Make sure it's correct in MainActivity.java
3. **Check WiFi**: Both devices must be on same network
4. **Firewall**: Allow port 8501 through Windows Firewall
5. **Logs**: Use Android Studio Logcat to see error messages

## 🎯 Next Steps

1. ✅ Build the APK
2. ✅ Install on your phone
3. ✅ Test all features
4. ✅ Show to your supervisor
5. ✅ Include in your project documentation

Good luck with your Final Year Project! 🚀
