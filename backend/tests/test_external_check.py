import io

REG = {"email": "ext@test.com", "password": "test12345", "name": "Checker"}


async def _auth(client):
    await client.post("/api/auth/register", json=REG)
    r = await client.post("/api/auth/login", json={"email": REG["email"], "password": REG["password"]})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def _upload_with_metadata(client, headers, certifier="ECOCERT", cert_number="TR-BIO-001"):
    r = await client.post(
        "/api/certificates/upload",
        files={"file": ("cert.pdf", io.BytesIO(f"ext check {certifier}".encode()), "application/pdf")},
    )
    cert_id = r.json()["id"]
    await client.put(f"/api/certificates/{cert_id}/metadata", json={
        "certifier_name": certifier,
        "certificate_number": cert_number,
    }, headers=headers)
    return cert_id


async def test_external_check_ecocert_valid(client):
    h = await _auth(client)
    cert_id = await _upload_with_metadata(client, h, certifier="ECOCERT", cert_number="TR-BIO-001")
    r = await client.get(f"/api/certificates/{cert_id}/external-check")
    assert r.status_code == 200
    data = r.json()
    assert len(data["checks"]) == 3
    # OTBIS should find TR-BIO prefix
    otbis = next(c for c in data["checks"] if c["provider"] == "OTBIS")
    assert otbis["status"] == "valid"
    # ECOCERT should find the certifier
    ecocert = next(c for c in data["checks"] if c["provider"] == "ECOCERT")
    assert ecocert["status"] == "valid"


async def test_external_check_unknown_certifier(client):
    h = await _auth(client)
    cert_id = await _upload_with_metadata(client, h, certifier="Unknown Corp", cert_number="XX-123")
    r = await client.get(f"/api/certificates/{cert_id}/external-check")
    assert r.status_code == 200
    data = r.json()
    # No registries should confirm
    valid_count = sum(1 for c in data["checks"] if c["status"] == "valid")
    assert valid_count == 0
    assert "No external registry" in data["summary"]


async def test_external_check_no_metadata(client):
    """Certificate without metadata — registries should return not_found."""
    r = await client.post(
        "/api/certificates/upload",
        files={"file": ("bare.pdf", io.BytesIO(b"no metadata cert"), "application/pdf")},
    )
    cert_id = r.json()["id"]
    r2 = await client.get(f"/api/certificates/{cert_id}/external-check")
    assert r2.status_code == 200
    assert all(c["status"] == "not_found" for c in r2.json()["checks"])


async def test_external_check_not_found(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    r = await client.get(f"/api/certificates/{fake_id}/external-check")
    assert r.status_code == 404
