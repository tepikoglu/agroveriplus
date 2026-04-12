import io

REG = {"email": "dash@test.com", "password": "test12345", "name": "Dashboard User"}


async def _auth(client):
    await client.post("/api/auth/register", json=REG)
    r = await client.post("/api/auth/login", json={"email": REG["email"], "password": REG["password"]})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def test_dashboard_empty(client):
    h = await _auth(client)
    r = await client.get("/api/dashboard/stats", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert data["total_certificates"] == 0
    assert data["total_verifications"] == 0
    assert data["my_certificates"] == 0
    assert data["my_parcels"] == 0


async def test_dashboard_with_data(client):
    h = await _auth(client)

    # Upload a certificate
    await client.post(
        "/api/certificates/upload",
        files={"file": ("test.pdf", io.BytesIO(b"dash cert"), "application/pdf")},
    )

    # Create a parcel
    await client.post("/api/parcels", json={
        "name": "Test Parcel",
        "location_lat": 41.0,
        "location_lon": 36.0,
        "area_hectares": 5.0,
        "crop_type": "hazelnut",
    }, headers=h)

    # Verify a certificate
    await client.post("/api/certificates/verify", json={"hash": "a" * 64})

    r = await client.get("/api/dashboard/stats", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert data["total_certificates"] == 1
    assert data["total_verifications"] == 1
    assert data["my_parcels"] == 1


async def test_dashboard_unauthenticated(client):
    r = await client.get("/api/dashboard/stats")
    assert r.status_code == 401
