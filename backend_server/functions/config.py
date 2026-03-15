# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     config.py
# Author:   Raghad Shatnawi
# Date:     March 2026
# Purpose:  Central configuration file for the server.
#           All settings live here so if anything changes
#           (port, collection names, etc.) we only update
#           this one file and everything else adapts.
# ============================================================


# ─── SERVER SETTINGS ────────────────────────────────────────
HOST = "0.0.0.0"   # accept connections from any machine on the network
PORT = 8000        # port the server runs on (http://localhost:8000)


# ─── FIRESTORE COLLECTION NAMES ─────────────────────────────
# These are the collection names used in Firestore database.
# Keeping them here means if we rename a collection we only
# change it in one place instead of hunting through every file.
SIGNALS_COLLECTION   = "signals"    # stores raw RSU signals
ALERTS_COLLECTION    = "alerts"     # stores generated traffic alerts
SEGMENTS_COLLECTION  = "segments"   # stores road segment summaries


# ─── TRAFFIC THRESHOLDS ─────────────────────────────────────
# These values are used by analyze.py to decide the traffic status
# of a road segment based on average speed.
# Units: km/h

SPEED_FREE_FLOW   = 60   # above this → traffic is flowing freely
SPEED_MODERATE    = 40   # between 40-60 → moderate traffic
SPEED_CONGESTED   = 20   # between 20-40 → heavy traffic
                         # below 20 → severe congestion


# ─── FIREBASE SETTINGS ──────────────────────────────────────
# Path to the Firebase service account key file.
# This file is downloaded from Firebase Console and gives our
# server permission to read/write Firestore.
# IMPORTANT: never push this file to GitHub.
FIREBASE_CREDENTIALS_PATH = "serviceAccountKey.json"