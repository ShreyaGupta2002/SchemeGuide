import pytest
from app.engine import evaluate_rule, evaluate_scheme
from app.models import ProfileInput


def rule(field, operator, value, rule_id=1):
    return {"id": rule_id, "field": field, "operator": operator, "value": value, "explanation": "test rule"}


# ---------------------------------------------------------------------------
# equals
# ---------------------------------------------------------------------------

def test_equals_pass():
    result = evaluate_rule(rule("caste_category", "equals", "SC"), ProfileInput(caste_category="SC"))
    assert result.result == "pass"


def test_equals_fail():
    result = evaluate_rule(rule("caste_category", "equals", "SC"), ProfileInput(caste_category="OBC"))
    assert result.result == "fail"


def test_equals_case_insensitive():
    result = evaluate_rule(rule("caste_category", "equals", "SC"), ProfileInput(caste_category="sc"))
    assert result.result == "pass"


def test_equals_unknown_when_field_missing():
    result = evaluate_rule(rule("caste_category", "equals", "SC"), ProfileInput())
    assert result.result == "unknown"


# ---------------------------------------------------------------------------
# not_equals
# ---------------------------------------------------------------------------

def test_not_equals_pass():
    result = evaluate_rule(rule("gender", "not_equals", "male"), ProfileInput(gender="female"))
    assert result.result == "pass"


def test_not_equals_fail():
    result = evaluate_rule(rule("gender", "not_equals", "male"), ProfileInput(gender="male"))
    assert result.result == "fail"


def test_not_equals_unknown_when_field_missing():
    result = evaluate_rule(rule("gender", "not_equals", "male"), ProfileInput())
    assert result.result == "unknown"


# ---------------------------------------------------------------------------
# in
# ---------------------------------------------------------------------------

def test_in_pass():
    result = evaluate_rule(
        rule("education_level", "in", "graduation,postgraduation,diploma"),
        ProfileInput(education_level="graduation"),
    )
    assert result.result == "pass"


def test_in_pass_trims_spaces():
    result = evaluate_rule(
        rule("education_level", "in", "graduation, postgraduation, diploma"),
        ProfileInput(education_level="postgraduation"),
    )
    assert result.result == "pass"


def test_in_fail():
    result = evaluate_rule(
        rule("education_level", "in", "graduation,postgraduation,diploma"),
        ProfileInput(education_level="secondary"),
    )
    assert result.result == "fail"


def test_in_unknown_when_field_missing():
    result = evaluate_rule(rule("education_level", "in", "graduation,diploma"), ProfileInput())
    assert result.result == "unknown"


# ---------------------------------------------------------------------------
# not_in
# ---------------------------------------------------------------------------

def test_not_in_pass():
    result = evaluate_rule(rule("state", "not_in", "MH,GJ,RJ"), ProfileInput(state="KA"))
    assert result.result == "pass"


def test_not_in_fail():
    result = evaluate_rule(rule("state", "not_in", "MH,GJ,RJ"), ProfileInput(state="MH"))
    assert result.result == "fail"


def test_not_in_unknown_when_field_missing():
    result = evaluate_rule(rule("state", "not_in", "MH,GJ"), ProfileInput())
    assert result.result == "unknown"


# ---------------------------------------------------------------------------
# gte
# ---------------------------------------------------------------------------

def test_gte_pass():
    result = evaluate_rule(rule("age", "gte", "18"), ProfileInput(age=20))
    assert result.result == "pass"


def test_gte_equal_is_pass():
    result = evaluate_rule(rule("age", "gte", "18"), ProfileInput(age=18))
    assert result.result == "pass"


def test_gte_fail():
    result = evaluate_rule(rule("age", "gte", "18"), ProfileInput(age=16))
    assert result.result == "fail"


def test_gte_unknown_when_field_missing():
    result = evaluate_rule(rule("age", "gte", "18"), ProfileInput())
    assert result.result == "unknown"


# ---------------------------------------------------------------------------
# lte
# ---------------------------------------------------------------------------

