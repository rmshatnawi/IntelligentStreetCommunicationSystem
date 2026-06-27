# Intelligent Street Communication System (ISCS)

**Graduation Project — Jordan University of Science and Technology**  
**Supervisor:** Dr. Ali AL-Shatnawi  
**Author:** Raghad Shatnawi  
**Last Modified:** 27/06/2026

---

## Overview

ISCS is a real-time distributed traffic monitoring platform built for the city of Irbid, Jordan. The system collects vehicle detection data from Roadside Units (RSUs), processes it on a central backend, and exposes it to drivers through a Flutter mobile application and to administrators through a web dashboard.

The platform covers four layers:

1. **RSU Simulator** — SUMO-based traffic simulator acting as the RSU hardware layer
2. **Backend Server** — FastAPI server with Firebase Authentication and Firestore
3. **Mobile App** — Flutter driver-facing application
4. **Web Dashboard** — Admin/government monitoring portal

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
│       │   └── auth.py                # Firebase token verification + RBAC
│       ├── models/
│       │   ├── signal_model.py        # RSUSignal, SignalInDB
│       │   ├── summary_model.py       # SegmentTrafficSummary
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
│           │   ├── home_page.dart     # Bottom nav shell
│           │   ├── map_page.dart      # Live traffic map
│           │   ├── history_page.dart  # Vehicle tracking history
│           │   ├── profile_page.dart  # Account + plate management
│           │   ├── settings_page.dart
│           │   └── obu_pairing_page.dart
│           ├── services/
│           │   └── obu_service.dart
│           └── widgets/
├── rsu_simulator/
│   ├── intersection.py                # Generates SUMO network, RSUs, routes
│   ├── intersection_test.py           # TraCI runner — POSTs detections to /ingest
│   ├── intersection.sumocfg
│   ├── intersection.net.xml
│   ├── intersection.nod.xml
│   ├── intersection.edg.xml
│   ├── intersection.add.xml           # Induction loop (RSU) definitions
│   ├── intersection.rou.xml
│   └── out.xml                        # SUMO detector output
└── web_dashboard/
    └── index.html                     # Admin/government portal
```

---

## Layer 1 — RSU Simulator (SUMO + TraCI)

The simulator replaces physical RSU hardware for development and demonstration.

### What it does

`intersection.py` builds a synthetic 4-way signalized intersection with:

- 4 road segments (street1–street4), each with a START and END induction loop acting as an RSU pair
- 120 unique Jordanian-format plate numbers, two of which (`STL-999`, `STL-555`) are pre-seeded as stolen in Firestore
- Configurable traffic phases: low → medium → high congestion → easing

`intersection_test.py` runs the simulation via TraCI and, on each vehicle detection event, POSTs a signal to the backend `/ingest` endpoint:

```json
{
  "event_id":      "uuid",
  "rsu_id":        "RSU_01_START",
  "segment":       "street1 St",
  "timestamp":     "2026-06-27T10:00:00Z",
  "speed":         38.5,
  "direction":     "Westbound",
  "vehicle_count": 1,
  "plate_number":  "CAR-001"
}
```

### Running the simulator

```bash
# 1. Generate network files (only needed once or after changes)
python intersection.py

# 2. Start the backend first (see Layer 2)

# 3. Run the simulation
python intersection_test.py
```

Set `SERVER_URL` in `intersection_test.py` to the backend's LAN address, e.g. `http://192.168.1.x:8000/ingest`.

---

## Layer 2 — Backend Server (FastAPI + Firebase)

### Tech stack

- Python 3.12 (required — 3.14 has no prebuilt `grpcio` wheels)
- FastAPI + Uvicorn
- Firebase Admin SDK (Authentication + Firestore)
- Pydantic v2

### Setup

```bash
cd backend_server/functions

python3.12 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Place your Firebase service account key:
cp /path/to/serviceAccountKey.json .
```

### Running

