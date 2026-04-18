# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     core/auth.py
# Author:   Raghad Shatnawi
# Last Modified: 18 April 2026
# Purpose:  Firebase token verification and role-based
#           FastAPI dependency functions.
#
#           How it works:
#             1. Flutter client signs in via Firebase Auth
#             2. Firebase returns an ID token to the client
#             3. Client sends: Authorization: Bearer <token>
#             4. get_current_user() verifies the token with Firebase
#             5. Role is extracted from the token's custom claims
#             6. Role-specific dependencies (require_admin etc.)
#                enforce access control per route
# ============================================================

from fastapi import Depends, HTTPException, Header
from firebase_admin import auth

from models.user_model import AuthenticatedUser, UserRole


# ─── get_current_user() ──────────────────────────────────────
# Core dependency. Verifies the Firebase ID token from the
# Authorization header and returns an AuthenticatedUser.
#
# Raises HTTP 401 if:
#   - Authorization header is missing
#   - Token is invalid, expired, or revoked
#
# Raises HTTP 403 if:
#   - Token is valid but the user has no role assigned
#     (user exists in Firebase but was never assigned a role
#      via the POST /admin/set-role endpoint)

async def get_current_user(
    authorization: str = Header(..., description="Bearer <Firebase ID token>")
) -> AuthenticatedUser:

    # ─── Extract token from header ────────────────────────
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header must be: Bearer <token>"
        )

    token = authorization.split("Bearer ")[1].strip()

    # ─── Verify token with Firebase ───────────────────────
    # firebase_admin.auth.verify_id_token() checks:
    #   - token signature (using Firebase project keys)
    #   - token expiry
    #   - token revocation status (check_revoked=True)
    try:
        decoded_token = auth.verify_id_token(token, check_revoked=True)

    except auth.RevokedIdTokenError:
        raise HTTPException(status_code=401, detail="Token has been revoked. Please sign in again.")

    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token has expired. Please sign in again.")

    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

    except Exception as e:
        print(f"[AUTH ERROR] Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed.")

    # ─── Extract role from custom claims ──────────────────
    # Custom claims are set by admin via POST /admin/set-role.
    # A valid user must have a role claim before they can use the API.
    role = decoded_token.get("role")

    if role not in ("driver", "public_safety", "admin"):
        raise HTTPException(
            status_code=403,
            detail="User has no role assigned. Contact an administrator."
        )

    return AuthenticatedUser(
        uid=decoded_token["uid"],
        email=decoded_token.get("email"),
        role=role,
    )


# ─── Role-based dependency functions ─────────────────────────
# Use these as FastAPI dependencies on protected routes.
#
# Usage in a route:
#   @router.get("/some-route")
#   async def some_route(user: AuthenticatedUser = Depends(require_driver)):
#       ...
#
# These call get_current_user() first (verifies token),
# then check the role. HTTP 403 is raised if role does not match.


async def require_driver(
    user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """Allows: driver, public_safety, admin"""
    # Drivers get the least privileged access.
    # Public safety and admin can also access driver routes.
    if user.role not in ("driver", "public_safety", "admin"):
        raise HTTPException(status_code=403, detail="Driver access required.")
    return user


async def require_public_safety(
    user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """Allows: public_safety, admin"""
    if user.role not in ("public_safety", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Authorized public safety access required."
        )
    return user


async def require_admin(
    user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """Allows: admin only"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user