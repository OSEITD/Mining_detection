# 📱 Mobile App Development Guide
# Illegal Mining Detection App - Android/iOS

## 🎯 App Overview

**App Name:** Chingola Mining Monitor  
**Platform:** Android & iOS (Flutter)  
**Purpose:** Real-time illegal mining detection and reporting  
**Target Users:** Field inspectors, government officials, researchers  

---

## 🏗️ App Architecture

```
┌─────────────────────────────────────────┐
│          PRESENTATION LAYER              │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │   Map    │  │Analytics│  │Reports ││
│  │  Screen  │  │ Screen  │  │ Screen ││
│  └──────────┘  └──────────┘  └────────┘│
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│           BUSINESS LOGIC LAYER           │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │  Mining  │  │   AI     │  │  Auth  ││
│  │ Service  │  │ Service  │  │Service ││
│  └──────────┘  └──────────┘  └────────┘│
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│             DATA LAYER                   │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │Firebase  │  │  Local   │  │  API   ││
│  │  Cloud   │  │ Storage  │  │Gateway ││
│  └──────────┘  └──────────┘  └────────┘│
└─────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
chingola_mining_app/
├── android/                    # Android native code
├── ios/                        # iOS native code
├── lib/
│   ├── main.dart              # App entry point
│   ├── core/
│   │   ├── constants.dart     # App constants
│   │   ├── theme.dart         # App theme
│   │   └── routes.dart        # Navigation routes
│   ├── data/
│   │   ├── models/
│   │   │   ├── mine_model.dart
│   │   │   ├── detection_model.dart
│   │   │   └── user_model.dart
│   │   ├── repositories/
│   │   │   ├── mining_repository.dart
│   │   │   └── auth_repository.dart
│   │   └── services/
│   │       ├── firebase_service.dart
│   │       ├── geolocation_service.dart
│   │       └── map_service.dart
│   ├── presentation/
│   │   ├── screens/
│   │   │   ├── splash_screen.dart
│   │   │   ├── login_screen.dart
│   │   │   ├── map_screen.dart
│   │   │   ├── analytics_screen.dart
│   │   │   ├── report_screen.dart
│   │   │   └── settings_screen.dart
│   │   ├── widgets/
│   │   │   ├── mine_marker.dart
│   │   │   ├── info_popup.dart
│   │   │   ├── map_controls.dart
│   │   │   └── legend_card.dart
│   │   └── providers/
│   │       ├── mining_provider.dart
│   │       └── auth_provider.dart
│   └── utils/
│       ├── helpers.dart
│       └── validators.dart
├── assets/
│   ├── images/
│   ├── icons/
│   └── geojson/
│       ├── chingola_mines.geojson
│       └── ai_predictions.geojson
├── test/                       # Unit tests
├── pubspec.yaml               # Dependencies
└── README.md
```

---

## 📦 Required Dependencies (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  provider: ^6.0.0
  
  # Firebase
  firebase_core: ^2.15.0
  firebase_auth: ^4.7.0
  firebase_storage: ^11.2.0
  cloud_firestore: ^4.8.0
  firebase_messaging: ^14.6.0
  
  # Maps
  google_maps_flutter: ^2.5.0
  geolocator: ^9.0.0
  geocoding: ^2.1.0
  
  # GeoJSON
  latlong2: ^0.9.0
  
  # UI
  flutter_svg: ^2.0.0
  cached_network_image: ^3.2.0
  shimmer: ^3.0.0
  
  # Charts
  fl_chart: ^0.63.0
  
  # Image
  image_picker: ^1.0.0
  
  # HTTP
  dio: ^5.3.0
  
  # Local Storage
  shared_preferences: ^2.2.0
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  
  # Utils
  intl: ^0.18.0
  path_provider: ^2.1.0
