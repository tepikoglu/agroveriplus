import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User

# --- Password hashing (PBKDF2-SHA256, stdlib only) ---
# Production: swap to bcrypt/argon2 via passlib when available
import secrets


def hash_password(plain: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 260_000)
    return f"pbkdf2:{salt}:{dk.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    _, salt, stored = hashed.split(":")
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 260_000)
    return hmac.compare_digest(dk.hex(), stored)


# --- JWT (HS256, stdlib only — no external dependency) ---

class JWTError(Exception):
    """Raised when JWT decode fails."""


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + "=" * padding)


def create_token(user_id: str, role: str, token_type: str = "access") -> str:
    if token_type == "access":
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=30)

    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(json.dumps({
        "sub": user_id,
        "role": role,
        "type": token_type,
        "exp": int(expire.timestamp()),
    }).encode())

    msg = f"{header}.{payload}".encode()
    sig = _b64url_encode(hmac.new(settings.jwt_secret.encode(), msg, hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}"


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises JWTError on failure."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise JWTError("Invalid token format")

        header_b64, payload_b64, sig_b64 = parts

        # Verify signature
        msg = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(settings.jwt_secret.encode(), msg, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise JWTError("Invalid signature")

        # Decode payload
        payload = json.loads(_b64url_decode(payload_b64))

        # Check expiration
        if "exp" in payload and datetime.now(timezone.utc).timestamp() > payload["exp"]:
            raise JWTError("Token expired")

        return payload
    except JWTError:
        raise
    except Exception as e:
        raise JWTError(str(e))


# --- Database operations ---

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID | str) -> User | None:
    if isinstance(user_id, str):
        user_id = UUID(user_id)
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    *,
    email: str,
    password: str,
    name: str,
    phone: str | None = None,
    role: str = "farmer",
) -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name,
        phone=phone,
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
