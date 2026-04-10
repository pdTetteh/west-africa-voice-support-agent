from app.retrieval.chunking import chunk_text
from app.retrieval.search import retrieve_support_chunks


def test_chunk_text_returns_chunks() -> None:
    text = "A" * 1000
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1


def test_retrieve_support_chunks_cashout_variant() -> None:
    results = retrieve_support_chunks("My cash-out failed and money was deducted", top_k=3)
    assert len(results) >= 1
    assert results[0].source == "cashout_failures.md"


def test_retrieve_support_chunks_wrong_person() -> None:
    results = retrieve_support_chunks("I sent money to the wrong person", top_k=3)
    assert len(results) >= 1
    assert results[0].source == "wrong_recipient.md"


def test_retrieve_support_chunks_login_locked() -> None:
    results = retrieve_support_chunks("I cannot log in because my account is locked", top_k=3)
    assert len(results) >= 1
    assert results[0].source == "account_locked.md"


def test_retrieve_support_chunks_locked_account_prefers_specific_doc() -> None:
    results = retrieve_support_chunks("I cannot sign in because my account is locked", top_k=5)
    assert len(results) >= 2
    assert results[0].source == "account_locked.md"
    assert any(item.source == "escalation_policy.md" for item in results)
    