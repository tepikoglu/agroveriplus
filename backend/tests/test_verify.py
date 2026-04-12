import io


CERT_CONTENT = b"organic hazelnut certificate from COFUB"


async def _upload(client):
    """Helper: upload a certificate and return the hash."""
    r = await client.post(
        "/api/certificates/upload",
        files={"file": ("findik.pdf", io.BytesIO(CERT_CONTENT), "application/pdf")},
    )
    return r.json()["sha256_hash"]


async def test_verify_valid_hash(client):
    """Verifying an uploaded certificate should return verified=True."""
    hash_val = await _upload(client)

    response = await client.post(
        "/api/certificates/verify",
        json={"hash": hash_val},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True
    assert data["message"] == "Certificate is authentic and has not been altered."
    assert data["certificate"]["sha256_hash"] == hash_val
    assert data["certificate"]["original_filename"] == "findik.pdf"


async def test_verify_invalid_hash(client):
    """Verifying a non-existent hash should return verified=False."""
    fake_hash = "a" * 64

    response = await client.post(
        "/api/certificates/verify",
        json={"hash": fake_hash},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is False
    assert data["certificate"] is None
    assert "not found" in data["message"].lower()


async def test_verify_via_get_endpoint(client):
    """GET /api/certificates/{hash} should also verify."""
    hash_val = await _upload(client)

    response = await client.get(f"/api/certificates/{hash_val}")
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True
    assert data["certificate"]["sha256_hash"] == hash_val


async def test_verify_get_invalid_hash(client):
    """GET with unknown hash should return not verified."""
    response = await client.get("/api/certificates/" + "b" * 64)
    assert response.status_code == 200
    assert response.json()["verified"] is False


async def test_upload_then_verify_roundtrip(client):
    """Full flow: upload → get hash → verify → confirmed authentic."""
    # Farmer uploads
    upload_r = await client.post(
        "/api/certificates/upload",
        files={"file": ("sertifika.jpg", io.BytesIO(b"JPEG cert data"), "image/jpeg")},
    )
    hash_val = upload_r.json()["sha256_hash"]
    assert len(hash_val) == 64

    # Consumer verifies
    verify_r = await client.post(
        "/api/certificates/verify",
        json={"hash": hash_val},
    )
    assert verify_r.json()["verified"] is True
    cert = verify_r.json()["certificate"]
    assert cert["original_filename"] == "sertifika.jpg"
    assert cert["content_type"] == "image/jpeg"
