# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     config.py
# Author:   Raghad Shatnawi
# Date:     March 2026
# Author:   Batool Alkhateeb
# Last Modified: June 2026
# Purpose:  Central configuration file for the server.
#           All settings live here so if anything changes
#           (port, collection names, thresholds, etc.) we only
#           update this one file and everything else adapts.
# Updates (May 2026 - Dana Omar)
#   - Added Firestore collections for Vehicle Tracking.
#   - Added Firestore collection for Stolen Vehicle Detection.
# Updates (June 2026)
#   - Added baseline & persistence parameters (FR from GP1 report).
#   - Moved DIRECTIONS_API_KEY here (security fix).
# ============================================================

import os
from dotenv import load_dotenv
load_dotenv()

DIRECTIONS_API_KEY = os.environ.get("DIRECTIONS_API_KEY", "")

# ─── SERVER SETTINGS ────────────────────────────────────────
HOST = "0.0.0.0"   # accept connections from any machine on the network
PORT = 8000        # port the server runs on (http://localhost:8000)


# ─── FIRESTORE COLLECTION NAMES ─────────────────────────────
SIGNALS_COLLECTION          = "signals"           # stores raw RSU signals
ALERTS_COLLECTION           = "alerts"            # stores generated traffic alerts
SEGMENTS_COLLECTION         = "traffic_summaries" # stores road segment summaries
STOLEN_VEHICLES_COLLECTION  = "stolen_vehicles"   # stores stolen vehicle records
VEHICLE_TRACKING_COLLECTION = "vehicle_tracking"  # stores vehicle movement/tracking records
SECURITY_ALERTS_COLLECTION  = "security_alerts"   # stores security alerts (stolen vehicle detections)
BASELINES_COLLECTION        = "segment_baselines" # stores rolling baseline per segment (NEW)


# ─── TRAFFIC THRESHOLDS ─────────────────────────────────────
# Used by analyze.py and aggregation_service.py to classify traffic state.
# Units: km/h

SPEED_FREE_FLOW = 60   # above this → traffic is flowing freely
SPEED_MODERATE  = 40   # between 40–60 → moderate traffic
SPEED_CONGESTED = 20   # between 20–40 → heavy traffic
                       # below 20 → severe congestion

# Density thresholds (vehicles/km) — used by aggregation_service.py
DENSITY_FREE_FLOW = 40    # below this → free flow
DENSITY_MODERATE  = 70    # 40–70 → moderate
DENSITY_CONGESTED = 100   # above 100 → congested / severe


# ─── AGGREGATION WINDOW ─────────────────────────────────────
# Length of each time window used by aggregation_service.py (seconds).
WINDOW_SECONDS = 60


# ─── BASELINE & PERSISTENCE PARAMETERS (from GP1 report) ────
#
# k  — number of recent windows used to compute the rolling baseline
#       Baseline AvgSpeed  = mean of avg_speed over last k summaries
#       Baseline FlowRate  = mean of flow_rate over last k summaries
#
# alpha — factor controlling anomaly detection strictness
#       Slowdown anomaly fires when:
#           CurrentAvgSpeed < BaselineAvgSpeed * alpha
#
# m   — number of consecutive congested/severe windows required
#       before an alert is generated (persistence requirement)

BASELINE_WINDOW_K  = 5     # use last 5 windows as baseline
BASELINE_ALPHA     = 0.7   # trigger anomaly if speed drops below 70 % of baseline
PERSISTENCE_M      = 2     # require 2 consecutive bad windows before alerting


# ─── SEGMENT LENGTH METADATA (km) ───────────────────────────
# Used by aggregation_service.py to compute density_proxy.
# Add a key for every segment monitored by the system.
# Format: "Segment Name": length_in_km

SEGMENT_LENGTH_KM: dict = {
    "street1 St": 0.5,
    "street2 St": 0.8,
    "street3 St": 1.0,
}
DEFAULT_SEGMENT_LENGTH_KM = 1.0   # fallback when segment is not in the dict above


# ─── GOOGLE DIRECTIONS API ──────────────────────────────────
# Server-side key (NOT the Android/iOS client key).
# Keep this in config and never commit the real value to Git.
# Replace the placeholder before deploying.
DIRECTIONS_API_KEY = "AIzaSyCvPDTWxqxfc8DGw4j0k67N0RQFQ1Qx-E4"


# ─── FIREBASE SETTINGS ──────────────────────────────────────
# Path to the Firebase service account key file.
# IMPORTANT: never push this file to GitHub.
FIREBASE_CREDENTIALS_PATH = "serviceAccountKey.json"
