from django.test import TestCase

from schemes.models import Scheme, SchemeVersion


def make_scheme(name="Test Scheme", department="Test Dept", status="published"):
    scheme = Scheme.objects.create(name=name, department=department, jurisdiction="central")
    SchemeVersion.objects.create(
        scheme=scheme,
        version_number=1,
        description="A test scheme for unit testing.",
        benefit_amount="10000",
        applicable_year="2024-25",
        official_url="https://example.gov.in",
        status=status,
    )
    return scheme


class SchemeListViewTest(TestCase):
    def test_returns_only_published_schemes(self):
        make_scheme(name="Published Scheme", status="published")
        make_scheme(name="Draft Scheme", status="draft")
        response = self.client.get("/api/v1/schemes/")
        self.assertEqual(response.status_code, 200)
        names = [s["name"] for s in response.json()]
        self.assertIn("Published Scheme", names)
        self.assertNotIn("Draft Scheme", names)

    def test_response_includes_latest_version(self):
        make_scheme(name="With Version")
        response = self.client.get("/api/v1/schemes/")
        self.assertEqual(response.status_code, 200)
        scheme = response.json()[0]
        self.assertIsNotNone(scheme["latest_version"])
        self.assertIn("benefit_amount", scheme["latest_version"])
        self.assertIn("official_url", scheme["latest_version"])

    def test_empty_list_when_no_published_schemes(self):
        make_scheme(name="Draft Only", status="draft")
        response = self.client.get("/api/v1/schemes/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_reviewed_scheme_not_returned(self):
        make_scheme(name="Reviewed Scheme", status="reviewed")
        response = self.client.get("/api/v1/schemes/")
        self.assertEqual(response.status_code, 200)
        names = [s["name"] for s in response.json()]
        self.assertNotIn("Reviewed Scheme", names)


class SchemeDetailViewTest(TestCase):
    def setUp(self):
        self.scheme = make_scheme(name="Detail Scheme")

    def test_returns_scheme_detail(self):
        response = self.client.get(f"/api/v1/schemes/{self.scheme.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Detail Scheme")
        self.assertIn("versions", data)

    def test_detail_includes_published_version_only(self):
        SchemeVersion.objects.create(
            scheme=self.scheme,
            version_number=2,
            description="Draft version.",
            benefit_amount="20000",
            applicable_year="2025-26",
            official_url="https://example.gov.in",
            status="draft",
        )
        response = self.client.get(f"/api/v1/schemes/{self.scheme.id}/")
        self.assertEqual(response.status_code, 200)
        versions = response.json()["versions"]
        statuses = [v["status"] for v in versions]
        self.assertNotIn("draft", statuses)

    def test_returns_404_for_missing_scheme(self):
        response = self.client.get("/api/v1/schemes/999/")
        self.assertEqual(response.status_code, 404)
