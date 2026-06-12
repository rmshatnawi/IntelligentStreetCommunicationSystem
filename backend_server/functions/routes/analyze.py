# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     routes/analyze.py
# Author:   Raghad Shatnawi
# Last Modified: April 2026
# Author:   Batool Alkhateeb
# Last Modified: June 2026
# Purpose:  Analyzes traffic signals for a given road segment.
#           Implements the full server pipeline from the GP1
#           report (Stages 3-5):
#             Stage 3 — Aggregation & Analytics
#             Stage 4 — Rule-based State Classification
#             Stage 5 — Alert Generation with baseline
#                       comparison and persistence check
#
#           Auth: public_safety and admin only.
# ============================================================

from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter

from config import (
    SIGNALS_COLLECTION,
    ALERTS_COLLECTION,
    SEGMENTS_COLLECTION,
    BASELINES_COLLECTION,
    SPEED_FREE_FLOW,
    SPEED_MODERATE,
    SPEED_CONGESTED,
    BASELINE_WINDOW_K,
    BASELINE_ALPHA,
    PERSISTENCE_M,
)
from models.signal_model import (
    TrafficAlert,          alert_to_dict,
    SegmentTrafficSummary, summary_to_dict,
)
from core.auth import require_public_safety
from models.user_model import AuthenticatedUser

router = APIRouter()


# ─── determine_traffic_status() ─────────────────────────────
# Speed-only classification used by the on-demand /analyze route.
# The aggregation_service uses the richer classify_traffic()
# which also considers density_proxy.

def determine_traffic_status(avg_speed: float) -> str:
    if avg_speed >= SPEED_FREE_FLOW:
        return "free"
    elif avg_speed >= SPEED_MODERATE:
        return "moderate"
    elif avg_speed >= SPEED_CONGESTED:
        return "congested"
    else:
        return "severe"


# ─── _get_rolling_baseline() ─────────────────────────────────
# Reads the last k SegmentTrafficSummary documents for the
# segment and returns (baseline_avg_speed, baseline_flow_rate).
# Returns (None, None) when there is not enough history yet.

def _get_rolling_baseline(segment: str, db, k: int = BASELINE_WINDOW_K):
    docs = (
        db.collection(SEGMENTS_COLLECTION)
        .where(filter=FieldFilter("segment", "==", segment))
        .order_by("computed_at", direction="DESCENDING")
        .limit(k)
        .stream()
    )
    summaries = [d.to_dict() for d in docs]
    if not summaries:
        return None, None

    speeds     = [s["avg_speed"]  for s in summaries if s.get("avg_speed")  is not None]
    flow_rates = [s["flow_rate"]  for s in summaries if s.get("flow_rate")  is not None]

    baseline_speed     = round(sum(speeds)     / len(speeds),     2) if speeds     else None
    baseline_flow_rate = round(sum(flow_rates) / len(flow_rates), 2) if flow_rates else None
    return baseline_speed, baseline_flow_rate


# ─── _get_persistence_count() ────────────────────────────────
# Returns how many of the last m summaries for this segment
# have a congested or severe traffic_state.
# Used to enforce the persistence requirement before firing an alert.

def _get_persistence_count(segment: str, db, m: int = PERSISTENCE_M) -> int:
    docs = (
        db.collection(SEGMENTS_COLLECTION)
        .where(filter=FieldFilter("segment", "==", segment))
        .order_by("computed_at", direction="DESCENDING")
        .limit(m)
        .stream()
    )
    count = 0
    for d in docs:
        state = d.to_dict().get("traffic_state", "free")
        if state in ("congested", "severe"):
            count += 1
    return count


# ─── _should_generate_alert() ────────────────────────────────
# Decides whether an alert should be saved for this analysis.
# Implements Stage 5 rules from the GP1 report:
#
#   Rule A — State transition into congested/severe
#             (traffic is currently bad regardless of history)
#
#   Rule B — Persistence requirement
#             Alert only if congested/severe state has persisted
#             for PERSISTENCE_M consecutive windows.
#
#   Rule C — Abnormal slowdown vs rolling baseline
#             Trigger when CurrentAvgSpeed < BaselineAvgSpeed * BASELINE_ALPHA
#             even if the raw threshold was not crossed.
#
# Returns (should_alert: bool, trigger_reason: str)

