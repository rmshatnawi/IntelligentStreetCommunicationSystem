# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     services/aggregation_service.py
# Author:   Dana Omar
# Date:     May 2026
# Purpose:  Implements window-based traffic aggregation logic.
#           Reads RSU signals, groups them by road segment and
#           time window, computes traffic metrics, classifies
#           traffic state, and saves summaries to Firestore.
# ============================================================

from datetime import datetime, timedelta
from collections import defaultdict

from models.summary_model import SegmentTrafficSummary
from config import SIGNALS_COLLECTION, SEGMENTS_COLLECTION
from services.alert import generate_alert


WINDOW_SECONDS = 60


SEGMENT_LENGTH_KM = {
    "street1 St": 0.5,
    "street2 St": 0.8,
    "street3 St": 1.0,
}


def get_window_start(timestamp: datetime) -> datetime:
    return timestamp.replace(second=0, microsecond=0)


def classify_traffic(avg_speed: float, density_proxy: float) -> str:
    if avg_speed < 20 and density_proxy > 100:
        return "severe"
    elif avg_speed < 40 or density_proxy > 70:
        return "congested"
    elif avg_speed < 60 or density_proxy > 40:
        return "moderate"
    return "free"


def build_summary(segment: str, signals: list):
    window_start = get_window_start(
        signals[0].timestamp or signals[0].received_at
    )
    window_end = window_start + timedelta(seconds=WINDOW_SECONDS)

    signal_count = len(signals)
    vehicle_count = sum(s.vehicle_count for s in signals)
    avg_speed = sum(s.speed for s in signals) / signal_count
    flow_rate = vehicle_count / (WINDOW_SECONDS / 60)

    segment_length = SEGMENT_LENGTH_KM.get(segment, 1.0)
    density_proxy = vehicle_count / segment_length

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


def generate_summaries(db):
    # Process only the last completed 60-second window.
    # Example: if current time is 12:33:10,
    # this processes 12:32:00 → 12:33:00.
    now = datetime.utcnow()
    window_end = get_window_start(now)
    window_start = window_end - timedelta(seconds=WINDOW_SECONDS)

    docs = (
        db.collection(SIGNALS_COLLECTION)
        .where("timestamp", ">=", window_start.isoformat())
        .where("timestamp", "<", window_end.isoformat())
        .stream()
    )

    grouped_signals = defaultdict(list)

    for doc in docs:
        data = doc.to_dict()

        timestamp = data.get("timestamp")
        if not timestamp:
            continue

        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        signal_window_start = get_window_start(timestamp)

        key = (
            data["segment"],
            signal_window_start,
        )

        grouped_signals[key].append(data)

    for (segment, _), signals_data in grouped_signals.items():

        class SignalObject:
            pass

        signals = []

        for item in signals_data:
            signal = SignalObject()

            signal.segment = item["segment"]
            signal.speed = item["speed"]
            signal.vehicle_count = item["vehicle_count"]

            signal.timestamp = (
                datetime.fromisoformat(item["timestamp"])
                if isinstance(item["timestamp"], str)
                else item["timestamp"]
            )

            signal.received_at = signal.timestamp
            signals.append(signal)

        summary = build_summary(segment, signals)

        summary_data = summary.model_dump()

        summary_data["window_start"] = summary.window_start.isoformat()
        summary_data["window_end"] = summary.window_end.isoformat()
        summary_data["computed_at"] = summary.computed_at.isoformat()

        doc_id = (
            f"{segment}_{summary.window_start.isoformat()}"
            .replace(" ", "_")
            .replace(":", "-")
        )

        print(
            f"[SUMMARY] Segment={segment} | "
            f"Window={summary.window_start} | "
            f"AvgSpeed={summary.avg_speed} | "
            f"Vehicles={summary.vehicle_count} | "
            f"Flow={summary.flow_rate} | "
            f"Density={summary.density_proxy} | "
            f"State={summary.traffic_state}"
        )

        db.collection(SEGMENTS_COLLECTION)\
            .document(doc_id)\
            .set(summary_data)

        generate_alert(summary, db)