```bash
python main.py
# or, for LAN access (required for simulator and mobile app):
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### API routes

| Method | Route | Auth | Purpose |
|--------|-------|------|---------|
| POST | `/ingest` | Open | Receive RSU signal |
| GET | `/state` | Open | Segment statuses + RSU positions for the map |
| GET | `/signals` | driver+ | Raw signal list |
| GET | `/signals/{segment}` | driver+ | Signals for one segment |
| GET | `/alerts` | Open (testing) | Active traffic alerts |
| GET | `/alerts/{segment}` | driver+ | Alerts for one segment |
| GET | `/summaries` | driver+ | Aggregated traffic summaries |
| GET | `/summaries/{segment}` | driver+ | Summary for one segment |
| GET | `/analyze/{segment}` | public_safety+ | On-demand analysis |
| GET | `/rsus` | Open | RSU list from Firestore |
| POST | `/report-incident` | Open (testing) | Submit incident report |
| POST | `/admin/set-role` | admin | Assign role to user |
| GET | `/admin/user/{uid}` | admin | Get user profile + role |
| DELETE | `/admin/user/{uid}` | admin | Disable user account |
| GET | `/health` | Open | Server health check |

**Note:** `/ingest` is intentionally unauthenticated. RSU hardware does not carry Firebase credentials. This is an acknowledged engineering tradeoff.

### Role-based access control

Roles are stored as Firebase custom claims and set via `POST /admin/set-role`.

| Role | Access level |
|------|-------------|
| `driver` | Traffic data, alerts, own vehicle history |
| `public_safety` | All driver routes + segment analysis |
| `admin` | All routes + user and RSU management |

### Firestore collections

| Collection | Contents |
|-----------|----------|
| `signals` | Raw RSU detections |
| `alerts` | Generated traffic alerts |
| `traffic_summaries` | Aggregated segment summaries |
| `vehicle_tracking` | Per-plate movement records |
| `stolen_vehicles` | Plates reported stolen |
| `security_alerts` | Alerts fired on stolen vehicle sightings |
| `segment_baselines` | Rolling speed/flow baselines per segment |
| `rsus` | RSU metadata (id, lat, lng, segment) |
| `users` | Driver profiles and plate registrations |
| `obus` | OBU device bindings |
| `incident_reports` | Driver-submitted incident reports |

### Traffic thresholds

| State | Speed |
|-------|-------|
| Free flow | > 60 km/h |
| Moderate | 40–60 km/h |
| Congested | 20–40 km/h |
| Severe | < 20 km/h |

---

## Layer 3 — Mobile App (Flutter)

### Tech stack

- Flutter / Dart
- Firebase Auth + Firestore (`firebase_auth`, `cloud_firestore`)
- Google Maps SDK (`google_maps_flutter`)
- GetX (state management)
- BLE via `flutter_blue_plus` (OBU pairing)
- Native Android `MethodChannel` for Google Maps directions (replaces `url_launcher`)

### Screens

| Screen | Route | Description |
|--------|-------|-------------|
| Welcome | `/welcome` | Sign In / Register entry point |
| Sign In | `/signin` | Firebase email/password auth |
| Register | `/register` | New account creation |
| Home | `/home` | Bottom nav shell (Map / History / Profile / Settings) |
| Map | `/home` → Map tab | Live color-coded traffic map. Segments colored green / amber / red by status. Long-press on segment opens native Google Maps directions. |
| History | `/history` | Per-plate movement timeline, route trace on map, stolen vehicle sighting panel |
| Profile | `/profile` | Account info, plate registration, report stolen / mark recovered |
| OBU Pairing | `/obu` | BLE scan, connect, send plate to OBU, bind in Firestore |
| Settings | `/settings` | App preferences, sign out with confirmation dialog |

### Running

```bash
cd mobile_app/app
flutter pub get
flutter run
```

The backend must be reachable on LAN. Set `kBaseUrl` in `map_page.dart` to `http://<server-ip>:8000`.

---

## Layer 4 — Web Dashboard

The web dashboard is a static HTML/JS portal for administrators and government users.

```bash
# Serve locally
cd web_dashboard
python -m http.server 5500
# Open http://localhost:5500
```

The dashboard reads from the same backend. Set `API_BASE_URL` in the dashboard source to the server's LAN IP. The backend's CORS middleware (`allow_origins: ["*"]`) allows browser requests from any origin. The map is centered on Irbid coordinates (`32.505, 35.95`).

---

## Environment notes

- **Windows PowerShell:** use `$env:VAR` syntax for environment variables, not `%VAR%`
- **Python paths on Windows:** use raw strings (`r"path\to\file"`) or forward slashes to avoid unicode escape errors
- **SUMO osmWebWizard output** lands in a timestamped subfolder, not the working directory
- **Firebase credentials** (`serviceAccountKey.json`) must never be committed to Git

---

## Project context

- **Institution:** Jordan University of Science and Technology
- **City:** Irbid, Jordan (real street coordinates used throughout)
- **Phase:** GP2 — implementation and presentation
- **Firebase project ID:** `smartstreetintelligencesystem`
