import io

REG = {"email": "notify@test.com", "password": "test12345", "name": "Notify User"}


async def _auth(client, role="farmer"):
    await client.post("/api/auth/register", json={**REG, "role": role, "email": f"{role}@test.com"})
    r = await client.post("/api/auth/login", json={"email": f"{role}@test.com", "password": REG["password"]})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


# ─── List notifications ──────────────────────────

async def test_notifications_empty(client):
    h = await _auth(client)
    r = await client.get("/api/notifications", headers=h)
    assert r.status_code == 200
    assert r.json() == []


async def test_notifications_unauthenticated(client):
    r = await client.get("/api/notifications")
    assert r.status_code == 401


# ─── Upload triggers notification ─────────────────

async def test_upload_creates_notification(client):
    h = await _auth(client)
    await client.post(
        "/api/certificates/upload",
        files={"file": ("organic.pdf", io.BytesIO(b"notify test"), "application/pdf")},
        headers=h,
    )
    r = await client.get("/api/notifications", headers=h)
    assert r.status_code == 200
    notifications = r.json()
    assert len(notifications) == 1
    assert notifications[0]["event"] == "certificate_uploaded"
    assert "organic.pdf" in notifications[0]["body"]
    assert notifications[0]["is_read"] is False


# ─── Parcel triggers notification ──────────────────

async def test_parcel_creates_notification(client):
    h = await _auth(client)
    await client.post("/api/parcels", json={
        "name": "Findik Bahcesi",
        "location_lat": 41.2, "location_lon": 36.7,
        "area_hectares": 10.0, "crop_type": "hazelnut",
    }, headers=h)
    r = await client.get("/api/notifications", headers=h)
    assert r.status_code == 200
    notifications = r.json()
    assert len(notifications) == 1
    assert notifications[0]["event"] == "parcel_created"
    assert "Findik Bahcesi" in notifications[0]["body"]


# ─── Mark as read ─────────────────────────────────

async def test_mark_notification_read(client):
    h = await _auth(client)
    await client.post(
        "/api/certificates/upload",
        files={"file": ("cert.pdf", io.BytesIO(b"read test"), "application/pdf")},
        headers=h,
    )
    r = await client.get("/api/notifications", headers=h)
    nid = r.json()[0]["id"]

    # Mark as read
    r2 = await client.post(f"/api/notifications/{nid}/read", headers=h)
    assert r2.status_code == 204

    # Should be read now
    r3 = await client.get("/api/notifications", headers=h)
    assert r3.json()[0]["is_read"] is True


async def test_unread_only_filter(client):
    h = await _auth(client)
    # Create 2 notifications
    await client.post("/api/certificates/upload", files={"file": ("a.pdf", io.BytesIO(b"aa"), "application/pdf")}, headers=h)
    await client.post("/api/certificates/upload", files={"file": ("b.pdf", io.BytesIO(b"bb"), "application/pdf")}, headers=h)

    # Mark first as read
    r = await client.get("/api/notifications", headers=h)
    nid = r.json()[-1]["id"]  # oldest
    await client.post(f"/api/notifications/{nid}/read", headers=h)

    # Filter unread only
    r2 = await client.get("/api/notifications?unread_only=true", headers=h)
    assert len(r2.json()) == 1


async def test_mark_nonexistent_notification(client):
    h = await _auth(client)
    r = await client.post("/api/notifications/00000000-0000-0000-0000-000000000000/read", headers=h)
    assert r.status_code == 404
