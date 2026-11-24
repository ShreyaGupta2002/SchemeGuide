import os
import logging
import httpx
from fastapi import APIRouter, HTTPException
from .models import ExplainRequest, ExplainResponse
from .catalog_client import get_scheme_detail

router = APIRouter()
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def _build_prompt(request: ExplainRequest, description: str) -> str:
    outcome_phrase = {
        "appears_eligible": "appears to be ELIGIBLE",
        "appears_non_eligible": "appears to be NOT ELIGIBLE",
        "more_information_needed": "needs MORE INFORMATION to decide",
    }.get(request.outcome, request.outcome)

    lines = []
    for c in request.conditions:
        icon = {"pass": "✓", "fail": "✗", "unknown": "?"}.get(c.result, "?")
        lines.append(f"  {icon} {c.field}: {c.explanation} [{c.result}]")
    conditions_text = "\n".join(lines)

    return f"""You are a helpful assistant explaining Indian government scholarship eligibility results to a student in simple English.

Scheme: {request.scheme_name}
Description: {description}

Result: The student {outcome_phrase} for this scheme.

Conditions checked:
{conditions_text}

In 2–3 clear sentences, explain the result to the student.
- If eligible: confirm what they qualify on and what to do next.
- If not eligible: tell them which condition(s) they did not meet and what they would need to qualify.
- If more info needed: tell them which details they did not provide.
Write plainly. Do not repeat the scheme name more than once."""


@router.post("/assistant/explain", response_model=ExplainResponse)
async def explain_result(request: ExplainRequest):
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not set. Add it to your .env to enable AI explanations.",
        )

    try:
        scheme = await get_scheme_detail(request.scheme_id)
    except Exception as e:
        logger.error("Catalog service error: %s", e)
        raise HTTPException(status_code=502, detail=f"Could not reach Catalog service: {e}")

    versions = scheme.get("versions", [])
    description = versions[0].get("description", "") if versions else ""

    prompt = _build_prompt(request, description)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": GROQ_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.3,
                },
            )
            resp.raise_for_status()
            explanation = resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error("Groq API error (model=%s): %s", GROQ_MODEL, e)
        raise HTTPException(status_code=502, detail=f"Groq API error: {e}")

    return ExplainResponse(scheme_id=request.scheme_id, explanation=explanation)
