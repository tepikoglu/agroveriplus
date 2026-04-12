import io


FAKE_PDF_CONTENT = b"%PDF-1.4 fake certificate content for testing"
FAKE_PNG_CONTENT = b"\x89PNG\r\n\x1a\n fake png content"


async def test_upload_pdf(client):
    """Upload a PDF certificate and get back hash + QR data."""
    response = await client.post(
        "/api/certificates/upload",
        files={"file": ("organic_cert.pdf", io.BytesIO(FAKE_PDF_CONTENT), "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["sha256_hash"]) == 64
    assert data["original_filename"] == "organic_cert.pdf"
    assert data["file_size"] == len(FAKE_PDF_CONTENT)
    assert data["qr_data"] == data["sha256_hash"]
    assert data["id"] is not None
    assert data["created_at"] is not None


async def test_upload_png(client):
    """Upload a PNG certificate image."""
    response = await client.post(
        "/api/certificates/upload",
        files={"file": ("cert_photo.png", io.BytesIO(FAKE_PNG_CONTENT), "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "cert_photo.png"
    assert len(data["sha256_hash"]) == 64


async def test_upload_duplicate_returns_same_hash(client):
    """Uploading the same file twice should return the same certificate."""
    file_content = b"duplicate test certificate"

    r1 = await client.post(
        "/api/certificates/upload",
        files={"file": ("cert.pdf", io.BytesIO(file_content), "application/pdf")},
    )
    r2 = await client.post(
        "/api/certificates/upload",
        files={"file": ("cert_copy.pdf", io.BytesIO(file_content), "application/pdf")},
    )

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["sha256_hash"] == r2.json()["sha256_hash"]
    assert r1.json()["id"] == r2.json()["id"]


async def test_upload_rejected_extension(client):
    """Files with disallowed extensions should be rejected."""
    response = await client.post(
        "/api/certificates/upload",
        files={"file": ("malware.exe", io.BytesIO(b"bad stuff"), "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


async def test_upload_different_files_different_hashes(client):
    """Different files must produce different hashes."""
    r1 = await client.post(
        "/api/certificates/upload",
        files={"file": ("a.pdf", io.BytesIO(b"certificate A"), "application/pdf")},
    )
    r2 = await client.post(
        "/api/certificates/upload",
        files={"file": ("b.pdf", io.BytesIO(b"certificate B"), "application/pdf")},
    )

    assert r1.json()["sha256_hash"] != r2.json()["sha256_hash"]
