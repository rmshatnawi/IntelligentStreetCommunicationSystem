# Intelligent Street Communication System

**Graduation Project — Jordan University of Science and Technology**  
**Supervisor:** Dr. Ali AL-Shatnawi  
**Last Modified:** 27/06/2026

---

## Team Contributions

| Member | Component |
|--------|-----------|
| Raghad Shatnawi | Backend server, mobile application, system testing |
| Batool Kreishan | Roadside Unit (RSU) hardware, On-Board Unit (OBU) hardware |
| Dana Omar | Backend server, cloud database (Firebase / Firestore) |
| Batool Khateeb | Management web dashboard |

---

## Overview

The Intelligent Street Communication System is a real-time distributed traffic monitoring platform built for the city of Irbid, Jordan. RSUs deployed on road segments detect passing vehicles via OBUs and send detection signals to a central backend, which classifies traffic conditions and exposes them to drivers through a Flutter mobile application and to administrators through a web dashboard.

The system comprises five layers:

1. **Hardware** — Roadside Units (RSU) and On-Board Units (OBU)
2. **Backend Server** — FastAPI server with Firebase Authentication
3. **Cloud Database** — Firebase Firestore
4. **Mobile App** — Flutter driver-facing application
5. **Web Dashboard** — Admin/government monitoring portal

---

## Repository Structure

```
iscs/
├── backend_server/
│   └── functions/
│       ├── main.py                    # FastAPI entry point
│       ├── config.py                  # All server settings
│       ├── serviceAccountKey.json     # Firebase credentials (not in Git)
│       ├── core/
│       │   └── auth.py                # Firebase token verification
│       ├── models/
│       │   ├── signal_model.py        # RSUSignal, SignalInDB, SegmentTrafficSummary
│       │   ├── summary_model.py       # SegmentTrafficSummary model
│       │   └── user_model.py          # UserRole, AuthenticatedUser
│       ├── routes/
│       │   ├── ingest.py              # POST /ingest
│       │   ├── analyze.py             # GET /analyze/{segment}
│       │   ├── api.py                 # Driver-facing routes
│       │   ├── summaries.py           # GET /summaries
│       │   └── admin.py               # Admin-only routes
│       └── services/
│           ├── vehicle_tracking.py    # Plate tracking + stolen vehicle detection
│           └── aggregation_service.py # Traffic summary generation
├── mobile_app/
│   └── app/
│       └── lib/
│           ├── main.dart
│           ├── app_theme.dart
│           ├── pages/
│           │   ├── welcome_page.dart
│           │   ├── signin_page.dart
│           │   ├── home_page.dart         # Bottom nav shell
│           │   ├── map_page.dart          # Live traffic map
│           │   ├── history_page.dart      # Vehicle tracking history
│           │   ├── profile_page.dart      # Account + plate management
│           │   ├── settings_page.dart
│           │   └── obu_pairing_page.dart  # BLE pairing + plate registration
│           ├── services/
│           │   └── obu_service.dart       # BLE abstraction (real + mock)
│           └── widgets/
└── web_dashboard/
    └── index.html                         # Admin/government portal
```

---

## Layer 1 — Hardware

### Roadside Unit (RSU)

RSUs are deployed at fixed positions along road segments. Each RSU detects vehicles passing through its coverage zone and sends a detection signal to the backend server via the `/ingest` endpoint. The signal includes the RSU ID, road segment, vehicle speed, vehicle count, plate number, and GPS coordinates.

### On-Board Unit (OBU)

OBUs are installed in vehicles. Each OBU stores the vehicle's plate number and communicates it to RSUs as the vehicle passes. The plate is registered by the driver through the mobile app's OBU pairing flow over BLE (Bluetooth Low Energy), which binds the plate to the OBU and the driver's account in Firestore.

---

## Layer 2 — Backend Server (FastAPI)

### Tech stack

- Python 3.12
- FastAPI + Uvicorn
- Firebase Admin SDK (Authentication + Firestore)
- Pydantic v2

### Setup

```bash
cd backend_server/functions

python3.12 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Place your Firebase service account key:
cp /path/to/serviceAccountKey.json .
```

### Running

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### API routes

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/ingest` | Receive RSU signal |
| GET | `/state` | Segment statuses + RSU positions for the map |
| GET | `/signals` | Raw signal list |
| GET | `/signals/{segment}` | Signals for one segment |
| GET | `/alerts` | Active traffic alerts |
| GET | `/alerts/{segment}` | Alerts for one segment |
| GET | `/summaries` | Aggregated traffic summaries |
| GET | `/summaries/{segment}` | Summary for one segment |
| GET | `/analyze/{segment}` | On-demand segment analysis |
| GET | `/rsus` | RSU list from Firestore |
| POST | `/report-incident` | Submit incident report |
| POST | `/admin/set-role` | Assign role to a user |
| GET | `/admin/user/{uid}` | Get user profile |
| DELETE | `/admin/user/{uid}` | Disable user account |
| GET | `/health` | Server health check |

### Traffic thresholds

| State | Speed |
|-------|-------|
| Free flow | > 60 km/h |
| Moderate | 40–60 km/h |
| Congested | 20–40 km/h |
| Severe | < 20 km/h |

---

## Layer 3 — Cloud Database (Firebase Firestore)

### Collections

| Collection | Contents |
|-----------|----------|
| `signals` | Raw RSU detections |
| `alerts` | Generated traffic alerts |
| `traffic_summaries` | Aggregated segment summaries |
| `vehicle_tracking` | Per-plate movement records |
| `stolen_vehicles` | Plates reported stolen by drivers |
| `security_alerts` | Alerts fired when a stolen plate is detected by an RSU |
| `segment_baselines` | Rolling speed/flow baseline per segment |
| `rsus` | RSU metadata (id, lat, lng, segment) |
| `users` | Driver profiles and plate registrations |
| `obus` | OBU device bindings |
| `incident_reports` | Driver-submitted incident reports |

---

## Layer 4 — Mobile App (Flutter)

### Tech stack

- Flutter / Dart
- Firebase Auth + Firestore (`firebase_auth`, `cloud_firestore`)
- Google Maps SDK (`google_maps_flutter`)
- GetX (state management)
- BLE via `flutter_blue_plus` (OBU pairing)
- Native Android `MethodChannel` for Google Maps directions

### Screens

| Screen | Route | Description |
|--------|-------|-------------|
| Welcome | `/welcome` | Sign In / Register entry point |
| Sign In | `/signin` | Firebase email/password authentication |
| Register | `/register` | New account creation |
| Home | `/home` | Bottom nav shell (Map / History / Profile / Settings) |
| Map | Map tab | Live color-coded traffic map. Segments colored green / amber / red by traffic state. Long-press opens native Google Maps directions. |
| History | History tab | Per-plate movement timeline, map route trace, stolen vehicle sighting panel |
| Profile | Profile tab | Account info, plate registration, report stolen / mark recovered |
| OBU Pairing | `/obu` | BLE scan, connect to OBU, send plate, bind in Firestore |
| Settings | Settings tab | App preferences, sign out with confirmation |

### Running

```bash
cd mobile_app/app
flutter pub get
flutter run
```

The backend must be reachable on LAN. Set `kBaseUrl` in `map_page.dart` to `http://<server-ip>:8000`.

---

## Layer 5 — Web Dashboard

Static HTML/JS portal for administrators and government users.

```bash
cd web_dashboard
python -m http.server 5500
# Open http://localhost:5500
```

Set `API_BASE_URL` in the dashboard source to the backend's LAN IP. The map is centered on Irbid coordinates (`32.505, 35.95`).
