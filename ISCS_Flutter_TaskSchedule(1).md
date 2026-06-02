# ISCS Flutter Mobile App — Complete Task Schedule
**Author:** Raghad Shatnawi  
**Last Modified:** May 2026  
**Purpose:** Full remaining work breakdown for the Flutter mobile application.  
Each task includes what to build, critical notes, a ready-to-use AI prompt, and a Git commit instruction.

---

## How to use this file

- Tasks are ordered by dependency. Do not skip phases.
- Every AI prompt assumes the AI has access to the project codebase. Paste the relevant existing files alongside the prompt.
- "Paste alongside" means: copy the file content into the chat before or after the prompt.
- Commit after every task — not after every phase. Small commits make bugs easier to isolate.
- Mark tasks done as you go.

---

## PHASE 0 — Package Setup

### Task 0.1 — Add all required packages to pubspec.yaml

**What to build:**  
Add every package the app will need across all phases. Do this once now to avoid repeated `flutter pub get` cycles mid-development.

**Packages to add:**
- `firebase_core` — Firebase initialization
- `firebase_auth` — Authentication
- `cloud_firestore` — optional, only if Flutter reads Firestore directly (not needed if all data goes through FastAPI)
- `google_maps_flutter` — interactive map
- `geolocator` — device GPS location
- `permission_handler` — runtime permissions (location, notifications)
- `get` — GetX state management + routing
- `flutter_local_notifications` — in-app notification banners
- `firebase_messaging` — push notifications (FCM)
- `http` — already in use via THttpHelper, verify it is declared

**Critical notes:**
- `get_storage` is already in use (storage_utility.dart). Do not add it again.
- `flutter_native_splash` is already in use (main.dart). Do not add it again.
- `google_maps_flutter` requires a Google Maps API key. Add it to `android/app/src/main/AndroidManifest.xml` and `ios/Runner/AppDelegate.swift`. Enable Maps SDK for Android and Maps SDK for iOS in Google Cloud Console.
- `geolocator` requires `ACCESS_FINE_LOCATION` and `ACCESS_COARSE_LOCATION` in `AndroidManifest.xml` and `NSLocationWhenInUseUsageDescription` in `ios/Runner/Info.plist`.
- `firebase_messaging` requires `google-services.json` in `android/app/` and `GoogleService-Info.plist` in `ios/Runner/`.

**AI prompt:**

```
I am working on an ISCS Flutter project. I need you to update pubspec.yaml to add the following packages at their latest stable versions:
- firebase_core
- firebase_auth
- google_maps_flutter
- geolocator
- permission_handler
- get (GetX)
- flutter_local_notifications
- firebase_messaging

Do not remove any existing packages. The following are already declared and must stay:
- flutter_native_splash
- get_storage
- http

Return the full updated dependencies and dev_dependencies sections only. Do not return the entire pubspec.yaml.
```

**Estimated time:** 1 hour (setup + key configuration)

**Git commit:**
```
git add pubspec.yaml android/app/src/main/AndroidManifest.xml ios/Runner/Info.plist
git commit -m "chore(mobile): add all required packages and platform permissions to pubspec"
```

---

## PHASE 1 — Firebase Auth Integration (BLOCKER — do this first)

### Task 1.1 — Firebase initialization in main.dart

**What to build:**  
Initialize `firebase_core` before `runApp()`. The splash screen must stay visible until initialization completes. `FlutterNativeSplash.remove()` must only be called after Firebase is ready and auth state is determined.

**Critical notes:**
- Current `main.dart` calls `FlutterNativeSplash.preserve()` but never calls `remove()`. The splash never disappears. The remove call belongs in the AuthGate after auth state resolves.
- `Firebase.initializeApp()` is async — `main()` must be `async`.
- Use `DefaultFirebaseOptions.currentPlatform` from the generated `firebase_options.dart` (produced by `flutterfire configure`).
- Replace the `home:` field in MaterialApp with `home: const AuthGate()`.

**Paste alongside prompt:** `lib/main.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is the current main.dart: [paste file]

Rewrite main.dart to:
1. Make main() async
2. Call WidgetsFlutterBinding.ensureInitialized() first
3. Call FlutterNativeSplash.preserve() immediately after
4. Call await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform)
5. Run the app — do NOT call FlutterNativeSplash.remove() here
6. Replace home: with home: const AuthGate()
7. Import: firebase_core, firebase_options, flutter_native_splash, AuthGate from lib/features/auth/screens/auth_gate.dart

Keep all existing theme setup unchanged.
File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/main.dart lib/firebase_options.dart
git commit -m "feat(mobile): initialize Firebase in main.dart before runApp"
```

---

### Task 1.2 — AuthService

