# # ============================================================
# # Project:  Intelligent Street Communication System (ISCS)
# # File:     RSU_Simulator/config.py
# # Author:   Raghad Shatnawi
# # Date:     March 2026
# # Purpose:  Configuration for the RSU Simulator.
# #           Defines the server URL, RSU identities, road
# #           segments, and simulation settings.
# #           Change values here to adjust the simulation
# #           without touching any other file.
# # ============================================================


# # ─── SERVER SETTINGS ────────────────────────────────────────
# # URL of the FastAPI server the RSUs will send signals to.
# # Change this to the deployed server URL when going to production.
# SERVER_URL = "http://localhost:8000"


# # ─── SIMULATION SETTINGS ────────────────────────────────────
# # How often each RSU sends a signal (in seconds)
# SIGNAL_INTERVAL = 60       # send a signal every 60 seconds

# # How many signals to send before stopping (None = run forever)
# MAX_SIGNALS = 30


# # ─── RSU DEFINITIONS ────────────────────────────────────────
# # Each RSU has an ID and is assigned to a road segment.
# # Add more RSUs here to simulate a larger city network.
# #
# # Future improvement: load this from a database or config file
# # so RSUs can be added without changing code.

# # RSUS = [
# #     {
# #         "rsu_id":  "RSU_01",
# #         "segment": "Petra St.",
# #         "direction": "Northbound",
# #         "lat": 32.49881838862495,
# #         "lng": 35.98445671317814
# #     },
# #     {
# #         "rsu_id":  "RSU_02",
# #         "segment": "Petra St.",
# #         "direction": "Southbound",
# #         "lat": 32.50376051952631,
# #         "lng": 35.933664952564776
# #     },
# #     {
# #         "rsu_id":  "RSU_03",
# #         "segment": "Petra St.",
# #         "direction": "Eastbound",
# #         "lat": 32.523566536629296,
# #         "lng": 35.90131674696526
# #     },
# # ]

# RSUS = [
#     {
#         "rsu_id": "RSU_01",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.49864319886971,
#         "lng": 35.98470036585473
#     },
#     {
#         "rsu_id": "RSU_02",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.500719751935,
#         "lng": 35.97792427671671
#     },
#     {
#         "rsu_id": "RSU_03",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.500774275135896,
#         "lng": 35.972406653154636
#     },
#     {
#         "rsu_id": "RSU_04",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.50086462795687,
#         "lng": 35.965555729061535
#     },
#     {
#         "rsu_id": "RSU_05",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.50092969808298,
#         "lng": 35.96046666556648
#     },
#     {
#         "rsu_id": "RSU_06",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.50098843720988,
#         "lng": 35.95421423482554
#     },
#     {
#         "rsu_id": "RSU_07",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.5010620983619,
#         "lng": 35.94981952530449
#     },
#     {
#         "rsu_id": "RSU_08",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.50115442548511,
#         "lng": 35.943733038636516
#     },
#     {
#         "rsu_id": "RSU_09",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.50215525640411,
#         "lng": 35.93793353679571
#     },
#     {
#         "rsu_id": "RSU_10",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.5037220780586,
#         "lng": 35.93405115296471
#     },
#     {
#         "rsu_id": "RSU_11",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.50644231885107,
#         "lng": 35.929706034194794
#     },
#     {
#         "rsu_id": "RSU_12",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.51034358248065,
#         "lng": 35.92386964833044
#     },
#     {
#         "rsu_id": "RSU_13",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.51788740546464,
#         "lng": 35.912577459505236
#     },
#     {
#         "rsu_id": "RSU_14",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.522638492938604,
#         "lng": 35.903318253173325
#     },
#     {
#         "rsu_id": "RSU_15",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.52348462486957,
#         "lng": 35.90128304825863
#     },
#     {
#         "rsu_id": "RSU_16",
#         "segment": "Petra St.",
#         "direction": "Northbound",
#         "lat": 32.52656217971231,
#         "lng": 35.896098203573985
#     }
# ]


# # ─── SPEED SIMULATION RANGES ────────────────────────────────
# # Random speed will be picked between MIN and MAX for each signal.
# # These represent realistic traffic conditions in km/h.
# SPEED_MIN = 10    # severe congestion
# SPEED_MAX = 80    # free flow

# # Random vehicle count range per signal
# VEHICLE_COUNT_MIN = 1
# VEHICLE_COUNT_MAX = 15

# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     RSU_Simulator/config.py
# Purpose:  Configuration for the RSU Simulator.
#           Server URL, RSU identities, road geometry,
#           vehicle behavior, traffic light, simulation timing.
# ============================================================


