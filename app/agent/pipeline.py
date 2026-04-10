from app.agent.generation import build_grounded_answer
from app.core.schemas import AskResponse, EvidenceItem, RetrievedChunk
from app.guardrails.escalation import should_escalate
from app.retrieval.hybrid_search import retrieve_support_chunks_hybrid
from app.retrieval.search import GENERIC_POLICY_SOURCES


def _pick_primary_chunk(chunks: list[RetrievedChunk]) -> RetrievedChunk | None:
    specific_chunks = [
        chunk for chunk in chunks if chunk.score > 0 and chunk.source not in GENERIC_POLICY_SOURCES
    ]
    if specific_chunks:
        return specific_chunks[0]

    fallback_chunks = [chunk for chunk in chunks if chunk.score > 0]
    return fallback_chunks[0] if fallback_chunks else None


def _pick_supporting_policy_chunk(
    chunks: list[RetrievedChunk],
    primary_source: str | None,
) -> RetrievedChunk | None:
    for chunk in chunks:
        if chunk.score <= 0:
            continue
        if chunk.source in GENERIC_POLICY_SOURCES and chunk.source != primary_source:
            return chunk
    return None


def _build_evidence(
    chunks: list[RetrievedChunk],
    primary_chunk: RetrievedChunk | None,
    supporting_chunk: RetrievedChunk | None,
    max_items: int = 3,
) -> list[EvidenceItem]:
    ordered: list[RetrievedChunk] = []

    if primary_chunk is not None:
        ordered.append(primary_chunk)

    if supporting_chunk is not None and supporting_chunk.chunk_id != (
        primary_chunk.chunk_id if primary_chunk else None
    ):
        ordered.append(supporting_chunk)

    seen_chunk_ids = {chunk.chunk_id for chunk in ordered}

    for chunk in chunks:
        if chunk.score <= 0:
            continue
        if chunk.chunk_id in seen_chunk_ids:
            continue
        ordered.append(chunk)
        seen_chunk_ids.add(chunk.chunk_id)
        if len(ordered) >= max_items:
            break

    return [
        EvidenceItem(
            source=chunk.source,
            chunk_id=chunk.chunk_id,
            snippet=chunk.text[:280].strip(),
        )
        for chunk in ordered[:max_items]
    ]


def _build_reason(
    primary_chunk: RetrievedChunk | None,
    supporting_chunk: RetrievedChunk | None,
    escalate: bool,
    base_reason: str,
) -> str:
    if primary_chunk is None:
        return base_reason

    if supporting_chunk is not None:
        if escalate:
            return (
                f"Primary evidence: {primary_chunk.source}; supporting policy: "
                f"{supporting_chunk.source}. {base_reason}"
            )
        return (
            f"Primary evidence: {primary_chunk.source}; additional guidance: "
            f"{supporting_chunk.source}. {base_reason}"
        )

    return f"Primary evidence: {primary_chunk.source}. {base_reason}"


def run_support_pipeline(query: str, transcript: str | None = None) -> AskResponse:
    retrieved_chunks = retrieve_support_chunks_hybrid(query=query, top_k=5)

    primary_chunk = _pick_primary_chunk(retrieved_chunks)
    primary_source = primary_chunk.source if primary_chunk is not None else None

    supporting_chunk = _pick_supporting_policy_chunk(
        retrieved_chunks,
        primary_source=primary_source,
    )

    generation_inputs: list[RetrievedChunk] = []
    if primary_chunk is not None:
        generation_inputs.append(primary_chunk)
    if supporting_chunk is not None:
        generation_inputs.append(supporting_chunk)

    for chunk in retrieved_chunks:
        if chunk.score <= 0:
            continue
        if chunk.chunk_id in {item.chunk_id for item in generation_inputs}:
            continue
        generation_inputs.append(chunk)
        if len(generation_inputs) >= 3:
            break

    answer, confidence = build_grounded_answer(
        query=query,
        chunks=generation_inputs,
    )

    escalate, base_reason = should_escalate(query=query, confidence=confidence)

    evidence = _build_evidence(
        chunks=retrieved_chunks,
        primary_chunk=primary_chunk,
        supporting_chunk=supporting_chunk,
        max_items=3,
    )

    reason = _build_reason(
        primary_chunk=primary_chunk,
        supporting_chunk=supporting_chunk,
        escalate=escalate,
        base_reason=base_reason,
    )

    return AskResponse(
        transcript=transcript,
        answer=answer,
        evidence=evidence,
        confidence=confidence,
        escalate=escalate,
        reason=reason,
    )