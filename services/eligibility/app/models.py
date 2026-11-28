
from pydantic import BaseModel


class ProfileInput(BaseModel):
    state: str | None = None
    annual_income: float | None = None
    education_level: str | None = None
    caste_category: str | None = None
    gender: str | None = None
    age: int | None = None
    parent_service: str | None = None  # e.g. "CAPF" for PM Scholarship


class ConditionResult(BaseModel):
    rule_id: int
    field: str
    operator: str
    expected_value: str
    actual_value: str | None
    result: str  # "pass", "fail", "unknown"
    explanation: str


class SchemeMatchResult(BaseModel):
    scheme_id: int
    scheme_name: str
    scheme_version_id: int
    outcome: str  # "appears_eligible", "appears_non_eligible", "more_information_needed"
    conditions: list[ConditionResult]


class MatchRequest(BaseModel):
    profile: ProfileInput
    scheme_ids: list[int] | None = None  # if None, check all published schemes


class MatchResponse(BaseModel):
    results: list[SchemeMatchResult]