# # ─── SERVER SETTINGS ────────────────────────────────────────
# SERVER_URL = "http://localhost:8000"

# # RSU detection events are POSTed here.
# INGEST_ENDPOINT = "/ingest"

# # Traffic-light map object + state changes are POSTed here.
# # The server must expose this endpoint for the light to appear
# # on the map. Set SEND_LIGHT_EVENTS = False if it does not.
# LIGHT_ENDPOINT = "/light"
# SEND_LIGHT_EVENTS = False


# # ─── SIMULATION TIMING ──────────────────────────────────────
# # Simulated seconds advanced per loop tick. Timestamps and
# # travel time use this clock, so they stay realistic regardless
# # of how fast the loop runs in wall-clock time.
# SIM_TICK_SECONDS = 1.0

# # Wall-clock sleep per tick. Smaller = faster playback.
# # 0.05 -> simulation runs ~20x faster than real time.
# REAL_TICK_SECONDS = 0.05


# # ─── VEHICLE SETTINGS ───────────────────────────────────────
# VEHICLE_CRUISE_SPEED = 50.0    # km/h, constant cruise speed
# VEHICLE_PLATE        = "ABC-123"
# VEHICLE_ID           = "VEH_0001"


# # ─── TRAFFIC LIGHT ──────────────────────────────────────────
# # Positioned between RSU_15 and RSU_16. Coordinates are the
# # midpoint of that segment. Adjust lat/lng to move the light.
# TRAFFIC_LIGHT = {
#     "light_id":      "TL_01",
#     "segment":       "Petra St.",
#     "between":       ["RSU_15", "RSU_16"],
#     "lat":           32.525023,
#     "lng":           35.898690,
#     "green_seconds": 30,
#     "red_seconds":   25,
# }

# # With one vehicle, force the light RED the moment the vehicle
# # reaches it, hold for red_seconds, then GREEN. Guarantees the
# # required visible stop before RSU_16. For multi-vehicle runs
# # set this False and the light cycles on green/red_seconds.
# DEMO_FORCE_STOP = True


# # ─── RSU DEFINITIONS (ROAD GEOMETRY) ────────────────────────
# # Ordered RSU_01 -> RSU_16. The vehicle travels this polyline
# # in order. The order defines the road; do not shuffle it.
# RSUS = [
#     {"rsu_id": "RSU_01", "segment": "Petra St.", "direction": "Northbound", "lat": 32.49864319886971, "lng": 35.98470036585473},
#     {"rsu_id": "RSU_02", "segment": "Petra St.", "direction": "Northbound", "lat": 32.500719751935,   "lng": 35.97792427671671},
#     {"rsu_id": "RSU_03", "segment": "Petra St.", "direction": "Northbound", "lat": 32.500774275135896,"lng": 35.972406653154636},
#     {"rsu_id": "RSU_04", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50086462795687, "lng": 35.965555729061535},
#     {"rsu_id": "RSU_05", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50092969808298, "lng": 35.96046666556648},
#     {"rsu_id": "RSU_06", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50098843720988, "lng": 35.95421423482554},
#     {"rsu_id": "RSU_07", "segment": "Petra St.", "direction": "Northbound", "lat": 32.5010620983619,  "lng": 35.94981952530449},
#     {"rsu_id": "RSU_08", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50115442548511, "lng": 35.943733038636516},
#     {"rsu_id": "RSU_09", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50215525640411, "lng": 35.93793353679571},
#     {"rsu_id": "RSU_10", "segment": "Petra St.", "direction": "Northbound", "lat": 32.5037220780586,  "lng": 35.93405115296471},
#     {"rsu_id": "RSU_11", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50644231885107, "lng": 35.929706034194794},
#     {"rsu_id": "RSU_12", "segment": "Petra St.", "direction": "Northbound", "lat": 32.51034358248065, "lng": 35.92386964833044},
#     {"rsu_id": "RSU_13", "segment": "Petra St.", "direction": "Northbound", "lat": 32.51788740546464, "lng": 35.912577459505236},
#     {"rsu_id": "RSU_14", "segment": "Petra St.", "direction": "Northbound", "lat": 32.522638492938604,"lng": 35.903318253173325},
#     {"rsu_id": "RSU_15", "segment": "Petra St.", "direction": "Northbound", "lat": 32.52348462486957, "lng": 35.90128304825863},
#     {"rsu_id": "RSU_16", "segment": "Petra St.", "direction": "Northbound", "lat": 32.52656217971231, "lng": 35.896098203573985},
# ]


