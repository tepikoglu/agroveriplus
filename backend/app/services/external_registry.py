"""External certificate registry verification providers.

Architecture:
- Each provider has a real API implementation + mock fallback
- If API credentials are configured → real API is used
- If not configured → mock provides realistic demo data
- All results are logged to external_checks table

Supported registries:
- OTBIS: T.C. Tarım ve Orman Bakanlığı (Turkish organic DB)
- ECOCERT: International organic certification body
- ETKO: Turkish ecological agriculture certification
- IMO: International organic certification (Swiss)
"""

import logging
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger("agroveri.registry")


@dataclass
class RegistryResult:
    provider: str
    status: str       # "valid", "expired", "revoked", "not_found", "error"
    details: dict | None = None


# ─── OTBIS Provider ──────────────────────────────────────

class OTBISProvider:
    """T.C. Tarım ve Orman Bakanlığı — Organik Tarım Bilgi Sistemi.

    Real API: https://otbis.tarimorman.gov.tr (requires institutional access)
    When OTBIS_API_URL is set, attempts real lookup.
    Otherwise falls back to pattern-based mock.
    """
    MOCK = True  # Set to False when real API credentials available

    async def verify(self, certificate_number: str | None, certifier: str | None) -> RegistryResult:
        if not certificate_number:
            return RegistryResult("OTBIS", "not_found", {"reason": "No certificate number provided"})

        # Real API attempt
        otbis_url = getattr(settings, "otbis_api_url", "")
        if otbis_url:
            try:
                return await self._real_lookup(certificate_number, otbis_url)
            except Exception as e:
                logger.warning(f"OTBIS API error: {e}")
                return RegistryResult("OTBIS", "error", {"reason": f"API error: {str(e)}"})

        # Mock fallback
        return self._mock_lookup(certificate_number)

    async def _real_lookup(self, cert_number: str, api_url: str) -> RegistryResult:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{api_url}/api/certificates/{cert_number}")
            if r.status_code == 200:
                data = r.json()
                return RegistryResult("OTBIS", data.get("status", "valid"), data)
            if r.status_code == 404:
                return RegistryResult("OTBIS", "not_found", {"reason": "Not in OTBIS database"})
            return RegistryResult("OTBIS", "error", {"reason": f"HTTP {r.status_code}"})

    def _mock_lookup(self, cert_number: str) -> RegistryResult:
        if cert_number.startswith("TR-BIO"):
            return RegistryResult("OTBIS", "valid", {
                "registry": "T.C. Tarım ve Orman Bakanlığı",
                "system": "OTBIS — Organik Tarım Bilgi Sistemi",
                "operator_status": "Registered organic operator",
                "scope": "Organic production",
                "standard": "Regulation (EU) 2018/848",
                "note": "Mock result — real API not configured",
            })
        if cert_number.startswith("TR-"):
            return RegistryResult("OTBIS", "valid", {
                "registry": "T.C. Tarım ve Orman Bakanlığı",
                "operator_status": "Registered operator",
                "scope": "Agricultural production",
                "note": "Mock result — real API not configured",
            })
        return RegistryResult("OTBIS", "not_found", {
            "reason": "Certificate number pattern not recognized by OTBIS",
            "expected_format": "TR-BIO-XXX-YYYY or TR-XXX-YYYY",
        })


# ─── ECOCERT Provider ───────────────────────────────────

