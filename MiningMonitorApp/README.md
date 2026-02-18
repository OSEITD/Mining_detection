# Chingola Mining Monitor - React Native Mobile App

🌍 **AI-Powered Illegal Mining Detection System for Chingola District, Zambia**

A professional mobile application built with React Native for detecting and monitoring illegal mining activities using deep learning and satellite imagery.

## Features

✅ **Dashboard** - Real-time statistics and mining site overview
✅ **Interactive Map** - Google Maps integration with mining site markers
✅ **AI Detection** - U-Net model performance metrics and insights
✅ **Analytics** - Charts and visualizations of mining data
✅ **Field Reporting** - GPS-enabled reporting with camera integration
✅ **Offline Support** - Works without internet connection
✅ **Native Performance** - Fast, smooth mobile experience

## Tech Stack

- **Frontend**: React Native 0.73, TypeScript
- **Navigation**: React Navigation
- **Maps**: React Native Maps (Google Maps)
- **Charts**: React Native Chart Kit
- **Backend**: FastAPI (Python)
- **AI Model**: PyTorch U-Net
- **Data**: GeoJSON, PostGIS

## Prerequisites

### For Development:
- Node.js 18+ 
- React Native CLI
- Android Studio (for Android)
- Xcode (for iOS, Mac only)
- Python 3.9+

### For Python Backend:
```bash
pip install fastapi uvicorn geopandas pandas
```

## Installation

### 1. Install Node Dependencies

```bash
cd MiningMonitorApp
npm install
```

### 2. Install iOS Pods (Mac only)

```bash
cd ios
pod install
cd ..
```

### 3. Start Python API Server

```bash
# In the Project root directory
python api_server.py
```

The API will be available at `http://localhost:5000`

**Important**: Update the API URL in `src/services/api.ts`:
```typescript
const API_BASE_URL = 'http://YOUR_IP_ADDRESS:5000/api';
```

Find your IP address:
- Windows: `ipconfig`
- Mac/Linux: `ifconfig`

### 4. Run the Mobile App

#### Android:
```bash
npm run android
```

#### iOS (Mac only):
```bash
npm run ios
```

## Building APK for Android

### Debug APK:
```bash
cd android
./gradlew assembleDebug
```

APK location: `android/app/build/outputs/apk/debug/app-debug.apk`

### Release APK:

1. Generate signing key:
```bash
keytool -genkeypair -v -storetype PKCS12 -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

2. Edit `android/gradle.properties`:
```properties
MYAPP_RELEASE_STORE_FILE=my-release-key.keystore
MYAPP_RELEASE_KEY_ALIAS=my-key-alias
MYAPP_RELEASE_STORE_PASSWORD=YOUR_PASSWORD
MYAPP_RELEASE_KEY_PASSWORD=YOUR_PASSWORD
```

3. Build release APK:
```bash
cd android
./gradlew assembleRelease
```

APK location: `android/app/build/outputs/apk/release/app-release.apk`

## Project Structure

```
MiningMonitorApp/
├── src/
│   ├── screens/           # App screens
│   │   ├── DashboardScreen.tsx
│   │   ├── MapScreen.tsx
│   │   ├── AIDetectionScreen.tsx
│   │   ├── AnalyticsScreen.tsx
│   │   └── ReportScreen.tsx
│   └── services/
│       └── api.ts         # API client
├── android/               # Android native code
├── ios/                   # iOS native code
├── App.tsx               # Main app component
└── package.json          # Dependencies

```

## API Endpoints

### Get Mining Sites
```
GET /api/mining-sites
Returns: List of all mining sites with coordinates
```

### Get Statistics
```
GET /api/stats
Returns: Mining statistics (total sites, active, abandoned, etc.)
```

### Submit Field Report
```
POST /api/field-reports
Body: {location, coordinates, description, photo, timestamp}
```

## Testing on Physical Device

### Android:
1. Enable Developer Options on your phone
2. Enable USB Debugging
3. Connect phone via USB
4. Run: `adb devices` to verify connection
5. Run: `npm run android`

### iOS:
1. Open `ios/ChingolaMiningMonitor.xcworkspace` in Xcode
2. Select your device
3. Click Run

## Permissions Required

### Android (`android/app/src/main/AndroidManifest.xml`):
- `ACCESS_FINE_LOCATION` - GPS coordinates
- `CAMERA` - Photo capture
- `READ_EXTERNAL_STORAGE` - Photo library
- `INTERNET` - API communication

### iOS (`ios/ChingolaMiningMonitor/Info.plist`):
- `NSLocationWhenInUseUsageDescription` - GPS
- `NSCameraUsageDescription` - Camera
- `NSPhotoLibraryUsageDescription` - Photo library

## Troubleshooting

### Metro Bundler Issues:
```bash
npm start -- --reset-cache
```

### Android Build Errors:
```bash
cd android
./gradlew clean
cd ..
npm run android
```

### Can't Connect to API:
1. Ensure API server is running (`python api_server.py`)
2. Check IP address in `src/services/api.ts`
3. Make sure phone and computer are on same WiFi
4. Disable firewall temporarily for testing

## Deployment

### Google Play Store:
1. Build release APK (see above)
2. Create Google Play Developer account ($25 one-time fee)
3. Upload APK to Play Console
4. Fill in app details, screenshots
5. Submit for review

### Apple App Store:
1. Enroll in Apple Developer Program ($99/year)
2. Archive app in Xcode
3. Submit to App Store Connect
4. Fill in app details
5. Submit for review

## Future Enhancements

- [ ] Push notifications for new detections
- [ ] Offline map caching
- [ ] AR visualization of mining sites
- [ ] ML model training from field reports
- [ ] Multi-language support (Bemba, Nyanja)
- [ ] Dark mode theme

## Author

Owen Mupeta - Final Year Project 2025
University of Zambia

## License

MIT License - This project is for educational purposes.

## Support

For issues or questions, create an issue on GitHub or contact the author.
