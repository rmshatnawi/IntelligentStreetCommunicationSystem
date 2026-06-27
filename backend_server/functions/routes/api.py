# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     routes/api.py
# Author:   Raghad Shatnawi
# Last Modified: 22/06/2026
# Purpose:  Provides endpoints for the Flutter mobile app.
#           Flutter calls these to display live traffic data,
#           road segment statuses, and active alerts.
#
#           Role access per route:
#             /signals              - driver, public_safety, admin
#             /signals/{segment}    - driver, public_safety, admin
#             /alerts               - driver, public_safety, admin
#             /alerts/{segment}     - driver, public_safety, admin
#             /state                - OPEN (auth disabled)
#             /report-incident      - OPEN (no role required for testing)
#
# ============================================================

import requests as http_requests
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends
from google.cloud.firestore_v1.base_query import FieldFilter
from collections import defaultdict
from pydantic import BaseModel

from config import SIGNALS_COLLECTION, ALERTS_COLLECTION, DIRECTIONS_API_KEY
from core.auth import require_driver
from models.user_model import AuthenticatedUser
from routes.analyze import determine_traffic_status


router = APIRouter()

_edge_cache: dict = {}


def _decode_polyline(encoded: str):
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
    if len(rsus) <= 2:
        return rsus
    lat_span = max(r["lat"] for r in rsus) - min(r["lat"] for r in rsus)
    lng_span = max(r["lng"] for r in rsus) - min(r["lng"] for r in rsus)
    axis = "lat" if lat_span > lng_span else "lng"
    return sorted(rsus, key=lambda r: r[axis])


def _edge_path(a: dict, b: dict):
    key = f'{a["rsu_id"]}->{b["rsu_id"]}'
    if key in _edge_cache:
        return _edge_cache[key]

    straight = [{"lat": a["lat"], "lng": a["lng"]},
                {"lat": b["lat"], "lng": b["lng"]}]

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

    _edge_cache[key] = straight
    return straight


# --- GET /state ----------------------------------------------
@router.get("/state")
async def get_state(request: Request):
    db = request.state.db
    docs = (
        db.collection(SIGNALS_COLLECTION)
        .order_by("received_at", direction="DESCENDING")
        .limit(2000)
        .stream()
    )
    signals = [d.to_dict() for d in docs]

    speeds_by_rsu = defaultdict(list)
    meta = {}
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

    by_segment = defaultdict(list)
    for rid, m in meta.items():
        sp = speeds_by_rsu.get(rid, [])
        avg = sum(sp) / len(sp) if sp else None
        entry = dict(m)
        entry["avg_speed"] = round(avg, 1) if avg is not None else None
        entry["status"] = determine_traffic_status(avg) if avg is not None else "free"
        by_segment[m["segment"]].append(entry)

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


# --- GET /signals --------------------------------------------
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


# --- GET /signals/{segment} ----------------------------------
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
        return {"success": True, "segment": segment, "count": len(signals), "signals": signals}
    except Exception as e:
        print(f"[ERROR] Failed to fetch signals for segment {segment}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch signals")


# --- GET /alerts ---------------------------------------------
@router.get("/alerts")
async def get_alerts(
    request: Request,
    # user: AuthenticatedUser = Depends(require_driver),
):
    try:
        docs = (
            request.state.db.collection(ALERTS_COLLECTION)
            .order_by("generated_at", direction="DESCENDING")
            .limit(20)
            .stream()
        )
        alerts = [doc.to_dict() for doc in docs]
        return {"success": True, "count": len(alerts), "alerts": alerts}
    except Exception as e:
        print(f"[ERROR] Failed to fetch alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


# --- GET /alerts/{segment} -----------------------------------
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
            .limit(10)
            .stream()
        )
        alerts = [doc.to_dict() for doc in docs]
        return {"success": True, "segment": segment, "count": len(alerts), "alerts": alerts}
    except Exception as e:
        print(f"[ERROR] Failed to fetch alerts for segment {segment}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


# --- GET /rsus -----------------------------------------------
@router.get("/rsus")
async def get_rsus(
    request: Request,
    # user: AuthenticatedUser = Depends(require_driver),
):
    try:
        docs = request.state.db.collection("rsus").stream()
        rsus = [doc.to_dict() for doc in docs]
        return {"success": True, "count": len(rsus), "rsus": rsus}
    except Exception as e:
        print(f"[ERROR] Failed to fetch RSUs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch RSUs")


# --- POST /report-incident -----------------------------------
# Open endpoint — no auth required (testing).
# Stores segment name, pinned coordinates, reporter UID, and timestamp
# into the incident_reports Firestore collection.

class _IncidentBody(BaseModel):
    segment:     str
    reported_by: Optional[str] = None
    lat:         Optional[float] = None
    lng:         Optional[float] = None


@router.post("/report-incident")
async def report_incident(body: _IncidentBody, request: Request):
    if not body.segment.strip():
        raise HTTPException(status_code=422, detail="segment must not be empty")

    doc = {
        "segment":     body.segment.strip(),
        "reported_by": body.reported_by or "anonymous",
        "reported_at": datetime.utcnow().isoformat(),
        "status":      "open",
        "lat":         body.lat,
        "lng":         body.lng,
    }

    request.state.db.collection("incident_reports").add(doc)

    print(f"[INCIDENT] {body.segment} | lat={body.lat} lng={body.lng} | by={body.reported_by}")

    return {
        "success": True,
        "message": f"Incident reported on {body.segment}",
    }