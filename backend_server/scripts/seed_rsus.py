"""
seed_rsus.py — Seed the `rsus` collection in Firestore.

Author: Raghad Shatnawi
Last Modified: 16 June 2026
"""

import firebase_admin
from firebase_admin import credentials, firestore

# Path to the Firebase service account key (same one the backend uses).
SERVICE_ACCOUNT_PATH = "C:/Users/tragh/Desktop/ISCS_Final/IntelligentStreetCommunicationSystem-main/backend_server/functions/serviceAccountKey.json"

RSUS = [
    {"rsu_id": "RSU_01", "segment": "Petra St.", "direction": "Northbound", "lat": 32.49864319886971, "lng": 35.98470036585473},
    {"rsu_id": "RSU_02", "segment": "Petra St.", "direction": "Northbound", "lat": 32.500719751935,    "lng": 35.97792427671671},
    {"rsu_id": "RSU_03", "segment": "Petra St.", "direction": "Northbound", "lat": 32.500774275135896, "lng": 35.972406653154636},
    {"rsu_id": "RSU_04", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50086462795687,  "lng": 35.965555729061535},
    {"rsu_id": "RSU_05", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50092969808298,  "lng": 35.96046666556648},
    {"rsu_id": "RSU_06", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50098843720988,  "lng": 35.95421423482554},
    {"rsu_id": "RSU_07", "segment": "Petra St.", "direction": "Northbound", "lat": 32.5010620983619,   "lng": 35.94981952530449},
    {"rsu_id": "RSU_08", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50115442548511,  "lng": 35.943733038636516},
    {"rsu_id": "RSU_09", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50215525640411,  "lng": 35.93793353679571},
    {"rsu_id": "RSU_10", "segment": "Petra St.", "direction": "Northbound", "lat": 32.5037220780586,   "lng": 35.93405115296471},
    {"rsu_id": "RSU_11", "segment": "Petra St.", "direction": "Northbound", "lat": 32.50644231885107,  "lng": 35.929706034194794},
    {"rsu_id": "RSU_12", "segment": "Petra St.", "direction": "Northbound", "lat": 32.51034358248065,  "lng": 35.92386964833044},
    {"rsu_id": "RSU_13", "segment": "Petra St.", "direction": "Northbound", "lat": 32.51788740546464,  "lng": 35.912577459505236},
    {"rsu_id": "RSU_14", "segment": "Petra St.", "direction": "Northbound", "lat": 32.522638492938604, "lng": 35.903318253173325},
    {"rsu_id": "RSU_15", "segment": "Petra St.", "direction": "Northbound", "lat": 32.52348462486957,  "lng": 35.90128304825863},
    {"rsu_id": "RSU_16", "segment": "Petra St.", "direction": "Northbound", "lat": 32.52656217971231,  "lng": 35.896098203573985},
]


def main():
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    batch = db.batch()

    for rsu in RSUS:
        doc_ref = db.collection("rsus").document(rsu["rsu_id"])
        batch.set(doc_ref, rsu)

    batch.commit()
    print(f"Seeded {len(RSUS)} RSUs into 'rsus' collection.")


if __name__ == "__main__":
    main()
