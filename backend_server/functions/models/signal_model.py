# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     models/signal_model.py
# Author:   Raghad Shatnawi
# Date:     March 2026
# Purpose:  Defines the exact structure of a signal received
#           from an RSU (Roadside Unit).
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── RSUSignal ───────────────────────────────────────────────
# This class represents one signal sent by an RSU.
# Every POST request to /ingest must match this structure.
#
# Example of a valid incoming JSON:
# {
#   "event_id":      "12345",
#   "rsu_id":        "RSU_01",
#   "segment":       "Petra St.",
#   "timestamp":     "2026-03-13T12:45:30",
#   "speed":         42.0,
#   "direction":     "Northbound",
#   "vehicle_count": 3
# }

class RSUSignal(BaseModel):

    # ─── REQUIRED FIELDS ────────────────────────────────────
    # These must be present in every signal.
    # If missing, FastAPI automatically returns a 422 error
    # with a clear message telling the RSU what is missing.

    rsu_id:        str   = Field(..., description="ID of the RSU that sent this signal")
    segment:       str   = Field(..., description="Road segment name e.g. Petra St.")
    speed:         float = Field(..., description="Average vehicle speed in km/h", ge=0)
    vehicle_count: int   = Field(..., description="Number of vehicles detected", ge=0)

    # ─── OPTIONAL FIELDS ────────────────────────────────────
    # These are not required — we provide defaults if missing.

    event_id:  Optional[str]      = Field(None,    description="Unique event ID from RSU")
    timestamp: Optional[datetime] = Field(None,    description="Time of detection from RSU")
    direction: Optional[str]      = Field("Unknown", description="Direction of travel")


# ─── SignalInDB ──────────────────────────────────────────────
# Represents the signal as it is stored in Firestore.
# Extends RSUSignal and adds server-side fields that we
# attach before saving (received_at).

class SignalInDB(RSUSignal):

    received_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of when the server received this signal"
    )


# ─── to_dict() ──────────────────────────────────────────────
# Converts a SignalInDB object into a plain dictionary
# so Firestore can save it.
# Firestore does not accept Pydantic objects directly.

def to_dict(signal: SignalInDB) -> dict:
    return {
        "event_id":      signal.event_id,
        "rsu_id":        signal.rsu_id,
        "segment":       signal.segment,
        "timestamp":     signal.timestamp.isoformat() if signal.timestamp else None,
        "speed":         signal.speed,
        "direction":     signal.direction,
        "vehicle_count": signal.vehicle_count,
        "received_at":   signal.received_at.isoformat(),
    }