```

---

## 🎨 Key Screens Design

### 1. **Splash Screen**
```dart
// Show app logo + "Loading mining data..."
// Auto-navigate to Login or Map (if logged in)
```

### 2. **Login/Register Screen**
```dart
// Firebase Authentication
// Email/Password or Google Sign-In
// Role selection: Inspector / Admin / Viewer
```

### 3. **Map Screen** (Main)
```dart
// Google Maps with custom markers
// Toggle layers: Manual / AI / NDVI
// Floating Action Buttons:
//   - My Location
//   - Report New Mine
//   - Filter by Status
//   - Legend
// Bottom Sheet: Mine details on tap
```

### 4. **Analytics Screen**
```dart
// Charts showing:
//   - Mining area over time
//   - Status distribution
//   - AI confidence levels
// Key metrics cards
```

### 5. **Report Screen**
```dart
// Form with:
//   - Auto GPS location
//   - Photo upload
//   - Mine details
//   - Submit button
// Shows submission history
```

### 6. **Settings Screen**
```dart
// User profile
// Sync settings
// Notification preferences
// App version & about
```

---

## 🗺️ Map Integration

### Google Maps Setup

```dart
// lib/presentation/screens/map_screen.dart

import 'package:google_maps_flutter/google_maps_flutter.dart';

class MapScreen extends StatefulWidget {
  @override
  _MapScreenState createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  GoogleMapController? _controller;
  Set<Marker> _markers = {};
  Set<Polygon> _polygons = {};
  
  static final CameraPosition _chingola = CameraPosition(
    target: LatLng(-12.5, 27.85),
    zoom: 11,
  );
  
  @override
  void initState() {
    super.initState();
    _loadMiningData();
  }
  
  void _loadMiningData() async {
    // Load GeoJSON from assets
    String geojson = await rootBundle.loadString('assets/geojson/chingola_mines.geojson');
    // Parse and create polygons
    // Add to _polygons set
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          GoogleMap(
            initialCameraPosition: _chingola,
            markers: _markers,
            polygons: _polygons,
            onMapCreated: (controller) => _controller = controller,
            onTap: _onMapTap,
          ),
          _buildLayerControls(),
          _buildLegend(),
        ],
      ),
      floatingActionButton: _buildFABs(),
    );
  }
  
  Widget _buildLayerControls() {
    return Positioned(
      top: 100,
      right: 16,
      child: Column(
        children: [
          FloatingActionButton(
            mini: true,
            child: Icon(Icons.layers),
            onPressed: _showLayerOptions,
          ),
          SizedBox(height: 8),
          FloatingActionButton(
            mini: true,
            child: Icon(Icons.my_location),
            onPressed: _goToCurrentLocation,
          ),
        ],
      ),
    );
  }
}
```

---

## 🔥 Firebase Integration

### 1. **Authentication**
```dart
// lib/data/services/firebase_service.dart

class FirebaseAuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  
  Future<User?> signIn(String email, String password) async {
    try {
      UserCredential result = await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      return result.user;
    } catch (e) {
      print(e);
      return null;
    }
  }
  
  Future<void> signOut() async {
    await _auth.signOut();
  }
}
```

### 2. **Cloud Firestore**
```dart
class MiningDataService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  
  Future<List<Mine>> getActiveMines() async {
    QuerySnapshot snapshot = await _firestore
        .collection('mines')
        .where('status', isEqualTo: 'active')
        .get();
    
    return snapshot.docs.map((doc) => Mine.fromFirestore(doc)).toList();
  }
  
  Future<void> reportNewMine(Mine mine) async {
    await _firestore.collection('mines').add(mine.toJson());
  }
}
```

### 3. **Push Notifications**
```dart
class NotificationService {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  
  Future<void> initialize() async {
    await _messaging.requestPermission();
    
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      // Show local notification
      _showNotification(message);
    });
  }
}
```

---

## 📊 Data Models

```dart
// lib/data/models/mine_model.dart

class Mine {
  final String id;
  final String name;
  final double latitude;
  final double longitude;
  final double area;
  final String status; // active, suspected, closed
  final DateTime detectedDate;
  final String? photoUrl;
  final double? confidence; // AI confidence (0-1)
  
