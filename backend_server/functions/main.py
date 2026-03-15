# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     main.py
# Author:   Raghad Shatnawi
# Date:     March 2026
# Purpose:  Entry point of the FastAPI server.
#           Initializes Firebase connection, registers all
#           routes, and starts the server.
# ============================================================

import uvicorn
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Request

from config import HOST, PORT, FIREBASE_CREDENTIALS_PATH
from routes import ingest, analyze, api


# ─── STEP 1: Initialize Firebase ────────────────────────────
# Load the service account key file to authenticate with Firebase.
# This gives our server permission to read/write Firestore.
# IMPORTANT: serviceAccountKey.json must be in the functions/ folder.
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Connect to Firestore database
db = firestore.client()


# ─── STEP 2: Create FastAPI app ─────────────────────────────
app = FastAPI(
    title="Intelligent Street Communication System",
    description="Backend server for receiving and processing RSU traffic signals",
    version="1.0.0"
)


# ─── STEP 3: Inject Firestore into every request ────────────
# This runs before every request and attaches the Firestore
# client to the request so all routes can access the database
# without importing it separately in every file.
@app.middleware("http")
async def attach_db(request: Request, call_next):
    request.state.db = db
    response = await call_next(request)
    return response


# ─── STEP 4: Register routes ────────────────────────────────
# Each route file handles a different part of the system.
# We will add analyze and api routes later.
app.include_router(ingest.router)
app.include_router(analyze.router)
app.include_router(api.router)


# ─── STEP 5: Health check endpoint ──────────────────────────
# A simple endpoint to confirm the server is running.
# Visit http://localhost:8000/health to check.
@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "server": "Intelligent Street Communication System",
        "version": "1.0.0"
    }


# ─── STEP 6: Start the server ───────────────────────────────
# uvicorn is the engine that runs the FastAPI app.
# Running this file directly starts the server on HOST:PORT.
if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
    # reload=True means the server auto-restarts when you save any file
    # very useful during development