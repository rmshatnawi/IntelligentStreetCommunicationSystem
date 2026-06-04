# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     services/alert.py
# Author:   Dana Omar
# Date:     May 2026
# Purpose:  Generates traffic alerts from segment summaries.
#           Detects congested or severe traffic conditions
#           and stores alerts in Firestore.
# ============================================================

from models.signal_model import (
    TrafficAlert,
    alert_to_dict,
)

from config import ALERTS_COLLECTION


# -------------------------------------------------
# Creates alerts from traffic summaries
# -------------------------------------------------
def generate_alert(summary, db):

    # Ignore normal traffic
    if summary.traffic_state in ["free", "moderate"]:
        return

    # -------------------------------------------------
    # Determine severity and trigger condition
    # -------------------------------------------------
    if summary.traffic_state == "severe":

        severity = "high"

        trigger_condition = (
            "speed_below_severe_threshold"
        )

    else:

        severity = "medium"

        trigger_condition = (
            "speed_below_congested_threshold"
        )

    # -------------------------------------------------
    # Create alert message
    # -------------------------------------------------
    message = (
        f"Heavy traffic detected on "
        f"{summary.segment} | "
        f"Average speed: {summary.avg_speed} km/h"
    )

    # -------------------------------------------------
    # Build alert object
    # -------------------------------------------------
    alert = TrafficAlert(

        segment=summary.segment,

        alert_type="congestion",

        severity=severity,

        trigger_condition=trigger_condition,

        avg_speed=summary.avg_speed,

        total_vehicles=summary.vehicle_count,

        signal_count=summary.signal_count,

        traffic_status=summary.traffic_state,

        alert_message=message,
    )

    # Convert to dictionary
    alert_data = alert_to_dict(alert)

    # -------------------------------------------------
    # Save alert to Firestore
    # -------------------------------------------------
    db.collection(ALERTS_COLLECTION).add(alert_data)

    print(
        f"[ALERT] {summary.segment} | "
        f"{summary.traffic_state.upper()} | "
        f"AvgSpeed={summary.avg_speed}"
    )
