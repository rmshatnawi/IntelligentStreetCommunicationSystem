# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     routes/analyze.py
# Author:   Raghad Shatnawi
# Date:     March 2026
# Purpose:  Analyzes traffic signals for a given road segment.
#           Calculates average speed, determines congestion
#           level, and generates alerts when traffic is bad.
#           This module is designed to be extended with a
#           machine learning model in the future.
# ============================================================

from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter

from config import (
    SIGNALS_COLLECTION,
    ALERTS_COLLECTION,
    SPEED_FREE_FLOW,
    SPEED_MODERATE,
    SPEED_CONGESTED,
)

router = APIRouter()


# ─── determine_traffic_status() ─────────────────────────────
# Takes an average speed and returns a traffic status string.
# Thresholds are defined in config.py so they are easy to tune.
#
# Future improvement: replace this function with an ML model
# that predicts congestion based on historical patterns.
def determine_traffic_status(avg_speed: float) -> str:
    if avg_speed >= SPEED_FREE_FLOW:
        return "free"           # traffic flowing normally
    elif avg_speed >= SPEED_MODERATE:
        return "moderate"       # some slowdown
    elif avg_speed >= SPEED_CONGESTED:
        return "congested"      # heavy traffic
    else:
        return "severe"         # near standstill


# ─── GET /analyze/{segment} ─────────────────────────────────
# Analyzes the latest signals for a specific road segment.
# Reads the last 10 signals, calculates average speed,
# determines traffic status, and saves an alert if needed.
#
# URL:    GET http://<server-ip>:8000/analyze/{segment}
# Params: segment — road segment name e.g. "Petra St."
# Returns: analysis result with traffic status and alert info
@router.get("/analyze/{segment}")
async def analyze_segment(segment: str, request: Request):

    try:
        db = request.state.db

        # ─── STEP 1: Fetch latest signals for this segment ──
        # Get the last 10 signals ordered by received_at.
        # 10 signals gives us a reliable average without
        # going too far back in time.
        from google.cloud.firestore_v1.base_query import FieldFilter

        signals_ref = (
            db.collection(SIGNALS_COLLECTION)
            .where(filter=FieldFilter("segment", "==", segment))
            .order_by("received_at", direction="DESCENDING")
            .limit(10)
        )

        signals = signals_ref.stream()
        signal_list = [s.to_dict() for s in signals]

        # ─── STEP 2: Check we have enough data ──────────────
        if not signal_list:
            raise HTTPException(
                status_code=404,
                detail=f"No signals found for segment: {segment}"
            )

        # ─── STEP 3: Calculate average speed ────────────────
        total_speed = sum(s["speed"] for s in signal_list)
        avg_speed   = total_speed / len(signal_list)

        # ─── STEP 4: Calculate total vehicle count ──────────
        total_vehicles = sum(s["vehicle_count"] for s in signal_list)

        # ─── STEP 5: Determine traffic status ───────────────
        # Uses thresholds from config.py
        # Future: replace with ML prediction
        status = determine_traffic_status(avg_speed)

        # ─── STEP 6: Build analysis result ──────────────────
        analysis = {
            "segment":        segment,
            "avg_speed":      round(avg_speed, 2),
            "total_vehicles": total_vehicles,
            "signal_count":   len(signal_list),
            "status":         status,
            "analyzed_at":    datetime.utcnow().isoformat(),
        }

        # ─── STEP 7: Save alert if traffic is bad ───────────
        # Only save to alerts collection if congested or severe.
        # Flutter app will read from alerts collection to notify drivers.
        if status in ["congested", "severe"]:
            alert = {
                **analysis,
                "alert_message": f"Heavy traffic on {segment} - avg speed {round(avg_speed, 2)} km/h",
            }
            db.collection(ALERTS_COLLECTION).add(alert)

        # ─── STEP 8: Return analysis result ─────────────────
        return analysis

    except HTTPException:
        raise

    except Exception as e:
        print(f"[ERROR] Failed to analyze segment {segment}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze segment")