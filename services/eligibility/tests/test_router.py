from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# A minimal scheme with two rules: caste_category equals SC, annual_income lte 250000
SCHEME = {
    "id": 1,
    "name": "SC Scholarship",
    "versions": [
        {
            "id": 1,
            "eligibility_rules": [
                {
                    "id": 1,
                    "field": "caste_category",
                    "operator": "equals",
                    "value": "SC",
                    "explanation": "Applicant must belong to SC category",
                },
                {
                    "id": 2,
                    "field": "annual_income",
                    "operator": "lte",
                    "value": "250000",
                    "explanation": "Family income must not exceed 2.5 lakh per year",
                },
            ],
        }
    ],
}


def mock_catalog(scheme=SCHEME):
    """Return (schemes_list_mock, scheme_detail_mock) patched to return SCHEME."""
    return (
        AsyncMock(return_value=[{"id": scheme["id"], "name": scheme["name"]}]),
        AsyncMock(return_value=scheme),
    )


class TestMatchesEndpoint:
    def test_eligible_profile_returns_appears_eligible(self):
        list_mock, detail_mock = mock_catalog()
        with patch("app.router.get_all_published_schemes", list_mock), \
             patch("app.router.get_scheme_with_rules", detail_mock):
            resp = client.post(
                "/api/v1/matches",
                json={"profile": {"caste_category": "SC", "annual_income": 200000}},
            )
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["outcome"] == "appears_eligible"

    def test_non_eligible_profile_returns_appears_non_eligible(self):
        list_mock, detail_mock = mock_catalog()
        with patch("app.router.get_all_published_schemes", list_mock), \
             patch("app.router.get_scheme_with_rules", detail_mock):
            resp = client.post(
                "/api/v1/matches",
                json={"profile": {"caste_category": "OBC", "annual_income": 200000}},
            )
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["outcome"] == "appears_non_eligible"

    def test_partial_profile_returns_more_information_needed(self):
        list_mock, detail_mock = mock_catalog()
        with patch("app.router.get_all_published_schemes", list_mock), \
             patch("app.router.get_scheme_with_rules", detail_mock):
            # caste passes, income not provided → unknown → more_information_needed
            resp = client.post(
                "/api/v1/matches",
                json={"profile": {"caste_category": "SC"}},
            )
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["outcome"] == "more_information_needed"

    def test_fail_beats_unknown(self):
        list_mock, detail_mock = mock_catalog()
        with patch("app.router.get_all_published_schemes", list_mock), \
             patch("app.router.get_scheme_with_rules", detail_mock):
            # caste fails, income not provided — fail must win over unknown
            resp = client.post(
                "/api/v1/matches",
                json={"profile": {"caste_category": "OBC"}},
            )
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["outcome"] == "appears_non_eligible"

    def test_conditions_included_in_response(self):
        list_mock, detail_mock = mock_catalog()
        with patch("app.router.get_all_published_schemes", list_mock), \
             patch("app.router.get_scheme_with_rules", detail_mock):
            resp = client.post(
                "/api/v1/matches",
                json={"profile": {"caste_category": "SC", "annual_income": 200000}},
            )
        result = resp.json()["results"][0]
        assert len(result["conditions"]) == 2
        assert all(c["result"] == "pass" for c in result["conditions"])

    def test_catalog_down_returns_502(self):
        error_mock = AsyncMock(side_effect=Exception("connection refused"))
        with patch("app.router.get_all_published_schemes", error_mock):
            resp = client.post("/api/v1/matches", json={"profile": {}})
        assert resp.status_code == 502

    def test_empty_profile_with_no_rules_returns_more_information_needed(self):
        no_rules_scheme = {**SCHEME, "versions": [{"id": 1, "eligibility_rules": []}]}
        list_mock, detail_mock = mock_catalog(no_rules_scheme)
        with patch("app.router.get_all_published_schemes", list_mock), \
             patch("app.router.get_scheme_with_rules", detail_mock):
            resp = client.post("/api/v1/matches", json={"profile": {}})
        assert resp.status_code == 200
        assert resp.json()["results"][0]["outcome"] == "more_information_needed"
