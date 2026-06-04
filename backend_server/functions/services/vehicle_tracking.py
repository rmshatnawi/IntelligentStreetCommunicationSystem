# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     services/vehicle_tracking.py
# Author:   Dana Omar
# Date:     May 2026
# Purpose:  Tracks vehicle movement between RSUs and
#           checks for stolen vehicles.
# ============================================================

from datetime import datetime

from config import (
    VEHICLE_TRACKING_COLLECTION,
    STOLEN_VEHICLES_COLLECTION,
    SECURITY_ALERTS_COLLECTION,
)


def process_vehicle_tracking(signal, db):

    # Ignore signals without plate numbers
    if not signal.plate_number:
        return

    # Default vehicle values
    vehicle_id = "Unknown"
    status = "normal"
    is_stolen = False

    # -------------------------------------------------
    # Check stolen vehicles collection
    # -------------------------------------------------
    stolen_docs = (
        db.collection(STOLEN_VEHICLES_COLLECTION)
        .where("plate_number", "==", signal.plate_number)
        .stream()
    )

    for doc in stolen_docs:
        stolen_data = doc.to_dict()

        vehicle_id = stolen_data.get("vehicle_id", "Unknown")
        status = "stolen"
        is_stolen = True

        print(
            f"[STOLEN VEHICLE DETECTED] "
            f"{signal.plate_number} "
            f"at {signal.segment}"
        )

        # Create stolen vehicle alert
        alert_data = {
            "alert_type": "stolen_vehicle",
            "vehicle_id": vehicle_id,
            "plate_number": signal.plate_number,
            "segment": signal.segment,
            "rsu_id": signal.rsu_id,
            "speed": signal.speed,
            "severity": "high",
            "status": "active",
            "alert_message": (
                f"Stolen vehicle detected: {signal.plate_number}"
            ),
            "generated_at": datetime.utcnow().isoformat(),
        }

        db.collection(SECURITY_ALERTS_COLLECTION).add(alert_data)
        break

    # -------------------------------------------------
    # Save tracking event
    # -------------------------------------------------
    tracking_record = {
        "vehicle_id": vehicle_id,
        "plate_number": signal.plate_number,
        "rsu_id": signal.rsu_id,
        "segment": signal.segment,
        "speed": signal.speed,
        "status": status,
        "is_stolen": is_stolen,
        "timestamp": datetime.utcnow().isoformat(),
    }

    db.collection(
        VEHICLE_TRACKING_COLLECTION
    ).add(tracking_record)
