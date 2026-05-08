# ISCS Flutter Mobile App — Complete Task Schedule
**Author:** Raghad Shatnawi  
**Last Modified:** May 2026  
**Purpose:** Full remaining work breakdown for the Flutter mobile application.  
Each task includes what to build, critical notes, and a ready-to-use AI prompt.

---

## How to use this file

- Tasks are ordered by dependency. Do not skip phases.
- Every AI prompt assumes the AI has access to the project codebase. Paste the relevant existing files alongside the prompt.
- "Paste alongside" means: copy the file content into the chat before or after the prompt.
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
- `google_maps_flutter` requires a Google Maps API key. This must be added to `android/app/src/main/AndroidManifest.xml` and `ios/Runner/AppDelegate.swift`. Get the key from Google Cloud Console with Maps SDK for Android and Maps SDK for iOS enabled.
- `geolocator` requires permission declarations in `AndroidManifest.xml` (`ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`) and `ios/Runner/Info.plist` (`NSLocationWhenInUseUsageDescription`).
- `firebase_messaging` on Android requires `google-services.json` in `android/app/`. On iOS requires `GoogleService-Info.plist` in `ios/Runner/`.

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

Return the full updated dependencies and dev_dependencies sections only. Do not return the entire pubspec.yaml — just those two sections.
```

**Estimated time:** 1 hour (setup + key configuration)

---

## PHASE 1 — Firebase Auth Integration (BLOCKER — do this first)

### Task 1.1 — Firebase initialization in main.dart

**What to build:**  
Initialize `firebase_core` before `runApp()`. The splash screen must stay visible until initialization completes. `FlutterNativeSplash.remove()` must only be called after Firebase is ready and auth state is determined — not immediately after init.

**Critical notes:**
- Current `main.dart` calls `FlutterNativeSplash.preserve()` but never calls `FlutterNativeSplash.remove()`. This means the splash never disappears. The remove call belongs in the AuthController after the auth state check resolves.
- `Firebase.initializeApp()` is async. `main()` must be `async`.
- Use `DefaultFirebaseOptions.currentPlatform` from the generated `firebase_options.dart` file (produced by `flutterfire configure` CLI command).
- The `home:` field in MaterialApp in main.dart must be replaced with an `AuthGate` widget (built in Task 1.3) instead of a hardcoded screen.
- Header must read: Author: Raghad Shatnawi, Last Modified: May 2026.

**Paste alongside prompt:** `lib/main.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is the current main.dart: [paste file]

I need you to rewrite main.dart to:
1. Make main() async
2. Call WidgetsFlutterBinding.ensureInitialized() first
3. Call FlutterNativeSplash.preserve() immediately after
4. Call await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform)
5. Run the app — do NOT call FlutterNativeSplash.remove() here. It will be called later by the AuthController once auth state resolves.
6. Replace the home: field in MaterialApp with home: const AuthGate() — AuthGate will be built separately.
7. Import: firebase_core, firebase_options (generated file), flutter_native_splash, and the AuthGate widget from lib/features/auth/screens/auth_gate.dart

Keep all existing theme setup (TAppTheme.lightTheme, TAppTheme.darkTheme, ThemeMode.system) unchanged.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 1.2 — AuthService

**What to build:**  
A service class at `lib/services/auth_service.dart` that wraps Firebase Auth. All screens and controllers interact with Firebase Auth only through this class — never directly.

**Methods to implement:**
- `signInWithEmailAndPassword(email, password)` → returns `UserCredential` or throws
- `signOut()` → signs out from Firebase
- `getIdToken()` → returns the current user's Firebase ID token as a `String`; forces a refresh if the token is expired
- `currentUser` → getter returning `FirebaseAuth.instance.currentUser`
- `authStateChanges` → stream of `User?` for listening to login/logout events

**Critical notes:**
- `getIdToken()` must call `user.getIdToken(true)` with `forceRefresh: true` on the first call after login, and can use `forceRefresh: false` for subsequent calls within the token's 1-hour validity. Simpler approach for graduation: always use `forceRefresh: false` and let Firebase handle refresh automatically.
- This method is what `THttpHelper` will call in Task 1.3.
- Error handling: wrap Firebase Auth exceptions and rethrow as readable strings for the UI.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create a new file at lib/services/auth_service.dart.

This is a singleton service class called AuthService that wraps Firebase Auth. It must expose:
- Future<UserCredential> signIn(String email, String password) — calls FirebaseAuth.instance.signInWithEmailAndPassword
- Future<void> signOut() — calls FirebaseAuth.instance.signOut()
- Future<String> getIdToken() — gets the current user's ID token; throws a readable exception if no user is logged in
- User? get currentUser — returns FirebaseAuth.instance.currentUser
- Stream<User?> get authStateChanges — returns FirebaseAuth.instance.authStateChanges()

Error handling: catch FirebaseAuthException and rethrow with a human-readable message string (e.g., 'wrong-password' → 'Incorrect password. Please try again.').

Use a private constructor and a static instance (singleton pattern), same pattern as TLocalStorage in the project.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 1.3 — Token injection in THttpHelper

