"""Tests for enhanced external registry providers."""

from app.services.external_registry import (
    OTBISProvider,
    ECOCERTProvider,
    ETKOProvider,
    EPhytoProvider,
    run_all_checks,
)


# ─── OTBIS ─────────────────────────────────────────────

async def test_otbis_tr_bio_valid():
    p = OTBISProvider()
    r = await p.verify("TR-BIO-154-2026", "ECOCERT")
    assert r.status == "valid"
    assert "Tarım" in r.details["registry"]


async def test_otbis_tr_prefix_valid():
    p = OTBISProvider()
    r = await p.verify("TR-ORG-001", None)
    assert r.status == "valid"


async def test_otbis_unknown_pattern():
    p = OTBISProvider()
    r = await p.verify("XX-FAKE-000", None)
    assert r.status == "not_found"
    assert "expected_format" in r.details


async def test_otbis_no_cert_number():
    p = OTBISProvider()
    r = await p.verify(None, "ECOCERT")
    assert r.status == "not_found"


# ─── ECOCERT ──────────────────────────────────────────

async def test_ecocert_match():
    p = ECOCERTProvider()
    r = await p.verify("TR-BIO-154", "ECOCERT SA")
    assert r.status == "valid"
    assert "COFRAC" in r.details["accreditation"]


async def test_ecocert_imo():
    p = ECOCERTProvider()
    r = await p.verify(None, "IMO Control")
    assert r.status == "valid"


async def test_ecocert_unknown():
    p = ECOCERTProvider()
    r = await p.verify(None, "Random Corp")
    assert r.status == "not_found"
    assert "suggestion" in r.details


# ─── ETKO ────────────────────────────────────────────

async def test_etko_valid():
    p = ETKOProvider()
    r = await p.verify(None, "ETKO")
    assert r.status == "valid"
    assert r.details["accreditation"] == "TÜRKAK"


async def test_etko_other_certifier():
    p = ETKOProvider()
    r = await p.verify(None, "BCS Öko-Garantie")
    assert r.status == "not_found"
    assert "suggestion" in r.details


# ─── ePhyto ──────────────────────────────────────────

async def test_ephyto_valid():
    p = EPhytoProvider()
    r = await p.verify("EPHYTO-TR-2026-001", None)
    assert r.status == "valid"
    assert "IPPC" in r.details["system"]


async def test_ephyto_no_reference():
    p = EPhytoProvider()
    r = await p.verify("TR-BIO-001", None)
    assert r.status == "not_found"


# ─── Run All ─────────────────────────────────────────

async def test_run_all_four_providers():
    results = await run_all_checks("TR-BIO-001", "ECOCERT")
    assert len(results) == 4
    providers = {r.provider for r in results}
    assert providers == {"OTBIS", "ECOCERT", "ETKO", "ePhyto"}
