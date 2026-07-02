from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_schema_validation():
    # Invalid schema should return 422
    response = client.post("/chat", json={"invalid": "payload"})
    assert response.status_code == 422

def test_chat_clarification():
    payload = {
        "messages": [
            {"role": "user", "content": "I need an assessment"}
        ]
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert "end_of_conversation" in data
