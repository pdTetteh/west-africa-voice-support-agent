from app.core.schemas import RetrievedChunk


CUSTOMER_ANSWERS = {
    "cashout_failures.md": (
        "I’m sorry about that. If your balance was deducted after a failed cash-out, "
        "please do not try the same transaction again immediately. The transaction may be "
        "under reconciliation review. Please wait for the review period, and contact support "
        "if the issue does not resolve after that."
    ),
    "wrong_recipient.md": (
        "I’m sorry that happened. I cannot guarantee reversal from here, but this should be "
        "reviewed by a support agent as soon as possible. Please contact support and provide "
        "the transaction details so the case can be checked manually."
    ),
    "account_locked.md": (
        "I’m sorry you’re unable to access your account. Your account may need secure "
        "verification before it can be unlocked. Please follow the official recovery steps, "
        "and contact support if you still cannot sign in."
    ),
    "kyc_help.md": (
        "This looks related to identity verification. Please follow the verification steps in "
        "the app and make sure your details are correct. If your documents need to be reviewed "
        "or your verification remains pending, please contact support for help."
    ),
    "faq.md": (
        "I do not have enough information to answer this safely. Please share more details or "
        "contact support so a human agent can help you."
    ),
    "escalation_policy.md": (
        "This issue may need help from a human support agent. Please contact support with the "
        "details of what happened so the team can review it safely."
    ),
}


def _select_primary_source(chunks: list[RetrievedChunk]) -> str | None:
    scored_chunks = [chunk for chunk in chunks if chunk.score > 0]
    if not scored_chunks:
        return None
    return scored_chunks[0].source


def _estimate_confidence(chunks: list[RetrievedChunk]) -> float:
    scored_chunks = [chunk for chunk in chunks if chunk.score > 0]

    if not scored_chunks:
        return 0.30

    top_score = max(scored_chunks[0].score, 0.0)
    second_score = max(scored_chunks[1].score, 0.0) if len(scored_chunks) > 1 else 0.0
    score_gap = max(top_score - second_score, 0.0)

    confidence = 0.56
    confidence += min(top_score, 1.0) * 0.14
    confidence += min(score_gap, 0.5) * 0.08

    if len(scored_chunks) >= 2:
        confidence += 0.03

    return round(min(confidence, 0.78), 3)


def build_grounded_answer(query: str, chunks: list[RetrievedChunk]) -> tuple[str, float]:
    """
    Build a customer-facing answer using retrieved evidence.

    The answer should not expose internal policy wording such as:
    - "the assistant should..."
    - "the system should..."
    - raw support policy headings
    """
    primary_source = _select_primary_source(chunks)
    confidence = _estimate_confidence(chunks)

    if primary_source is None:
        return (
            "I do not have enough information to answer this safely. Please contact support "
            "so a human agent can help you.",
            0.30,
        )

    answer = CUSTOMER_ANSWERS.get(
        primary_source,
        (
            "I found related support guidance, but this issue may need help from a human "
            "support agent. Please contact support with the details of what happened."
        ),
    )

    return answer, confidence