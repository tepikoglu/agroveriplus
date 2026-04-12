REG = {"email": "ali@cofub.org", "password": "findik2026", "name": "Ali Yılmaz", "phone": "+905551234567"}


async def _register(client, **overrides):
    payload = {**REG, **overrides}
    return await client.post("/api/auth/register", json=payload)


async def _login(client, email=REG["email"], password=REG["password"]):
    return await client.post("/api/auth/login", json={"email": email, "password": password})


async def _tokens(client, **overrides):
    """Register + login, return (access_token, refresh_token)."""
    await _register(client, **overrides)
    r = await _login(client, overrides.get("email", REG["email"]), overrides.get("password", REG["password"]))
    data = r.json()
    return data["access_token"], data["refresh_token"]


# ─── Register ─────────────────────────────────────────────

async def test_register_success(client):
    r = await _register(client)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == REG["email"]
    assert data["name"] == REG["name"]
    assert data["role"] == "farmer"
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


async def test_register_with_role(client):
    r = await _register(client, role="agronomist")
    assert r.status_code == 201
    assert r.json()["role"] == "agronomist"


async def test_register_all_roles(client):
    roles = ["farmer", "agronomist", "cooperative_admin", "analyst"]
    for i, role in enumerate(roles):
        r = await _register(client, email=f"user{i}@test.com", role=role)
        assert r.status_code == 201
        assert r.json()["role"] == role


async def test_register_invalid_role(client):
    r = await _register(client, role="hacker")
    assert r.status_code == 400
    assert "Invalid role" in r.json()["detail"]


async def test_register_duplicate_email(client):
    await _register(client)
    r = await _register(client)
    assert r.status_code == 409
    assert "already registered" in r.json()["detail"]


async def test_register_short_password(client):
    r = await _register(client, password="abc")
    assert r.status_code == 400
    assert "8 characters" in r.json()["detail"]


# ─── Login ─────────────────────────────────────────────────

async def test_login_success(client):
    await _register(client)
    r = await _login(client)
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client):
    await _register(client)
    r = await _login(client, password="wrongpassword")
    assert r.status_code == 401


async def test_login_nonexistent_email(client):
    r = await _login(client, email="nobody@nowhere.com")
    assert r.status_code == 401


# ─── Refresh ──────────────────────────────────────────────

async def test_refresh_success(client):
    _, refresh = await _tokens(client)
    r = await client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_refresh_with_access_token_fails(client):
    access, _ = await _tokens(client)
    r = await client.post("/api/auth/refresh", json={"refresh_token": access})
    assert r.status_code == 401
    assert "Not a refresh token" in r.json()["detail"]


async def test_refresh_with_garbage_fails(client):
    r = await client.post("/api/auth/refresh", json={"refresh_token": "not.a.token"})
    assert r.status_code == 401


# ─── /me (Protected) ─────────────────────────────────────

async def test_me_authenticated(client):
    access, _ = await _tokens(client)
    r = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == REG["email"]
    assert data["name"] == REG["name"]


async def test_me_no_token(client):
    r = await client.get("/api/auth/me")
    assert r.status_code == 401


async def test_me_invalid_token(client):
    r = await client.get("/api/auth/me", headers={"Authorization": "Bearer garbage.token.here"})
    assert r.status_code == 401


# ─── Upload with auth (optional) ─────────────────────────

async def test_upload_works_without_auth(client):
    """Upload should still work without authentication."""
    import io
    r = await client.post(
        "/api/certificates/upload",
        files={"file": ("cert.pdf", io.BytesIO(b"anon upload test"), "application/pdf")},
    )
    assert r.status_code == 200


async def test_upload_works_with_auth(client):
    """Upload should also work when authenticated."""
    import io
    access, _ = await _tokens(client)
    r = await client.post(
        "/api/certificates/upload",
        files={"file": ("cert.pdf", io.BytesIO(b"auth upload test"), "application/pdf")},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200
