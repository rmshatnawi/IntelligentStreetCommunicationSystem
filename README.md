# Intelligent Street Communication System (ISCS)

**Graduation Project — Computer Engineering**  
**Author: Raghad Shatnawi**  
**Date: March 2026**

---

## Overview

ISCS is a smart traffic monitoring system that uses Roadside Units (RSUs) to detect vehicles, analyze traffic conditions in real time, and alert drivers through a mobile application.

---

## System Architecture
```
RSU Simulator (Python)
        │
        │  HTTP POST /ingest
        ▼
FastAPI Backend Server (Python)
        │
        ├── Validates incoming signals
        ├── Saves to Firestore database
        ├── Analyzes traffic congestion
        └── Generates alerts
        │
        ▼
Firestore Database (Firebase)
        │
        ▼
Flutter Mobile App
        │
        ├── Displays live traffic map
        └── Shows alerts to drivers
```

---

## Project Structure
```
GP_ISCS/
├── IntelligentStreetCommunicationSystem/
│   └── backend_server/
│       └── functions/              ← FastAPI server
│           ├── main.py             ← server entry point
│           ├── config.py           ← all settings
│           ├── requirements.txt    ← Python packages
│           ├── models/
│           │   └── signal_model.py ← signal data structure
│           └── routes/
│               ├── ingest.py       ← receives RSU signals
│               ├── analyze.py      ← traffic analysis
│               └── api.py          ← Flutter endpoints
└── RSU_Simulator/
    ├── main.py                     ← simulator entry point
    ├── config.py                   ← RSU settings
    ├── core/
    │   └── publisher.py            ← sends signals to server
    └── models/
        └── signal.py               ← builds signal objects
```

---

## Server Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest` | Receive signal from RSU |
| GET | `/analyze/{segment}` | Analyze traffic for a segment |
| GET | `/signals` | Get all latest signals |
| GET | `/signals/{segment}` | Get signals for a segment |
| GET | `/alerts` | Get all active alerts |
| GET | `/alerts/{segment}` | Get alerts for a segment |
| GET | `/health` | Server health check |

---

## Signal Structure

Every RSU sends a signal in this format:
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

---

## Traffic Status Levels

| Status | Speed |
|--------|-------|
| Free | above 60 km/h |
| Moderate | 40 - 60 km/h |
| Congested | 20 - 40 km/h |
| Severe | below 20 km/h |

---

## How to Run

### 1. Backend Server
```bash
cd IntelligentStreetCommunicationSystem/backend_server/functions
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

> Add your `serviceAccountKey.json` to the `functions/` folder before running.

### 2. RSU Simulator
```bash
cd RSU_Simulator
python main.py
```

---

## Future Improvements

- Machine learning module for congestion prediction
- Docker containerization for production deployment
- Real RSU hardware integration
- Historical traffic pattern analysis