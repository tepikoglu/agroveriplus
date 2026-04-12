"""External certificate registry verification providers.

Each provider checks a certificate against an external registry
(OTBIS, ECOCERT, ETKO, etc.) and returns a standardized result.

Sprint 2: MockProvider for demo. Sprint 3: real API integrations.
"""

from dataclasses import dataclass


@dataclass
class RegistryResult:
    provider: str
    status: str       # "valid", "expired", "revoked", "not_found", "error"
    details: dict | None = None


class MockOTBISProvider:
    """Mock Turkish Organic Trade Information System."""

    async def verify(self, certificate_number: str | None, certifier: str | None) -> RegistryResult:
        if not certificate_number:
            return RegistryResult("OTBIS", "not_found", {"reason": "No certificate number provided"})
        if certificate_number.startswith("TR-BIO"):
            return RegistryResult("OTBIS", "valid", {
                "registry": "T.C. Tarım ve Orman Bakanlığı",
                "operator": "Registered organic operator",
                "scope": "Organic production",
            })
        return RegistryResult("OTBIS", "not_found", {"reason": "Certificate not in OTBIS database"})


class MockECOCERTProvider:
    """Mock ECOCERT international registry."""

    async def verify(self, certificate_number: str | None, certifier: str | None) -> RegistryResult:
        if certifier and "ecocert" in certifier.lower():
            return RegistryResult("ECOCERT", "valid", {
                "certifier": "ECOCERT SA",
                "standard": "EU 2018/848",
                "scope": "Organic production and processing",
            })
        if not certifier:
            return RegistryResult("ECOCERT", "not_found", {"reason": "No certifier information"})
        return RegistryResult("ECOCERT", "not_found", {"reason": f"Certifier '{certifier}' not in ECOCERT registry"})


class MockETKOProvider:
    """Mock ETKO (Ecological Agriculture Organization) registry."""

    async def verify(self, certificate_number: str | None, certifier: str | None) -> RegistryResult:
        if certifier and "etko" in certifier.lower():
            return RegistryResult("ETKO", "valid", {
                "certifier": "ETKO",
                "standard": "EU organic regulation",
                "accreditation": "TÜRKAK",
            })
        return RegistryResult("ETKO", "not_found", {"reason": "Not certified by ETKO"})


# Provider registry
PROVIDERS = [
    MockOTBISProvider(),
    MockECOCERTProvider(),
    MockETKOProvider(),
]


async def run_all_checks(certificate_number: str | None, certifier: str | None) -> list[RegistryResult]:
    """Run verification against all configured providers."""
    results = []
    for provider in PROVIDERS:
        results.append(await provider.verify(certificate_number, certifier))
    return results
