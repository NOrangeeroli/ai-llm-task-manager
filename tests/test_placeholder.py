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