def _should_generate_alert(
    status: str,
    avg_speed: float,
    baseline_speed,
    persistence_count: int,
) -> tuple[bool, str]:

    # Rule C — baseline-aware anomaly (fires for any state)
    if baseline_speed is not None and avg_speed < baseline_speed * BASELINE_ALPHA:
        return True, "baseline_deviation"

    # Rules A+B only apply when state is already congested or severe
    if status not in ("congested", "severe"):
        return False, ""

    # Rule B — persistence: require m consecutive bad windows
    if persistence_count >= PERSISTENCE_M:
        if status == "severe":
            return True, "speed_below_severe_threshold"
        return True, "speed_below_congested_threshold"

    return False, ""


# ─── GET /analyze/{segment} ─────────────────────────────────
# On-demand analysis endpoint.
# Reads the last 10 signals, computes traffic indicators,
# applies baseline & persistence checks, and saves an alert
# and a summary to Firestore.
#
# Auth:   public_safety, admin
# URL:    GET http://<server-ip>:8000/analyze/{segment}

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
        signal_list = [s.to_dict() for s in signals_ref.stream()]

        if not signal_list:
            raise HTTPException(
                status_code=404,
                detail=f"No signals found for segment: {segment}"
            )

        # ─── STEP 2: Compute indicators (Stage 3) ───────────
        avg_speed      = round(sum(s["speed"] for s in signal_list) / len(signal_list), 2)
        total_vehicles = sum(s["vehicle_count"] for s in signal_list)

        # ─── STEP 3: Classify state (Stage 4) ───────────────
        status = determine_traffic_status(avg_speed)

        # ─── STEP 4: Rolling baseline ────────────────────────
        baseline_speed, baseline_flow = _get_rolling_baseline(segment, db)

        # ─── STEP 5: Persistence count ───────────────────────
        persistence_count = _get_persistence_count(segment, db)

        # ─── STEP 6: Build analysis result ──────────────────
        analysis = {
            "segment":           segment,
            "avg_speed":         avg_speed,
            "total_vehicles":    total_vehicles,
            "signal_count":      len(signal_list),
            "status":            status,
            "baseline_speed":    baseline_speed,
            "persistence_count": persistence_count,
            "analyzed_at":       datetime.utcnow().isoformat(),
        }

        # ─── STEP 7: Alert generation (Stage 5) ─────────────
        should_alert, trigger_reason = _should_generate_alert(
            status, avg_speed, baseline_speed, persistence_count
        )

        if should_alert:
            severity = "high" if status == "severe" else "medium"
            if trigger_reason == "baseline_deviation":
                severity = "medium"

            alert = TrafficAlert(
                segment=segment,
                alert_type=(
                    "abnormal_slowdown"
                    if trigger_reason == "baseline_deviation"
                    else "congestion"
                ),
                severity=severity,
                trigger_condition=trigger_reason,
                status="active",
                avg_speed=avg_speed,
                total_vehicles=total_vehicles,
                signal_count=len(signal_list),
                traffic_status=status,
                alert_message=(
                    f"Heavy traffic on {segment} — avg speed {avg_speed} km/h"
                    if trigger_reason != "baseline_deviation"
                    else f"Abnormal slowdown on {segment} — avg speed {avg_speed} km/h "
                         f"(baseline {baseline_speed} km/h)"
                ),
            )
            db.collection(ALERTS_COLLECTION).add(alert_to_dict(alert))

            analysis["alert_generated"] = True
            analysis["alert_severity"]  = alert.severity
            analysis["alert_id"]        = alert.alert_id
            analysis["trigger_reason"]  = trigger_reason
        else:
            analysis["alert_generated"] = False

        # ─── STEP 8: Save segment summary ────────────────────
        summary = SegmentTrafficSummary(
            segment=segment,
            traffic_state=status,
            avg_speed=avg_speed,
            vehicle_count=total_vehicles,
            signal_count=len(signal_list),
        )
        db.collection(SEGMENTS_COLLECTION).add(summary_to_dict(summary))
        analysis["summary_id"] = summary.summary_id

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to analyze segment {segment}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze segment")