# # ─── LEGACY (unused by the tracked-vehicle flow) ────────────
# SIGNAL_INTERVAL   = 60
# MAX_SIGNALS       = 30
# SPEED_MIN         = 10
# SPEED_MAX         = 80
# VEHICLE_COUNT_MIN = 1
# VEHICLE_COUNT_MAX = 15

# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     RSU_Simulator/config.py
# Purpose:  Configuration for the RSU Simulator.
#           Real-time traffic: vehicles enter at RSU_01 and
#           move along the road; RSUs detect them live.
# ============================================================


# --- SERVER SETTINGS ----------------------------------------
SERVER_URL = "http://localhost:8000"
INGEST_ENDPOINT = "/ingest"

# Traffic-light map object endpoint. Your server returned 404
# for this, so it is OFF. Turn it on only after adding /light.
LIGHT_ENDPOINT = "/light"
SEND_LIGHT_EVENTS = False


# --- SIMULATION TIMING (REAL TIME) --------------------------
# 1 simulated second == 1 wall-clock second.
# Detections fire live as vehicles pass each RSU.
SIM_TICK_SECONDS  = 1.0
REAL_TICK_SECONDS = 1.0
# To fast-forward instead of real time, lower REAL_TICK_SECONDS
# (e.g. 0.05 for ~20x speed). Keep SIM_TICK_SECONDS at 1.0.


# --- TRAFFIC GENERATION -------------------------------------
# A new vehicle enters at RSU_01 every SPAWN_INTERVAL_SECONDS.
SPAWN_INTERVAL_SECONDS = 20

# Total vehicles to release. None = keep spawning forever
# (stop with Ctrl+C).
MAX_VEHICLES = 30

# Each vehicle gets a random cruise speed in this range (km/h).
VEHICLE_SPEED_MIN = 45.0
VEHICLE_SPEED_MAX = 60.0


# --- TRAFFIC LIGHT ------------------------------------------
# Between RSU_15 and RSU_16. Cycles green -> red continuously.
# Any vehicle reaching it during red stops until green.
TRAFFIC_LIGHT = {
    "light_id":      "TL_01",
    "segment":       "Petra St.",
    "between":       ["RSU_15", "RSU_16"],
    "lat":           32.525023,
    "lng":           35.898690,
    "green_seconds": 30,
    "red_seconds":   25,
}


# --- RSU DEFINITIONS (ROAD GEOMETRY) ------------------------
# Ordered RSU_01 -> RSU_16. This order defines the road.
RSUS = [
    {"rsu_id": "RSU_01", "segment": "Petra St.", "direction": "Northbound", "lat": 32.49864319886971, "lng": 35.98470036585473},
    {"rsu_id": "RSU_02", "segment": "Petra St.", "direction": "Northbound", "lat": 32.500719751935,   "lng": 35.97792427671671},
    {"rsu_id": "RSU_03", "segment": "Petra St.", "direction": "Northbound", "lat": 32.500774275135896,"lng": 35.972406653154636},
    {"rsu_id": "RSU_04", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50086462795687, "lng": 35.965555729061535},
    {"rsu_id": "RSU_05", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50092969808298, "lng": 35.96046666556648},
    {"rsu_id": "RSU_06", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50098843720988, "lng": 35.95421423482554},
    {"rsu_id": "RSU_07", "segment": "Petra St.", "direction": "Northbound", "lat": 32.5010620983619,  "lng": 35.94981952530449},
    {"rsu_id": "RSU_08", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50115442548511, "lng": 35.943733038636516},
    {"rsu_id": "RSU_09", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50215525640411, "lng": 35.93793353679571},
    {"rsu_id": "RSU_10", "segment": "Petra St.", "direction": "Northbound", "lat": 32.5037220780586,  "lng": 35.93405115296471},
    {"rsu_id": "RSU_11", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50644231885107, "lng": 35.929706034194794},
    {"rsu_id": "RSU_12", "segment": "Petra St.", "direction": "Northbound", "lat": 32.51034358248065, "lng": 35.92386964833044},
    {"rsu_id": "RSU_13", "segment": "Petra St.", "direction": "Northbound", "lat": 32.51788740546464, "lng": 35.912577459505236},
    {"rsu_id": "RSU_14", "segment": "Petra St.", "direction": "Northbound", "lat": 32.522638492938604,"lng": 35.903318253173325},
    {"rsu_id": "RSU_15", "segment": "Petra St.", "direction": "Northbound", "lat": 32.52348462486957, "lng": 35.90128304825863},
    {"rsu_id": "RSU_16", "segment": "Petra St.", "direction": "Northbound", "lat": 32.52656217971231, "lng": 35.896098203573985},
]