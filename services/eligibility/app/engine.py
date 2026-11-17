from typing import Dict, Any, List
from .models import ConditionResult, SchemeMatchResult, ProfileInput


def get_profile_value(profile: ProfileInput, field: str):
    return getattr(profile, field, None)


def evaluate_rule(rule: Dict[str, Any], profile: ProfileInput) -> ConditionResult:
    field = rule["field"]
    operator = rule["operator"]
    expected_raw = rule["value"]
    explanation = rule["explanation"]
    actual = get_profile_value(profile, field)

    if actual is None:
        return ConditionResult(
            rule_id=rule["id"],
            field=field,
            operator=operator,
            expected_value=expected_raw,
            actual_value=None,
            result="unknown",
            explanation=explanation,
        )

    actual_str = str(actual)

    try:
        if operator == "equals":
            passed = str(actual).lower() == expected_raw.lower()

        elif operator == "not_equals":
            passed = str(actual).lower() != expected_raw.lower()

        elif operator == "in":
            allowed = [v.strip().lower() for v in expected_raw.split(",")]
            passed = str(actual).lower() in allowed

        elif operator == "not_in":
            excluded = [v.strip().lower() for v in expected_raw.split(",")]
            passed = str(actual).lower() not in excluded

        elif operator == "gte":
            passed = float(actual) >= float(expected_raw)

        elif operator == "lte":
            passed = float(actual) <= float(expected_raw)

        elif operator == "gt":
            passed = float(actual) > float(expected_raw)

        elif operator == "lt":
            passed = float(actual) < float(expected_raw)

        else:
            return ConditionResult(
                rule_id=rule["id"],
                field=field,
                operator=operator,
                expected_value=expected_raw,
                actual_value=actual_str,
                result="unknown",
                explanation=explanation,
            )

    except (ValueError, TypeError):
        return ConditionResult(
            rule_id=rule["id"],
            field=field,
            operator=operator,
            expected_value=expected_raw,
            actual_value=actual_str,
            result="unknown",
            explanation=explanation,
        )

    return ConditionResult(
        rule_id=rule["id"],
        field=field,
        operator=operator,
        expected_value=expected_raw,
        actual_value=actual_str,
        result="pass" if passed else "fail",
        explanation=explanation,
    )


def evaluate_scheme(
    scheme_id: int,
    scheme_name: str,
    scheme_version_id: int,
    rules: List[Dict[str, Any]],
    profile: ProfileInput,
) -> SchemeMatchResult:

    if not rules:
        return SchemeMatchResult(
            scheme_id=scheme_id,
            scheme_name=scheme_name,
            scheme_version_id=scheme_version_id,
            outcome="more_information_needed",
            conditions=[],
        )

    conditions = [evaluate_rule(rule, profile) for rule in rules]

    results = [c.result for c in conditions]

    if "fail" in results:
        outcome = "appears_ineligible"
    elif "unknown" in results:
        outcome = "more_information_needed"
    else:
        outcome = "appears_eligible"

    return SchemeMatchResult(
        scheme_id=scheme_id,
        scheme_name=scheme_name,
        scheme_version_id=scheme_version_id,
        outcome=outcome,
        conditions=conditions,
    )
