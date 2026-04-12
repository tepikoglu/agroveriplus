import hashlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certificate import Certificate
from app.models.verification import Verification


async def compute_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


async def store_certificate(
    db: AsyncSession,
    *,
    sha256_hash: str,
    original_filename: str,
    file_size: int,
    content_type: str,
    farmer_id=None,
) -> Certificate:
    cert = Certificate(
        sha256_hash=sha256_hash,
        original_filename=original_filename,
        file_size=file_size,
        content_type=content_type,
        farmer_id=farmer_id,
    )
    db.add(cert)
    await db.commit()
    await db.refresh(cert)
    return cert


async def find_by_hash(db: AsyncSession, sha256_hash: str) -> Certificate | None:
    result = await db.execute(
        select(Certificate).where(Certificate.sha256_hash == sha256_hash)
    )
    return result.scalar_one_or_none()


async def log_verification(
    db: AsyncSession,
    *,
    queried_hash: str,
    is_valid: bool,
    certificate_id=None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Verification:
    v = Verification(
        queried_hash=queried_hash,
        is_valid=is_valid,
        certificate_id=certificate_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(v)
    await db.commit()
    return v
