@echo off
REM ========================================
REM Mining Detector - Android APK Builder
REM Quick build script for Windows
REM ========================================

echo.
echo ============================================
echo Mining Detector - Android APK Builder
echo ============================================
echo.

REM Check if we're in the right directory
if not exist "app\build.gradle" (
    echo ERROR: Please run this script from the android-app directory
    echo.
    echo Current directory: %CD%
    echo Expected: [Your path]\android-app
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking Gradle wrapper...
if not exist "gradlew.bat" (
    echo ERROR: gradlew.bat not found
    echo Please ensure you have the complete android-app folder
    pause
    exit /b 1
)
echo ✓ Gradle wrapper found

echo.
echo [2/4] Cleaning previous builds...
call gradlew.bat clean >nul 2>&1
echo ✓ Clean complete

echo.
echo [3/4] Building APK (this may take 1-3 minutes)...
echo Please wait...
call gradlew.bat assembleDebug

if errorlevel 1 (
    echo.
    echo ❌ BUILD FAILED
    echo.
    echo Common issues:
    echo - Java JDK not installed (need JDK 17+)
    echo - Android SDK not found
    echo - Internet connection required for first build
    echo.
    echo Try opening the project in Android Studio instead
    pause
    exit /b 1
)

echo.
echo ============================================
echo ✅ BUILD SUCCESSFUL!
echo ============================================
echo.
echo [4/4] Locating APK...
echo.

set APK_PATH=app\build\outputs\apk\debug\app-debug.apk

if exist "%APK_PATH%" (
    echo ✓ APK created successfully!
    echo.
    echo 📍 Location: %CD%\%APK_PATH%
    echo 📏 Size: 
    for %%A in ("%APK_PATH%") do echo    %%~zA bytes
    echo.
    echo ============================================
    echo Next Steps:
    echo ============================================
    echo 1. Transfer app-debug.apk to your Android phone
    echo 2. On your phone, tap the APK file to install
    echo 3. Allow "Install from unknown sources" if asked
    echo 4. Start Streamlit on your PC:
    echo    streamlit run app_enhanced.py --server.address 0.0.0.0
    echo 5. Open the Mining Detector app on your phone
    echo.
    echo ⚠️  REMINDER: Update IP address in MainActivity.java
    echo    Current IP in code: 169.254.49.183
    echo    Your computer's IP: Run 'ipconfig' to check
    echo.
    
    REM Ask if user wants to open the APK folder
    choice /C YN /M "Open APK folder now"
    if errorlevel 2 goto :end
    if errorlevel 1 explorer "app\build\outputs\apk\debug"
) else (
    echo ❌ APK not found at expected location
    echo Expected: %APK_PATH%
    echo.
    echo Check build output above for errors
)

:end
echo.
echo Press any key to exit...
pause >nul
