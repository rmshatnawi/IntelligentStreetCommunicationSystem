# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     RSU_Simulator/models/signal.py
# Author:   Raghad Shatnawi
# Date:     March 2026
# Purpose:  Defines the signal data structure used by the
#           RSU Simulator when building signals to send
#           to the server.
# Updates (May 2026 - Dana Omar)
#   - Added plate_number field to generated signals.
#   - Added vehicle identification support.
#   - Added Stolen Car Detection support. 
# ============================================================

import uuid
from datetime import datetime


# ─── build_signal() ─────────────────────────────────────────
# Builds a signal dictionary ready to be sent to the server.
#
# Parameters:
#   rsu_id        — ID of the RSU sending this signal e.g. "RSU_01"
#   segment       — road segment name e.g. "Petra St"
#   speed         — detected average speed in km/h
#   vehicle_count — number of vehicles detected
#   direction     — direction of travel e.g. "Northbound" (optional)
#
# Returns:
#   A dictionary matching the server's expected signal structure
def build_signal(
    rsu_id:        str,
    segment:       str,
    speed:         float,
    vehicle_count: int,
    direction:     str = "Unknown",
    plate_number:  str = "Unknown"
) -> dict:

    return {
        "event_id":      str(uuid.uuid4()),         # unique ID for every signal
        "rsu_id":        rsu_id,
        "segment":       segment,
        "timestamp":     datetime.utcnow().isoformat(),
        "speed":         speed,
        "direction":     direction,
        "vehicle_count": vehicle_count,
        "plate_number":  plate_number,
    }
