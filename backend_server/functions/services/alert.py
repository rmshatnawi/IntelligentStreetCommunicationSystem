# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     services/alert.py
# Author:   Dana Omar
# Last Modified: June 2026
# Author:   Batool Alkhateeb
# Last Modified: June 2026
# Purpose:  Generates traffic alerts from segment summaries.
#
#           Implements Stage 5 alert rules from the GP1 report:
#             Rule A — State transition into congested/severe
#             Rule B — Persistence requirement (m consecutive windows)
#             Rule C — Abnormal slowdown vs rolling baseline
#                      (CurrentAvgSpeed < BaselineAvgSpeed * alpha)
#
#           Called by aggregation_service.generate_summaries()
#           which passes baseline_speed and persistence_count.
# ============================================================

from models.signal_model import TrafficAlert, alert_to_dict
from config import ALERTS_COLLECTION, BASELINE_ALPHA, PERSISTENCE_M


def generate_alert(
    summary,
    db,
    baseline_speed=None,
    persistence_count: int = 0,
):
    """
    Decide whether to create a TrafficAlert and, if so, save it to Firestore.

    Parameters
    ----------
    summary          : SegmentTrafficSummary (summary_model or signal_model)
    db               : Firestore client
    baseline_speed   : float | None — rolling average speed over last k windows
    persistence_count: int          — number of recent windows in congested/severe state
    """

    alert_type        = None
    severity          = None
    trigger_condition = None
    message           = None

    # ── Rule C: Baseline deviation ────────────────────────────
    # Fires for any traffic state when speed drops well below normal.
    if (
        baseline_speed is not None
        and summary.avg_speed < baseline_speed * BASELINE_ALPHA
    ):
        alert_type        = "abnormal_slowdown"
        severity          = "medium"
        trigger_condition = "baseline_deviation"
        message = (
            f"Abnormal slowdown on {summary.segment} | "
            f"Avg speed: {summary.avg_speed} km/h "
            f"(baseline: {baseline_speed} km/h)"
        )

    # ── Rules A + B: Congested / Severe with persistence ─────
    elif summary.traffic_state in ("congested", "severe"):
        if persistence_count >= PERSISTENCE_M:
            if summary.traffic_state == "severe":
                severity          = "high"
                trigger_condition = "speed_below_severe_threshold"
            else:
                severity          = "medium"
                trigger_condition = "speed_below_congested_threshold"

            alert_type = "congestion"
            message = (
                f"Heavy traffic on {summary.segment} | "
                f"Avg speed: {summary.avg_speed} km/h | "
                f"Persisted for {persistence_count} window(s)"
            )

    # ── No alert condition met ────────────────────────────────
    if alert_type is None:
        return

    # ── Build and save the alert ─────────────────────────────
    alert = TrafficAlert(
        segment           = summary.segment,
        alert_type        = alert_type,
        severity          = severity,
        trigger_condition = trigger_condition,
        avg_speed         = summary.avg_speed,
        total_vehicles    = summary.vehicle_count,
        signal_count      = summary.signal_count,
        traffic_status    = summary.traffic_state,
        alert_message     = message,
    )

    db.collection(ALERTS_COLLECTION).add(alert_to_dict(alert))

    print(
        f"[ALERT] {summary.segment} | "
        f"{summary.traffic_state.upper()} | "
        f"Trigger={trigger_condition} | "
        f"AvgSpeed={summary.avg_speed}"
    )
