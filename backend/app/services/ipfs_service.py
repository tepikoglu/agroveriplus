"""IPFS pinning service — uses Pinata API.

Currently a placeholder. To activate:
1. Sign up at https://pinata.cloud
2. Set IPFS_API_KEY and IPFS_API_SECRET in .env
3. Uncomment the real implementation below
"""

import httpx

from app.config import settings


async def pin_to_ipfs(file_bytes: bytes, filename: str) -> str | None:
    """Pin a file to IPFS via Pinata. Returns CID or None if not configured."""
    if not settings.ipfs_api_key:
        return None

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ipfs_api_url}/pinning/pinFileToIPFS",
            headers={
                "pinata_api_key": settings.ipfs_api_key,
                "pinata_secret_api_key": settings.ipfs_api_secret,
            },
            files={"file": (filename, file_bytes)},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["IpfsHash"]
