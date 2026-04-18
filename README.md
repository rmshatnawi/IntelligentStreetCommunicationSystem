# Intelligent Street Communication System (ISCS)

**Graduation Project — Computer Engineering**  
**Jordan University of Science and Technology**  
**Supervised by: Dr. Ali AL-Shatnawi**

| Name | Role |
|------|------|
| Raghad Shatnawi |  System Architecture, Backend, RSU Simulator |
| Batool Kreishan |  |
| Batool AL-Khateeb |  |
| Dana Altohul |  |

---

## Overview

ISCS is a distributed intelligent traffic monitoring system. Roadside Units (RSUs) detect vehicles and generate traffic events. A backend server ingests, stores, and analyzes those events. A Flutter mobile app delivers real-time traffic conditions and alerts to drivers.

The system is currently in the base implementation phase. Core pipeline components are functional. Full feature implementation is in progress.

---

## System Architecture

```
RSU (Hardware Unit)  ──┐
                       ├──  HTTP POST /ingest
RSU Simulator (Python)─┘
                            ▼
                   FastAPI Backend Server
                            │
                   ┌────────┼────────┐
                   │        │        │
                Ingest   Analyze   API
                   │        │        │
                   └────────┴────────┘
                            │
                   Firestore Database
                            │
                   Flutter Mobile App
                            │
                   ┌────────┴────────┐
                   │                 │
              Driver View     Monitoring Dashboard
```

---

## RSU Components

The system includes two RSU implementations that serve different purposes. Both send identical signals to the same `/ingest` endpoint and must remain in sync with the signal schema defined in `backend_server/models/signal_model.py`.

### Hardware RSU (`services/RSU/`)
A physical roadside sensing unit built for real deployment and hardware testing. Detects passing vehicles using onboard sensors and transmits structured traffic events to the backend server.

### RSU Simulator (`rsu_simulator/`)
A Python-based software simulator that runs on a laptop. Used for development, testing, and demonstrations without requiring physical hardware. Simulates multiple RSUs running simultaneously via multithreading, each generating randomized but realistic vehicle detection data.

---

## Project Structure

```
GP_ISCS/
├── README.md
├── .gitignore
│
├── rsu_simulator/              ← Python simulator (development & testing)
│   ├── main.py                 ← entry point, starts all RSU threads
│   ├── config.py               ← RSU definitions, server URL, simulation settings
│   ├── core/
│   │   └── publisher.py        ← sends signals to server via HTTP POST
│   └── models/
│       └── signal.py           ← builds signal objects
│
├── services/
│   └── RSU/                    ← physical hardware RSU implementation
│
├── backend_server/
│   └── functions/
│       ├── main.py             ← FastAPI entry point
│       ├── config.py           ← server settings, Firestore collection names, thresholds
│       ├── requirements.txt
│       ├── models/
│       │   └── signal_model.py ← signal schema (source of truth for all components)
│       └── routes/
│           ├── ingest.py       ← receives and stores RSU signals
│           ├── analyze.py      ← traffic analysis and alert generation
│           └── api.py          ← Flutter-facing endpoints
│
├── mobile_app/                 ← Flutter application (in progress)
│
└── docs/
    ├── SRS/                    ← Software Requirements Specification
    ├── report/                 ← GP1 report
    ├── diagrams/
    └── signal_model.md         ← signal schema documentation
```

---

## Signal Schema

Every RSU — hardware or simulator — sends signals in this format. This schema is the single source of truth. Any change must be reflected in both RSU implementations and the backend model.

```json
{
  "event_id":      "uuid",
  "rsu_id":        "RSU_01",
  "segment":       "Petra St",
  "timestamp":     "2026-03-15T12:45:30",
  "speed":         42.0,
  "direction":     "Northbound",
  "vehicle_count": 3
}
```

See `docs/signal_model.md` for full field definitions.

---

## Server Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest` | Receive signal from RSU |
| GET | `/analyze/{segment}` | Analyze traffic for a segment |
| GET | `/signals` | Get latest signals (all segments) |
| GET | `/signals/{segment}` | Get latest signals for a segment |
| GET | `/alerts` | Get all active alerts |
| GET | `/alerts/{segment}` | Get alerts for a segment |
| GET | `/health` | Server health check |

---

## Traffic Status Levels

| Status | Average Speed |
|--------|---------------|
| Free | ≥ 60 km/h |
| Moderate | 40 – 59 km/h |
| Congested | 20 – 39 km/h |
| Severe | < 20 km/h |

---

## How to Run

### Backend Server

```bash
cd backend_server/functions
python3.14 -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
python main.py
```

> Place `serviceAccountKey.json` in the `functions/` folder before running. Never commit this file.

### RSU Simulator

```bash
cd rsu_simulator
python main.py
```

Server must be running before starting the simulator.

---

## Implementation Status

| Component | Status |
|-----------|--------|
| RSU Simulator | Done |
| Signal ingestion (`/ingest`) | Done |
| Traffic analysis (`/analyze`) | Done — base version |
| Flutter API endpoints | Done |
| Alert generation | Partial — schema incomplete |
| SegmentTrafficSummary | Not started |
| Firebase Authentication | Not started |
| Role-based access control | Not started |
| Flutter mobile app | Not started |
| Time-window aggregation | Not started |
| Baseline/anomaly logic | Not started |
| External API integration | Not started |

---

## Planned Improvements

- Time-windowed traffic aggregation (60-second windows)
- Rolling baseline comparison and persistence-based alert suppression
- Full `TrafficAlert` schema with severity, trigger condition, and status
- Firebase Authentication with role-based access (Driver / Admin / Public Safety)
- Flutter mobile app with live traffic map and alert notifications
- Authorized monitoring dashboard
- ML-based congestion prediction module
- Docker containerization for production deployment
