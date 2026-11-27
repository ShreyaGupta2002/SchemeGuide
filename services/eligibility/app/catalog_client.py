import os
from typing import Any

import httpx

CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8001")


async def get_all_published_schemes() -> list[dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/api/v1/schemes/")
        response.raise_for_status()
        return response.json()


async def get_scheme_with_rules(scheme_id: int) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/api/v1/schemes/{scheme_id}/")
        response.raise_for_status()
        return response.json()