  Mine({
    required this.id,
    required this.name,
    required this.latitude,
    required this.longitude,
    required this.area,
    required this.status,
    required this.detectedDate,
    this.photoUrl,
    this.confidence,
  });
  
  factory Mine.fromJson(Map<String, dynamic> json) {
    return Mine(
      id: json['id'],
      name: json['name'],
      latitude: json['latitude'],
      longitude: json['longitude'],
      area: json['area'],
      status: json['status'],
      detectedDate: DateTime.parse(json['detectedDate']),
      photoUrl: json['photoUrl'],
      confidence: json['confidence'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'latitude': latitude,
      'longitude': longitude,
      'area': area,
      'status': status,
      'detectedDate': detectedDate.toIso8601String(),
      'photoUrl': photoUrl,
      'confidence': confidence,
    };
  }
}
```

---

## 🎨 UI Theme

```dart
// lib/core/theme.dart

class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      primaryColor: Color(0xFF667eea),
      colorScheme: ColorScheme.light(
        primary: Color(0xFF667eea),
        secondary: Color(0xFF764ba2),
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        backgroundColor: Color(0xFF667eea),
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: Color(0xFF667eea),
      ),
    );
  }
}
```

---

## 🚀 Build & Deploy

### Android
```bash
# Debug build
flutter build apk --debug

# Release build
flutter build apk --release

# Output: build/app/outputs/flutter-apk/app-release.apk
```

### iOS
```bash
flutter build ios --release
```

### Play Store Deployment
1. Create signed APK/AAB
2. Upload to Google Play Console
3. Fill store listing
4. Submit for review

---

## 📱 Features Implementation Priority

### Phase 1 (MVP - 2 weeks)
- ✅ Login/Register with Firebase
- ✅ Map view with manual mining labels
- ✅ Mine info popup on tap
- ✅ Basic legend and controls

### Phase 2 (Core - 2 weeks)
- ✅ AI predictions layer toggle
- ✅ Report new mine form
- ✅ Photo upload to Firebase Storage
- ✅ Push notifications setup

### Phase 3 (Advanced - 2 weeks)
- ✅ NDVI visualization layer
- ✅ Analytics dashboard
- ✅ Offline mode with local storage
- ✅ Change detection visualization

### Phase 4 (Polish - 1 week)
- ✅ App icon & splash screen
- ✅ Loading animations
- ✅ Error handling
- ✅ Performance optimization

---

## 🧪 Testing Checklist

- [ ] Login/Logout flow
- [ ] Map loads correctly
- [ ] Polygons display with correct colors
- [ ] Tap on polygon shows info
- [ ] Layer toggles work
- [ ] GPS location accuracy
- [ ] Photo capture & upload
- [ ] Offline data persistence
- [ ] Push notifications received
- [ ] App doesn't crash on poor network

---

## 📝 Presentation Demo Script

**Minute 1:** Splash → Login
- "Welcome to Chingola Mining Monitor"

**Minute 2:** Map View
- "This is the interactive map showing all mining areas"
- Toggle layers: Manual → AI → NDVI

**Minute 3:** Tap on Polygon
- "Here we can see mine details"
- Show: Name, Status, Area, Confidence

**Minute 4:** Report Feature
- "Inspectors can report new mining"
- Capture GPS, photo, details

**Minute 5:** Analytics
- "Dashboard shows trends and statistics"
- Charts, metrics, change detection

---

## 💡 Advanced Features (Future)

- [ ] Machine learning on-device (TensorFlow Lite)
- [ ] AR view for field verification
- [ ] Route planning for inspections
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Export reports as PDF
- [ ] Integration with government databases
- [ ] Real-time collaboration

---

## 📞 Support Resources

- **Flutter Docs:** https://flutter.dev/docs
- **Firebase Docs:** https://firebase.google.com/docs
- **Google Maps Flutter:** https://pub.dev/packages/google_maps_flutter
- **GeoJSON Parser:** https://pub.dev/packages/geojson

---

**You now have a complete blueprint to build a professional mobile app!** 📱🚀
