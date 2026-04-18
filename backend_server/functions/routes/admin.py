# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     routes/admin.py
# Author:   Raghad Shatnawi
# Last Modified: 18 April 2026
# Purpose:  Admin-only endpoints for user and role management.
#           Corresponds to FR-24, FR-25, FR-26 from the SRS.
#
#           FR-24: Administrators manage RSU configurations
#           FR-25: Administrators manage user accounts and permissions
#           FR-26: Administrators monitor server and RSU status
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from firebase_admin import auth

from core.auth import require_admin
from models.user_model import AuthenticatedUser, UserRole

router = APIRouter(prefix="/admin", tags=["admin"])


# ─── SetRoleRequest ──────────────────────────────────────────
# Request body for POST /admin/set-role.

class SetRoleRequest(BaseModel):
    uid:  str      # Firebase UID of the target user
    role: UserRole # Role to assign: driver / public_safety / admin


# ─── POST /admin/set-role ────────────────────────────────────
# Assigns a role to a Firebase user by setting a custom claim.
# The role is embedded in the user's ID token after next sign-in.
#
# Only admins can call this endpoint (require_admin dependency).
#
# FR-25: The system shall allow administrators to manage
#        user accounts and permissions.
#
# URL:    POST http://<server-ip>:8000/admin/set-role
# Auth:   Admin token required
# Body:   { "uid": "<firebase-uid>", "role": "driver" }
# Returns: confirmation of role assignment

@router.post("/set-role")
async def set_user_role(
    body: SetRoleRequest,
    admin: AuthenticatedUser = Depends(require_admin),
):
    try:
        # Set custom claim on the Firebase user.
        # The user must sign out and sign in again for the new
        # role to appear in their ID token.
        auth.set_custom_user_claims(body.uid, {"role": body.role})

        print(f"[ADMIN] {admin.uid} set role '{body.role}' on user {body.uid}")

        return {
            "success": True,
            "message": f"Role '{body.role}' assigned to user {body.uid}. "
                       f"User must sign in again for the change to take effect.",
            "uid":     body.uid,
            "role":    body.role,
        }

    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"No Firebase user found with UID: {body.uid}"
        )

    except Exception as e:
        print(f"[ERROR] Failed to set role: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign role.")


# ─── GET /admin/user/{uid} ───────────────────────────────────
# Returns the Firebase profile and current role of a user.
# Useful for verifying role assignments.
#
# URL:    GET http://<server-ip>:8000/admin/user/{uid}
# Auth:   Admin token required

@router.get("/user/{uid}")
async def get_user(
    uid: str,
    admin: AuthenticatedUser = Depends(require_admin),
):
    try:
        user_record = auth.get_user(uid)
        claims      = user_record.custom_claims or {}

        return {
            "uid":          user_record.uid,
            "email":        user_record.email,
            "display_name": user_record.display_name,
            "role":         claims.get("role", "no role assigned"),
            "disabled":     user_record.disabled,
        }

    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"No Firebase user found with UID: {uid}"
        )

    except Exception as e:
        print(f"[ERROR] Failed to get user {uid}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user.")


# ─── DELETE /admin/user/{uid} ────────────────────────────────
# Disables a Firebase user account.
# Does not delete the account — disabling is reversible.
#
# FR-25: Administrators manage user accounts and permissions.
#
# URL:    DELETE http://<server-ip>:8000/admin/user/{uid}
# Auth:   Admin token required

@router.delete("/user/{uid}")
async def disable_user(
    uid: str,
    admin: AuthenticatedUser = Depends(require_admin),
):
    try:
        auth.update_user(uid, disabled=True)

        print(f"[ADMIN] {admin.uid} disabled user {uid}")

        return {
            "success": True,
            "message": f"User {uid} has been disabled.",
        }

    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"No Firebase user found with UID: {uid}"
        )

    except Exception as e:
        print(f"[ERROR] Failed to disable user {uid}: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable user.")