from app.core.config import settings


RISKY_KEYWORDS = {
    "wrong recipient",
    "wrong person",
    "sent money to the wrong",
    "wrong_recipient",
    "account locked",
    "cannot log in",
    "locked account",
    "blocked account",
    "manual review",
}

UNCLEAR_KEYWORDS = {
    "unclear",
    "not sure",
    "don't know",
    "do not know",
    "issue",
    "problem",
    "help",
}

DOCUMENT_REVIEW_KEYWORDS = {
    "document",
    "documents",
    "verify my account",
    "review my account",
    "review my documents",
    "verify my documents",
}


def should_escalate(query: str, confidence: float) -> tuple[bool, str]:
    query_lower = query.lower()

    if any(keyword in query_lower for keyword in DOCUMENT_REVIEW_KEYWORDS):
        return True, "Document-specific or account-specific review requires human support."

    if any(keyword in query_lower for keyword in RISKY_KEYWORDS):
        return True, "Risky or account-sensitive issue requires human support."

    if any(keyword in query_lower for keyword in UNCLEAR_KEYWORDS):
        return True, "Issue is unclear and should be escalated to human support."

    if confidence < settings.confidence_threshold:
        return True, "Low confidence response."

    return False, "Grounded answer supported by available policy."