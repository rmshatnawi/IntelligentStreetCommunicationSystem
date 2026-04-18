# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     routes/analyze.py
# Author:   Raghad Shatnawi
# Last Modified: 18 April 2026
# Purpose:  Analyzes traffic signals for a given road segment.
#           Calculates average speed, determines congestion
#           level, saves a SegmentTrafficSummary on every call,
#           and generates a structured TrafficAlert when
#           traffic is congested or severe.
#
#           Auth: public_safety and admin only (require_public_safety)
# ============================================================

from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter

from config import (
    SIGNALS_COLLECTION,
    ALERTS_COLLECTION,
    SEGMENTS_COLLECTION,
    SPEED_FREE_FLOW,
    SPEED_MODERATE,
    SPEED_CONGESTED,
)
from models.signal_model import (
    TrafficAlert,          alert_to_dict,
    SegmentTrafficSummary, summary_to_dict,
)
from core.auth import require_public_safety
from models.user_model import AuthenticatedUser

router = APIRouter()


# ─── determine_traffic_status() ─────────────────────────────
# Takes an average speed and returns a traffic status string.
# Thresholds are defined in config.py.
#
# Future: replace with ML model or time-windowed aggregation.

def determine_traffic_status(avg_speed: float) -> str:
    if avg_speed >= SPEED_FREE_FLOW:
        return "free"
    elif avg_speed >= SPEED_MODERATE:
        return "moderate"
    elif avg_speed >= SPEED_CONGESTED:
        return "congested"
    else:
        return "severe"


# ─── determine_severity() ────────────────────────────────────
# Maps traffic status to an alert severity level.
# congested → medium, severe → high.

def determine_severity(status: str) -> str:
    if status == "severe":
        return "high"
    return "medium"


# ─── determine_trigger_condition() ───────────────────────────
# Maps traffic status to the trigger condition that caused the alert.
# Reflects what rule fired, not just the outcome.
#
# Future: add baseline_deviation and persistence triggers
# once time-window aggregation and baseline logic are implemented.

def determine_trigger_condition(status: str) -> str:
    if status == "severe":
        return "speed_below_severe_threshold"
    return "speed_below_congested_threshold"


# ─── GET /analyze/{segment} ─────────────────────────────────
# Analyzes the latest signals for a specific road segment.
# Reads the last 10 signals, calculates average speed,
# determines traffic status, and saves a structured alert
# to Firestore if traffic is congested or severe.
#
# Auth:   public_safety, admin
# URL:    GET http://<server-ip>:8000/analyze/{segment}
# Params: segment — road segment name e.g. "Petra St"
# Returns: analysis result with traffic status and alert info

@router.get("/analyze/{segment}")
async def analyze_segment(
    segment: str,
    request: Request,
    user: AuthenticatedUser = Depends(require_public_safety),
):

    try:
        db = request.state.db

        # ─── STEP 1: Fetch latest signals ───────────────────
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
        total_speed    = sum(s["speed"] for s in signal_list)
        avg_speed      = round(total_speed / len(signal_list), 2)

        # ─── STEP 4: Calculate total vehicle count ──────────
        total_vehicles = sum(s["vehicle_count"] for s in signal_list)

        # ─── STEP 5: Determine traffic status ───────────────
        status = determine_traffic_status(avg_speed)

        # ─── STEP 6: Build analysis result ──────────────────
        analysis = {
            "segment":        segment,
            "avg_speed":      avg_speed,
            "total_vehicles": total_vehicles,
            "signal_count":   len(signal_list),
            "status":         status,
            "analyzed_at":    datetime.utcnow().isoformat(),
        }

        # ─── STEP 7: Save structured alert if traffic is bad ─
        # Only save to alerts collection if congested or severe.
        # Uses the full TrafficAlert schema from signal_model.py.
        if status in ["congested", "severe"]:

            alert = TrafficAlert(
                segment=segment,
                alert_type="congestion",
                severity=determine_severity(status),
                trigger_condition=determine_trigger_condition(status),
                status="active",
                avg_speed=avg_speed,
                total_vehicles=total_vehicles,
                signal_count=len(signal_list),
                traffic_status=status,
                alert_message=f"Heavy traffic on {segment} — avg speed {avg_speed} km/h",
            )

            db.collection(ALERTS_COLLECTION).add(alert_to_dict(alert))

            # Include alert summary in response so caller knows an alert was saved
            analysis["alert_generated"] = True
            analysis["alert_severity"]  = alert.severity
            analysis["alert_id"]        = alert.alert_id

        else:
            analysis["alert_generated"] = False

        # ─── STEP 8: Save segment traffic summary ────────────
        # Written on every analysis call regardless of traffic state.
        # window_start, window_end, flow_rate, density_proxy are
        # stubbed as None until time-window aggregation is implemented.
        summary = SegmentTrafficSummary(
            segment=segment,
            traffic_state=status,
            avg_speed=avg_speed,
            vehicle_count=total_vehicles,
            signal_count=len(signal_list),
        )

        db.collection(SEGMENTS_COLLECTION).add(summary_to_dict(summary))

        analysis["summary_id"] = summary.summary_id

        # ─── STEP 9: Return analysis result ─────────────────
        return analysis

    except HTTPException:
        raise

    except Exception as e:
        print(f"[ERROR] Failed to analyze segment {segment}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze segment")