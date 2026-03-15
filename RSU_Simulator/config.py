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
SIGNAL_INTERVAL = 5       # send a signal every 5 seconds

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
        "segment": "Petra St",
        "direction": "Northbound"
    },
    {
        "rsu_id":  "RSU_02",
        "segment": "Queen Alia St",
        "direction": "Southbound"
    },
    {
        "rsu_id":  "RSU_03",
        "segment": "University St",
        "direction": "Eastbound"
    },
]


# ─── SPEED SIMULATION RANGES ────────────────────────────────
# Random speed will be picked between MIN and MAX for each signal.
# These represent realistic traffic conditions in km/h.
SPEED_MIN = 10    # severe congestion
SPEED_MAX = 80    # free flow

# Random vehicle count range per signal
VEHICLE_COUNT_MIN = 1
VEHICLE_COUNT_MAX = 15