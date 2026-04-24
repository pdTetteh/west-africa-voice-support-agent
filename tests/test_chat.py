from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_start_and_history() -> None:
    start_response = client.post("/chat/start", json={"user_label": "demo-user"})
    assert start_response.status_code == 200
    session_id = start_response.json()["session_id"]

    message_response = client.post(
        f"/chat/{session_id}/message",
        json={"query": "My cash out failed but my balance was deducted"},
    )
    assert message_response.status_code == 200
    payload = message_response.json()
    assert payload["session_id"] == session_id
    assert "answer" in payload

    history_response = client.get(f"/chat/{session_id}")
    assert history_response.status_code == 200
    history = history_response.json()
    assert history["session_id"] == session_id
    assert len(history["messages"]) >= 2


def test_escalated_message_creates_ticket() -> None:
    start_response = client.post("/chat/start", json={})
    session_id = start_response.json()["session_id"]

    message_response = client.post(
        f"/chat/{session_id}/message",
        json={"query": "I sent money to the wrong person"},
    )
    assert message_response.status_code == 200
    payload = message_response.json()
    assert payload["escalate"] is True
    assert payload["ticket_id"] is not None

    tickets_response = client.get("/tickets")
    assert tickets_response.status_code == 200
    tickets = tickets_response.json()
    assert any(ticket["session_id"] == session_id for ticket in tickets)