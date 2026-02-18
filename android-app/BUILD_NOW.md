# 🚀 Build Your Android App - Step by Step

## ✅ Good News!
- ✓ Java 22 installed
- ✓ Android SDK installed
- ✓ IP address updated (192.168.1.172)

## 📱 Building the APK - Choose Your Method

---

## METHOD 1: Android Studio (RECOMMENDED - Easiest!)

### Step 1: Open Android Studio
1. Launch **Android Studio**
2. If you see "Welcome to Android Studio" screen:
   - Click **"Open"**
3. Navigate to:
   ```
   c:\Users\oseim\OneDrive\School\Final Year Project\Project\android-app
   ```
4. Click **"OK"**

### Step 2: Wait for Gradle Sync
- Android Studio will automatically sync the project
- You'll see a progress bar at the bottom: "Gradle sync..."
- **First time takes 5-10 minutes** (downloads dependencies)
- Wait until you see: "✓ Gradle sync finished"

### Step 3: Build the APK
1. Click **Build** menu (top menu bar)
2. Select **Build Bundle(s) / APK(s)**
3. Click **Build APK(s)**
4. Wait 1-3 minutes
5. You'll see a notification: "✓ APK(s) generated successfully"
6. Click **"locate"** in the notification

### Step 4: Find Your APK
Your APK is here:
```
c:\Users\oseim\OneDrive\School\Final Year Project\Project\android-app\app\build\outputs\apk\debug\app-debug.apk
```

Size: ~2-5 MB
Name: **app-debug.apk**

---

## METHOD 2: Command Line (If you prefer terminal)

If Android Studio doesn't work or you prefer command line:

### Step 1: Download Gradle Wrapper
```powershell
# In PowerShell, run:
cd "c:\Users\oseim\OneDrive\School\Final Year Project\Project\android-app"

# Download Gradle wrapper jar (required)
mkdir gradle\wrapper -Force
Invoke-WebRequest -Uri "https://github.com/gradle/gradle/raw/master/gradle/wrapper/gradle-wrapper.jar" -OutFile "gradle\wrapper\gradle-wrapper.jar"
```

### Step 2: Build
```powershell
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
.\gradlew.bat assembleDebug
```

---

## 📲 NEXT: Install on Your Phone

Once you have **app-debug.apk**, follow these steps:

### Option A: USB Cable (Fastest)
1. **Connect phone to PC** with USB cable
2. **On your phone:**
   - Notification: "USB charging" → Tap it
   - Select: **"File transfer"**
3. **On your PC:**
   - Open File Explorer
   - Go to: This PC → [Your Phone] → Internal Storage → Download
   - **Copy app-debug.apk** to the Download folder

### Option B: Email
1. Email **app-debug.apk** to yourself
2. Open email on your phone
3. Download the attachment

### Option C: Cloud Storage
1. Upload **app-debug.apk** to Google Drive / OneDrive
2. Download it on your phone

---

## 📥 Installing on Android

### Step 1: Find the APK
1. Open **Files** or **My Files** app on your phone
2. Go to **Downloads** folder
3. Tap **app-debug.apk**

### Step 2: Allow Installation (First time only)
If you see "Can't install apps from this source":
1. Tap **Settings**
2. Toggle **"Allow from this source"** ON
3. Go back and tap app-debug.apk again

### Step 3: Install
1. Tap **"Install"**
2. Wait 5-10 seconds
3. Tap **"Open"**

---

## 🎉 Using the App

### Step 1: Keep Streamlit Running on PC
The app needs your PC to be running Streamlit:
```powershell
# Make sure this is still running:
streamlit run app_enhanced.py --server.address 0.0.0.0 --server.port 8501
```

### Step 2: Connect to Same WiFi
- PC: Connected to WiFi
- Phone: Connected to **SAME WiFi network**

### Step 3: Open App
1. Tap the **Mining Detector** app icon on your phone
2. It will connect to: `http://192.168.1.172:8501`
3. You should see the login screen!

---

## ⚠️ Troubleshooting

### "Connection Error" in app
**Fix:**
- Check PC is running Streamlit (see Step 1 above)
- Check both on same WiFi
- Check Windows Firewall:
  ```powershell
  netsh advfirewall firewall add rule name="Streamlit" dir=in action=allow protocol=TCP localport=8501
  ```

### Can't install APK on phone
**Fix:**
- Settings → Security → Unknown Sources (enable)
- OR Settings → Apps → Special Access → Install unknown apps → Files (allow)

### Build failed in Android Studio
**Fix:**
- Tools → SDK Manager
- Install "Android SDK Build-Tools 34"
- Install "Android SDK Platform 34"
- File → Sync Project with Gradle Files

---

## 🎯 Summary

**What you need to do:**
1. ✅ Open Android Studio
2. ✅ Open the android-app folder
3. ✅ Wait for Gradle sync
4. ✅ Build → Build APK(s)
5. ✅ Transfer app-debug.apk to phone
6. ✅ Install on phone
7. ✅ Run Streamlit on PC
8. ✅ Open app on phone

**Total Time:** 15-20 minutes (including first Gradle sync)

---

## 📍 Current Status

✅ Java installed (version 22)
✅ Android SDK installed
✅ IP address configured (192.168.1.172)
✅ Project files ready
✅ Streamlit server running

**Next:** Open Android Studio and build the APK!

Good luck! 🚀📱
