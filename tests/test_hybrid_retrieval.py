from app.retrieval.hybrid_search import retrieve_support_chunks_hybrid


def test_hybrid_retrieve_cashout_variant() -> None:
    results = retrieve_support_chunks_hybrid(
        "My withdrawal failed and my money was deducted",
        top_k=3,
    )
    assert len(results) >= 1
    assert results[0].source == "cashout_failures.md"


def test_hybrid_retrieve_wrong_recipient_variant() -> None:
    results = retrieve_support_chunks_hybrid(
        "I transferred funds to the wrong person",
        top_k=3,
    )
    assert len(results) >= 1
    assert results[0].source == "wrong_recipient.md"


def test_hybrid_retrieve_locked_account_variant() -> None:
    results = retrieve_support_chunks_hybrid(
        "I cannot access my profile because it is blocked",
        top_k=3,
    )
    assert len(results) >= 1
    assert results[0].source == "account_locked.md"