# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     models/user_model.py
# Author:   Raghad Shatnawi
# Last Modified: 18 April 2026
# Purpose:  Defines user roles and the authenticated user
#           object that is injected into protected routes
#           after Firebase token verification.
# ============================================================

from pydantic import BaseModel
from typing import Optional, Literal


# ─── UserRole ────────────────────────────────────────────────
# The three roles defined in the SRS (section 2.7).
#
# driver        — end users who view traffic conditions and alerts
# public_safety — authorized users who access the monitoring dashboard
# admin         — manages RSUs, users, and server configuration
#
# Roles are stored as Firebase custom claims on each user account.
# They are set by an admin via the POST /admin/set-role endpoint.
# Firebase propagates them inside the ID token on next sign-in.

UserRole = Literal["driver", "public_safety", "admin"]


# ─── AuthenticatedUser ───────────────────────────────────────
# Represents a verified Firebase user extracted from the ID token.
# Injected into route handlers by the auth dependency functions
# defined in core/auth.py.
#
# uid   — Firebase UID, unique per user
# email — user email from Firebase Auth (may be None if phone auth)
# role  — extracted from Firebase custom claims

class AuthenticatedUser(BaseModel):
    uid:   str
    email: Optional[str] = None
    role:  UserRole