**What to build:**  
Modify `lib/utils/http/http_client.dart` to attach the Firebase ID token to every request header as `Authorization: Bearer <token>`. This is the single highest-priority fix — every backend call returns HTTP 401 without it.

**Critical notes:**
- The backend's `core/auth.py` expects the header: `Authorization: Bearer <Firebase ID token>`.
- `THttpHelper` must call `AuthService().getIdToken()` before every request.
- If `getIdToken()` throws (user not logged in), the request should not proceed — throw an exception that propagates up to the controller.
- The existing GET/POST/PUT/DELETE methods must each have `headers` updated to include `Authorization` and `Content-Type`.

**Paste alongside prompt:** `lib/utils/http/http_client.dart`, `lib/services/auth_service.dart` (just built)

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is the current http_client.dart: [paste file]
Here is the AuthService I just built: [paste file]

Modify THttpHelper so that every request (GET, POST, PUT, DELETE) automatically attaches the Firebase ID token as an Authorization header.

Steps:
1. Add a private static method _buildHeaders() that calls await AuthService().getIdToken() and returns a Map<String, String> with:
   - 'Authorization': 'Bearer <token>'
   - 'Content-Type': 'application/json'
2. Update every method to await _buildHeaders() and pass the result as the headers parameter.
3. If getIdToken() throws, let the exception propagate — do not swallow it.
4. Keep all existing error handling and exception messages.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 1.4 — AuthGate widget (auth state routing)

**What to build:**  
A widget at `lib/features/auth/screens/auth_gate.dart` that listens to `AuthService().authStateChanges` and routes the user to the login screen or home screen accordingly. This is what `main.dart` sets as `home:`.

