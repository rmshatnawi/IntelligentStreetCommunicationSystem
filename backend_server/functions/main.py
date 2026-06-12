# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     main.py
# Author:   Raghad Shatnawi
# Last Modified: June 2026
# Author:   Batool Alkhateeb
# Last Modified: June 2026
# Purpose:  Entry point of the FastAPI server.
#           Initializes Firebase connection, registers all
#           routes, and starts the server.
# ============================================================

import uvicorn
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Request

from config import HOST, PORT, FIREBASE_CREDENTIALS_PATH
from routes import ingest, analyze, api, admin, summaries


# ─── STEP 1: Initialize Firebase ────────────────────────────
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
@app.middleware("http")
async def attach_db(request: Request, call_next):
    request.state.db = db
    response = await call_next(request)
    return response


# ─── STEP 4: Register routes ────────────────────────────────
#
# Route auth summary:
#   /ingest              — open (RSUs do not use Firebase Auth)
#   /analyze/{segment}   — public_safety, admin
#   /signals             — driver, public_safety, admin
#   /signals/{segment}   — driver, public_safety, admin
#   /alerts              — driver, public_safety, admin
#   /alerts/{segment}    — driver, public_safety, admin
#   /state               — driver, public_safety, admin
#   /summaries           — driver, public_safety, admin
#   /summaries/{segment} — driver, public_safety, admin
#   /admin/*             — admin only

app.include_router(ingest.router)
app.include_router(analyze.router)
app.include_router(api.router)
app.include_router(admin.router)
app.include_router(summaries.router)   # ← was missing; now registered


# ─── STEP 5: Health check ───────────────────────────────────
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
