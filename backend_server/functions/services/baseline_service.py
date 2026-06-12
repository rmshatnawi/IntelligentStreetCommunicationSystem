# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     services/baseline_service.py
# Author:   Batool Alkhateeb
# Last Modified: June 2026
# Purpose:  Maintains a rolling baseline per road segment as
#           described in section "Baseline and Anomaly Logic"
#           of the GP1 report.
#
#           The baseline tracks:
#             - Baseline Average Speed  (mean of last k avg_speed values)
#             - Baseline Flow Rate      (mean of last k flow_rate values)
#
#           It is updated after every aggregation window and
#           stored in the BASELINES_COLLECTION so that it
#           survives server restarts.
#
#           Usage (called by aggregation_service after saving a summary):
#               from services.baseline_service import update_baseline, get_baseline
#               update_baseline(segment, summary, db)
#               b_speed, b_flow = get_baseline(segment, db)
# ============================================================

from datetime import datetime, timezone

from google.cloud.firestore_v1.base_query import FieldFilter

from config import (
    BASELINES_COLLECTION,
    SEGMENTS_COLLECTION,
    BASELINE_WINDOW_K,
)


def update_baseline(segment: str, db) -> dict:
    """
    Compute rolling baseline (avg speed + flow rate)
    from last K segment summaries and store it in Firestore.
    """

    docs = (
        db.collection(SEGMENTS_COLLECTION)
        .where(filter=FieldFilter("segment", "==", segment))
        .order_by("computed_at", direction="DESCENDING")
        .limit(BASELINE_WINDOW_K)
        .stream()
    )

    rows = [d.to_dict() for d in docs]

    speeds = [r["avg_speed"] for r in rows if r.get("avg_speed") is not None]
    flows = [r["flow_rate"] for r in rows if r.get("flow_rate") is not None]

    baseline = {
        "segment": segment,
        "baseline_avg_speed": round(sum(speeds) / len(speeds), 2) if speeds else None,
        "baseline_flow_rate": round(sum(flows) / len(flows), 2) if flows else None,
        "window_count": len(rows),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    doc_id = segment.replace(" ", "_")

    db.collection(BASELINES_COLLECTION).document(doc_id).set(baseline)

    print(
        f"[BASELINE] {segment} | "
        f"AvgSpeed={baseline['baseline_avg_speed']} | "
        f"FlowRate={baseline['baseline_flow_rate']} | "
        f"Windows={baseline['window_count']}"
    )

    return baseline


def get_baseline(segment: str, db) -> tuple:
    """
    Retrieve stored baseline for a segment.
    """

    doc_id = segment.replace(" ", "_")
    doc = db.collection(BASELINES_COLLECTION).document(doc_id).get()

    if not doc.exists:
        return None, None

    data = doc.to_dict()
    return data.get("baseline_avg_speed"), data.get("baseline_flow_rate")