**Critical notes:**
- While the auth state is loading (stream hasn't emitted yet), show a loading indicator — NOT a blank screen. The splash screen is already removed by this point.
- If `user == null` → navigate to `LoginScreen`.
- If `user != null` → navigate to `HomeScreen` (or `MapScreen` — whatever Dana named the main screen).
- `FlutterNativeSplash.remove()` must be called here, after the first emission from the auth state stream, before navigating.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/auth/screens/auth_gate.dart.

This widget:
1. Is a StatelessWidget named AuthGate
2. Listens to AuthService().authStateChanges using a StreamBuilder
3. While waiting (connectionState != done/active with data): shows a centered CircularProgressIndicator
4. Calls FlutterNativeSplash.remove() exactly once after the first stream emission — use a bool flag to ensure it only fires once
5. If user == null: returns LoginScreen()
6. If user != null: returns HomeScreen() (use the name Dana gave the main screen — if unknown, use a placeholder named HomeScreen from lib/features/home/screens/home_screen.dart)

Import AuthService from lib/services/auth_service.dart.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 1.5 — Connect Login screen to AuthService

**What to build:**  
Wire the existing login screen UI (built by Dana) to `AuthService.signIn()`. Add a GetX controller to manage loading state, error display, and navigation after login.

**What to create:**
- `lib/features/auth/controllers/auth_controller.dart` — GetX controller with `signIn()` method
- Connect the login button in the existing screen to the controller

**Critical notes:**
- The login screen UI already exists. Do not redesign it. Only add the controller wiring.
- On successful login: GetX routing navigates to the HomeScreen. Use `Get.offAll(() => HomeScreen())` to clear the navigation stack so back button does not return to login.
- On failure: show the error string from `AuthService` in a `SnackBar` or error text widget.
- Show a loading indicator on the button while the sign-in request is in flight.
- The email field must use `TextEditingController`. Trim whitespace before passing to `signIn()`.

**Paste alongside prompt:** The existing login screen dart file from Dana

**AI prompt:**

```
I am working on the ISCS Flutter project. The login screen UI is already built. I need you to:

1. Create lib/features/auth/controllers/auth_controller.dart — a GetX controller (extends GetxController) with:
   - RxBool isLoading = false.obs
   - RxString errorMessage = ''.obs
   - Future<void> signIn(String email, String password) method that calls AuthService().signIn(), sets isLoading during the call, catches errors and sets errorMessage, and on success calls Get.offAll(() => HomeScreen())

2. In the existing login screen file [paste Dana's login screen file], add:
   - final AuthController controller = Get.put(AuthController()) at the top of the State or build method
   - Wrap the submit button with Obx(() => ...) to show a CircularProgressIndicator when controller.isLoading.value is true
   - Show controller.errorMessage.value below the form if it is not empty
   - On button tap: call controller.signIn(emailController.text.trim(), passwordController.text)

Do not change any UI styling, layout, or widget structure. Only add the controller binding and the three behaviors listed above.

File header for auth_controller.dart: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

## PHASE 2 — Data Models

### Task 2.1 — Signal model

**What to build:**  
`lib/models/signal_model.dart` — a Dart class that mirrors the backend signal schema exactly.

**Backend signal schema (from signal_model.py and signal_model.md):**
```json
{
  "event_id":      "uuid string",
  "rsu_id":        "RSU_01",
  "segment":       "Petra St",
  "timestamp":     "2026-03-15T12:45:30",
  "speed":         42.0,
  "direction":     "Northbound",
  "vehicle_count": 3
}
```

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/models/signal_model.dart.

The class is named Signal and must:
1. Have fields matching this JSON schema exactly:
   - String eventId (maps to 'event_id')
   - String rsuId (maps to 'rsu_id')
   - String segment
   - String timestamp
   - double speed
   - String direction
   - int vehicleCount (maps to 'vehicle_count')
2. Have a const constructor
3. Have a factory Signal.fromJson(Map<String, dynamic> json) constructor
4. Have a Map<String, dynamic> toJson() method

Use standard Dart naming conventions (camelCase fields, snake_case JSON keys).

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 2.2 — TrafficAlert model

**What to build:**  
`lib/models/traffic_alert_model.dart` — mirrors the `TrafficAlert` Firestore schema from the backend.

**Critical notes:**  
Check `backend_server/functions/routes/analyze.py` or the GP1 report Table 4 for the exact alert fields before writing this model. The alert schema has known gaps (severity, trigger_condition fields may be null or missing). The model must handle null fields gracefully using nullable types.

**Paste alongside prompt:** `backend_server/functions/routes/analyze.py` — the section where alerts are written to Firestore

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is the analyze.py file that writes TrafficAlert documents to Firestore: [paste analyze.py]

Create lib/models/traffic_alert_model.dart.

The class is named TrafficAlert. Extract the exact field names and types from the Firestore write operation in analyze.py. 
- Use nullable types (String?, double?) for any field that may not always be present.
- Include a factory TrafficAlert.fromJson(Map<String, dynamic> json) that uses null-safe access (json['field'] as String?).
- Include a toJson() method.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 2.3 — SegmentSummary model (for map display)

**What to build:**  
`lib/models/segment_summary_model.dart` — a lightweight model used to represent one road segment on the map. Derived from signal data (not from the backend's SegmentTrafficSummary collection, which has known null fields). This is a client-side computed model.

**Fields:**
- `String segment` — segment name
- `String status` — traffic status string ('free', 'moderate', 'congested', 'severe')
- `double averageSpeed`
- `int vehicleCount`
- `String lastUpdated` — ISO timestamp of the most recent signal

**Critical notes:**  
This model is NOT fetched from any endpoint directly. It is computed in `SignalService` by grouping signals by segment and deriving status from average speed using the same thresholds as the backend (≥60 free, 40–59 moderate, 20–39 congested, <20 severe).

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/models/segment_summary_model.dart.

This is a client-side model (not fetched from any API) with fields:
- String segment
- String status (one of: 'free', 'moderate', 'congested', 'severe')
- double averageSpeed
- int vehicleCount
- String lastUpdated

Include:
- const constructor
- factory SegmentSummary.fromSignals(String segment, List<Signal> signals) — computes averageSpeed as the mean of all signal.speed values, vehicleCount as the sum of all signal.vehicleCount values, lastUpdated as the timestamp of the first (most recent) signal, and status using these thresholds: averageSpeed >= 60 → 'free', >= 40 → 'moderate', >= 20 → 'congested', else 'severe'
- toJson() and fromJson() methods

Import Signal from lib/models/signal_model.dart.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

## PHASE 3 — Service Layer

### Task 3.1 — SignalService

**What to build:**  
`lib/services/signal_service.dart` — fetches signals from the backend and computes segment summaries.

**Methods:**
- `Future<List<Signal>> getSignals()` — calls `GET /signals`, parses response into `List<Signal>`
- `Future<List<Signal>> getSignalsBySegment(String segment)` — calls `GET /signals/{segment}`
- `List<SegmentSummary> computeSegmentSummaries(List<Signal> signals)` — groups signals by segment, calls `SegmentSummary.fromSignals()` for each group

**Critical notes:**  
The backend response format for `/signals` is:
```json
{ "success": true, "count": N, "signals": [ ... ] }
```
Parse the `"signals"` key from the response, not the root object.

**Paste alongside prompt:** `lib/utils/http/http_client.dart`, `lib/utils/constants/api_constants.dart`, `lib/models/signal_model.dart`, `lib/models/segment_summary_model.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Here are the relevant files: [paste THttpHelper, TApiConstants, Signal model, SegmentSummary model]

Create lib/services/signal_service.dart with a class SignalService (singleton pattern, private constructor + static instance).

Methods:
1. Future<List<Signal>> getSignals() — calls THttpHelper.get(TApiConstants.signals), extracts the 'signals' list from the response map, maps each item to Signal.fromJson(), returns the list. Throws a readable exception on failure.
2. Future<List<Signal>> getSignalsBySegment(String segment) — calls THttpHelper.get('${TApiConstants.signalsBySegment}/$segment'), same parsing logic, handles 404 by returning an empty list.
3. List<SegmentSummary> computeSegmentSummaries(List<Signal> signals) — groups signals by their segment field using a Map<String, List<Signal>>, then calls SegmentSummary.fromSignals(segment, signals) for each group. Returns the list of summaries.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 3.2 — AlertService

**What to build:**  
`lib/services/alert_service.dart` — fetches alerts from the backend.

**Methods:**
- `Future<List<TrafficAlert>> getAlerts()` — calls `GET /alerts`
- `Future<List<TrafficAlert>> getAlertsBySegment(String segment)` — calls `GET /alerts/{segment}`

**Backend response format for `/alerts`:**
```json
{ "success": true, "count": N, "alerts": [ ... ] }
```

**Paste alongside prompt:** `lib/utils/http/http_client.dart`, `lib/utils/constants/api_constants.dart`, `lib/models/traffic_alert_model.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Here are the relevant files: [paste THttpHelper, TApiConstants, TrafficAlert model]

Create lib/services/alert_service.dart with a class AlertService (singleton pattern).

Methods:
1. Future<List<TrafficAlert>> getAlerts() — calls THttpHelper.get(TApiConstants.alerts), extracts the 'alerts' list, maps to TrafficAlert.fromJson(), returns the list.
2. Future<List<TrafficAlert>> getAlertsBySegment(String segment) — calls THttpHelper.get('${TApiConstants.alertsBySegment}/$segment'), handles 404 by returning empty list.

Both methods must throw readable exceptions on non-404 failures.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

## PHASE 4 — State Management (GetX Controllers)

### Task 4.1 — MapController / HomeController

**What to build:**  
`lib/features/home/controllers/map_controller.dart` — drives the map screen state.

**Responsibilities:**
- Call `SignalService.getSignals()` on init and every 30 seconds (auto-refresh)
- Compute `SegmentSummary` list from signals
- Expose `RxList<SegmentSummary> segmentSummaries`
- Expose `RxBool isLoading` and `RxString errorMessage`
- Expose `RxList<TrafficAlert> alerts` — fetched from `AlertService`
- Handle refresh triggered by user (pull-to-refresh)

**Critical notes:**  
Use `GetX`'s `ever()` or a `Timer.periodic()` for auto-refresh. Cancel the timer in `onClose()` to prevent memory leaks.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/home/controllers/map_controller.dart.

This is a GetX controller (extends GetxController) named MapController with:
- RxList<SegmentSummary> segmentSummaries = <SegmentSummary>[].obs
- RxList<TrafficAlert> alerts = <TrafficAlert>[].obs
- RxBool isLoading = true.obs
- RxString errorMessage = ''.obs

On onInit():
1. Call fetchData() immediately
2. Set up a Timer.periodic with a 30-second interval that calls fetchData()
3. Store the timer and cancel it in onClose()

fetchData() method:
1. Sets isLoading to true, clears errorMessage
2. Awaits SignalService().getSignals() and AlertService().getAlerts() in parallel using Future.wait()
3. Calls SignalService().computeSegmentSummaries(signals) and assigns to segmentSummaries
4. Assigns alerts
5. Sets isLoading to false
6. On error: sets errorMessage to the exception message, sets isLoading to false

Import: signal_service.dart, alert_service.dart, segment_summary_model.dart, traffic_alert_model.dart

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 4.2 — AlertController (for Alerts screen)

**What to build:**  
`lib/features/alerts/controllers/alert_controller.dart` — drives the standalone alerts screen.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/alerts/controllers/alert_controller.dart.

This is a GetX controller named AlertController with:
- RxList<TrafficAlert> alerts = <TrafficAlert>[].obs
- RxBool isLoading = true.obs
- RxString errorMessage = ''.obs

On onInit(): call fetchAlerts()

fetchAlerts(): calls AlertService().getAlerts(), assigns to alerts, handles errors via errorMessage. Sets isLoading appropriately.

Also add fetchAlertsBySegment(String segment) that calls AlertService().getAlertsBySegment(segment) and assigns to alerts.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

## PHASE 5 — Map Screen Integration

### Task 5.1 — Google Maps widget in HomeScreen/MapScreen

**What to build:**  
Replace any placeholder in the map screen with a real `GoogleMap` widget. Render one colored marker per segment using `SegmentSummary` data from `MapController`.

**Critical notes:**
- Initial camera position should center on Irbid, Jordan: `LatLng(32.5556, 35.8500)`, zoom 13.
- Each marker's `BitmapDescriptor` color must match the segment's traffic status using `THelperFunctions.getTrafficStatusColor()`. Use `BitmapDescriptor.defaultMarkerWithHue()` — map the Color to a hue value, or use custom colored icons.
- Tapping a marker should open a bottom sheet or navigate to the segment detail screen.
- Wrap the GoogleMap widget in `Obx(() => ...)` so it rebuilds when `MapController.segmentSummaries` updates.
- Show a loading overlay when `MapController.isLoading.value` is true.
- You need hardcoded `LatLng` coordinates for each segment name (e.g., "Petra St" maps to a specific lat/lng in Irbid). Create a constant map in a new file `lib/utils/constants/segment_coordinates.dart`.

**Paste alongside prompt:** The existing map screen dart file from Dana, `lib/features/home/controllers/map_controller.dart`, `lib/models/segment_summary_model.dart`, `lib/utils/helpers/helper_functions.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is the existing map screen: [paste Dana's map screen file]. Here is the MapController: [paste file]. Here is SegmentSummary model: [paste file]. Here is THelperFunctions: [paste file].

I need you to integrate Google Maps into the existing screen without changing its overall layout or scaffold structure.

Tasks:
1. Add a GoogleMap widget where the map placeholder currently is (do not redesign the screen layout)
2. Initial camera position: LatLng(32.5556, 35.8500), zoom 13.0 (Irbid, Jordan)
3. Wrap in Obx(() => ...) bound to MapController.segmentSummaries
4. For each SegmentSummary, add a Marker at its coordinates. Use a constant Map<String, LatLng> defined in lib/utils/constants/segment_coordinates.dart — populate it with placeholder coordinates for now, noting that real coordinates must be filled in.
5. Each marker's hue: use BitmapDescriptor.defaultMarkerWithHue() with these values: free → BitmapDescriptor.hueGreen, moderate → BitmapDescriptor.hueOrange, congested → BitmapDescriptor.hueRed, severe → BitmapDescriptor.hueMagenta
6. Show a loading overlay (semi-transparent with CircularProgressIndicator) when MapController.isLoading.value is true
7. Show a SnackBar with MapController.errorMessage.value if it is not empty

Do not change anything outside the map widget area.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 5.2 — Segment coordinates constant file

**What to build:**  
`lib/utils/constants/segment_coordinates.dart` — maps segment name strings (exactly as they appear in the backend) to `LatLng` values.

**Critical notes:**  
The segment names in the backend are defined in `rsu_simulator/config.py`. List every segment name from that config. Use real GPS coordinates for each street in Irbid. Verify coordinates using Google Maps before hardcoding.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/utils/constants/segment_coordinates.dart.

This file defines a const Map<String, LatLng> named kSegmentCoordinates.

The segment names come from the RSU simulator config: [paste the segment list from rsu_simulator/config.py].

For each segment name, provide a LatLng using realistic GPS coordinates for streets in Irbid, Jordan. Use Google Maps to verify each coordinate. Add a comment above each entry with the street name for readability.

If a segment name does not correspond to a real street (e.g., it's a simulator placeholder like 'Segment_A'), use a dummy coordinate near Irbid city center (32.5556, 35.8500) with a small offset per segment and add a TODO comment.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 5.3 — Current location on map (FR-18)

**What to build:**  
Enable device GPS location on the map screen. Show the user's position as the native Google Maps blue dot.

**Critical notes:**
- Request location permission using `permission_handler` before accessing GPS.
- If permission is denied: show a dialog explaining why location is needed. If permanently denied: direct user to app settings using `openAppSettings()`.
- After permission is granted: call `Geolocator.getCurrentPosition()` and move the camera to the user's location.
- `GoogleMap` widget has a built-in `myLocationEnabled: true` and `myLocationButtonEnabled: true` that handles the blue dot automatically once permission is granted.
- Add location permission to `AndroidManifest.xml` if not already there from Task 0.1.

**Paste alongside prompt:** The updated map screen file after Task 5.1

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is the current map screen after Google Maps integration: [paste updated file]

Add current location support:

1. Create a method _requestLocationAndCenter() in the screen's State class
2. In this method: check permission using Permission.locationWhenInUse.status
   - If denied: call Permission.locationWhenInUse.request()
   - If permanently denied: show a dialog with a button that calls openAppSettings()
   - If granted: call Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high) and animate the map camera to that position using _mapController.animateCamera(CameraUpdate.newLatLng(...))
3. Call _requestLocationAndCenter() in initState()
4. Set myLocationEnabled: true and myLocationButtonEnabled: true on the GoogleMap widget

Store the GoogleMapController in a Completer<GoogleMapController> and assign it in the onMapCreated callback.

Do not change any existing layout or controller logic.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

## PHASE 6 — Alerts Screen Integration

### Task 6.1 — Connect Alerts screen to AlertController

**What to build:**  
Wire the existing alerts screen UI (built by Dana) to `AlertController`. Display real alert data with loading, empty, and error states.

**Critical notes:**
- The screen must show: alert segment name, alert status/type, generated_at timestamp (formatted using `TFormatter.formatDateTime()`), and any available severity or description field.
- Empty state: display `TTexts.noAlertsMessage`.
- Error state: display the error string with a retry button that calls `AlertController.fetchAlerts()`.
- Use `RefreshIndicator` for pull-to-refresh.

**Paste alongside prompt:** Dana's alerts screen file, `lib/features/alerts/controllers/alert_controller.dart`, `lib/models/traffic_alert_model.dart`

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is the existing alerts screen: [paste Dana's alerts screen]. Here is the AlertController: [paste file]. Here is the TrafficAlert model: [paste file].

Wire the alerts screen to real data:
1. Add final AlertController controller = Get.put(AlertController()) at the screen level
2. Wrap the list widget in Obx(() => ...) bound to controller.alerts
3. Show a CircularProgressIndicator when controller.isLoading.value is true
4. Show the noAlertsMessage text (from TTexts) when controller.alerts is empty and not loading
5. Show an error message + retry button when controller.errorMessage is not empty
6. Wrap the list in a RefreshIndicator that calls controller.fetchAlerts()
7. Each list item must show: segment name, status or type, and timestamp formatted with TFormatter

Do not change any widget styling or layout outside of these additions.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

## PHASE 7 — Congested Areas Visual Layer (FR-16)

### Task 7.1 — Segment detail bottom sheet

**What to build:**  
When a map marker is tapped, show a `DraggableScrollableSheet` or `ModalBottomSheet` with segment-specific detail: current status, average speed, vehicle count, last updated time, and a list of recent alerts for that segment.

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is the MapController: [paste file]. Here is SegmentSummary model: [paste file]. Here is TrafficAlert model: [paste file].

Create lib/features/home/widgets/segment_detail_sheet.dart.

This is a StatelessWidget named SegmentDetailSheet that takes a SegmentSummary as a required parameter.

It displays inside a showModalBottomSheet call (call this from the map marker's onTap):
- Segment name as a title
- A colored status chip using THelperFunctions.getTrafficStatusColor(summary.status) as background color and the status string as label
- Average speed formatted as 'X.X km/h'
- Vehicle count
- Last updated timestamp formatted with THelperFunctions.formatTimestamp()
- A section titled 'Recent Alerts' that fetches alerts for this segment using AlertService().getAlertsBySegment(summary.segment) in a FutureBuilder

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 7.2 — Map legend widget

**What to build:**  
A small overlay widget on the map screen showing what each marker color means.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/home/widgets/map_legend.dart.

This is a StatelessWidget named MapLegend. It is a small card widget positioned in the bottom-left corner of the map using a Stack.

It shows four rows, each with a colored circle and a label:
- Green circle: 'Free (≥ 60 km/h)'
- Orange circle: 'Moderate (40–59 km/h)'
- Red circle: 'Congested (20–39 km/h)'
- Purple circle: 'Severe (< 20 km/h)'

Colors must come from TColors (trafficFree, trafficModerate, trafficCongested, trafficSevere).
The card should have slight opacity (0.85) to not fully block the map.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

## PHASE 8 — Settings & Notification Preferences (FR-19)

### Task 8.1 — Connect Settings screen to local preferences

**What to build:**  
Wire the existing settings screen (built by Dana) to `TLocalStorage` for persisting user preferences. The settings include notification toggles and display preferences.

**Preference keys to store:**
- `'notif_congestion_alerts'` (bool) — receive congestion alerts
- `'notif_severe_only'` (bool) — only show severe alerts
- `'map_auto_refresh'` (bool) — auto-refresh map every 30 seconds
- `'preferred_segment'` (String?) — last-viewed segment

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is the existing settings screen: [paste Dana's settings screen]. Here is TLocalStorage: [paste storage_utility.dart].

Create lib/features/settings/controllers/settings_controller.dart as a GetX controller named SettingsController.

It must:
1. On init: read all four preference keys from TLocalStorage and expose them as Rx observables:
   - RxBool notifCongestionAlerts
   - RxBool notifSevereOnly
   - RxBool mapAutoRefresh
   - RxString preferredSegment
2. For each bool preference: a toggle method that flips the value and writes it back to TLocalStorage
3. For preferredSegment: a setPreferredSegment(String segment) method

Then wire the existing settings screen to the controller:
- Add Get.put(SettingsController()) in the screen
- Wrap each toggle switch in Obx(() => ...) bound to the relevant observable
- Call the toggle method on onChange

Do not change the UI layout.

File header for controller: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 8.2 — FCM push notifications (if in scope)

**What to build:**  
Set up Firebase Cloud Messaging so the backend can push alert notifications to the device. This requires both Flutter changes and a new backend endpoint.

**Critical notes:**
- This task is optional for the graduation demo. Local in-app alerts (Task 6.1) already satisfy FR-17. FCM adds push delivery when the app is in the background.
- Requires: `firebase_messaging` package, `flutter_local_notifications` for foreground display, FCM token registration on login, and a backend endpoint `POST /notify/{segment}` that sends an FCM message.
- Only implement this if the demo requires receiving alerts while the app is closed.

**AI prompt (Flutter side):**

```
I am working on the ISCS Flutter project. Set up Firebase Cloud Messaging in the Flutter app.

In main.dart (after Firebase.initializeApp()):
1. Request notification permission: await FirebaseMessaging.instance.requestPermission()
2. Get the FCM token: final token = await FirebaseMessaging.instance.getToken()
3. Store the token in TLocalStorage under key 'fcm_token'
4. Set up FirebaseMessaging.onMessage.listen() to show a local notification using flutter_local_notifications when the app is in the foreground
5. Set up FirebaseMessaging.onMessageOpenedApp.listen() to navigate to the Alerts screen when user taps a notification

Initialize FlutterLocalNotificationsPlugin with an Android notification channel named 'ISCS Alerts' with high importance.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

## PHASE 9 — Alternative Routes (Use Case: Show Alternative Routes)

### Task 9.1 — Google Directions API integration

**What to build:**  
When a user selects a congested segment, offer to show an alternative route avoiding that segment using the Google Directions API.

**Critical notes:**
- This requires a separate Google Maps Directions API key (same project, different API enabled in Google Cloud Console).
- The request goes to: `https://maps.googleapis.com/maps/api/directions/json?origin=...&destination=...&avoid=tolls&key=...`
- Draw the route as a `Polyline` on the map.
- For the graduation demo, this can be simplified: hardcode origin as current device location and destination as a fixed point, with the alternative route avoiding the congested segment's coordinates.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/services/directions_service.dart.

This service fetches alternative route directions from the Google Directions API.

Method: Future<List<LatLng>> getRoute({required LatLng origin, required LatLng destination})

1. Calls https://maps.googleapis.com/maps/api/directions/json with origin, destination, and API key as query parameters
2. Parses the 'overview_polyline' > 'points' field from the response
3. Decodes the encoded polyline string to a List<LatLng> using the standard polyline decoding algorithm (implement the decode function inline)
4. Returns the list of LatLng points

Then in the map screen, add a method showAlternativeRoute(SegmentSummary congested) that:
1. Gets current location using Geolocator.getCurrentPosition()
2. Calls DirectionsService().getRoute(origin: currentLocation, destination: LatLng from kSegmentCoordinates[congested.segment])
3. Draws the result as a Polyline on the map with blue color and width 5

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

## PHASE 10 — Government Dashboard (Use Case: Access Dashboard)

### Task 10.1 — Dashboard screen (Track Vehicles, View Speed Data, View Congestion Map)

**What to build:**  
A screen accessible only to users with the `public_safety` or `admin` role (enforced client-side by checking the Firebase token's custom claims). Displays a live vehicle count per segment, speed data table, and congestion map view.

**Critical notes:**
- Role check: after login, read the custom claim from the Firebase ID token using `user.getIdTokenResult()` which returns `IdTokenResult` containing `claims['role']`. Store the role in the `AuthController` after login.
- If role is `driver`: this screen is not accessible. Do not show it in navigation.
- If role is `public_safety` or `admin`: show a "Dashboard" tab or navigation item.
- The backend endpoints (`/signals`, `/alerts`, `/signals/{segment}`) are already built and already support `public_safety` and `admin` roles.
- The dashboard is a richer view of the same data — vehicle counts per segment, speed trends, congestion map identical to the driver map but without routing features.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/dashboard/screens/dashboard_screen.dart.

This screen is accessible only to public_safety and admin roles. It shows:
1. A top summary row: total active alerts count, total segments monitored count, number of congested/severe segments
2. A data table listing each segment with: segment name, traffic status (colored chip), average speed, vehicle count, last updated
3. A button 'View on Map' per row that navigates to the map screen centered on that segment

Use MapController (already built) as the data source via Get.find<MapController>() — do not create a new controller.

For the role check: the screen should be guarded — if the current user's role is 'driver', show an 'Access Denied' message instead of the dashboard content. Read the role from AuthController.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 10.2 — Role storage in AuthController

**What to build:**  
After login, read the Firebase ID token result to extract the custom claim `role` and store it in `AuthController` as an `RxString`. All role-gated screens check this value.

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is the current AuthController: [paste file].

After a successful signIn():
1. Call await FirebaseAuth.instance.currentUser!.getIdTokenResult() to get the IdTokenResult
2. Extract claims['role'] as a String (default to 'driver' if null)
3. Store it in a new field: RxString userRole = 'driver'.obs

Add a getter bool get canAccessDashboard => userRole.value == 'public_safety' || userRole.value == 'admin'

Update the file header: Last Modified: May 2026.
```

---

## PHASE 11 — Admin Screens

### Task 11.1 — Manage Users screen

**What to build:**  
Screen at `lib/features/admin/screens/manage_users_screen.dart` that allows the admin to look up a Firebase user by UID and assign a role using the backend's `POST /admin/set-role` and `GET /admin/user/{uid}` endpoints.

**Critical notes:**
- Accessible only to `admin` role. Guard with `AuthController.userRole`.
- The backend already implements both endpoints in `routes/admin.py`.
- The admin must enter the Firebase UID manually (for graduation scope — no user listing endpoint exists).

**AI prompt:**

```
I am working on the ISCS Flutter project. The backend has these endpoints already implemented:
- GET /admin/user/{uid} — returns uid, email, display_name, role, disabled
- POST /admin/set-role — body: {uid: string, role: string}

Create lib/features/admin/screens/manage_users_screen.dart and lib/features/admin/controllers/manage_users_controller.dart.

Controller (GetX):
- RxString foundUserInfo = ''.obs
- RxBool isLoading = false.obs
- RxString errorMessage = ''.obs
- Future<void> lookupUser(String uid) — calls THttpHelper.get('/admin/user/$uid'), formats the result as a readable string, assigns to foundUserInfo
- Future<void> setRole(String uid, String role) — calls THttpHelper.post('/admin/set-role', {'uid': uid, 'role': role}), shows a success or error message

Screen:
- TextField for UID input
- 'Look Up' button → calls controller.lookupUser()
- Display foundUserInfo result
- Dropdown for role selection (driver, public_safety, admin)
- 'Assign Role' button → calls controller.setRole()
- Loading and error states

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 11.2 — Monitor Server Data screen

**What to build:**  
Screen that calls `GET /health` and displays the server status, plus a summary count of signals and alerts in the database.

**AI prompt:**

```
I am working on the ISCS Flutter project. The backend has GET /health which returns server status.

Create lib/features/admin/screens/server_monitor_screen.dart.

This screen calls THttpHelper.get('/health') on load and displays:
- Server status (up/down indicator)
- Total signal count (from MapController.segmentSummaries aggregated vehicle counts)
- Total active alert count (from AlertController.alerts.length)
- A 'Refresh' button

Use FutureBuilder for the health check call. Show a green icon if status is 200, red icon if it fails.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 11.3 — Configure Alerts screen (Admin)

**What to build:**  
Screen allowing the admin to configure the alert thresholds — specifically the speed thresholds that determine traffic status. 

**Critical notes:**
- The thresholds are currently hardcoded in `backend_server/functions/config.py`. There is no backend endpoint to update them dynamically. For graduation scope, this screen either: (a) shows the current threshold values as read-only with a note that they are configured on the server, or (b) stores admin-preferred display thresholds locally. Option (a) is accurate to the current system state.

**AI prompt:**

```
I am working on the ISCS Flutter project. Create lib/features/admin/screens/configure_alerts_screen.dart.

The backend alert thresholds are hardcoded in config.py and cannot be changed from the app in the current implementation. 

This screen should:
1. Display the current thresholds as read-only information cards:
   - Free: ≥ 60 km/h
   - Moderate: 40–59 km/h
   - Congested: 20–39 km/h
   - Severe: < 20 km/h
2. Show a note: 'These thresholds are configured on the backend server. Contact the system administrator to change them.'
3. Display the currently active alert count fetched from AlertService().getAlerts()
4. Display a list of active alerts with segment and status

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

## PHASE 12 — Navigation & Routing

### Task 12.1 — GetX route setup

**What to build:**  
Replace Flutter's default navigator with GetX named routes. Define all routes in one place.

**Critical notes:**
- All current `Get.to()` and `Get.offAll()` calls across the codebase must be consistent with the named routes defined here.
- Navigation guards: routes for `dashboard`, `admin/*` must check `AuthController.canAccessDashboard` and redirect to home if the role is insufficient.

**AI prompt:**

```
I am working on the ISCS Flutter project. Set up GetX named routes.

Create lib/routes/app_routes.dart with a class AppRoutes containing:
- static const String login = '/login'
- static const String home = '/home'
- static const String alerts = '/alerts'
- static const String settings = '/settings'
- static const String dashboard = '/dashboard'
- static const String manageUsers = '/admin/users'
- static const String serverMonitor = '/admin/server'
- static const String configureAlerts = '/admin/alerts'

Create lib/routes/app_pages.dart with a class AppPages containing a static List<GetPage> pages that maps each route to its screen class. Add a middleware to the dashboard and admin routes that checks AuthController.userRole and redirects to AppRoutes.home if access is denied.

Then update main.dart to use GetMaterialApp instead of MaterialApp and pass initialRoute and getPages.

File header for both files: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

## PHASE 13 — Error Handling & Edge Cases

### Task 13.1 — Token expiry handling

**What to build:**  
If any API call returns HTTP 401, intercept it in `THttpHelper` and attempt a token refresh. If refresh fails (user session is expired), sign out and redirect to login.

**AI prompt:**

```
I am working on the ISCS Flutter project. Here is the current THttpHelper: [paste file]. Here is AuthService: [paste file].

Modify THttpHelper so that if any API call returns HTTP 401:
1. Attempt to refresh the token by calling AuthService().getIdToken() with forceRefresh: true (update getIdToken() to accept a bool forceRefresh parameter)
2. Retry the original request once with the new token
3. If the retry also returns 401 OR getIdToken() throws: call AuthService().signOut() and then Get.offAllNamed(AppRoutes.login)
4. If the retry succeeds: return the response normally

Apply this logic to the GET method first as a pattern, then replicate for POST, PUT, DELETE.

File header: Author: Raghad Shatnawi, Last Modified: May 2026.
```

---

### Task 13.2 — Network connectivity check

**What to build:**  
Before any screen makes an API call, check connectivity using the existing `TDeviceUtility.hasInternetConnection()`. Show a persistent banner if the device is offline.

**AI prompt:**

```
I am working on the ISCS Flutter project. TDeviceUtility.hasInternetConnection() already exists at lib/utils/device/device_utility.dart.

In MapController.fetchData() and AlertController.fetchAlerts(), add a connectivity check at the start:
1. Call await TDeviceUtility.hasInternetConnection()
2. If false: set errorMessage to TTexts.errorNetwork and return early without making any HTTP calls
3. If true: proceed with the existing fetch logic

Also in the map screen, show a top banner (MaterialBanner or a custom colored Container) when the errorMessage contains TTexts.errorNetwork, indicating the app is offline.

File header changes: update Last Modified to May 2026 in every modified file.
```

---

## PHASE 14 — Final Integration Testing

### Task 14.1 — End-to-end test checklist

Run these manually before the graduation demo. No AI prompt — this is a manual verification step.

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

---

## Dependency Order Summary

```
Phase 0  → must be done before anything compiles  (done)
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
