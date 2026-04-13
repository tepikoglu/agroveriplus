import io

REG = {"email": "dds@test.com", "password": "test12345", "name": "DDS User"}
PARCEL = {
    "name": "Çarşamba Fındık",
    "location_lat": 41.2,
    "location_lon": 36.7,
    "area_hectares": 12.5,
    "crop_type": "hazelnut",
    "province": "Samsun",
    "district": "Çarşamba",
    "commodity_code": "0802.22",
    "geojson_polygon": {"type": "Polygon", "coordinates": [[[36.6, 41.1], [36.8, 41.1], [36.8, 41.3], [36.6, 41.3], [36.6, 41.1]]]},
}


async def _auth(client):
    await client.post("/api/auth/register", json=REG)
    r = await client.post("/api/auth/login", json={"email": REG["email"], "password": REG["password"]})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def _setup(client, h):
    """Create a parcel + upload and link a certificate with metadata."""
    # Create parcel
    pr = await client.post("/api/parcels", json=PARCEL, headers=h)
    pid = pr.json()["id"]

    # Upload certificate
    cr = await client.post("/api/certificates/upload", files={"file": ("organic.pdf", io.BytesIO(b"dds cert"), "application/pdf")}, headers=h)
    cid = cr.json()["id"]

    # Add metadata + link to parcel
    await client.put(f"/api/certificates/{cid}/metadata", json={
        "certifier_name": "ECOCERT",
        "certificate_number": "TR-BIO-154-2026",
        "product_type": "Organic Hazelnut",
        "parcel_id": pid,
    }, headers=h)

    return pid, cid


async def test_dds_export_full(client):
    """Full DDS export with parcel + linked certificate + metadata."""
    h = await _auth(client)
    pid, cid = await _setup(client, h)

    r = await client.get(f"/api/parcels/{pid}/dds-export", headers=h)
    assert r.status_code == 200
    dds = r.json()

    # Structure
    assert dds["regulation"] == "EU 2023/1115 (EUDR)"
    assert dds["dds_version"] == "1.0"

    # Product
    assert dds["product"]["commodity"] == "hazelnut"
    assert dds["product"]["hs_code"] == "0802.22"
    assert "Hazelnuts" in dds["product"]["hs_description"]

    # Geolocation
    assert dds["geolocation"]["latitude"] == 41.2
    assert dds["geolocation"]["country"] == "Türkiye"
    assert dds["geolocation"]["plot_boundary"] is not None

    # Certificates
    assert len(dds["certificates"]) == 1
    cert = dds["certificates"][0]
    assert cert["certifier"] == "ECOCERT"
    assert cert["certificate_number"] == "TR-BIO-154-2026"
    assert len(cert["sha256"]) == 64

    # Risk
    assert dds["risk_assessment"]["level"] == "low"
    assert dds["risk_assessment"]["deforestation_free"] is True

    # Completeness
    assert dds["completeness"]["percent"] >= 80


async def test_dds_export_minimal_parcel(client):
    """DDS for parcel without certificate or EUDR fields."""
    h = await _auth(client)
    pr = await client.post("/api/parcels", json={
        "name": "Bare Plot",
        "location_lat": 40.0, "location_lon": 35.0,
        "area_hectares": 3.0, "crop_type": "olive",
    }, headers=h)
    pid = pr.json()["id"]

    r = await client.get(f"/api/parcels/{pid}/dds-export", headers=h)
    assert r.status_code == 200
    dds = r.json()
    assert dds["certificates"] == []
    assert dds["risk_assessment"]["level"] == "high"
    assert dds["completeness"]["percent"] < 50


async def test_dds_export_not_found(client):
    h = await _auth(client)
    r = await client.get("/api/parcels/00000000-0000-0000-0000-000000000000/dds-export", headers=h)
    assert r.status_code == 404


async def test_dds_export_unauthenticated(client):
    r = await client.get("/api/parcels/00000000-0000-0000-0000-000000000000/dds-export")
    assert r.status_code == 401
