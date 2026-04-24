from app.retrieval.search import build_chunk_index
from app.retrieval.vector_search import build_vector_index


def clear_retrieval_caches() -> None:
    build_chunk_index.cache_clear()
    build_vector_index.cache_clear()