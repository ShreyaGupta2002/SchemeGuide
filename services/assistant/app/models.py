
from pydantic import BaseModel


class ConditionSummary(BaseModel):
    field: str
    result: str         # pass | fail | unknown
    explanation: str


class ExplainRequest(BaseModel):
    scheme_id: int
    scheme_name: str
    outcome: str        # appears_eligible | appears_non_eligible | more_information_needed
    conditions: list[ConditionSummary]
    profile: dict


class ExplainResponse(BaseModel):
    scheme_id: int
    explanation: str
