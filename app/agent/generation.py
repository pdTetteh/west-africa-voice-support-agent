import re
from typing import Iterable

from app.core.schemas import RetrievedChunk
from app.retrieval.normalize import expand_tokens, tokenize


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
MARKDOWN_HEADER_RE = re.compile(r"^\s*#+\s*", re.MULTILINE)

GUIDANCE_HINTS = {
    "wait",
    "review",
    "retrying",
    "retry",
    "reconciliation",
    "escalate",
    "manual",
    "verification",
    "identity",
    "secure",
    "recovery",
    "support",
    "guarantee",
    "reversal",
}


def _clean_text(text: str) -> str:
    text = MARKDOWN_HEADER_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_sentences(text: str) -> list[str]:
    cleaned = _clean_text(text)
    if not cleaned:
        return []

    sentences = SENTENCE_SPLIT_RE.split(cleaned)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def score_sentence(query: str, sentence: str) -> float:
    query_tokens = set(expand_tokens(tokenize(query)))
    sentence_tokens = expand_tokens(tokenize(sentence))

    if not sentence_tokens:
        return 0.0

    overlap = sum(1 for token in sentence_tokens if token in query_tokens)
    guidance_bonus = sum(1 for token in sentence_tokens if token in GUIDANCE_HINTS) * 0.15

    return float(overlap) + guidance_bonus


def select_grounding_sentences(
    query: str,
    chunks: Iterable[RetrievedChunk],
    max_sentences: int = 3,
) -> list[str]:
    candidates: list[tuple[float, str]] = []

    for chunk in chunks:
        for sentence in split_sentences(chunk.text):
            sentence_score = score_sentence(query, sentence)
            if sentence_score > 0:
                candidates.append((sentence_score + max(chunk.score, 0.0), sentence))

    candidates.sort(key=lambda item: item[0], reverse=True)

    selected: list[str] = []
    seen_normalized: set[str] = set()

    for _, sentence in candidates:
        normalized = sentence.lower().strip()
        if normalized in seen_normalized:
            continue
        selected.append(sentence)
        seen_normalized.add(normalized)
        if len(selected) >= max_sentences:
            break

    return selected


def build_grounded_answer(query: str, chunks: list[RetrievedChunk]) -> tuple[str, float]:
    scored_chunks = [chunk for chunk in chunks if chunk.score > 0]

    if not scored_chunks:
        return (
            "I could not find enough grounded support information for this issue. "
            "Please escalate this case to a human support agent.",
            0.30,
        )

    grounding_sentences = select_grounding_sentences(query=query, chunks=scored_chunks, max_sentences=3)

    if not grounding_sentences:
        return (
            "I found related support content, but not enough clear guidance to answer safely. "
            "Please escalate this case to a human support agent.",
            0.40,
        )

    if len(grounding_sentences) == 1:
        answer = f"Based on the available support guidance: {grounding_sentences[0]}"
    elif len(grounding_sentences) == 2:
        answer = (
            f"Based on the available support guidance: {grounding_sentences[0]} "
            f"In addition, {grounding_sentences[1][0].lower() + grounding_sentences[1][1:]}"
        )
    else:
        answer = (
            f"Based on the available support guidance: {grounding_sentences[0]} "
            f"In addition, {grounding_sentences[1][0].lower() + grounding_sentences[1][1:]} "
            f"Also, {grounding_sentences[2][0].lower() + grounding_sentences[2][1:]}"
        )

    top_score = max(scored_chunks[0].score, 0.0)
    second_score = max(scored_chunks[1].score, 0.0) if len(scored_chunks) > 1 else 0.0
    score_gap = max(top_score - second_score, 0.0)

    confidence = 0.42
    confidence += min(top_score, 1.0) * 0.18
    confidence += min(score_gap, 0.5) * 0.12
    confidence += min(len(grounding_sentences), 3) * 0.04
    confidence = min(confidence, 0.78)

    return answer, confidence