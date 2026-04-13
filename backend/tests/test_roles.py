"""Role-based access control tests across all protected endpoints."""

REG_BASE = {"password": "test12345", "name": "Role Test"}
PARCEL = {"name": "Test", "location_lat": 41.0, "location_lon": 36.0, "area_hectares": 5.0, "crop_type": "hazelnut"}


async def _auth(client, role="farmer", email=None):
    e = email or f"{role}@role.test"
    await client.post("/api/auth/register", json={**REG_BASE, "email": e, "role": role})
    r = await client.post("/api/auth/login", json={"email": e, "password": REG_BASE["password"]})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def test_farmer_can_create_parcel(client):
    h = await _auth(client, "farmer")
    r = await client.post("/api/parcels", json=PARCEL, headers=h)
    assert r.status_code == 201


async def test_agronomist_cannot_create_parcel(client):
    h = await _auth(client, "agronomist")
    r = await client.post("/api/parcels", json=PARCEL, headers=h)
    assert r.status_code == 403


async def test_analyst_cannot_create_parcel(client):
    h = await _auth(client, "analyst")
    r = await client.post("/api/parcels", json=PARCEL, headers=h)
    assert r.status_code == 403


async def test_cooperative_admin_can_create_parcel(client):
    h = await _auth(client, "cooperative_admin")
    r = await client.post("/api/parcels", json=PARCEL, headers=h)
    assert r.status_code == 201
