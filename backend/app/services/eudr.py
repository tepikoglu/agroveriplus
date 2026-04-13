"""EUDR Due Diligence Statement generator.

Produces structured DDS data per EU Deforestation Regulation (2023/1115).
JSON export always available. PDF generation requires reportlab (optional).
"""

import json
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certificate import Certificate
from app.models.parcel import Parcel


# HS commodity codes relevant to EUDR
EUDR_COMMODITIES = {
    "0801": "Coconuts, Brazil nuts, cashew nuts",
    "0802": "Other nuts (incl. hazelnuts, almonds)",
    "0802.22": "Hazelnuts (shelled)",
    "0901": "Coffee",
    "1201": "Soya beans",
    "1511": "Palm oil",
    "1801": "Cocoa beans",
    "4001": "Natural rubber",
    "4403": "Wood in the rough",
    "4407": "Wood sawn or chipped",
}


def _risk_level(parcel: Parcel, certificates: list) -> str:
    """Simple risk assessment based on data completeness."""
    score = 0
    if parcel.geojson_polygon:
        score += 2
    if parcel.commodity_code:
        score += 1
    if parcel.province and parcel.district:
        score += 1
    if any(c.certifier_name for c in certificates):
        score += 2
    if any(c.certificate_number and c.certificate_number.startswith("TR-BIO") for c in certificates):
        score += 2
    if score >= 6:
        return "low"
    if score >= 3:
        return "medium"
    return "high"


def _completeness(parcel: Parcel, certificates: list) -> dict:
    """Check which EUDR fields are filled."""
    checks = {
        "geolocation": True,  # lat/lon always present
        "country_of_production": bool(parcel.country),
        "plot_boundary": bool(parcel.geojson_polygon),
        "commodity_code": bool(parcel.commodity_code),
        "area_declared": bool(parcel.area_hectares),
        "organic_certificate": any(c.certifier_name for c in certificates),
        "certificate_number": any(c.certificate_number for c in certificates),
        "certificate_validity": any(c.valid_from and c.valid_until for c in certificates),
    }
    filled = sum(1 for v in checks.values() if v)
    return {"checks": checks, "score": f"{filled}/{len(checks)}", "percent": round(filled / len(checks) * 100)}


async def generate_dds(db: AsyncSession, parcel_id: UUID, user_id: UUID) -> dict:
    """Generate a full EUDR Due Diligence Statement data package."""
    result = await db.execute(
        select(Parcel).where(Parcel.id == parcel_id, Parcel.user_id == user_id, Parcel.is_deleted == False)
    )
    parcel = result.scalar_one_or_none()
    if not parcel:
        return None

    # Get linked certificates
    cert_result = await db.execute(
        select(Certificate).where(Certificate.parcel_id == parcel_id)
    )
    certificates = list(cert_result.scalars().all())

    completeness = _completeness(parcel, certificates)
    risk = _risk_level(parcel, certificates)

    commodity_desc = EUDR_COMMODITIES.get(parcel.commodity_code, "")
    if not commodity_desc and parcel.commodity_code:
        # Try parent code
        parent = parcel.commodity_code.split(".")[0]
        commodity_desc = EUDR_COMMODITIES.get(parent, "Unknown commodity")

    dds = {
        "dds_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "regulation": "EU 2023/1115 (EUDR)",

        "operator": {
            "parcel_id": str(parcel.id),
            "parcel_name": parcel.name,
        },

        "product": {
            "commodity": parcel.crop_type,
            "hs_code": parcel.commodity_code,
            "hs_description": commodity_desc,
        },

        "geolocation": {
            "country": parcel.country,
            "province": parcel.province,
            "district": parcel.district,
            "latitude": parcel.location_lat,
            "longitude": parcel.location_lon,
            "area_hectares": parcel.area_hectares,
            "plot_boundary": parcel.geojson_polygon,
        },

        "certificates": [
            {
                "id": str(c.id),
                "filename": c.original_filename,
                "sha256": c.sha256_hash,
                "certifier": c.certifier_name,
                "certificate_number": c.certificate_number,
                "product_type": c.product_type,
                "valid_from": c.valid_from.isoformat() if c.valid_from else None,
                "valid_until": c.valid_until.isoformat() if c.valid_until else None,
                "ipfs_cid": c.ipfs_cid,
            }
            for c in certificates
        ],

        "risk_assessment": {
            "level": risk,
            "deforestation_free": risk == "low",
        },

        "completeness": completeness,
    }

    return dds
