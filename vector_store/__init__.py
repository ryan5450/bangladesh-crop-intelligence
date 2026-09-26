"""Bangladesh Crop Intelligence Assistant - Vector Store Package.

Provides high-performance vector embeddings, ChromaDB indexing, and semantic retrieval
for Bangladesh agriculture intelligence.
"""

from vector_store.config import VectorStoreConfig, default_config
from vector_store.embedding_service import get_embedding_function
from vector_store.indexer import ChromaIndexer
from vector_store.retriever import ChromaRetriever, SearchResult, get_retriever

__all__ = [
    "VectorStoreConfig",
    "default_config",
    "get_embedding_function",
    "ChromaIndexer",
    "ChromaRetriever",
    "SearchResult",
    "get_retriever",
]
