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
    assert "i’m sorry" in payload["answer"].lower() or "i'm sorry" in payload["answer"].lower()
    assert "assistant should" not in payload["answer"].lower()
    assert "system should" not in payload["answer"].lower()


def test_ask_wrong_person_includes_specific_evidence() -> None:
    response = client.post(
        "/ask",
        json={"query": "I sent money to the wrong person"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["escalate"] is True
    assert payload["evidence"][0]["source"] == "wrong_recipient.md"
    assert "cannot guarantee reversal" in payload["answer"].lower()
    assert "primary evidence" in payload["reason"].lower()


def test_ask_locked_account_returns_customer_friendly_answer() -> None:
    response = client.post(
        "/ask",
        json={"query": "I cannot sign in because my account is locked"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["evidence"][0]["source"] == "account_locked.md"
    assert "unable to access your account" in payload["answer"].lower()
    assert "assistant should" not in payload["answer"].lower()