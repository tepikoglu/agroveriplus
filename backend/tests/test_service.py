import hashlib

from app.services.certificate_service import (
    compute_sha256,
    find_by_hash,
    log_verification,
    store_certificate,
)


async def test_compute_sha256():
    """SHA-256 hash should match Python's hashlib."""
    data = b"test certificate content"
    result = await compute_sha256(data)
    expected = hashlib.sha256(data).hexdigest()
    assert result == expected
    assert len(result) == 64


async def test_compute_sha256_deterministic():
    """Same input must always produce the same hash."""
    data = b"findik sertifikasi"
    h1 = await compute_sha256(data)
    h2 = await compute_sha256(data)
    assert h1 == h2


async def test_compute_sha256_different_inputs():
    """Different inputs must produce different hashes."""
    h1 = await compute_sha256(b"certificate A")
    h2 = await compute_sha256(b"certificate B")
    assert h1 != h2


async def test_store_and_find_certificate(db_session):
    """Store a certificate, then find it by hash."""
    cert = await store_certificate(
        db_session,
        sha256_hash="abc123" + "0" * 58,
        original_filename="test.pdf",
        file_size=1024,
        content_type="application/pdf",
    )
    assert cert.id is not None
    assert cert.original_filename == "test.pdf"

    found = await find_by_hash(db_session, "abc123" + "0" * 58)
    assert found is not None
    assert found.id == cert.id


async def test_find_nonexistent_hash(db_session):
    """Looking up a hash that doesn't exist should return None."""
    result = await find_by_hash(db_session, "f" * 64)
    assert result is None


async def test_log_verification_valid(db_session):
    """Log a successful verification."""
    cert = await store_certificate(
        db_session,
        sha256_hash="d" * 64,
        original_filename="organic.pdf",
        file_size=2048,
        content_type="application/pdf",
    )
    v = await log_verification(
        db_session,
        queried_hash="d" * 64,
        is_valid=True,
        certificate_id=cert.id,
        ip_address="192.168.1.1",
        user_agent="TestBrowser/1.0",
    )
    assert v.is_valid is True
    assert v.queried_hash == "d" * 64
    assert v.certificate_id == cert.id


async def test_log_verification_invalid(db_session):
    """Log a failed verification (hash not found)."""
    v = await log_verification(
        db_session,
        queried_hash="e" * 64,
        is_valid=False,
    )
    assert v.is_valid is False
    assert v.certificate_id is None
