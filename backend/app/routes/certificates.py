from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.schemas import (
    CertificateDetail,
    CertificateMetadataUpdate,
    CertificateUploadResponse,
    ExternalCheckResponse,
    ExternalCheckResult,
    VerifyRequest,
    VerifyResponse,
)
from app.services.certificate_service import (
    compute_sha256,
    find_by_hash,
    log_verification,
    store_certificate,
)
from app.services.ipfs_service import pin_to_ipfs

router = APIRouter()

MAX_UPLOAD_BYTES = settings.max_upload_size_mb * 1024 * 1024


@router.post("/upload", response_model=CertificateUploadResponse)
async def upload_certificate(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Upload a certificate file and generate its SHA-256 hash + QR data."""
    # Validate extension
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(400, f"File type .{ext} not allowed. Use: {settings.allowed_extensions}")

    # Read and validate size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(400, f"File exceeds {settings.max_upload_size_mb} MB limit")

    sha256_hash = await compute_sha256(file_bytes)

    # Check for duplicate
    existing = await find_by_hash(db, sha256_hash)
    if existing:
        return CertificateUploadResponse(
            id=existing.id,
            sha256_hash=existing.sha256_hash,
            original_filename=existing.original_filename,
            file_size=existing.file_size,
            ipfs_cid=existing.ipfs_cid,
            created_at=existing.created_at,
            qr_data=existing.sha256_hash,
        )

    # Pin to IPFS (if configured)
    ipfs_cid = await pin_to_ipfs(file_bytes, file.filename or "certificate")

    cert = await store_certificate(
        db,
        sha256_hash=sha256_hash,
        original_filename=file.filename or "unknown",
        file_size=len(file_bytes),
        content_type=file.content_type or "application/octet-stream",
        farmer_id=current_user.id if current_user else None,
    )

    if ipfs_cid:
        cert.ipfs_cid = ipfs_cid
        await db.commit()

    # Notify if authenticated
    if current_user:
        from app.services.notifications import NotificationEvent, notify
        await notify(db, user_id=current_user.id, event=NotificationEvent.certificate_uploaded, filename=file.filename or "unknown")

    return CertificateUploadResponse(
        id=cert.id,
        sha256_hash=cert.sha256_hash,
        original_filename=cert.original_filename,
        file_size=cert.file_size,
        ipfs_cid=cert.ipfs_cid,
        created_at=cert.created_at,
        qr_data=cert.sha256_hash,
    )


@router.get("/my", response_model=list[CertificateDetail])
async def my_certificates(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List certificates uploaded by the current user."""
    from sqlalchemy import select
    from app.models.certificate import Certificate

    result = await db.execute(
        select(Certificate)
        .where(Certificate.farmer_id == user.id)
        .order_by(Certificate.created_at.desc())
    )
    return [CertificateDetail.model_validate(c) for c in result.scalars().all()]


@router.post("/verify", response_model=VerifyResponse)
async def verify_certificate(
    body: VerifyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Verify a certificate by its SHA-256 hash."""
    cert = await find_by_hash(db, body.hash)
    is_valid = cert is not None

    await log_verification(
        db,
        queried_hash=body.hash,
        is_valid=is_valid,
        certificate_id=cert.id if cert else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    if cert:
        from app.schemas import CertificateDetail

        return VerifyResponse(
            verified=True,
            message="Certificate is authentic and has not been altered.",
            certificate=CertificateDetail.model_validate(cert),
        )

    return VerifyResponse(
        verified=False,
        message="Certificate not found. Request the original from your supplier.",
    )


@router.put("/{cert_id}/metadata", response_model=CertificateDetail)
async def update_metadata(
    cert_id: str,
    body: CertificateMetadataUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Add or update certificate metadata (certifier, product type, validity, parcel)."""
    from uuid import UUID as _UUID
    from sqlalchemy import select
    from app.models.certificate import Certificate

    result = await db.execute(select(Certificate).where(Certificate.id == _UUID(cert_id)))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(cert, field, value)
    await db.commit()
    await db.refresh(cert)
    return CertificateDetail.model_validate(cert)


@router.get("/{cert_id}/external-check", response_model=ExternalCheckResult)
async def run_external_check(
    cert_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run verification against external registries (OTBIS, ECOCERT, ETKO)."""
    from uuid import UUID as _UUID
    from sqlalchemy import select
    from app.models.certificate import Certificate
    from app.models.external_check import ExternalCheck
    from app.services.external_registry import run_all_checks

    result = await db.execute(select(Certificate).where(Certificate.id == _UUID(cert_id)))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    results = await run_all_checks(cert.certificate_number, cert.certifier_name)

    checks = []
    for r in results:
        ec = ExternalCheck(
            certificate_id=cert.id,
            provider=r.provider,
            status=r.status,
            details=r.details,
        )
        db.add(ec)
        checks.append(ec)
    await db.commit()
    for ec in checks:
        await db.refresh(ec)

    valid_count = sum(1 for r in results if r.status == "valid")
    total = len(results)
    if valid_count == total:
        summary = f"All {total} registries confirmed this certificate."
    elif valid_count > 0:
        summary = f"{valid_count}/{total} registries confirmed. Some could not verify."
    else:
        summary = "No external registry could verify this certificate."

    # Notify certificate owner about failed checks
    if valid_count < total and cert.farmer_id:
        from app.services.notifications import NotificationEvent, notify as _notify
        failed = [r.provider for r in results if r.status != "valid"]
        await _notify(db, user_id=cert.farmer_id, event=NotificationEvent.external_check_failed, filename=cert.original_filename, provider=", ".join(failed))

    return ExternalCheckResult(
        certificate_id=cert.id,
        checks=[ExternalCheckResponse.model_validate(ec) for ec in checks],
        summary=summary,
    )


@router.get("/{sha256_hash}", response_model=VerifyResponse)
async def get_certificate(
    sha256_hash: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Look up a certificate by hash (used by QR code scans)."""
    return await verify_certificate(VerifyRequest(hash=sha256_hash), request, db)
