from fastapi.testclient import TestClient

from api.dependencies import get_repository
from api.main import app


def client_for(repo):
    app.dependency_overrides[get_repository] = lambda: repo
    return TestClient(app)


def test_health_endpoint(repo):
    with client_for(repo) as client:
        response = client.get("/health")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_recommendation_endpoint_persists_components(repo, user):
    with client_for(repo) as client:
        response = client.post("/recommendations", json={"user_id": user.user_id})
    app.dependency_overrides.clear()
    assert response.status_code == 201
    body = response.json()
    assert 0 <= body["personalization_priority"] <= 1
    assert 0 <= body["completion_probability"] <= 1
    assert 0 <= body["final_score"] <= 1


def test_unknown_user_returns_404(repo):
    with client_for(repo) as client:
        response = client.get("/users/99999")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_checkin_session_and_score_endpoints(repo, user):
    client = client_for(repo)
    checkin = client.post("/checkins", json={"user_id": user.user_id, "energy_level": 3,
        "mood": 4, "sleep_quality": 3, "available_training_time": 15,
        "perceived_readiness": 4})
    session = client.post("/sessions", json={"user_id": user.user_id})
    exercise = {"exercise_type": "target_count", "category": "Attention",
        "difficulty": "easy", "instruction": "Count the target number in the sequence.",
        "content": {"sequence": [1, 2, 2]}, "expected_answer": "2",
        "hint": "Count from left to right.", "estimated_seconds": 30,
        "scoring_type": "exact_match"}
    scored = client.post("/score", json={"exercise": exercise, "response": "2",
        "user_id": user.user_id, "session_id": session.json()["session_id"]})
    app.dependency_overrides.clear()
    assert checkin.status_code == 201
    assert session.status_code == 201
    assert scored.status_code == 200
    assert scored.json()["normalized_score"] == 100
