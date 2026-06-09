# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     RSU_Simulator/config.py
# Author:   Raghad Shatnawi
# Date:     March 2026
# Purpose:  Configuration for the RSU Simulator.
#           Defines the server URL, RSU identities, road
#           segments, and simulation settings.
#           Change values here to adjust the simulation
#           without touching any other file.
# ============================================================


# ─── SERVER SETTINGS ────────────────────────────────────────
# URL of the FastAPI server the RSUs will send signals to.
# Change this to the deployed server URL when going to production.
SERVER_URL = "http://localhost:8000"


# ─── SIMULATION SETTINGS ────────────────────────────────────
# How often each RSU sends a signal (in seconds)
SIGNAL_INTERVAL = 20       # send a signal every 20 seconds

# How many signals to send before stopping (None = run forever)
MAX_SIGNALS = None


# ─── RSU DEFINITIONS ────────────────────────────────────────
# Each RSU has an ID and is assigned to a road segment.
# Add more RSUs here to simulate a larger city network.
#
# Future improvement: load this from a database or config file
# so RSUs can be added without changing code.

RSUS = [
    {
        "rsu_id":  "RSU_01",
        "segment": "Petra St.",
        "direction": "Northbound",
        "lat": 32.49881838862495,
        "lng": 35.98445671317814
    },
    {
        "rsu_id":  "RSU_02",
        "segment": "Petra St.",
        "direction": "Southbound",
        "lat": 32.50376051952631,
        "lng": 35.933664952564776
    },
    {
        "rsu_id":  "RSU_03",
        "segment": "Petra St.",
        "direction": "Eastbound",
        "lat": 32.523566536629296,
        "lng": 35.90131674696526
    },
]

# class Rsu {
#   final String id;
#   final String segment;
#   final double lat;
#   final double lng;
#   const Rsu(this.id, this.segment, this.lat, this.lng);

#   LatLng get position => LatLng(lat, lng);
# }

# const List<Rsu> kRsus = [
#   // Road A — 3 RSUs on the same segment.
#   Rsu('RSU_01', 'Petra St.', 32.49881838862495, 35.98445671317814),
#   Rsu('RSU_02', 'Petra St.', 32.50376051952631, 35.933664952564776),
#   Rsu('RSU_03', 'Petra St.', 32.523566536629296, 35.90131674696526),

#   //Rsu('RSU_04', 'Petra St.', 32.53802806187248, 35.8810722338297),
# ];


# ─── SPEED SIMULATION RANGES ────────────────────────────────
# Random speed will be picked between MIN and MAX for each signal.
# These represent realistic traffic conditions in km/h.
SPEED_MIN = 10    # severe congestion
SPEED_MAX = 80    # free flow

# Random vehicle count range per signal
VEHICLE_COUNT_MIN = 1
VEHICLE_COUNT_MAX = 15