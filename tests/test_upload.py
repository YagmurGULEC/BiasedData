import pytest
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_sync_upload():
    response = client.post("/sync-upload",files={"file": ("test_data.csv", open("test_data.csv", "rb"))})
    assert response.status_code == 200
    assert response.json().get("message") == "File uploaded successfully"

def test_async_upload():
    response = client.post("/async-upload",files={"file": ("test_data.csv", open("test_data.csv", "rb"))})
    assert response.status_code == 200
    assert response.json().get("message") == "File uploaded successfully"
