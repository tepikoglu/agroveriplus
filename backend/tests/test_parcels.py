PARCEL = {
    "name": "Çarşamba Fındık Bahçesi",
    "location_lat": 41.2,
    "location_lon": 36.7,
    "area_hectares": 12.5,
    "crop_type": "hazelnut",
    "province": "Samsun",
    "district": "Çarşamba",
}

REG = {"email": "farmer@cofub.org", "password": "findik2026", "name": "Mehmet"}


async def _auth(client, role="farmer"):
    r = await client.post("/api/auth/register", json={**REG, "role": role})
    r2 = await client.post("/api/auth/login", json={"email": REG["email"], "password": REG["password"]})
    return {"Authorization": f"Bearer {r2.json()['access_token']}"}


async def _create_parcel(client, headers, **overrides):
    return await client.post("/api/parcels", json={**PARCEL, **overrides}, headers=headers)


# ─── Create ───────────────────────────────────────

async def test_create_parcel(client):
    h = await _auth(client)
    r = await _create_parcel(client, h)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == PARCEL["name"]
    assert data["crop_type"] == "hazelnut"
    assert data["area_hectares"] == 12.5


async def test_create_parcel_cooperative_admin(client):
    h = await _auth(client, role="cooperative_admin")
    r = await _create_parcel(client, h)
    assert r.status_code == 201


async def test_create_parcel_analyst_forbidden(client):
    h = await _auth(client, role="analyst")
    r = await _create_parcel(client, h)
    assert r.status_code == 403


async def test_create_parcel_unauthenticated(client):
    r = await client.post("/api/parcels", json=PARCEL)
    assert r.status_code == 401


# ─── List ─────────────────────────────────────────

async def test_list_parcels(client):
    h = await _auth(client)
    await _create_parcel(client, h, name="Parcel A")
    await _create_parcel(client, h, name="Parcel B")
    r = await client.get("/api/parcels", headers=h)
    assert r.status_code == 200
    assert len(r.json()) == 2


# ─── Get ──────────────────────────────────────────

async def test_get_parcel(client):
    h = await _auth(client)
    cr = await _create_parcel(client, h)
    pid = cr.json()["id"]
    r = await client.get(f"/api/parcels/{pid}", headers=h)
    assert r.status_code == 200
    assert r.json()["name"] == PARCEL["name"]


# ─── Update ───────────────────────────────────────

async def test_update_parcel(client):
    h = await _auth(client)
    cr = await _create_parcel(client, h)
    pid = cr.json()["id"]
    r = await client.put(f"/api/parcels/{pid}", json={"area_hectares": 15.0}, headers=h)
    assert r.status_code == 200
    assert r.json()["area_hectares"] == 15.0
    assert r.json()["name"] == PARCEL["name"]  # unchanged


# ─── Delete (soft) ────────────────────────────────

async def test_delete_parcel(client):
    h = await _auth(client)
    cr = await _create_parcel(client, h)
    pid = cr.json()["id"]
    r = await client.delete(f"/api/parcels/{pid}", headers=h)
    assert r.status_code == 204
    # Should not appear in list anymore
    r2 = await client.get("/api/parcels", headers=h)
    assert len(r2.json()) == 0


# ─── EUDR Summary ────────────────────────────────

async def test_eudr_summary(client):
    h = await _auth(client)
    cr = await _create_parcel(client, h, commodity_code="0802.22")
    pid = cr.json()["id"]
    r = await client.get(f"/api/parcels/{pid}/eudr-summary", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert data["commodity"] == "hazelnut"
    assert data["commodity_code"] == "0802.22"
    assert data["geolocation"]["lat"] == 41.2
