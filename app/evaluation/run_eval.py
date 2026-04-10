import json
from pathlib import Path
from statistics import mean

from app.agent.pipeline import run_support_pipeline
from app.core.schemas import EvalExample, EvalSummary


BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "eval" / "eval_set.jsonl"
REPORT_PATH = BASE_DIR / "eval" / "report.md"


def load_eval_examples(path: Path) -> list[EvalExample]:
    if not path.exists():
        raise FileNotFoundError(f"Eval dataset not found: {path}")

    examples: list[EvalExample] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        examples.append(EvalExample(**payload))

    return examples


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def gold_coverage(answer: str, gold_points: list[str]) -> float:
    if not gold_points:
        return 0.0

    answer_norm = normalize_text(answer)
    matched = 0

    for point in gold_points:
        point_norm = normalize_text(point)
        if point_norm in answer_norm:
            matched += 1
            continue

        point_tokens = point_norm.split()
        if point_tokens:
            overlap = sum(token in answer_norm for token in point_tokens) / len(point_tokens)
            if overlap >= 0.6:
                matched += 1

    return matched / len(gold_points)


def run_eval() -> EvalSummary:
    examples = load_eval_examples(DATASET_PATH)

    if not examples:
        raise ValueError("Eval dataset is empty")

    top1_hits = 0
    recall_hits = 0
    escalation_hits = 0
    coverages: list[float] = []
    confidences: list[float] = []
    unsupported_answer_count = 0

    per_example_rows: list[dict] = []

    for example in examples:
        response = run_support_pipeline(example.query)

        evidence_sources = [item.source for item in response.evidence]
        top_source = evidence_sources[0] if evidence_sources else None

        top1_hit = top_source == example.expected_primary_source
        recall_hit = example.expected_primary_source in evidence_sources
        escalation_hit = response.escalate == example.expected_escalation
        coverage = gold_coverage(response.answer, example.gold_points)

        top1_hits += int(top1_hit)
        recall_hits += int(recall_hit)
        escalation_hits += int(escalation_hit)
        coverages.append(coverage)
        confidences.append(response.confidence)

        if coverage < 0.34 and not response.escalate:
            unsupported_answer_count += 1

        per_example_rows.append(
            {
                "id": example.id,
                "query": example.query,
                "expected_source": example.expected_primary_source,
                "predicted_source": top_source,
                "expected_escalation": example.expected_escalation,
                "predicted_escalation": response.escalate,
                "coverage": round(coverage, 3),
                "confidence": round(response.confidence, 3),
            }
        )

    summary = EvalSummary(
        total_examples=len(examples),
        top1_retrieval_accuracy=top1_hits / len(examples),
        evidence_recall_at_3=recall_hits / len(examples),
        escalation_accuracy=escalation_hits / len(examples),
        average_gold_coverage=mean(coverages),
        average_confidence=mean(confidences),
        unsupported_answer_count=unsupported_answer_count,
        report_path=str(REPORT_PATH),
    )

    write_report(summary=summary, rows=per_example_rows, output_path=REPORT_PATH)
    return summary


def write_report(summary: EvalSummary, rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# Evaluation Report",
        "",
        "## Summary",
        "",
        f"- Total examples: {summary.total_examples}",
        f"- Top-1 retrieval accuracy: {summary.top1_retrieval_accuracy:.2%}",
        f"- Evidence recall@3: {summary.evidence_recall_at_3:.2%}",
        f"- Escalation accuracy: {summary.escalation_accuracy:.2%}",
        f"- Average gold coverage: {summary.average_gold_coverage:.2%}",
        f"- Average confidence: {summary.average_confidence:.3f}",
        f"- Unsupported answer count: {summary.unsupported_answer_count}",
        "",
        "## Per-example results",
        "",
        "| ID | Expected Source | Predicted Source | Expected Escalation | Predicted Escalation | Coverage | Confidence |",
        "|---|---|---|---:|---:|---:|---:|",
    ]

    for row in rows:
        lines.append(
            f"| {row['id']} | {row['expected_source']} | {row['predicted_source']} | "
            f"{row['expected_escalation']} | {row['predicted_escalation']} | "
            f"{row['coverage']:.3f} | {row['confidence']:.3f} |"
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    summary = run_eval()
    print(summary.model_dump_json(indent=2))