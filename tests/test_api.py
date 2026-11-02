from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_incidents_returns_between_one_and_five():
    response = client.get("/api/incidents")
    assert response.status_code == 200
    body = response.json()
    assert 1 <= body["count"] <= 5
    assert len(body["incidents"]) == body["count"]


def test_requested_count_and_incident_fields():
    body = client.get("/api/incidents?count=4&seed=42").json()
    assert body["count"] == 4
    assert len(body["incidents"]) == 4
    incident = body["incidents"][0]
    assert {"id", "rule_name", "severity", "status", "source", "destination", "mitre_technique"} <= incident.keys()


def test_count_out_of_range_is_rejected():
    assert client.get("/api/incidents?count=6").status_code == 422
