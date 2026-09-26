"""Authentication and Role-Based Access Control (RBAC) dependencies.

Validates Supabase Auth JWT tokens and verifies administrator status against the `admins` table.
"""

import logging
import os
from typing import Dict, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from postgrest.exceptions import APIError

from supabase_client import supabase

logger = logging.getLogger(__name__)

# Security scheme for Bearer token extraction
security = HTTPBearer(auto_error=False)

# Optional environment toggle: set to "false" to bypass auth in local offline debugging
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "true").lower() in ("true", "1", "yes")


async def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Dict[str, str]:
    """Verify that the request is authenticated by an active administrator.
    
    1. Extracts Bearer JWT from Authorization header.
    2. Validates JWT with Supabase Auth (`supabase.auth.get_user`).
    3. Checks the `admins` table for `role = 'admin'`.
    """
    if not credentials:
        if not REQUIRE_AUTH:
            logger.warning("[AUTH] REQUIRE_AUTH is false. Bypassing admin authentication for local dev.")
            return {"id": "dev-admin-id", "email": "dev@admin.local", "role": "admin"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in with an administrator account.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Step 1: Validate session token with Supabase Auth
        auth_response = supabase.auth.get_user(token)
        user = auth_response.user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = user.id
        email = user.email or ""

        # Step 2: Verify role in the 'admins' table
        try:
            admin_check = (
                supabase.table("admins")
                .select("role")
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )

            if not admin_check.data or admin_check.data[0].get("role") != "admin":
                logger.warning(f"[AUTH] User {email} ({user_id}) denied access: not registered as admin.")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You do not have administrator permissions.",
                )

            return {
                "id": user_id,
                "email": email,
                "role": admin_check.data[0].get("role", "admin"),
            }

        except APIError as api_err:
            # If the admins table hasn't been migrated yet, inform the user
            if "admins" in str(api_err):
                logger.error("[AUTH] Table 'admins' not found. Migration required.")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="System configuration error: 'admins' table is not yet created in Supabase.",
                )
            raise

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[AUTH] Unexpected error verifying administrator: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )
