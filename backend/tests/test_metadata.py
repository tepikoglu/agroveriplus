import io

REG = {"email": "meta@test.com", "password": "test12345", "name": "Test User"}


async def _auth(client):
    await client.post("/api/auth/register", json=REG)
    r = await client.post("/api/auth/login", json={"email": REG["email"], "password": REG["password"]})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def _upload(client):
    r = await client.post(
        "/api/certificates/upload",
        files={"file": ("cert.pdf", io.BytesIO(b"metadata test cert"), "application/pdf")},
    )
    return r.json()["id"]


async def test_update_metadata(client):
    h = await _auth(client)
    cert_id = await _upload(client)
    r = await client.put(f"/api/certificates/{cert_id}/metadata", json={
        "certifier_name": "ECOCERT",
        "certificate_number": "TR-BIO-001-2026",
        "product_type": "Organic Hazelnut",
    }, headers=h)
    assert r.status_code == 200
    data = r.json()
    assert data["certifier_name"] == "ECOCERT"
    assert data["certificate_number"] == "TR-BIO-001-2026"
    assert data["product_type"] == "Organic Hazelnut"


async def test_partial_metadata_update(client):
    h = await _auth(client)
    cert_id = await _upload(client)
    # Only update one field
    r = await client.put(f"/api/certificates/{cert_id}/metadata", json={
        "product_type": "Organic Olive Oil",
    }, headers=h)
    assert r.status_code == 200
    assert r.json()["product_type"] == "Organic Olive Oil"
    assert r.json()["certifier_name"] is None  # not set


async def test_metadata_not_found(client):
    h = await _auth(client)
    fake_id = "00000000-0000-0000-0000-000000000000"
    r = await client.put(f"/api/certificates/{fake_id}/metadata", json={
        "product_type": "test",
    }, headers=h)
    assert r.status_code == 404
