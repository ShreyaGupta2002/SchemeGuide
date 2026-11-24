from pydantic import BaseModel
from typing import Optional, List


class ProfileInput(BaseModel):
    state: Optional[str] = None
    annual_income: Optional[float] = None
    education_level: Optional[str] = None
    caste_category: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    parent_service: Optional[str] = None  # e.g. "CAPF" for PM Scholarship


class ConditionResult(BaseModel):
    rule_id: int
    field: str
    operator: str
    expected_value: str
    actual_value: Optional[str]
    result: str  # "pass", "fail", "unknown"
    explanation: str


class SchemeMatchResult(BaseModel):
    scheme_id: int
    scheme_name: str
    scheme_version_id: int
    outcome: str  # "appears_eligible", "appears_non_eligible", "more_information_needed"
    conditions: List[ConditionResult]


class MatchRequest(BaseModel):
    profile: ProfileInput
    scheme_ids: Optional[List[int]] = None  # if None, check all published schemes


class MatchResponse(BaseModel):
    results: List[SchemeMatchResult]
