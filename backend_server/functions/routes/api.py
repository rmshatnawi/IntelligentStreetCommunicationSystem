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
#           Role access per route:
#             /signals            — driver, public_safety, admin
#             /signals/{segment}  — driver, public_safety, admin
#             /alerts             — driver, public_safety, admin
#             /alerts/{segment}   — driver, public_safety, admin
#             /state              — OPEN (auth disabled, see note below)
#
#           NOTE: /state currently has no auth dependency. Re-enable
#           require_driver on it once the Flutter app sends a token.
# ============================================================

import requests as http_requests
from fastapi import APIRouter, HTTPException, Request, Depends
from google.cloud.firestore_v1.base_query import FieldFilter
from collections import defaultdict

from config import SIGNALS_COLLECTION, ALERTS_COLLECTION, DIRECTIONS_API_KEY
from core.auth import require_driver
from models.user_model import AuthenticatedUser
from routes.analyze import determine_traffic_status


router = APIRouter()

# Road shapes never change, so each piece is fetched once and reused.
# Failures are also cached (as a straight line) so a bad/disabled
# Directions key does not trigger a fresh Google call on every poll.
_edge_cache: dict = {}


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


def _order_rsus(rsus: list):
    # Order the RSUs along the road's dominant axis (E-W or N-S).
    if len(rsus) <= 2:
        return rsus
    lat_span = max(r["lat"] for r in rsus) - min(r["lat"] for r in rsus)
    lng_span = max(r["lng"] for r in rsus) - min(r["lng"] for r in rsus)
    axis = "lat" if lat_span > lng_span else "lng"
    return sorted(rsus, key=lambda r: r[axis])


def _edge_path(a: dict, b: dict):
    # Road-following shape between two consecutive RSUs, cached.
    key = f'{a["rsu_id"]}->{b["rsu_id"]}'
    if key in _edge_cache:
        return _edge_cache[key]

    straight = [{"lat": a["lat"], "lng": a["lng"]},
                {"lat": b["lat"], "lng": b["lng"]}]

    # No key configured -> skip Google entirely, use a straight line.
    if not DIRECTIONS_API_KEY:
        _edge_cache[key] = straight
        return straight

    params = {
        "origin":      f'{a["lat"]},{a["lng"]}',
        "destination": f'{b["lat"]},{b["lng"]}',
        "key":         DIRECTIONS_API_KEY,
    }

    try:
        r = http_requests.get(
            "https://maps.googleapis.com/maps/api/directions/json",
            params=params, timeout=6,
        )
        data = r.json()
        if data.get("status") == "OK":
            path = _decode_polyline(data["routes"][0]["overview_polyline"]["points"])
            _edge_cache[key] = path
            return path
        print(f"[DIR] {key} status={data.get('status')} {data.get('error_message', '')}")
    except Exception as e:
        print(f"[DIR] {key} EXCEPTION {e!r}")

    # Cache the fallback so we stop refetching on every /state poll.
    _edge_cache[key] = straight
    return straight


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
# Per-RSU status + a colored road piece between each pair of RSUs.
# Flutter draws one line per piece and colors each marker by its RSU.
# Auth is currently disabled. To require a logged-in driver again,
# uncomment the dependency below.
@router.get("/state")
async def get_state(
    request: Request,
    # user: AuthenticatedUser = Depends(require_driver),
):
    db = request.state.db
    docs = (
        db.collection(SIGNALS_COLLECTION)
        .order_by("received_at", direction="DESCENDING")
        .limit(2000)
        .stream()
    )
    signals = [d.to_dict() for d in docs]

    # Average speed and position per RSU.
    speeds_by_rsu = defaultdict(list)
    meta = {}  # rsu_id -> {rsu_id, lat, lng, segment}
    for s in signals:
        seg = s.get("segment")
        rid = s.get("rsu_id")
        if seg is None or rid is None:
            continue
        if s.get("speed") is not None:
            speeds_by_rsu[rid].append(s["speed"])
        if rid not in meta and s.get("lat") is not None:
            meta[rid] = {
                "rsu_id":  rid,
                "lat":     s["lat"],
                "lng":     s["lng"],
                "segment": seg,
            }

    # Group RSUs by segment, with each RSU's own status.
    by_segment = defaultdict(list)
    for rid, m in meta.items():
        sp = speeds_by_rsu.get(rid, [])
        avg = sum(sp) / len(sp) if sp else None
        entry = dict(m)
        entry["avg_speed"] = round(avg, 1) if avg is not None else None
        entry["status"] = determine_traffic_status(avg) if avg is not None else "free"
        by_segment[m["segment"]].append(entry)

    # Build one colored edge between each consecutive pair of RSUs.
    segments = []
    for seg, rsus in by_segment.items():
        ordered = _order_rsus(rsus)
        edges = []
        for i in range(len(ordered) - 1):
            a, b = ordered[i], ordered[i + 1]
            vals = [v for v in (a["avg_speed"], b["avg_speed"]) if v is not None]
            eavg = sum(vals) / len(vals) if vals else None
            edges.append({
                "status":    determine_traffic_status(eavg) if eavg is not None else "free",
                "avg_speed": round(eavg, 1) if eavg is not None else None,
                "path":      _edge_path(a, b),
            })
        segments.append({
            "segment": seg,
            "rsus":    ordered,
            "edges":   edges,
        })

    return {"success": True, "segments": segments}