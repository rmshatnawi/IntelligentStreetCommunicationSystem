# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     routes/ingest.py
# Author:   Raghad Shatnawi
# Date:     March 2026
# Purpose:  Handles incoming signals from RSU Simulators.
#Updates (May 2026 - Dana Omar)
#Added vehicle tracking processing.
#Added stolen vehicle detection integration.
#Added traffic summary generation.
#Added traffic alert generation.
#Connected signal ingestion with tracking and analytics services.
# ============================================================

from fastapi import APIRouter, HTTPException, Request
from datetime import datetime

from models.signal_model import RSUSignal, SignalInDB, to_dict
from config import SIGNALS_COLLECTION

from services.vehicle_tracking import process_vehicle_tracking
from services.aggregation_service import generate_summaries


router = APIRouter()


@router.post("/ingest")
async def ingest_signal(signal: RSUSignal, request: Request):

    try:
        # STEP 1: Build the full signal object
        signal_in_db = SignalInDB(
            **signal.model_dump(),
            received_at=datetime.utcnow()
        )

        # STEP 2: Convert to dictionary
        signal_dict = to_dict(signal_in_db)

        # STEP 3: Save signal to Firestore
        request.state.db.collection(SIGNALS_COLLECTION).add(signal_dict)

        # STEP 4: Vehicle tracking + stolen vehicle detection
        process_vehicle_tracking(signal_in_db, request.state.db)

        # STEP 5: Traffic summaries + alerts
        generate_summaries(request.state.db)

        # STEP 6: Return success response
        return {
            "success": True,
            "message": "Signal received, saved, and processed",
            "rsu_id": signal.rsu_id,
            "segment": signal.segment,
        }

    except Exception as e:
        print(f"[ERROR] Failed to process signal: {e}")
        raise HTTPException(status_code=500, detail="Failed to process signal")
