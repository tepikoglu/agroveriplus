import io

REG = {"email": "mycert@test.com", "password": "test12345", "name": "Cert Owner"}


async def _auth(client, email=None):
    e = email or REG["email"]
    await client.post("/api/auth/register", json={**REG, "email": e})
    r = await client.post("/api/auth/login", json={"email": e, "password": REG["password"]})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def test_my_certs_empty(client):
    h = await _auth(client)
    r = await client.get("/api/certificates/my", headers=h)
    assert r.status_code == 200
    assert r.json() == []


async def test_my_certs_returns_own(client):
    h = await _auth(client)
    await client.post("/api/certificates/upload", files={"file": ("a.pdf", io.BytesIO(b"cert A"), "application/pdf")}, headers=h)
    await client.post("/api/certificates/upload", files={"file": ("b.pdf", io.BytesIO(b"cert B"), "application/pdf")}, headers=h)
    r = await client.get("/api/certificates/my", headers=h)
    assert r.status_code == 200
    assert len(r.json()) == 2
    names = {c["original_filename"] for c in r.json()}
    assert names == {"a.pdf", "b.pdf"}


async def test_my_certs_isolation(client):
    """User A should not see User B's certificates."""
    ha = await _auth(client, email="userA@test.com")
    hb = await _auth(client, email="userB@test.com")
    await client.post("/api/certificates/upload", files={"file": ("a.pdf", io.BytesIO(b"user A cert"), "application/pdf")}, headers=ha)
    await client.post("/api/certificates/upload", files={"file": ("b.pdf", io.BytesIO(b"user B cert"), "application/pdf")}, headers=hb)
    ra = await client.get("/api/certificates/my", headers=ha)
    rb = await client.get("/api/certificates/my", headers=hb)
    assert len(ra.json()) == 1
    assert ra.json()[0]["original_filename"] == "a.pdf"
    assert len(rb.json()) == 1
    assert rb.json()[0]["original_filename"] == "b.pdf"


async def test_my_certs_unauthenticated(client):
    r = await client.get("/api/certificates/my")
    assert r.status_code == 401


async def test_my_certs_includes_metadata(client):
    h = await _auth(client)
    r = await client.post("/api/certificates/upload", files={"file": ("cert.pdf", io.BytesIO(b"meta cert"), "application/pdf")}, headers=h)
    cid = r.json()["id"]
    await client.put(f"/api/certificates/{cid}/metadata", json={"certifier_name": "ECOCERT", "product_type": "Hazelnut"}, headers=h)
    r2 = await client.get("/api/certificates/my", headers=h)
    cert = r2.json()[0]
    assert cert["certifier_name"] == "ECOCERT"
    assert cert["product_type"] == "Hazelnut"


async def test_anon_upload_not_in_my_certs(client):
    """Anonymous uploads should not appear in any user's /my list."""
    await client.post("/api/certificates/upload", files={"file": ("anon.pdf", io.BytesIO(b"anon"), "application/pdf")})
    h = await _auth(client)
    r = await client.get("/api/certificates/my", headers=h)
    assert len(r.json()) == 0
