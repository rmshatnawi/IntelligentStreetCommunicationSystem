# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     routes/ingest.py
# Author:   Raghad Shatnawi
# Date:     March 2026
# Purpose:  Handles incoming signals from RSU Simulators.
#           Receives a POST request, validates the data using
#           the signal model, and saves it to Firestore.
# ============================================================

from fastapi import APIRouter, HTTPException, Request
from datetime import datetime

from models.signal_model import RSUSignal, SignalInDB, to_dict
from config import SIGNALS_COLLECTION

# ─── ROUTER ─────────────────────────────────────────────────
# APIRouter lets us define routes in separate files
# instead of cramming everything into main.py.
# main.py will import and register this router.
router = APIRouter()


# ─── POST /ingest ────────────────────────────────────────────
# This is the endpoint the RSU Simulator calls.
# It receives a JSON signal, validates it, and saves to Firestore.
#
# URL:    POST http://<server-ip>:8000/ingest
# Body:   RSUSignal JSON
# Returns: success message + basic signal info
@router.post("/ingest")
async def ingest_signal(signal: RSUSignal, request: Request):

    try:

        # ─── STEP 1: Build the full signal object ────────────
        # Take the incoming RSUSignal and create a SignalInDB
        # which adds the received_at timestamp from the server.
        signal_in_db = SignalInDB(
            **signal.model_dump(),          # copy all fields from RSUSignal
            received_at=datetime.utcnow()   # add server timestamp
        )

        # ─── STEP 2: Convert to dictionary ───────────────────
        # Firestore cannot save Pydantic objects directly.
        # to_dict() converts it to a plain Python dictionary.
        signal_dict = to_dict(signal_in_db)

        # ─── STEP 3: Save to Firestore ────────────────────────
        # SIGNALS_COLLECTION = "signals" (defined in config.py)
        # .add() creates a new document with an auto-generated ID.
        request.state.db.collection(SIGNALS_COLLECTION).add(signal_dict)

        # ─── STEP 4: Return success response ─────────────────
        # Tells the RSU the signal was received and saved.
        return {
            "success": True,
            "message": "Signal received and saved",
            "rsu_id":  signal.rsu_id,
            "segment": signal.segment,
        }

    except Exception as e:
        # ─── ERROR HANDLER ────────────────────────────────────
        # If anything goes wrong log it and return HTTP 500
        print(f"[ERROR] Failed to save signal: {e}")
        raise HTTPException(status_code=500, detail="Failed to save signal")