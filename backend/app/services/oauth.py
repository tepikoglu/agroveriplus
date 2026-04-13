"""Google OAuth ID token verification.

Flow:
1. Frontend gets ID token via Google Sign-In
2. Backend receives the token at POST /api/auth/google
3. This service verifies the token against Google's public keys
4. Returns user info (email, name, sub) if valid

In test/demo mode without GOOGLE_CLIENT_ID set, accepts a special
test token format for development.
"""

import json
import logging

import httpx

from app.config import settings

logger = logging.getLogger("agroveri.oauth")

GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class GoogleAuthError(Exception):
    """Raised when Google token verification fails."""


async def verify_google_token(id_token: str) -> dict:
    """Verify a Google ID token and return user info.

    Returns: {"email": "...", "name": "...", "sub": "...", "picture": "..."}
    Raises: GoogleAuthError on failure.
    """
    if not settings.google_client_id:
        # Dev/test mode: accept mock tokens (format: mock:email:name)
        if id_token.startswith("mock:"):
            parts = id_token.split(":", 2)
            if len(parts) == 3:
                return {"email": parts[1], "name": parts[2], "sub": f"mock_{parts[1]}", "picture": None}
        raise GoogleAuthError("Google OAuth not configured (set GOOGLE_CLIENT_ID)")

    # Production: verify against Google
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(GOOGLE_TOKEN_INFO_URL, params={"id_token": id_token})

        if r.status_code != 200:
            raise GoogleAuthError("Invalid Google token")

        payload = r.json()

        # Verify audience matches our client ID
        if payload.get("aud") != settings.google_client_id:
            raise GoogleAuthError("Token audience mismatch")

        # Verify issuer
        if payload.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
            raise GoogleAuthError("Invalid token issuer")

        # Verify email is verified
        if payload.get("email_verified") != "true":
            raise GoogleAuthError("Email not verified by Google")

        return {
            "email": payload["email"],
            "name": payload.get("name", payload["email"].split("@")[0]),
            "sub": payload["sub"],
            "picture": payload.get("picture"),
        }

    except httpx.RequestError as e:
        logger.error(f"Google API request failed: {e}")
        raise GoogleAuthError(f"Could not reach Google: {e}")
