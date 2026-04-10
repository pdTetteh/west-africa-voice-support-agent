from pathlib import Path

from app.evaluation.run_eval import run_eval


def test_run_eval_generates_report() -> None:
    summary = run_eval()

    assert summary.total_examples >= 1
    assert 0.0 <= summary.top1_retrieval_accuracy <= 1.0
    assert 0.0 <= summary.evidence_recall_at_3 <= 1.0
    assert 0.0 <= summary.escalation_accuracy <= 1.0
    assert Path(summary.report_path).exists()