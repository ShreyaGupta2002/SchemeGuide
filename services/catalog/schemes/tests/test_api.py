from django.test import TestCase
from schemes.models import Scheme, SchemeVersion


def make_scheme(name="Test Scheme", status="published"):
    scheme = Scheme.objects.create(
        name=name,
        department="Test Department",
        jurisdiction="central",
    )
    SchemeVersion.objects.create(
        scheme=scheme,
        version_number=1,
        description="A test scheme for unit testing.",
        benefit_amount="Rs. 1000/month",
        applicable_year="2024-25",
        official_url="https://example.gov.in/scheme",
        status=status,
    )
    return scheme


class SchemeListAPITest(TestCase):

    def setUp(self):
        self.published = make_scheme("Published Scheme", "published")
        self.draft = make_scheme("Draft Scheme", "draft")
        self.reviewed = make_scheme("Reviewed Scheme", "reviewed")

    def test_list_returns_200(self):
        response = self.client.get("/api/v1/schemes/")
        self.assertEqual(response.status_code, 200)

    def test_list_returns_only_published(self):
        response = self.client.get("/api/v1/schemes/")
        names = [s["name"] for s in response.json()]
        self.assertIn("Published Scheme", names)
        self.assertNotIn("Draft Scheme", names)
        self.assertNotIn("Reviewed Scheme", names)

    def test_list_includes_latest_version(self):
        response = self.client.get("/api/v1/schemes/")
        scheme = next(s for s in response.json() if s["name"] == "Published Scheme")
        self.assertIsNotNone(scheme["latest_version"])
        self.assertEqual(scheme["latest_version"]["applicable_year"], "2024-25")

    def test_list_excludes_latest_version_when_no_published_version(self):
        response = self.client.get("/api/v1/schemes/")
        for scheme in response.json():
            self.assertNotEqual(scheme["name"], "Draft Scheme")


class SchemeDetailAPITest(TestCase):

    def setUp(self):
        self.scheme = make_scheme("Detail Scheme", "published")

    def test_detail_returns_200(self):
        response = self.client.get(f"/api/v1/schemes/{self.scheme.id}/")
        self.assertEqual(response.status_code, 200)

    def test_detail_returns_correct_scheme(self):
        response = self.client.get(f"/api/v1/schemes/{self.scheme.id}/")
        self.assertEqual(response.json()["name"], "Detail Scheme")

    def test_detail_includes_versions(self):
        response = self.client.get(f"/api/v1/schemes/{self.scheme.id}/")
        self.assertIn("versions", response.json())
        self.assertEqual(len(response.json()["versions"]), 1)

    def test_detail_404_for_nonexistent(self):
        response = self.client.get("/api/v1/schemes/99999/")
        self.assertEqual(response.status_code, 404)

    def test_detail_draft_scheme_has_no_published_versions(self):
        draft_scheme = make_scheme("Hidden Draft", "draft")
        response = self.client.get(f"/api/v1/schemes/{draft_scheme.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["versions"], [])
