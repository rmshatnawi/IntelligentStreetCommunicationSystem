# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     routes/api.py
# Author:   Raghad Shatnawi
# Last Modified: April 2026
# Author:   Batool Alkhateeb
# Last Modified: June 2026
# Purpose:  Provides endpoints for the Flutter mobile app.
#           Flutter calls these to display live traffic data,
#           road segment statuses, and active alerts.
#
#           All routes require authentication.
#           Role access per route:
#             /signals            — driver, public_safety, admin
#             /signals/{segment}  — driver, public_safety, admin
#             /alerts             — driver, public_safety, admin
#             /alerts/{segment}   — driver, public_safety, admin
#             /state              — driver, public_safety, admin
# ============================================================

import requests                                       # ← fix: was missing
from fastapi import APIRouter, HTTPException, Request, Depends
from google.cloud.firestore_v1.base_query import FieldFilter
from collections import defaultdict

from config import SIGNALS_COLLECTION, ALERTS_COLLECTION, DIRECTIONS_API_KEY  # ← key from config
from core.auth import require_driver
from models.user_model import AuthenticatedUser
from routes.analyze import determine_traffic_status


router = APIRouter()

# Road shapes never change, so we fetch each one once and reuse it.
_path_cache: dict = {}


def _decode_polyline(encoded: str):
    """Decode a Google encoded polyline into a list of {lat, lng} dicts."""
    points, index, lat, lng = [], 0, 0, 0
    while index < len(encoded):
        for is_lat in (True, False):
            shift = result = 0
            while True:
                b = ord(encoded[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            delta = ~(result >> 1) if (result & 1) else (result >> 1)
            if is_lat:
                lat += delta
            else:
                lng += delta
        points.append({"lat": lat / 1e5, "lng": lng / 1e5})
    return points


def _road_path(segment: str, pts: list):
    """Return the road-following polyline for a segment, cached after first fetch."""
    if segment in _path_cache:
        return _path_cache[segment]

    straight = [{"lat": p["lat"], "lng": p["lng"]} for p in pts]
    if len(pts) < 2:
        return straight

    ordered = sorted(pts, key=lambda p: p["lng"])
    params = {
        "origin":      f'{ordered[0]["lat"]},{ordered[0]["lng"]}',
        "destination": f'{ordered[-1]["lat"]},{ordered[-1]["lng"]}',
        "key":         DIRECTIONS_API_KEY,
    }
    mid = ordered[1:-1]
    if mid:
        params["waypoints"] = "|".join(f'{w["lat"]},{w["lng"]}' for w in mid)

    try:
        r = requests.get(
            "https://maps.googleapis.com/maps/api/directions/json",
            params=params, timeout=6,
        )
        data = r.json()
        if data.get("status") == "OK":
            path = _decode_polyline(data["routes"][0]["overview_polyline"]["points"])
            _path_cache[segment] = path
            return path
        print(f"[DIRECTIONS] {segment}: {data.get('status')} {data.get('error_message', '')}")
    except Exception as e:
        print(f"[DIRECTIONS] {segment}: {e}")

    return straight   # fall back to straight line on any failure


# ─── GET /signals ────────────────────────────────────────────
@router.get("/signals")
async def get_signals(
    request: Request,
    user: AuthenticatedUser = Depends(require_driver),
):
    try:
        docs = (
            request.state.db.collection(SIGNALS_COLLECTION)
            .order_by("received_at", direction="DESCENDING")
            .limit(20)
            .stream()
        )
        signals = [doc.to_dict() for doc in docs]
        return {"success": True, "count": len(signals), "signals": signals}

    except Exception as e:
        print(f"[ERROR] Failed to fetch signals: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch signals")


# ─── GET /signals/{segment} ──────────────────────────────────
@router.get("/signals/{segment}")
async def get_signals_by_segment(
    segment: str,
    request: Request,
    user: AuthenticatedUser = Depends(require_driver),
):
    try:
        docs = (
            request.state.db.collection(SIGNALS_COLLECTION)
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
        return {"success": True, "segment": segment, "count": len(signals), "signals": signals}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to fetch signals for {segment}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch signals")


# ─── GET /alerts ─────────────────────────────────────────────
@router.get("/alerts")
async def get_alerts(
    request: Request,
    user: AuthenticatedUser = Depends(require_driver),
):
    try:
        docs = (
            request.state.db.collection(ALERTS_COLLECTION)
            .order_by("generated_at", direction="DESCENDING")
            .limit(10)
            .stream()
        )
        alerts = [doc.to_dict() for doc in docs]
        return {"success": True, "count": len(alerts), "alerts": alerts}

    except Exception as e:
        print(f"[ERROR] Failed to fetch alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


# ─── GET /alerts/{segment} ───────────────────────────────────
@router.get("/alerts/{segment}")
async def get_alerts_by_segment(
    segment: str,
    request: Request,
    user: AuthenticatedUser = Depends(require_driver),
):
    try:
        docs = (
            request.state.db.collection(ALERTS_COLLECTION)
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
        return {"success": True, "segment": segment, "count": len(alerts), "alerts": alerts}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to fetch alerts for {segment}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


# ─── GET /state ──────────────────────────────────────────────
# Returns the current traffic state for every segment.
# Flutter uses this to colour-code roads on the map.
# Privacy: returns only aggregated summaries (no raw event data,
# no RSU identifiers exposed beyond what is needed for map pins).

@router.get("/state")
async def get_state(
    request: Request,
    user: AuthenticatedUser = Depends(require_driver),
):
    db = request.state.db
    docs = (
        db.collection(SIGNALS_COLLECTION)
        .order_by("received_at", direction="DESCENDING")
        .limit(40)
        .stream()
    )
    signals = [d.to_dict() for d in docs]

    speeds = defaultdict(list)
    points = defaultdict(dict)   # segment -> {rsu_id: point}
    for s in signals:
        seg = s.get("segment")
        if seg is None:
            continue
        if s.get("speed") is not None:
            speeds[seg].append(s["speed"])
        rid = s.get("rsu_id")
        if rid and rid not in points[seg] and s.get("lat") is not None:
            points[seg][rid] = {"rsu_id": rid, "lat": s["lat"], "lng": s["lng"]}

    segments = []
    for seg, sp in speeds.items():
        avg  = sum(sp) / len(sp)
        rsus = list(points[seg].values())
        segments.append({
            "segment":   seg,
            "status":    determine_traffic_status(avg),
            "avg_speed": round(avg, 1),
            "rsus":      rsus,
            "path":      _road_path(seg, rsus),
        })

    return {"success": True, "segments": segments}
