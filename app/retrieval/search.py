import math
from collections import Counter
from functools import lru_cache
from pathlib import Path

from app.core.config import settings
from app.core.schemas import EvidenceItem, RetrievedChunk
from app.retrieval.chunking import chunk_text
from app.retrieval.loader import load_markdown_documents
from app.retrieval.normalize import expand_tokens, normalize_text, tokenize


GENERIC_POLICY_SOURCES = {"faq.md", "escalation_policy.md"}

SOURCE_PRIORITY_BOOSTS = {
    "account_locked.md": {"account", "locked", "login", "blocked", "access", "profile"},
    "cashout_failures.md": {"cashout", "deducted_balance", "withdrawal", "withdraw"},
    "wrong_recipient.md": {"wrong_recipient", "transfer", "recipient", "transferred", "funds"},
    "kyc_help.md": {"identity_verification", "kyc", "verification", "identity"},
}


@lru_cache(maxsize=1)
def build_chunk_index() -> tuple[RetrievedChunk, ...]:
    kb_dir = Path("knowledge_base")
    docs = load_markdown_documents(kb_dir)

    chunks: list[RetrievedChunk] = []

    for filename, content in docs:
        raw_chunks = chunk_text(content, chunk_size=420, overlap=60)
        for idx, text in enumerate(raw_chunks, start=1):
            chunks.append(
                RetrievedChunk(
                    source=filename,
                    chunk_id=f"{filename.replace('.md', '')}_{idx:03d}",
                    text=text,
                    score=0.0,
                )
            )

    return tuple(chunks)


def _source_priority_bonus(source: str, query_tokens: list[str]) -> float:
    bonus = 0.0
    query_token_set = set(query_tokens)

    if source in SOURCE_PRIORITY_BOOSTS:
        matched = query_token_set.intersection(SOURCE_PRIORITY_BOOSTS[source])
        bonus += 1.5 * len(matched)

    if source in GENERIC_POLICY_SOURCES and bonus == 0.0:
        bonus -= 0.75

    return bonus


def score_chunk_lexical(query: str, chunk: RetrievedChunk) -> float:
    normalized_query = normalize_text(query)
    normalized_chunk = normalize_text(chunk.text)
    normalized_source = normalize_text(chunk.source.replace(".md", ""))

    query_tokens = expand_tokens(tokenize(normalized_query))
    chunk_tokens = expand_tokens(tokenize(normalized_chunk))
    filename_tokens = expand_tokens(tokenize(normalized_source))

    if not query_tokens or not chunk_tokens:
        return 0.0

    query_counts = Counter(query_tokens)
    chunk_counts = Counter(chunk_tokens)
    filename_counts = Counter(filename_tokens)

    score = 0.0
    chunk_length_norm = math.sqrt(len(chunk_tokens)) if chunk_tokens else 1.0

    for token, q_count in query_counts.items():
        token_score = 0.0

        if token in chunk_counts:
            tf = chunk_counts[token]
            token_score += (1.0 + math.log1p(tf)) * q_count

        if token in filename_counts:
            token_score += 2.0 * q_count

        score += token_score

    phrase_boosts = {
        "cashout": 2.5,
        "wrong_recipient": 3.5,
        "identity_verification": 2.2,
        "login": 1.8,
        "locked": 1.8,
        "deducted_balance": 2.0,
    }

    for phrase, boost in phrase_boosts.items():
        if phrase in normalized_query and phrase in normalized_chunk:
            score += boost
        if phrase in normalized_query and phrase in normalized_source:
            score += boost + 1.0

    score += _source_priority_bonus(chunk.source, query_tokens)

    return score / chunk_length_norm


def retrieve_support_chunks(query: str, top_k: int | None = None) -> list[RetrievedChunk]:
    top_k = top_k or settings.retrieval_top_k
    chunks = build_chunk_index()

    scored: list[RetrievedChunk] = []

    for chunk in chunks:
        lexical_score = score_chunk_lexical(query, chunk)
        scored.append(
            RetrievedChunk(
                source=chunk.source,
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                score=lexical_score,
            )
        )

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:top_k]


def retrieve_support_evidence(query: str, top_k: int | None = None) -> list[EvidenceItem]:
    chunks = retrieve_support_chunks(query=query, top_k=top_k)

    return [
        EvidenceItem(
            source=chunk.source,
            chunk_id=chunk.chunk_id,
            snippet=chunk.text[:280].strip(),
        )
        for chunk in chunks
        if chunk.score > 0
    ]