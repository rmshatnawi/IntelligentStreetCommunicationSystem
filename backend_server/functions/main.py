# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     main.py
# Author:   Raghad Shatnawi
# Last Modified: 18 April 2026
# Purpose:  Entry point of the FastAPI server.
#           Initializes Firebase connection, registers all
#           routes, and starts the server.
# ============================================================

import uvicorn
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Request

from config import HOST, PORT, FIREBASE_CREDENTIALS_PATH
from routes import ingest, analyze, api, admin


# ─── STEP 1: Initialize Firebase ────────────────────────────
# Loads the service account key to authenticate with Firebase.
# Gives the server permission to:
#   - read/write Firestore (traffic data)
#   - verify ID tokens (Firebase Auth)
#   - manage users and custom claims (role assignment)
# IMPORTANT: serviceAccountKey.json must be in functions/ folder.
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ─── STEP 2: Create FastAPI app ─────────────────────────────
app = FastAPI(
    title="Intelligent Street Communication System",
    description="Backend server for receiving and processing RSU traffic signals",
    version="1.0.0"
)


# ─── STEP 3: Inject Firestore into every request ────────────
# Attaches the Firestore client to the request so all routes
# can access the database without importing it separately.
@app.middleware("http")
async def attach_db(request: Request, call_next):
    request.state.db = db
    response = await call_next(request)
    return response


# ─── STEP 4: Register routes ────────────────────────────────
#
# Route auth summary:
#   /ingest            — open (RSUs do not use Firebase Auth)
#   /analyze/{segment} — public_safety, admin
#   /signals           — driver, public_safety, admin
#   /signals/{segment} — driver, public_safety, admin
#   /alerts            — driver, public_safety, admin
#   /alerts/{segment}  — driver, public_safety, admin
#   /admin/*           — admin only
#
# Note on /ingest:
#   RSU hardware and simulator do not authenticate via Firebase.
#   This endpoint is open by design for the prototype phase.
#   Future: add API key or RSU certificate-based authentication.

app.include_router(ingest.router)
app.include_router(analyze.router)
app.include_router(api.router)
app.include_router(admin.router)


# ─── STEP 5: Health check ───────────────────────────────────
# Open endpoint — no auth required.
# Visit http://localhost:8000/health to verify server is running.
@app.get("/health")
async def health_check():
    return {
        "status":  "online",
        "server":  "Intelligent Street Communication System",
        "version": "1.0.0"
    }


# ─── STEP 6: Start the server ───────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)