"""Google OAuth endpoint tests using mock token format (mock:email:name)."""


async def test_google_auth_new_user(client):
    """First Google login should auto-register the user."""
    r = await client.post("/api/auth/google", json={
        "id_token": "mock:ali@gmail.com:Ali Yilmaz",
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Verify user was created
    me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {data['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "ali@gmail.com"
    assert me.json()["name"] == "Ali Yilmaz"
    assert me.json()["role"] == "farmer"  # default


async def test_google_auth_with_role(client):
    """Google auth should respect role parameter."""
    r = await client.post("/api/auth/google", json={
        "id_token": "mock:admin@cofub.org:Kooperatif Admin",
        "role": "cooperative_admin",
    })
    assert r.status_code == 200
    me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {r.json()['access_token']}"})
    assert me.json()["role"] == "cooperative_admin"


async def test_google_auth_existing_user(client):
    """Second Google login should return same user, not create duplicate."""
    # First login
    r1 = await client.post("/api/auth/google", json={"id_token": "mock:repeat@test.com:Repeat"})
    assert r1.status_code == 200
    me1 = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {r1.json()['access_token']}"})

    # Second login
    r2 = await client.post("/api/auth/google", json={"id_token": "mock:repeat@test.com:Repeat"})
    assert r2.status_code == 200
    me2 = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {r2.json()['access_token']}"})

    assert me1.json()["id"] == me2.json()["id"]  # same user


async def test_google_auth_links_existing_email_account(client):
    """If user registered with email/password, Google login should link OAuth."""
    # Register with email
    await client.post("/api/auth/register", json={
        "email": "linked@test.com", "password": "test12345", "name": "Linked User",
    })

    # Google login with same email
    r = await client.post("/api/auth/google", json={"id_token": "mock:linked@test.com:Linked User"})
    assert r.status_code == 200

    # Should still be able to login with password
    r2 = await client.post("/api/auth/login", json={"email": "linked@test.com", "password": "test12345"})
    assert r2.status_code == 200


async def test_google_auth_invalid_role(client):
    r = await client.post("/api/auth/google", json={
        "id_token": "mock:bad@test.com:Bad",
        "role": "superadmin",
    })
    assert r.status_code == 400
    assert "Invalid role" in r.json()["detail"]


async def test_google_auth_invalid_token(client):
    r = await client.post("/api/auth/google", json={"id_token": "not-a-valid-token"})
    assert r.status_code == 401


async def test_google_auth_empty_token(client):
    r = await client.post("/api/auth/google", json={"id_token": ""})
    assert r.status_code == 401
