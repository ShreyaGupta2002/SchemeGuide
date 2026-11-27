import os
from typing import Any

import httpx

CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://catalog:8001")


async def get_scheme_detail(scheme_id: int) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/api/v1/schemes/{scheme_id}/")
        response.raise_for_status()
        return response.json()
