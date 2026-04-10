from app.agent.generation import build_grounded_answer
from app.core.schemas import RetrievedChunk


def test_build_grounded_answer_cashout() -> None:
    chunks = [
        RetrievedChunk(
            source="cashout_failures.md",
            chunk_id="cashout_failures_001",
            text=(
                "If a cash-out fails after the customer balance appears to be deducted, "
                "the system should advise the customer to wait for the reconciliation or "
                "review window before retrying. The assistant should avoid instructing "
                "repeated retries immediately."
            ),
            score=0.90,
        )
    ]

    answer, confidence = build_grounded_answer(
        query="My cash-out failed and money was deducted",
        chunks=chunks,
    )

    assert "reconciliation" in answer.lower() or "review window" in answer.lower()
    assert confidence >= 0.60


def test_build_grounded_answer_wrong_recipient() -> None:
    chunks = [
        RetrievedChunk(
            source="wrong_recipient.md",
            chunk_id="wrong_recipient_001",
            text=(
                "If a customer reports sending funds to the wrong recipient, the assistant "
                "should not guarantee reversal. These cases may require manual investigation "
                "and policy-based review."
            ),
            score=0.88,
        )
    ]

    answer, confidence = build_grounded_answer(
        query="I transferred funds to the wrong person",
        chunks=chunks,
    )

    assert "guarantee reversal" in answer.lower() or "manual investigation" in answer.lower()
    assert confidence >= 0.60