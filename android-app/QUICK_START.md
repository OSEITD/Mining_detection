# 🚀 Quick Start - Build Your Android App in 5 Minutes

## Step 1: Update IP Address (REQUIRED)

1. **Get your computer's IP:**
   ```powershell
   ipconfig
   ```
   Look for: `IPv4 Address. . . . . . . . . . . : 192.168.X.X`

2. **Edit this file:**
   ```
   android-app\app\src\main\java\com\mining\detector\MainActivity.java
   ```

3. **Change line 24:**
   ```java
   private static final String APP_URL = "http://YOUR_IP_HERE:8501";
   ```

## Step 2: Build APK

### Option A: Have Android Studio?
1. Open Android Studio
2. Open project: `android-app` folder
3. Wait for Gradle sync (5-10 min first time)
4. Build → Build Bundle(s) / APK(s) → Build APK(s)
5. Find APK at: `app\build\outputs\apk\debug\app-debug.apk`

### Option B: Command Line
```powershell
cd android-app
.\gradlew.bat assembleDebug
```
APK will be at: `app\build\outputs\apk\debug\app-debug.apk`

## Step 3: Install on Phone

1. **Copy `app-debug.apk` to your phone**
   - USB cable → Copy to Downloads folder
   - Or email it to yourself

2. **On your phone:**
   - Open the APK file
   - Allow "Install unknown apps" if asked
   - Tap Install

## Step 4: Run

1. **Start Streamlit on your PC:**
   ```powershell
   streamlit run app_enhanced.py --server.address 0.0.0.0 --server.port 8501
   ```

2. **Open the app on your phone**
   - Make sure both are on same WiFi
   - The app should connect automatically!

## ⚠️ Common Issues

**"Connection Error"?**
- Check Streamlit is running on PC
- Check IP address is correct in MainActivity.java
- Make sure both on same WiFi
- Add firewall rule:
  ```powershell
  netsh advfirewall firewall add rule name="Streamlit" dir=in action=allow protocol=TCP localport=8501
  ```

**"Can't install"?**
- Settings → Security → Allow install from unknown sources
- Need at least 50MB free space

**"Build failed"?**
- Install Android Studio first
- Or install JDK 17+ for command line build

---

That's it! 🎉 You now have a native Android app for your Mining Detection System!
