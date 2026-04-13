import io

REG_ADMIN = {"email": "admin@agroveri.plus", "password": "admin12345", "name": "Admin User", "role": "admin"}
REG_FARMER = {"email": "farmer@test.com", "password": "test12345", "name": "Farmer User", "role": "farmer"}


async def _auth(client, reg=None):
    reg = reg or REG_ADMIN
    await client.post("/api/auth/register", json=reg)
    r = await client.post("/api/auth/login", json={"email": reg["email"], "password": reg["password"]})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


# ─── Access control ──────────────────────────────────

async def test_admin_stats_requires_admin(client):
    h = await _auth(client, REG_FARMER)
    r = await client.get("/api/admin/stats", headers=h)
    assert r.status_code == 403


async def test_admin_stats_unauthenticated(client):
    r = await client.get("/api/admin/stats")
    assert r.status_code == 401


# ─── Stats ───────────────────────────────────────────

async def test_admin_stats(client):
    h = await _auth(client)
    r = await client.get("/api/admin/stats", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert "users" in data
    assert data["users"]["total"] >= 1
    assert "by_role" in data["users"]
    assert "certificates" in data
    assert "parcels" in data
    assert "verifications" in data
    assert "external_checks" in data


# ─── User listing ────────────────────────────────────

async def test_admin_list_users(client):
    h = await _auth(client)
    # Create another user
    await client.post("/api/auth/register", json=REG_FARMER)
    r = await client.get("/api/admin/users", headers=h)
    assert r.status_code == 200
    assert len(r.json()) >= 2


# ─── Role change ─────────────────────────────────────

async def test_admin_change_role(client):
    h = await _auth(client)
    await client.post("/api/auth/register", json=REG_FARMER)
    users = (await client.get("/api/admin/users", headers=h)).json()
    farmer = next(u for u in users if u["email"] == REG_FARMER["email"])

    r = await client.put(f"/api/admin/users/{farmer['id']}/role?role=analyst", headers=h)
    assert r.status_code == 200
    assert r.json()["role"] == "analyst"


async def test_admin_change_role_invalid(client):
    h = await _auth(client)
    await client.post("/api/auth/register", json=REG_FARMER)
    users = (await client.get("/api/admin/users", headers=h)).json()
    farmer = next(u for u in users if u["email"] == REG_FARMER["email"])

    r = await client.put(f"/api/admin/users/{farmer['id']}/role?role=superuser", headers=h)
    assert r.status_code == 400


# ─── Deactivate / Activate ───────────────────────────

async def test_admin_deactivate_user(client):
    h = await _auth(client)
    await client.post("/api/auth/register", json=REG_FARMER)
    users = (await client.get("/api/admin/users", headers=h)).json()
    farmer = next(u for u in users if u["email"] == REG_FARMER["email"])

    r = await client.put(f"/api/admin/users/{farmer['id']}/deactivate", headers=h)
    assert r.status_code == 200
    assert r.json()["is_active"] is False

    # Deactivated user cannot login
    r2 = await client.post("/api/auth/login", json={"email": REG_FARMER["email"], "password": REG_FARMER["password"]})
    assert r2.status_code == 403


async def test_admin_activate_user(client):
    h = await _auth(client)
    await client.post("/api/auth/register", json=REG_FARMER)
    users = (await client.get("/api/admin/users", headers=h)).json()
    farmer = next(u for u in users if u["email"] == REG_FARMER["email"])

    await client.put(f"/api/admin/users/{farmer['id']}/deactivate", headers=h)
    r = await client.put(f"/api/admin/users/{farmer['id']}/activate", headers=h)
    assert r.status_code == 200
    assert r.json()["is_active"] is True


async def test_admin_cannot_deactivate_self(client):
    h = await _auth(client)
    users = (await client.get("/api/admin/users", headers=h)).json()
    me = next(u for u in users if u["email"] == REG_ADMIN["email"])

    r = await client.put(f"/api/admin/users/{me['id']}/deactivate", headers=h)
    assert r.status_code == 400


# ─── All certificates ────────────────────────────────

async def test_admin_list_certificates(client):
    h = await _auth(client)
    await client.post("/api/certificates/upload", files={"file": ("admin.pdf", io.BytesIO(b"admin cert"), "application/pdf")})
    r = await client.get("/api/admin/certificates", headers=h)
    assert r.status_code == 200
    assert len(r.json()) >= 1
    assert "sha256" in r.json()[0]
