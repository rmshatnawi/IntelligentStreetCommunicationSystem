# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     services/aggregation_service.py
# Author:   Dana Omar
# Last Modified: May 2026
# Author:   Batool Alkhateeb
# Last Modified: June 2026
# Purpose:  Implements window-based traffic aggregation (Stage 2-5
#           of the server pipeline described in the GP1 report).
#
#   Stage 2  — Partition signals into (segment, window) pairs
#   Stage 3  — Compute avg_speed, vehicle_count, flow_rate, density_proxy
#   Stage 4  — Classify traffic state using speed + density rules
#   Stage 5  — Generate alerts with baseline comparison &
#               persistence check (k windows, alpha factor, m consecutive)
# ============================================================

from datetime import datetime, timedelta
from collections import defaultdict

from models.summary_model import SegmentTrafficSummary
from models.signal_model import RSUSignal
from config import (
    SIGNALS_COLLECTION,
    SEGMENTS_COLLECTION,
    WINDOW_SECONDS,
    SPEED_FREE_FLOW,
    SPEED_MODERATE,
    SPEED_CONGESTED,
    DENSITY_FREE_FLOW,
    DENSITY_MODERATE,
    DENSITY_CONGESTED,
    SEGMENT_LENGTH_KM,
    DEFAULT_SEGMENT_LENGTH_KM,
    BASELINE_WINDOW_K,
    BASELINE_ALPHA,
    PERSISTENCE_M,
)
from services.alert import generate_alert
from services.baseline_service import update_baseline, get_baseline


# ─── get_window_start() ──────────────────────────────────────
# Truncates a datetime to the nearest WINDOW_SECONDS boundary.

def get_window_start(timestamp: datetime) -> datetime:
    return timestamp.replace(second=0, microsecond=0)


# ─── classify_traffic() ──────────────────────────────────────
# Stage 4: rule-based state classification using speed AND density.
# Mirrors Table 2 from the GP1 report.

def classify_traffic(avg_speed: float, density_proxy: float) -> str:
    # Severe: speed very low AND density very high
    if avg_speed < SPEED_CONGESTED and density_proxy > DENSITY_CONGESTED:
        return "severe"
    # Congested: speed below moderate OR density high
    if avg_speed < SPEED_MODERATE or density_proxy > DENSITY_CONGESTED:
        return "congested"
    # Moderate: speed below free-flow OR density elevated
    if avg_speed < SPEED_FREE_FLOW or density_proxy > DENSITY_MODERATE:
        return "moderate"
    return "free"


# ─── _get_rolling_baseline() ─────────────────────────────────
# Returns (baseline_avg_speed, baseline_flow_rate) computed from
# the last k summaries for this segment.
# Returns (None, None) when there is not enough history yet.

def _get_rolling_baseline(segment: str, db):
    docs = (
        db.collection(SEGMENTS_COLLECTION)
        .where("segment", "==", segment)
        .order_by("computed_at", direction="DESCENDING")
        .limit(BASELINE_WINDOW_K)
        .stream()
    )
    rows = [d.to_dict() for d in docs]
    if not rows:
        return None, None

    speeds = [r["avg_speed"]  for r in rows if r.get("avg_speed")  is not None]
    flows  = [r["flow_rate"]  for r in rows if r.get("flow_rate")  is not None]

    b_speed = round(sum(speeds) / len(speeds), 2) if speeds else None
    b_flow  = round(sum(flows)  / len(flows),  2) if flows  else None
    return b_speed, b_flow


# ─── _get_persistence_count() ────────────────────────────────
# Returns how many of the last m summaries are congested/severe.

def _get_persistence_count(segment: str, db) -> int:
    docs = (
        db.collection(SEGMENTS_COLLECTION)
        .where("segment", "==", segment)
        .order_by("computed_at", direction="DESCENDING")
        .limit(PERSISTENCE_M)
        .stream()
    )
    count = 0
    for d in docs:
        if d.to_dict().get("traffic_state") in ("congested", "severe"):
            count += 1
    return count


# ─── build_summary() ─────────────────────────────────────────
# Builds a SegmentTrafficSummary from a list of RSUSignal objects
# belonging to the same (segment, window) group.

