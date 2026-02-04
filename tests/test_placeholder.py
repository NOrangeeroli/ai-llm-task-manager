from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_create_and_get_task() -> None:
    payload = {"title": "test task", "description": "desc", "priority": "medium", "status": "pending", "tags": []}
    r = client.post("/api/tasks", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "test task"

    task_id = data["id"]
    r2 = client.get(f"/api/tasks/{task_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == task_id


def test_list_tasks() -> None:
    r = client.get("/api/tasks")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_not_found() -> None:
    r = client.get("/api/tasks/999999")
    assert r.status_code == 404


def test_natural_language_creation() -> None:
    r = client.post("/api/tasks/natural-language", json={"text": "Buy milk tomorrow."})
    assert r.status_code == 201
    data = r.json()
    assert "Buy milk" in data["title"]


def test_tag_suggestion_and_summary() -> None:
    # Create a task first
    create_resp = client.post(
        "/api/tasks",
        json={"title": "AI task", "description": "Use embeddings", "priority": "medium", "status": "pending", "tags": ["ai"]},
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    # Tag suggestion
    suggest_resp = client.post(
        f"/api/tasks/{task_id}/tags/suggestions",
        json={"title": "AI task", "description": "Use embeddings"},
    )
    assert suggest_resp.status_code == 200
    assert "suggestion" in suggest_resp.json()

    # Summary
    summary_resp = client.post("/api/tasks/summary", json={"task_ids": [task_id]})
    assert summary_resp.status_code == 200
    body = summary_resp.json()
    assert "summary" in body and body["count"] >= 1


def test_semantic_search() -> None:
    r = client.post("/api/tasks/search", json={"query": "ai", "limit": 5})
    assert r.status_code == 200
    assert "results" in r.json()