def test_lte_pass():
    result = evaluate_rule(rule("annual_income", "lte", "250000"), ProfileInput(annual_income=200000))
    assert result.result == "pass"


def test_lte_equal_is_pass():
    result = evaluate_rule(rule("annual_income", "lte", "250000"), ProfileInput(annual_income=250000))
    assert result.result == "pass"


def test_lte_fail():
    result = evaluate_rule(rule("annual_income", "lte", "250000"), ProfileInput(annual_income=300000))
    assert result.result == "fail"


def test_lte_unknown_when_field_missing():
    result = evaluate_rule(rule("annual_income", "lte", "250000"), ProfileInput())
    assert result.result == "unknown"


# ---------------------------------------------------------------------------
# gt
# ---------------------------------------------------------------------------

def test_gt_pass():
    result = evaluate_rule(rule("age", "gt", "18"), ProfileInput(age=19))
    assert result.result == "pass"


def test_gt_fail_when_equal():
    result = evaluate_rule(rule("age", "gt", "18"), ProfileInput(age=18))
    assert result.result == "fail"


def test_gt_fail():
    result = evaluate_rule(rule("age", "gt", "18"), ProfileInput(age=17))
    assert result.result == "fail"


def test_gt_unknown_when_field_missing():
    result = evaluate_rule(rule("age", "gt", "18"), ProfileInput())
    assert result.result == "unknown"


# ---------------------------------------------------------------------------
# lt
# ---------------------------------------------------------------------------

def test_lt_pass():
    result = evaluate_rule(rule("age", "lt", "25"), ProfileInput(age=24))
    assert result.result == "pass"


def test_lt_fail_when_equal():
    result = evaluate_rule(rule("age", "lt", "25"), ProfileInput(age=25))
    assert result.result == "fail"


def test_lt_fail():
    result = evaluate_rule(rule("age", "lt", "25"), ProfileInput(age=26))
    assert result.result == "fail"


def test_lt_unknown_when_field_missing():
    result = evaluate_rule(rule("age", "lt", "25"), ProfileInput())
    assert result.result == "unknown"


# ---------------------------------------------------------------------------
# outcome logic in evaluate_scheme
# ---------------------------------------------------------------------------

def test_outcome_eligible_all_pass():
    rules = [
        rule("caste_category", "equals", "SC", rule_id=1),
        rule("annual_income", "lte", "250000", rule_id=2),
    ]
    profile = ProfileInput(caste_category="SC", annual_income=200000)
    result = evaluate_scheme(1, "Test Scheme", 1, rules, profile)
    assert result.outcome == "appears_eligible"
    assert all(c.result == "pass" for c in result.conditions)


def test_outcome_non_eligible_any_fail():
    rules = [
        rule("caste_category", "equals", "SC", rule_id=1),
        rule("annual_income", "lte", "250000", rule_id=2),
    ]
    profile = ProfileInput(caste_category="SC", annual_income=300000)
    result = evaluate_scheme(1, "Test Scheme", 1, rules, profile)
    assert result.outcome == "appears_non_eligible"


def test_outcome_more_info_needed_when_unknown_no_fail():
    rules = [
        rule("caste_category", "equals", "SC", rule_id=1),
        rule("annual_income", "lte", "250000", rule_id=2),
    ]
    # income not provided → unknown; caste passes
    profile = ProfileInput(caste_category="SC")
    result = evaluate_scheme(1, "Test Scheme", 1, rules, profile)
    assert result.outcome == "more_information_needed"


def test_outcome_fail_takes_precedence_over_unknown():
    rules = [
        rule("caste_category", "equals", "SC", rule_id=1),
        rule("annual_income", "lte", "250000", rule_id=2),
    ]
    # caste fails, income unknown — fail wins
    profile = ProfileInput(caste_category="OBC")
    result = evaluate_scheme(1, "Test Scheme", 1, rules, profile)
    assert result.outcome == "appears_non_eligible"


def test_outcome_no_rules_is_more_info_needed():
    result = evaluate_scheme(1, "Test Scheme", 1, [], ProfileInput())
    assert result.outcome == "more_information_needed"
    assert result.conditions == []
