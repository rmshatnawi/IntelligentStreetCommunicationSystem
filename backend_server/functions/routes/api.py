# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     routes/api.py
# Author:   Raghad Shatnawi
# Date:     March 2026
# Purpose:  Provides endpoints for the Flutter mobile app.
#           Flutter calls these to display live traffic data,
#           road segment statuses, and active alerts.
# ============================================================

from fastapi import APIRouter, HTTPException, Request
from google.cloud.firestore_v1.base_query import FieldFilter

from config import SIGNALS_COLLECTION, ALERTS_COLLECTION

router = APIRouter()


# ─── GET /signals ────────────────────────────────────────────
# Returns the latest signals across all segments.
# Flutter uses this to display a live feed of RSU activity.
#
# URL:    GET http://<server-ip>:8000/signals
# Returns: list of the last 20 signals
@router.get("/signals")
async def get_signals(request: Request):
    try:
        db = request.state.db

        # fetch last 20 signals ordered by received_at
        docs = (
            db.collection(SIGNALS_COLLECTION)
            .order_by("received_at", direction="DESCENDING")
            .limit(20)
            .stream()
        )

        signals = [doc.to_dict() for doc in docs]

        return {
            "success": True,
            "count":   len(signals),
            "signals": signals,
        }

    except Exception as e:
        print(f"[ERROR] Failed to fetch signals: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch signals")


# ─── GET /signals/{segment} ──────────────────────────────────
# Returns the latest signals for a specific road segment.
# Flutter uses this to show details when a driver taps a segment.
#
# URL:    GET http://<server-ip>:8000/signals/{segment}
# Params: segment — road segment name e.g. "Petra St"
# Returns: list of the last 10 signals for that segment
@router.get("/signals/{segment}")
async def get_signals_by_segment(segment: str, request: Request):
    try:
        db = request.state.db

        docs = (
            db.collection(SIGNALS_COLLECTION)
            .where(filter=FieldFilter("segment", "==", segment))
            .order_by("received_at", direction="DESCENDING")
            .limit(10)
            .stream()
        )

        signals = [doc.to_dict() for doc in docs]

        if not signals:
            raise HTTPException(
                status_code=404,
                detail=f"No signals found for segment: {segment}"
            )

        return {
            "success": True,
            "segment": segment,
            "count":   len(signals),
            "signals": signals,
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"[ERROR] Failed to fetch signals for {segment}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch signals")


# ─── GET /alerts ─────────────────────────────────────────────
# Returns all active traffic alerts.
# Flutter uses this to show warnings to drivers on the map.
#
# URL:    GET http://<server-ip>:8000/alerts
# Returns: list of the last 10 alerts
@router.get("/alerts")
async def get_alerts(request: Request):
    try:
        db = request.state.db

        docs = (
            db.collection(ALERTS_COLLECTION)
            .order_by("analyzed_at", direction="DESCENDING")
            .limit(10)
            .stream()
        )

        alerts = [doc.to_dict() for doc in docs]

        return {
            "success": True,
            "count":  len(alerts),
            "alerts": alerts,
        }

    except Exception as e:
        print(f"[ERROR] Failed to fetch alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


# ─── GET /alerts/{segment} ───────────────────────────────────
# Returns alerts for a specific road segment.
# Flutter uses this to show segment-specific warnings.
#
# URL:    GET http://<server-ip>:8000/alerts/{segment}
# Params: segment — road segment name e.g. "Petra St"
# Returns: list of the last 5 alerts for that segment
@router.get("/alerts/{segment}")
async def get_alerts_by_segment(segment: str, request: Request):
    try:
        db = request.state.db

        docs = (
            db.collection(ALERTS_COLLECTION)
            .where(filter=FieldFilter("segment", "==", segment))
            .order_by("analyzed_at", direction="DESCENDING")
            .limit(5)
            .stream()
        )

        alerts = [doc.to_dict() for doc in docs]

        if not alerts:
            raise HTTPException(
                status_code=404,
                detail=f"No alerts found for segment: {segment}"
            )

        return {
            "success": True,
            "segment": segment,
            "count":   len(alerts),
            "alerts":  alerts,
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"[ERROR] Failed to fetch alerts for {segment}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")