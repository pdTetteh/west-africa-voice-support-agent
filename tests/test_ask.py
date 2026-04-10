from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ask_returns_structured_response() -> None:
    response = client.post(
        "/ask",
        json={"query": "My cash out failed but my balance was deducted"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "answer" in payload
    assert "evidence" in payload
    assert "confidence" in payload
    assert isinstance(payload["evidence"], list)
    assert payload["evidence"][0]["source"] == "cashout_failures.md"
    assert "support guidance" in payload["answer"].lower()


def test_ask_wrong_person_includes_specific_evidence() -> None:
    response = client.post(
        "/ask",
        json={"query": "I sent money to the wrong person"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["escalate"] is True
    assert payload["evidence"][0]["source"] == "wrong_recipient.md"
    assert "primary evidence" in payload["reason"].lower()


def test_ask_locked_account_returns_grounded_answer() -> None:
    response = client.post(
        "/ask",
        json={"query": "I cannot sign in because my account is locked"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["evidence"][0]["source"] == "account_locked.md"
    assert "support guidance" in payload["answer"].lower()