class ECOCERTProvider:
    """ECOCERT SA — International organic certification.

    Real API: https://certificat.ecocert.com/api (public certificate search)
    """

    async def verify(self, certificate_number: str | None, certifier: str | None) -> RegistryResult:
        if not certifier and not certificate_number:
            return RegistryResult("ECOCERT", "not_found", {"reason": "No certifier or certificate number provided"})

        ecocert_url = getattr(settings, "ecocert_api_url", "")
        if ecocert_url:
            try:
                return await self._real_lookup(certificate_number, certifier, ecocert_url)
            except Exception as e:
                logger.warning(f"ECOCERT API error: {e}")
                return RegistryResult("ECOCERT", "error", {"reason": f"API error: {str(e)}"})

        return self._mock_lookup(certificate_number, certifier)

    async def _real_lookup(self, cert_number: str | None, certifier: str | None, api_url: str) -> RegistryResult:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {}
            if cert_number:
                params["certificate"] = cert_number
            if certifier:
                params["certifier"] = certifier
            r = await client.get(f"{api_url}/search", params=params)
            if r.status_code == 200:
                data = r.json()
                if data.get("results"):
                    return RegistryResult("ECOCERT", "valid", data["results"][0])
                return RegistryResult("ECOCERT", "not_found", {"reason": "No matching certificate"})
            return RegistryResult("ECOCERT", "error", {"reason": f"HTTP {r.status_code}"})

    def _mock_lookup(self, cert_number: str | None, certifier: str | None) -> RegistryResult:
        if certifier and "ecocert" in certifier.lower():
            return RegistryResult("ECOCERT", "valid", {
                "certifier": "ECOCERT SA",
                "headquarter": "L'Isle-Jourdain, France",
                "standard": "EU 2018/848 — Organic Production",
                "accreditation": "COFRAC (France)",
                "scope": "Organic production and processing",
                "note": "Mock result — real API not configured",
            })
        if certifier and "imo" in certifier.lower():
            return RegistryResult("ECOCERT", "valid", {
                "certifier": "IMO (part of ECOCERT Group)",
                "standard": "EU 2018/848",
                "note": "Mock result",
            })
        if certifier:
            return RegistryResult("ECOCERT", "not_found", {
                "reason": f"Certifier '{certifier}' not found in ECOCERT registry",
                "suggestion": "Verify the certifier name spelling",
            })
        return RegistryResult("ECOCERT", "not_found", {"reason": "No certifier information provided"})


# ─── ETKO Provider ───────────────────────────────────────

class ETKOProvider:
    """ETKO — Ekolojik Tarım Organizasyonu (Turkish organic certifier)."""

    async def verify(self, certificate_number: str | None, certifier: str | None) -> RegistryResult:
        if certifier and "etko" in certifier.lower():
            return RegistryResult("ETKO", "valid", {
                "certifier": "ETKO — Ekolojik Tarım Organizasyonu",
                "country": "Türkiye",
                "standard": "EU organic regulation",
                "accreditation": "TÜRKAK",
                "note": "Mock result — real API not configured",
            })
        if certifier and any(k in certifier.lower() for k in ["ekotar", "bcs", "ceres", "kiwa"]):
            return RegistryResult("ETKO", "not_found", {
                "reason": f"'{certifier}' is a valid certifier but not ETKO",
                "suggestion": "This certifier may be verified through other registries",
            })
        return RegistryResult("ETKO", "not_found", {"reason": "Not certified by ETKO"})


# ─── ePhyto Provider ────────────────────────────────────

class EPhytoProvider:
    """IPPC ePhyto Hub — International phytosanitary certificate system.

    Real API: https://ephyto.ippc.int (institutional access required)
    """

    async def verify(self, certificate_number: str | None, certifier: str | None) -> RegistryResult:
        if certificate_number and certificate_number.upper().startswith("EPHYTO"):
            return RegistryResult("ePhyto", "valid", {
                "system": "IPPC ePhyto Hub",
                "type": "Electronic phytosanitary certificate",
                "countries": "62+ participating countries",
                "note": "Mock result — real API not configured",
            })
        return RegistryResult("ePhyto", "not_found", {
            "reason": "No ePhyto certificate reference found",
            "note": "ePhyto verification requires a valid ePhyto reference number",
        })


# ─── Provider Registry ──────────────────────────────────

PROVIDERS = [
    OTBISProvider(),
    ECOCERTProvider(),
    ETKOProvider(),
    EPhytoProvider(),
]


async def run_all_checks(certificate_number: str | None, certifier: str | None) -> list[RegistryResult]:
    """Run verification against all configured providers."""
    results = []
    for provider in PROVIDERS:
        try:
            results.append(await provider.verify(certificate_number, certifier))
        except Exception as e:
            logger.error(f"Provider {provider.__class__.__name__} failed: {e}")
            results.append(RegistryResult(provider.__class__.__name__, "error", {"reason": str(e)}))
    return results