**What to build:**  
`lib/services/auth_service.dart` — a singleton service class wrapping Firebase Auth. All screens and controllers interact with Firebase Auth only through this class.

**Methods:**
- `signIn(email, password)` → `UserCredential` or throws
- `signOut()` → void
- `getIdToken()` → `String` (current user's Firebase ID token)
- `currentUser` → `User?`
- `authStateChanges` → `Stream<User?>`

**Critical notes:**
- Error handling: catch `FirebaseAuthException` and rethrow as readable strings (e.g. `'wrong-password'` → `'Incorrect password. Please try again.'`).
- Use the same singleton pattern as `TLocalStorage` — private constructor + static instance.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/services/auth_service.dart.

Singleton service class named AuthService wrapping Firebase Auth. Expose:
- Future<UserCredential> signIn(String email, String password)
- Future<void> signOut()
- Future<String> getIdToken() — throws readable exception if no user logged in
- User? get currentUser
- Stream<User?> get authStateChanges

Catch FirebaseAuthException and rethrow with human-readable messages.
Use private constructor + static instance singleton pattern.
File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/services/auth_service.dart
git commit -m "feat(mobile): add AuthService singleton wrapping Firebase Auth"
```

---

### Task 1.3 — Token injection in THttpHelper

**What to build:**  
Modify `lib/utils/http/http_client.dart` to attach the Firebase ID token as `Authorization: Bearer <token>` to every request. This is the single highest-priority fix — every backend call returns HTTP 401 without it.

**Critical notes:**
- Backend `core/auth.py` expects exactly: `Authorization: Bearer <Firebase ID token>`.
- If `getIdToken()` throws (no logged-in user), the request must not proceed — propagate the exception.
- All four methods (GET, POST, PUT, DELETE) must be updated.

**Paste alongside prompt:** `lib/utils/http/http_client.dart`, `lib/services/auth_service.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is http_client.dart: [paste file]. Here is AuthService: [paste file].

Modify THttpHelper so every request attaches the Firebase ID token:
1. Add private static method _buildHeaders() that calls await AuthService().getIdToken() and returns Map<String, String> with 'Authorization': 'Bearer <token>' and 'Content-Type': 'application/json'
2. Update all GET, POST, PUT, DELETE methods to await _buildHeaders() and pass as headers
3. If getIdToken() throws, let it propagate — do not swallow it
4. Keep all existing error handling

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/utils/http/http_client.dart
git commit -m "fix(mobile): inject Firebase ID token into all THttpHelper request headers"
```

---

### Task 1.4 — AuthGate widget

**What to build:**  
`lib/features/auth/screens/auth_gate.dart` — listens to `authStateChanges` and routes to `LoginScreen` or `HomeScreen`. This is what `main.dart` uses as `home:`.

**Critical notes:**
- While auth state is loading: show `CircularProgressIndicator` — NOT a blank screen.
- Call `FlutterNativeSplash.remove()` exactly once on first stream emission.
- `user == null` → `LoginScreen`. `user != null` → `HomeScreen`.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/auth/screens/auth_gate.dart.

StatelessWidget named AuthGate:
1. Uses StreamBuilder on AuthService().authStateChanges
2. While waiting: shows centered CircularProgressIndicator
3. Calls FlutterNativeSplash.remove() exactly once after first emission (use a static bool flag)
4. user == null → returns LoginScreen()
5. user != null → returns HomeScreen()

Import AuthService from lib/services/auth_service.dart.
File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/auth/screens/auth_gate.dart
git commit -m "feat(mobile): add AuthGate for auth state routing and splash screen dismissal"
```

---

### Task 1.5 — Connect Login screen to AuthService

**What to build:**  
Create `lib/features/auth/controllers/auth_controller.dart` and wire the existing login screen UI to it.

**Critical notes:**
- Do not redesign the login screen. Only add controller wiring.
- On success: `Get.offAll(() => HomeScreen())` to clear navigation stack.
- On failure: show error from `AuthService` in a `SnackBar` or error text.
- Trim whitespace from email before passing to `signIn()`.

**Paste alongside prompt:** Dana's login screen dart file

**AI prompt:**

```
I am working on the ISCS Flutter project. The login screen UI is already built: [paste Dana's login screen].

1. Create lib/features/auth/controllers/auth_controller.dart — GetX controller with:
   - RxBool isLoading = false.obs
   - RxString errorMessage = ''.obs
   - Future<void> signIn(String email, String password) — calls AuthService().signIn(), sets isLoading, on success Get.offAll(() => HomeScreen()), on error sets errorMessage

2. In the existing login screen, add:
   - Get.put(AuthController()) at screen level
   - Obx() wrapping submit button to show CircularProgressIndicator when isLoading is true
   - Show errorMessage below form if not empty
   - Button onTap calls controller.signIn(email.trim(), password)

Do not change any UI styling or layout.
File header for controller: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/auth/controllers/auth_controller.dart lib/features/auth/screens/login_screen.dart
git commit -m "feat(mobile): wire login screen to AuthController with loading and error states"
```

---

## PHASE 2 — Data Models

### Task 2.1 — Signal model

**What to build:** `lib/models/signal_model.dart`

**Backend schema:**
```json
{ "event_id": "", "rsu_id": "", "segment": "", "timestamp": "", "speed": 0.0, "direction": "", "vehicle_count": 0 }
```

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/models/signal_model.dart.

Class named Signal with:
- Fields: String eventId, String rsuId, String segment, String timestamp, double speed, String direction, int vehicleCount
- JSON keys use snake_case: 'event_id', 'rsu_id', 'vehicle_count'
- const constructor
- factory Signal.fromJson(Map<String, dynamic> json)
- Map<String, dynamic> toJson()

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/models/signal_model.dart
git commit -m "feat(mobile): add Signal data model matching backend schema"
```

---

### Task 2.2 — TrafficAlert model

**What to build:** `lib/models/traffic_alert_model.dart`

**Critical notes:**  
Check `backend_server/functions/routes/analyze.py` for the exact field names written to Firestore. Use nullable types for any field that may not always be present.

**Paste alongside prompt:** `backend_server/functions/routes/analyze.py`

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is analyze.py: [paste file].

Create lib/models/traffic_alert_model.dart.
Class named TrafficAlert. Extract exact field names and types from the Firestore write in analyze.py.
- Use nullable types (String?, double?) for fields that may be absent
- factory TrafficAlert.fromJson(Map<String, dynamic> json) with null-safe access
- toJson() method

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/models/traffic_alert_model.dart
git commit -m "feat(mobile): add TrafficAlert data model with null-safe fields from Firestore schema"
```

---

### Task 2.3 — SegmentSummary model

**What to build:** `lib/models/segment_summary_model.dart` — client-side computed model, not fetched from any endpoint.

**Fields:** `String segment`, `String status`, `double averageSpeed`, `int vehicleCount`, `String lastUpdated`

**Speed thresholds:** ≥60 → free, ≥40 → moderate, ≥20 → congested, <20 → severe

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/models/segment_summary_model.dart.

Class named SegmentSummary with fields: segment, status, averageSpeed, vehicleCount, lastUpdated.

Include:
- const constructor
- factory SegmentSummary.fromSignals(String segment, List<Signal> signals): computes averageSpeed (mean of signal.speed), vehicleCount (sum of signal.vehicleCount), lastUpdated (timestamp of first signal), status from thresholds: >=60 free, >=40 moderate, >=20 congested, else severe
- toJson() and fromJson()

Import Signal from lib/models/signal_model.dart.
File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/models/segment_summary_model.dart
git commit -m "feat(mobile): add SegmentSummary client-side model computed from signal list"
```

---

## PHASE 3 — Service Layer

### Task 3.1 — SignalService

**What to build:** `lib/services/signal_service.dart`

**Backend response format:** `{ "success": true, "count": N, "signals": [...] }` — parse the `"signals"` key.

**Paste alongside prompt:** `lib/utils/http/http_client.dart`, `lib/utils/constants/api_constants.dart`, `lib/models/signal_model.dart`, `lib/models/segment_summary_model.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Files: [paste THttpHelper, TApiConstants, Signal model, SegmentSummary model].

Create lib/services/signal_service.dart, singleton class SignalService:

1. Future<List<Signal>> getSignals() — GET TApiConstants.signals, parse 'signals' list, map to Signal.fromJson()
2. Future<List<Signal>> getSignalsBySegment(String segment) — GET '/signals/$segment', 404 returns empty list
3. List<SegmentSummary> computeSegmentSummaries(List<Signal> signals) — group by segment field, call SegmentSummary.fromSignals() per group

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/services/signal_service.dart
git commit -m "feat(mobile): add SignalService to fetch signals and compute segment summaries"
```

---

### Task 3.2 — AlertService

**What to build:** `lib/services/alert_service.dart`

**Backend response format:** `{ "success": true, "count": N, "alerts": [...] }`

**Paste alongside prompt:** `lib/utils/http/http_client.dart`, `lib/utils/constants/api_constants.dart`, `lib/models/traffic_alert_model.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Files: [paste THttpHelper, TApiConstants, TrafficAlert model].

Create lib/services/alert_service.dart, singleton class AlertService:

1. Future<List<TrafficAlert>> getAlerts() — GET TApiConstants.alerts, parse 'alerts' list, map to TrafficAlert.fromJson()
2. Future<List<TrafficAlert>> getAlertsBySegment(String segment) — GET '/alerts/$segment', 404 returns empty list

Throw readable exceptions on non-404 failures.
File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/services/alert_service.dart
git commit -m "feat(mobile): add AlertService to fetch traffic alerts from backend"
```

---

## PHASE 4 — State Management (GetX Controllers)

### Task 4.1 — MapController

**What to build:** `lib/features/home/controllers/map_controller.dart` — auto-refreshes every 30 seconds, fetches signals and alerts in parallel.

**Critical notes:** Cancel the `Timer` in `onClose()` to prevent memory leaks.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/home/controllers/map_controller.dart.

GetX controller named MapController:
- RxList<SegmentSummary> segmentSummaries = <SegmentSummary>[].obs
- RxList<TrafficAlert> alerts = <TrafficAlert>[].obs
- RxBool isLoading = true.obs
- RxString errorMessage = ''.obs

onInit(): call fetchData() immediately, set up Timer.periodic(30 seconds, fetchData), store timer, cancel in onClose()

fetchData():
1. isLoading = true, clear errorMessage
2. Future.wait([SignalService().getSignals(), AlertService().getAlerts()])
3. computeSegmentSummaries from signals, assign both lists
4. isLoading = false
5. On error: set errorMessage, isLoading = false

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/home/controllers/map_controller.dart
git commit -m "feat(mobile): add MapController with 30s auto-refresh and parallel data fetching"
```

---

### Task 4.2 — AlertController

**What to build:** `lib/features/alerts/controllers/alert_controller.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/alerts/controllers/alert_controller.dart.

GetX controller named AlertController:
- RxList<TrafficAlert> alerts = <TrafficAlert>[].obs
- RxBool isLoading = true.obs
- RxString errorMessage = ''.obs

onInit(): call fetchAlerts()
fetchAlerts(): calls AlertService().getAlerts(), assigns to alerts, handles errors
fetchAlertsBySegment(String segment): calls AlertService().getAlertsBySegment(segment), assigns to alerts

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/alerts/controllers/alert_controller.dart
git commit -m "feat(mobile): add AlertController for alerts screen state management"
```

---

## PHASE 5 — Map Screen Integration

### Task 5.1 — Google Maps widget in map screen

**What to build:**  
Replace the map placeholder in Dana's screen with a real `GoogleMap` widget. Render colored markers per segment.

**Critical notes:**
- Initial camera: `LatLng(32.5556, 35.8500)` zoom 13 — Irbid center.
- Hues: free → `hueGreen`, moderate → `hueOrange`, congested → `hueRed`, severe → `hueMagenta`.
- Wrap in `Obx()`. Show loading overlay when `MapController.isLoading` is true.
- Do not change the screen layout outside the map area.

**Paste alongside prompt:** Dana's map screen, `map_controller.dart`, `segment_summary_model.dart`, `helper_functions.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Existing map screen: [paste]. MapController: [paste]. SegmentSummary: [paste]. THelperFunctions: [paste].

Integrate Google Maps into the existing screen without changing the layout:
1. Add GoogleMap where the placeholder is. Camera: LatLng(32.5556, 35.8500), zoom 13
2. Wrap in Obx() bound to MapController.segmentSummaries
3. One Marker per SegmentSummary using coordinates from lib/utils/constants/segment_coordinates.dart (create this file with placeholder LatLng values for now)
4. Marker hues: free → hueGreen, moderate → hueOrange, congested → hueRed, severe → hueMagenta
5. Loading overlay (semi-transparent CircularProgressIndicator) when MapController.isLoading is true
6. SnackBar when MapController.errorMessage is not empty

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/home/screens/map_screen.dart lib/utils/constants/segment_coordinates.dart
git commit -m "feat(mobile): integrate GoogleMap with live segment markers and loading state"
```

---

### Task 5.2 — Segment coordinates constant file

**What to build:** `lib/utils/constants/segment_coordinates.dart` — maps segment name strings to `LatLng` values.

**Critical notes:** Get segment names from `rsu_simulator/config.py`. Verify GPS coordinates in Google Maps before hardcoding.

**Paste alongside prompt:** Segment name list from `rsu_simulator/config.py`

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/utils/constants/segment_coordinates.dart.

const Map<String, LatLng> named kSegmentCoordinates.
Segment names: [paste list from rsu_simulator/config.py]

For each segment, provide a LatLng for its real street location in Irbid, Jordan. Add a comment per entry with the street name. If a name is a simulator placeholder (e.g. 'Segment_A'), use LatLng near (32.5556, 35.8500) with a small offset and add a TODO comment.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/utils/constants/segment_coordinates.dart
git commit -m "feat(mobile): add GPS coordinate constants for all road segments in Irbid"
```

---

### Task 5.3 — Current location on map (FR-18)

**What to build:**  
Enable GPS location on the map screen with runtime permission handling. Show the Google Maps blue dot.

**Critical notes:**
- Handle all permission states: denied, permanently denied (→ `openAppSettings()`), granted.
- `myLocationEnabled: true` on `GoogleMap` handles the blue dot once permission is granted.
- Store `GoogleMapController` in a `Completer` assigned in `onMapCreated`.

**Paste alongside prompt:** Updated map screen after Task 5.1

**AI prompt:**

```
I am working on the ISCS Flutter project. Updated map screen: [paste].

Add current location:
1. Method _requestLocationAndCenter() in the State class
2. Check Permission.locationWhenInUse.status — request if denied, openAppSettings() if permanently denied
3. If granted: Geolocator.getCurrentPosition() then _mapController.animateCamera(CameraUpdate.newLatLng(...))
4. Call _requestLocationAndCenter() in initState()
5. Set myLocationEnabled: true and myLocationButtonEnabled: true on GoogleMap
6. Store GoogleMapController in Completer<GoogleMapController>, assign in onMapCreated

Do not change existing layout or controller logic.
File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/home/screens/map_screen.dart
git commit -m "feat(mobile): add GPS location with permission handling and camera centering"
```

---

## PHASE 6 — Alerts Screen Integration

### Task 6.1 — Connect Alerts screen to AlertController

**What to build:**  
Wire Dana's existing alerts screen to `AlertController` with real data, loading, empty, and error states.

**Critical notes:**
- Empty state: `TTexts.noAlertsMessage`. Error state: message + retry button.
- Each item shows: segment name, status/type, timestamp via `TFormatter.formatDateTime()`.
- `RefreshIndicator` for pull-to-refresh.

**Paste alongside prompt:** Dana's alerts screen, `alert_controller.dart`, `traffic_alert_model.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Alerts screen: [paste]. AlertController: [paste]. TrafficAlert model: [paste].

Wire the screen to real data without changing layout:
1. Get.put(AlertController()) at screen level
2. Wrap list in Obx() bound to controller.alerts
3. Show CircularProgressIndicator when isLoading is true
4. Show TTexts.noAlertsMessage when alerts is empty and not loading
5. Show error message + retry button when errorMessage is not empty
6. RefreshIndicator calling controller.fetchAlerts()
7. Each item: segment name, status/type, timestamp via TFormatter

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/alerts/screens/alerts_screen.dart
git commit -m "feat(mobile): connect alerts screen to AlertController with real backend data"
```

---

## PHASE 7 — Congested Areas Visual Layer (FR-16)

### Task 7.1 — Segment detail bottom sheet

**What to build:** `lib/features/home/widgets/segment_detail_sheet.dart` — shown when a map marker is tapped.

**Content:** segment name, colored status chip, average speed, vehicle count, last updated, recent alerts via `FutureBuilder`.

**Paste alongside prompt:** `map_controller.dart`, `segment_summary_model.dart`, `traffic_alert_model.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Files: [paste MapController, SegmentSummary, TrafficAlert].

Create lib/features/home/widgets/segment_detail_sheet.dart.
StatelessWidget named SegmentDetailSheet, takes SegmentSummary as required parameter.
Displayed via showModalBottomSheet from the marker's onTap.

Content:
- Segment name title
- Colored status chip using THelperFunctions.getTrafficStatusColor(summary.status)
- Average speed: 'X.X km/h'
- Vehicle count
- Last updated via THelperFunctions.formatTimestamp()
- 'Recent Alerts' section using FutureBuilder on AlertService().getAlertsBySegment(summary.segment)

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/home/widgets/segment_detail_sheet.dart lib/features/home/screens/map_screen.dart
git commit -m "feat(mobile): add segment detail bottom sheet triggered on marker tap"
```

---

### Task 7.2 — Map legend widget

**What to build:** `lib/features/home/widgets/map_legend.dart` — small overlay card positioned bottom-left on the map.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/home/widgets/map_legend.dart.

StatelessWidget named MapLegend, positioned in a Stack at the bottom-left of the map.
Four rows with colored circle + label:
- TColors.trafficFree: 'Free (≥ 60 km/h)'
- TColors.trafficModerate: 'Moderate (40–59 km/h)'
- TColors.trafficCongested: 'Congested (20–39 km/h)'
- TColors.trafficSevere: 'Severe (< 20 km/h)'

Card opacity: 0.85.
File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/home/widgets/map_legend.dart lib/features/home/screens/map_screen.dart
git commit -m "feat(mobile): add traffic status color legend overlay to map screen"
```

---

## PHASE 8 — Settings & Notification Preferences (FR-19)

### Task 8.1 — Connect Settings screen to local preferences

**What to build:**  
Create `lib/features/settings/controllers/settings_controller.dart` and wire Dana's settings screen to `TLocalStorage`.

**Preference keys:** `'notif_congestion_alerts'` (bool), `'notif_severe_only'` (bool), `'map_auto_refresh'` (bool), `'preferred_segment'` (String?)

**Paste alongside prompt:** Dana's settings screen, `lib/utils/local_storage/storage_utility.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Settings screen: [paste]. TLocalStorage: [paste].

Create lib/features/settings/controllers/settings_controller.dart, GetX controller named SettingsController:
- On init: read all four preference keys from TLocalStorage, expose as Rx observables (RxBool x3, RxString x1)
- Toggle method per bool preference: flips value and writes back to TLocalStorage
- setPreferredSegment(String segment) method

Wire existing settings screen:
- Get.put(SettingsController())
- Wrap each switch in Obx(), call toggle on onChange

Do not change UI layout.
File header for controller: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/settings/controllers/settings_controller.dart lib/features/settings/screens/settings_screen.dart
git commit -m "feat(mobile): wire settings screen to TLocalStorage via SettingsController"
```

---

### Task 8.2 — FCM push notifications (optional — only if demo requires background alerts)

**What to build:**  
Firebase Cloud Messaging so alerts reach the device when the app is closed.

**Critical notes:**  
Only do this if the demo requires background delivery. In-app alerts from Task 6.1 satisfy FR-17 as written. This also requires a new backend endpoint to send FCM payloads.

**AI prompt:**

```
I am working on the ISCS Flutter project. Add FCM push notifications to main.dart (after Firebase.initializeApp()):

1. await FirebaseMessaging.instance.requestPermission()
2. final token = await FirebaseMessaging.instance.getToken() → store in TLocalStorage under 'fcm_token'
3. FirebaseMessaging.onMessage.listen() → show local notification via flutter_local_notifications when app is in foreground
4. FirebaseMessaging.onMessageOpenedApp.listen() → navigate to Alerts screen when user taps notification

Initialize FlutterLocalNotificationsPlugin with Android channel named 'ISCS Alerts', high importance.
File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/main.dart
git commit -m "feat(mobile): set up FCM push notifications and local notification channel"
```

---

## PHASE 9 — Alternative Routes (Use Case: Show Alternative Routes)

### Task 9.1 — DirectionsService and route polyline

**What to build:** `lib/services/directions_service.dart` — fetches a route from Google Directions API and draws it as a polyline on the map.

**Critical notes:**  
Enable the Directions API in Google Cloud Console (same project as Maps SDK). For the demo: origin = current device location, destination = congested segment's coordinate from `kSegmentCoordinates`.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/services/directions_service.dart.

Method: Future<List<LatLng>> getRoute({required LatLng origin, required LatLng destination})
1. GET https://maps.googleapis.com/maps/api/directions/json with origin, destination, key params
2. Parse 'overview_polyline' > 'points' string
3. Decode encoded polyline to List<LatLng> (implement decode algorithm inline)
4. Return the list

Then in the map screen, add showAlternativeRoute(SegmentSummary congested):
1. Geolocator.getCurrentPosition()
2. DirectionsService().getRoute(origin: currentPosition, destination: kSegmentCoordinates[congested.segment])
3. Draw result as Polyline on map — blue color, strokeWidth 5

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/services/directions_service.dart lib/features/home/screens/map_screen.dart
git commit -m "feat(mobile): add DirectionsService and alternative route polyline on map"
```

---

## PHASE 10 — Government Dashboard (Use Case: Access Dashboard)

### Task 10.1 — Role storage in AuthController

**What to build:**  
After login, extract the `role` custom claim from the Firebase ID token and store it in `AuthController`.

**Paste alongside prompt:** `lib/features/auth/controllers/auth_controller.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Current AuthController: [paste].

After successful signIn():
1. await FirebaseAuth.instance.currentUser!.getIdTokenResult()
2. Extract claims['role'] as String, default to 'driver' if null
3. Store as RxString userRole = 'driver'.obs

Add getter: bool get canAccessDashboard => userRole.value == 'public_safety' || userRole.value == 'admin'

Update file header: Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/auth/controllers/auth_controller.dart
git commit -m "feat(mobile): extract and store user role from Firebase token claims after login"
```

---

### Task 10.2 — Dashboard screen

**What to build:** `lib/features/dashboard/screens/dashboard_screen.dart` — accessible to `public_safety` and `admin` only. Shows summary row, segment data table, and map navigation per row.

**Critical notes:** Use `Get.find<MapController>()` — do not create a new controller.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/dashboard/screens/dashboard_screen.dart.

Accessible to public_safety and admin roles only (show 'Access Denied' to drivers).
Uses Get.find<MapController>() for data.

Shows:
1. Summary row: total active alerts, total segments, count of congested/severe segments
2. Data table: segment name, status chip (colored), average speed, vehicle count, last updated
3. 'View on Map' button per row — navigates to map screen

Role check: read from Get.find<AuthController>().userRole
File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/dashboard/screens/dashboard_screen.dart
git commit -m "feat(mobile): add government dashboard screen with role guard and segment table"
```

---

## PHASE 11 — Admin Screens

### Task 11.1 — Manage Users screen

**What to build:**  
`lib/features/admin/screens/manage_users_screen.dart` and `lib/features/admin/controllers/manage_users_controller.dart` — lookup user by UID and assign role.

**Backend endpoints used:** `GET /admin/user/{uid}`, `POST /admin/set-role`

**AI prompt:**

```
I am working on the ISCS Flutter project. Backend endpoints: GET /admin/user/{uid} returns uid/email/display_name/role/disabled. POST /admin/set-role body: {uid, role}.

Create manage_users_controller.dart (GetX) and manage_users_screen.dart.

Controller:
- RxString foundUserInfo = ''.obs, RxBool isLoading, RxString errorMessage
- lookupUser(String uid): GET /admin/user/$uid, format result as readable string → foundUserInfo
- setRole(String uid, String role): POST /admin/set-role, show success/error

Screen:
- TextField for UID input + 'Look Up' button
- Display foundUserInfo
- Dropdown (driver / public_safety / admin) + 'Assign Role' button
- Loading and error states

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/admin/screens/manage_users_screen.dart lib/features/admin/controllers/manage_users_controller.dart
git commit -m "feat(mobile): add admin Manage Users screen with UID lookup and role assignment"
```

---

### Task 11.2 — Monitor Server Data screen

**What to build:** `lib/features/admin/screens/server_monitor_screen.dart` — shows server health, signal count, alert count.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/admin/screens/server_monitor_screen.dart.

Uses FutureBuilder to call THttpHelper.get('/health') on load. Displays:
- Green icon if status 200, red icon if fails
- Total vehicle count aggregated from MapController.segmentSummaries via Get.find()
- Total active alert count from Get.find<AlertController>().alerts.length
- 'Refresh' button

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/admin/screens/server_monitor_screen.dart
git commit -m "feat(mobile): add admin Server Monitor screen with health check and data counts"
```

---

### Task 11.3 — Configure Alerts screen (Admin)

**What to build:** `lib/features/admin/screens/configure_alerts_screen.dart` — shows read-only thresholds and active alerts. Thresholds cannot be changed from the app in the current backend implementation.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/admin/screens/configure_alerts_screen.dart.

Thresholds are hardcoded in backend config.py — cannot be changed from the app.

Screen shows:
1. Read-only threshold cards: Free ≥60, Moderate 40–59, Congested 20–39, Severe <20 (all in km/h)
2. Note: 'These thresholds are configured on the backend server. Contact the system administrator to change them.'
3. Active alert count from AlertService().getAlerts() via FutureBuilder
4. List of active alerts with segment and status

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/features/admin/screens/configure_alerts_screen.dart
git commit -m "feat(mobile): add admin Configure Alerts screen with read-only thresholds and active alerts"
```

---

## PHASE 12 — Navigation & Routing

### Task 12.1 — GetX named routes

**What to build:**  
`lib/routes/app_routes.dart` and `lib/routes/app_pages.dart`. Replace `MaterialApp` with `GetMaterialApp` in `main.dart`. Add role-based middleware for dashboard and admin routes.

**AI prompt:**

```
I am working on the ISCS Flutter project. Set up GetX named routes.

Create lib/routes/app_routes.dart with class AppRoutes:
- login, home, alerts, settings, dashboard, manageUsers (/admin/users), serverMonitor (/admin/server), configureAlerts (/admin/alerts)

Create lib/routes/app_pages.dart with class AppPages:
- static List<GetPage> pages mapping each route to its screen
- Middleware on dashboard and admin routes: if AuthController.userRole is 'driver', redirect to AppRoutes.home

Update main.dart: MaterialApp → GetMaterialApp, pass initialRoute and getPages.
File headers: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/routes/app_routes.dart lib/routes/app_pages.dart lib/main.dart
git commit -m "feat(mobile): set up GetX named routes with role-based middleware for protected screens"
```

---

## PHASE 13 — Error Handling & Edge Cases

### Task 13.1 — Token expiry handling in THttpHelper

**What to build:**  
On HTTP 401 response, attempt a token refresh and retry once. If retry fails, sign out and redirect to login.

**Paste alongside prompt:** Updated `lib/utils/http/http_client.dart`, `lib/services/auth_service.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. THttpHelper: [paste]. AuthService: [paste].

Modify THttpHelper: on any HTTP 401 response:
1. Call AuthService().getIdToken(forceRefresh: true) — update getIdToken() to accept bool forceRefresh
2. Retry the request once with the new token
3. If retry is also 401 or getIdToken() throws: call AuthService().signOut() then Get.offAllNamed(AppRoutes.login)
4. If retry succeeds: return normally

Apply to GET first, then replicate for POST, PUT, DELETE.
File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

**Git commit:**
```
git add lib/utils/http/http_client.dart lib/services/auth_service.dart
git commit -m "fix(mobile): auto-refresh token and redirect to login on persistent 401 responses"
```

---

### Task 13.2 — Network connectivity check

**What to build:**  
Add an offline check in `MapController.fetchData()` and `AlertController.fetchAlerts()` using `TDeviceUtility.hasInternetConnection()`. Show an offline banner on the map screen.

**AI prompt:**

```
I am working on the ISCS Flutter project. TDeviceUtility.hasInternetConnection() exists at lib/utils/device/device_utility.dart.

In MapController.fetchData() and AlertController.fetchAlerts(), add at the start:
1. await TDeviceUtility.hasInternetConnection()
2. If false: set errorMessage to TTexts.errorNetwork and return early
3. If true: proceed

In the map screen: show a top banner when errorMessage equals TTexts.errorNetwork, indicating offline status.

Update Last Modified to May 2026 in every modified file.
```

**Git commit:**
```
git add lib/features/home/controllers/map_controller.dart lib/features/alerts/controllers/alert_controller.dart lib/features/home/screens/map_screen.dart
git commit -m "feat(mobile): add offline detection and banner across map and alerts"
```

---

## PHASE 14 — Final Integration Testing

### Task 14.1 — End-to-end test checklist

Run manually before the graduation demo. No AI prompt. No commit until all boxes are checked.

```
[ ] App launches → splash shows → Firebase initializes → auth state checked
[ ] Not logged in → redirected to Login screen
[ ] Login with wrong password → error message shown, no crash
[ ] Login with correct credentials → navigated to Home/Map screen
[ ] Map loads → markers appear for each segment with correct colors
[ ] Current location permission prompt appears on first launch
[ ] Location granted → blue dot appears on map, camera moves to user
[ ] Marker tapped → bottom sheet shows segment detail with real data
[ ] Alerts screen shows real alerts from backend
[ ] Pull-to-refresh on both map and alerts works
[ ] Settings screen toggles save between app restarts (TLocalStorage)
[ ] Logged in as public_safety or admin → Dashboard tab visible
[ ] Logged in as driver → Dashboard tab not visible
[ ] Admin: Manage Users lookup works with a real Firebase UID
[ ] Admin: set-role call works and returns success
[ ] No internet → offline banner shows, no crash
[ ] Token expires during session → auto-refresh happens transparently
[ ] Sign out → returned to Login screen, navigation stack cleared
```

**Git commit (after all checks pass):**
```
git add .
git commit -m "test(mobile): all end-to-end integration checks passed — app ready for demo"
```

---

## Dependency Order Summary

```
Phase 0  → must be done before anything compiles
Phase 1  → must be fully done before Phase 3, 4, 5
Phase 2  → must be done before Phase 3
Phase 3  → must be done before Phase 4
Phase 4  → must be done before Phase 5, 6
Phase 5  → can run parallel with Phase 6 after Phase 4
Phase 7  → depends on Phase 5
Phase 8  → independent after Phase 1
Phase 9  → depends on Phase 5
Phase 10 → depends on Phase 4 and Phase 1 (role storage)
Phase 11 → depends on Phase 10
Phase 12 → can be done any time after Phase 1 screens exist
Phase 13 → done last before Phase 14
Phase 14 → final
```

---

## Time Estimate

| Phase | Content | Focused days |
|---|---|---|
| 0 | Package setup | 0.5 |
| 1 | Firebase Auth end-to-end | 2 |
| 2 | Data models | 0.5 |
| 3 | Service layer | 1 |
| 4 | GetX controllers | 1 |
| 5 | Map integration + location | 2.5 |
| 6 | Alerts screen | 0.5 |
| 7 | Congestion layer + detail sheet + legend | 1.5 |
| 8 | Settings + FCM (optional) | 1–3 |
| 9 | Alternative routes | 1.5 |
| 10 | Government dashboard | 1.5 |
| 11 | Admin screens (3 screens) | 2 |
| 12 | Routing setup | 0.5 |
| 13 | Error handling | 1 |
| 14 | Testing | 2 |
| **Total** | | **19–22 focused days** |

At part-time pace: **5–7 weeks**.  
At full-time pace: **4 weeks**.
