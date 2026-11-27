from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from main import app

# StaticPool forces all connections to share one underlying connection,
# so the in-memory database persists across the entire test session.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

PAYLOAD = {
    "scheme_version_id": 1,
    "scheme_name": "Test Scheme",
    "problem_description": "The income limit appears to be wrong",
    "correct_information": "Should be 3 lakh per the latest notification",
    "official_source_url": "https://example.gov.in/notification",
}


class TestFeedbackEndpoints:
    def setup_method(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_submit_feedback_returns_201(self):
        resp = client.post("/api/v1/feedback", json=PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["scheme_name"] == "Test Scheme"
        assert data["status"] == "open"
        assert "id" in data
        assert "created_at" in data

    def test_submit_feedback_optional_fields_can_be_omitted(self):
        resp = client.post("/api/v1/feedback", json={
            "scheme_version_id": 1,
            "scheme_name": "Minimal Scheme",
            "problem_description": "Something is wrong",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["correct_information"] is None
        assert data["official_source_url"] is None

    def test_list_feedback_returns_all_submissions(self):
        client.post("/api/v1/feedback", json=PAYLOAD)
        client.post("/api/v1/feedback", json={**PAYLOAD, "scheme_name": "Another Scheme"})
        resp = client.get("/api/v1/feedback")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_feedback_filter_by_open_status(self):
        resp1 = client.post("/api/v1/feedback", json=PAYLOAD).json()
        client.post("/api/v1/feedback", json=PAYLOAD)
        client.patch(f"/api/v1/feedback/{resp1['id']}/resolve")
        resp = client.get("/api/v1/feedback?status=open")
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 1
        assert results[0]["status"] == "open"

    def test_get_single_feedback(self):
        created = client.post("/api/v1/feedback", json=PAYLOAD).json()
        resp = client.get(f"/api/v1/feedback/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]
        assert resp.json()["problem_description"] == PAYLOAD["problem_description"]

    def test_get_feedback_404_for_missing_id(self):
        resp = client.get("/api/v1/feedback/999")
        assert resp.status_code == 404

    def test_resolve_feedback_sets_status_to_resolved(self):
        created = client.post("/api/v1/feedback", json=PAYLOAD).json()
        resp = client.patch(f"/api/v1/feedback/{created['id']}/resolve")
        assert resp.status_code == 200
        assert resp.json()["status"] == "resolved"

    def test_resolve_feedback_404_for_missing_id(self):
        resp = client.patch("/api/v1/feedback/999/resolve")
        assert resp.status_code == 404