def build_summary(segment: str, signals: list) -> SegmentTrafficSummary:
    window_start = get_window_start(
        signals[0].timestamp or signals[0].received_at
    )
    window_end = window_start + timedelta(seconds=WINDOW_SECONDS)

    signal_count  = len(signals)
    vehicle_count = sum(s.vehicle_count for s in signals)
    avg_speed     = sum(s.speed for s in signals) / signal_count
    flow_rate     = vehicle_count / (WINDOW_SECONDS / 60)   # vehicles per minute

    segment_length = SEGMENT_LENGTH_KM.get(segment, DEFAULT_SEGMENT_LENGTH_KM)
    density_proxy  = vehicle_count / segment_length

    traffic_state = classify_traffic(avg_speed, density_proxy)

    return SegmentTrafficSummary(
        segment=segment,
        window_start=window_start,
        window_end=window_end,
        signal_count=signal_count,
        vehicle_count=vehicle_count,
        avg_speed=round(avg_speed, 2),
        flow_rate=round(flow_rate, 2),
        density_proxy=round(density_proxy, 2),
        traffic_state=traffic_state,
        computed_at=datetime.utcnow(),
    )


# ─── generate_summaries() ────────────────────────────────────
# Entry point called by the scheduler (e.g. every 60 seconds).
# Processes only the last completed time window.

def generate_summaries(db):
    now          = datetime.utcnow()
    window_end   = get_window_start(now)
    window_start = window_end - timedelta(seconds=WINDOW_SECONDS)

    # ── Fetch signals in the completed window ────────────────
    docs = (
        db.collection(SIGNALS_COLLECTION)
        .where("timestamp", ">=", window_start.isoformat())
        .where("timestamp", "<",  window_end.isoformat())
        .stream()
    )

    # ── Group by (segment, window_start) ────────────────────
    grouped: dict[tuple, list[RSUSignal]] = defaultdict(list)

    for doc in docs:
        data = doc.to_dict()

        ts = data.get("timestamp")
        if not ts:
            continue
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)

        # Re-hydrate as RSUSignal so we get proper validation
        try:
            signal = RSUSignal(
                rsu_id        = data["rsu_id"],
                segment       = data["segment"],
                speed         = data["speed"],
                vehicle_count = data["vehicle_count"],
                event_id      = data.get("event_id"),
                timestamp     = ts,
                direction     = data.get("direction", "Unknown"),
                plate_number  = data.get("plate_number"),
                lat           = data.get("lat"),
                lng           = data.get("lng"),
            )
        except Exception as e:
            print(f"[AGG] Skipping malformed signal: {e}")
            continue

        # Attach received_at for fallback in build_summary
        signal.__dict__["received_at"] = ts

        key = (data["segment"], get_window_start(ts))
        grouped[key].append(signal)

    # ── Build and save a summary for each group ──────────────
    for (segment, _), signals in grouped.items():

        summary = build_summary(segment, signals)

        # ── Baseline & persistence (Stage 5) ─────────────────
        # Read baseline BEFORE saving summary (compare against prior history)
        b_speed, _ = get_baseline(segment, db)
        persistence = _get_persistence_count(segment, db)

        # Persist summary first so the alert generator can read it
        summary_data = summary.model_dump()
        summary_data["window_start"] = summary.window_start.isoformat()
        summary_data["window_end"]   = summary.window_end.isoformat()
        summary_data["computed_at"]  = summary.computed_at.isoformat()

        doc_id = (
            f"{segment}_{summary.window_start.isoformat()}"
            .replace(" ", "_")
            .replace(":", "-")
        )

        db.collection(SEGMENTS_COLLECTION).document(doc_id).set(summary_data)

        print(
            f"[SUMMARY] Segment={segment} | "
            f"Window={summary.window_start} | "
            f"AvgSpeed={summary.avg_speed} | "
            f"Vehicles={summary.vehicle_count} | "
            f"Flow={summary.flow_rate} | "
            f"Density={summary.density_proxy} | "
            f"State={summary.traffic_state}"
        )

        # ── Update stored baseline after saving summary ────────
        update_baseline(segment, db)

        # ── Alert generation with baseline + persistence ──────
        generate_alert(
            summary,
            db,
            baseline_speed=b_speed,
            persistence_count=persistence,
        )
