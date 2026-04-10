from functools import lru_cache
from typing import NamedTuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.schemas import RetrievedChunk
from app.retrieval.normalize import normalize_text
from app.retrieval.search import build_chunk_index


class VectorIndex(NamedTuple):
    vectorizer: TfidfVectorizer
    matrix: np.ndarray
    chunks: tuple[RetrievedChunk, ...]


def _prepare_corpus_text(chunk: RetrievedChunk) -> str:
    source_text = chunk.source.replace(".md", "").replace("_", " ")
    return normalize_text(f"{source_text} {chunk.text}")


@lru_cache(maxsize=1)
def build_vector_index() -> VectorIndex:
    chunks = build_chunk_index()
    corpus = [_prepare_corpus_text(chunk) for chunk in chunks]

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
        norm="l2",
    )
    matrix = vectorizer.fit_transform(corpus)

    return VectorIndex(
        vectorizer=vectorizer,
        matrix=matrix,
        chunks=chunks,
    )


def vector_similarity_scores(query: str) -> dict[str, float]:
    index = build_vector_index()
    query_text = normalize_text(query)
    query_vec = index.vectorizer.transform([query_text])

    similarities = (index.matrix @ query_vec.T).toarray().ravel()

    scores: dict[str, float] = {}
    for chunk, score in zip(index.chunks, similarities, strict=False):
        scores[chunk.chunk_id] = float(score)

    return scores