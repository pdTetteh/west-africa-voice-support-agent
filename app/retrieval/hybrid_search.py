from app.core.config import settings
from app.core.schemas import EvidenceItem, RetrievedChunk
from app.retrieval.normalize import expand_tokens, tokenize
from app.retrieval.search import (
    GENERIC_POLICY_SOURCES,
    SOURCE_PRIORITY_BOOSTS,
    build_chunk_index,
    score_chunk_lexical,
)
from app.retrieval.vector_search import vector_similarity_scores


def _normalize_scores(raw_scores: dict[str, float]) -> dict[str, float]:
    if not raw_scores:
        return {}

    max_score = max(raw_scores.values())
    min_score = min(raw_scores.values())

    if max_score == min_score:
        return {key: 1.0 for key in raw_scores}

    return {
        key: (value - min_score) / (max_score - min_score)
        for key, value in raw_scores.items()
    }


def _source_prior(source: str, query_tokens: list[str]) -> float:
    query_set = set(query_tokens)
    matched = query_set.intersection(SOURCE_PRIORITY_BOOSTS.get(source, set()))

    prior = 0.0

    if matched:
        prior += 0.12 * len(matched)

    if source in GENERIC_POLICY_SOURCES and not matched:
        prior -= 0.10

    return prior


def retrieve_support_chunks_hybrid(query: str, top_k: int | None = None) -> list[RetrievedChunk]:
    top_k = top_k or settings.retrieval_top_k
    chunks = build_chunk_index()

    query_tokens = expand_tokens(tokenize(query))

    lexical_scores = {
        chunk.chunk_id: score_chunk_lexical(query, chunk)
        for chunk in chunks
    }
    vector_scores = vector_similarity_scores(query)

    lexical_norm = _normalize_scores(lexical_scores)
    vector_norm = _normalize_scores(vector_scores)

    scored: list[RetrievedChunk] = []

    for chunk in chunks:
        lexical = lexical_norm.get(chunk.chunk_id, 0.0)
        vector = vector_norm.get(chunk.chunk_id, 0.0)
        prior = _source_prior(chunk.source, query_tokens)

        hybrid_score = 0.60 * lexical + 0.30 * vector + 0.10 * max(lexical, vector)
        hybrid_score += prior

        scored.append(
            RetrievedChunk(
                source=chunk.source,
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                score=hybrid_score,
            )
        )

    scored.sort(key=lambda item: item.score, reverse=True)

    ranked = scored[: max(top_k * 2, top_k)]

    if ranked and ranked[0].source in GENERIC_POLICY_SOURCES:
        specific_candidates = [item for item in ranked if item.source not in GENERIC_POLICY_SOURCES]
        if specific_candidates:
            best_specific = specific_candidates[0]
            if best_specific.score >= ranked[0].score - 0.15:
                ranked.remove(best_specific)
                ranked.insert(0, best_specific)

    return ranked[:top_k]


def retrieve_support_evidence_hybrid(query: str, top_k: int | None = None) -> list[EvidenceItem]:
    chunks = retrieve_support_chunks_hybrid(query=query, top_k=top_k)

    return [
        EvidenceItem(
            source=chunk.source,
            chunk_id=chunk.chunk_id,
            snippet=chunk.text[:280].strip(),
        )
        for chunk in chunks
        if chunk.score > 0
    ]