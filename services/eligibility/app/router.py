from fastapi import APIRouter, HTTPException

from .catalog_client import get_all_published_schemes, get_scheme_with_rules
from .engine import evaluate_scheme
from .models import MatchRequest, MatchResponse

router = APIRouter()


@router.post("/matches", response_model=MatchResponse)
async def match_schemes(request: MatchRequest):
    try:
        if request.scheme_ids:
            schemes = []
            for sid in request.scheme_ids:
                scheme = await get_scheme_with_rules(sid)
                schemes.append(scheme)
        else:
            schemes = await get_all_published_schemes()
            full_schemes = []
            for s in schemes:
                full_schemes.append(await get_scheme_with_rules(s["id"]))
            schemes = full_schemes

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not reach Catalog service: {e!s}")

    results = []
    for scheme in schemes:
        versions = scheme.get("versions", [])
        if not versions:
            continue

        latest_version = versions[0]
        rules = latest_version.get("eligibility_rules", [])

        result = evaluate_scheme(
            scheme_id=scheme["id"],
            scheme_name=scheme["name"],
            scheme_version_id=latest_version["id"],
            rules=rules,
            profile=request.profile,
        )
        results.append(result)

    return MatchResponse(results=results)
