from app.guardrails.tickets import build_ticket_summary, infer_issue_type


def test_wrong_recipient_ticket_summary_is_internal_and_clean() -> None:
    query = "I sent money to the wrong person"
    issue_type = infer_issue_type(query)
    summary = build_ticket_summary(query, issue_type)

    assert issue_type == "wrong_recipient"
    assert "Manual support review required" in summary
    assert "Customer query" in summary
    assert "Based on the available support guidance" not in summary