# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     routes/api.py
# Author:   Raghad Shatnawi
# Last Modified: 18 April 2026
# Purpose:  Provides endpoints for the Flutter mobile app.
#           Flutter calls these to display live traffic data,
#           road segment statuses, and active alerts.
#
#           All routes require authentication.
#           Role access per route:
#             /signals          — driver, public_safety, admin
#             /signals/{segment}— driver, public_safety, admin
#             /alerts           — driver, public_safety, admin
#             /alerts/{segment} — driver, public_safety, admin
# ============================================================

from fastapi import APIRouter, HTTPException, Request, Depends
from google.cloud.firestore_v1.base_query import FieldFilter

from config import SIGNALS_COLLECTION, ALERTS_COLLECTION
from core.auth import require_driver
from models.user_model import AuthenticatedUser

router = APIRouter()


# ─── GET /signals ────────────────────────────────────────────
# Returns the latest signals across all segments.
# Flutter uses this to display a live feed of RSU activity.
#
# Auth: driver, public_safety, admin
# URL:  GET http://<server-ip>:8000/signals

@router.get("/signals")
async def get_signals(
    request: Request,
    user: AuthenticatedUser = Depends(require_driver),
):
    try:
        db = request.state.db

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
# Auth: driver, public_safety, admin
# URL:  GET http://<server-ip>:8000/signals/{segment}

@router.get("/signals/{segment}")
async def get_signals_by_segment(
    segment: str,
    request: Request,
    user: AuthenticatedUser = Depends(require_driver),
):
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
# Auth: driver, public_safety, admin
# URL:  GET http://<server-ip>:8000/alerts

@router.get("/alerts")
async def get_alerts(
    request: Request,
    user: AuthenticatedUser = Depends(require_driver),
):
    try:
        db = request.state.db

        docs = (
            db.collection(ALERTS_COLLECTION)
            .order_by("generated_at", direction="DESCENDING")
            .limit(10)
            .stream()
        )

        alerts = [doc.to_dict() for doc in docs]

        return {
            "success": True,
            "count":   len(alerts),
            "alerts":  alerts,
        }

    except Exception as e:
        print(f"[ERROR] Failed to fetch alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


# ─── GET /alerts/{segment} ───────────────────────────────────
# Returns alerts for a specific road segment.
# Flutter uses this to show segment-specific warnings.
#
# Auth: driver, public_safety, admin
# URL:  GET http://<server-ip>:8000/alerts/{segment}

@router.get("/alerts/{segment}")
async def get_alerts_by_segment(
    segment: str,
    request: Request,
    user: AuthenticatedUser = Depends(require_driver),
):
    try:
        db = request.state.db

        docs = (
            db.collection(ALERTS_COLLECTION)
            .where(filter=FieldFilter("segment", "==", segment))
            .order_by("generated_at", direction="DESCENDING")
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