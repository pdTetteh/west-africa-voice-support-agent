def infer_issue_type(query: str) -> str:
    query_lower = query.lower()

    if "wrong recipient" in query_lower or "wrong person" in query_lower:
        return "wrong_recipient"

    if "locked" in query_lower or "log in" in query_lower or "sign in" in query_lower:
        return "account_locked"

    if "kyc" in query_lower or "identity" in query_lower or "document" in query_lower:
        return "identity_verification"

    if "cash out" in query_lower or "cash-out" in query_lower or "cashout" in query_lower:
        return "cashout_issue"

    return "general_support"


def build_ticket_summary(query: str, issue_type: str) -> str:
    query_preview = query.strip()[:180]

    summaries = {
        "wrong_recipient": (
            "Customer reports sending money to the wrong recipient. Manual support review required."
        ),
        "account_locked": (
            "Customer reports locked account or login/access issue. Secure verification may be required."
        ),
        "identity_verification": (
            "Customer reports identity verification or document-review issue. Human review may be required."
        ),
        "cashout_issue": (
            "Customer reports failed cash-out or deducted balance issue. Check transaction status and reconciliation."
        ),
        "general_support": (
            "Customer issue requires human support review."
        ),
    }

    return f"{summaries.get(issue_type, summaries['general_support'])} Customer query: {query_preview}"