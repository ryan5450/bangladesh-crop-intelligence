"""Semantic retrieval engine querying ChromaDB with metadata filters and citation formatting."""

from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.api.models.Collection import Collection

from vector_store.config import VectorStoreConfig, default_config
from vector_store.embedding_service import get_embedding_function
from vector_store.cross_lingual import expand_query_bilingual

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Individual retrieved chunk with similarity score and metadata."""

    chunk_id: str
    text: str
    distance: float
    relevance_score: float  # Normalized 0.0 - 1.0 (1.0 = exact match)
    source: str
    category: str
    page_number: int
    language: str
    document_id: str
    variety_name: str = ""

    def citation(self) -> str:
        """Format an inline academic/official citation."""
        page_str = f", Page {self.page_number}" if self.page_number > 0 else ""
        return f"[{self.source} - {self.category.capitalize()}{page_str}]"


class ChromaRetriever:
    """High-performance semantic retriever for the Bangladesh agriculture RAG pipeline."""

    def __init__(self, config: Optional[VectorStoreConfig] = None):
        self.config = config or default_config
        self.client = chromadb.PersistentClient(path=str(self.config.persist_dir))
        self.embedding_fn = get_embedding_function(self.config.embedding_provider)

        self.collection: Collection = self.client.get_collection(
            name=self.config.collection_name,
            embedding_function=self.embedding_fn
        )

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        category: Optional[str] = None,
        source: Optional[str] = None,
        language: Optional[str] = None,
        max_distance: Optional[float] = None,
        expand_bilingual: bool = True
    ) -> List[SearchResult]:
        """Perform semantic search against ChromaDB with optional metadata filtering.

        Args:
            query: User's question or search query (Bangla or English).
            top_k: Number of chunks to retrieve. Defaults to config.default_top_k (5).
            category: Filter by agricultural category (e.g. 'cereals', 'diseases', 'fertilizer_management').
            source: Filter by institute ('BRRI', 'BARI', 'DAE', 'BAMIS', 'FAO').
            language: Filter by document language ('Bangla', 'English').
            max_distance: Maximum distance threshold for relevance.
            expand_bilingual: If True, augments query with cross-lingual domain keywords (e.g. English <-> Bangla).

        Returns:
            List of SearchResult objects sorted by descending relevance.
        """
        k = top_k or self.config.default_top_k
        search_query = expand_query_bilingual(query) if expand_bilingual else query

        # Build ChromaDB 'where' filter
        where_clauses = []
        if category:
            where_clauses.append({"category": category.lower()})
        if source:
            where_clauses.append({"source": source.upper()})
        if language:
            where_clauses.append({"language": language})

        where_filter = None
        if len(where_clauses) == 1:
            where_filter = where_clauses[0]
        elif len(where_clauses) > 1:
            where_filter = {"$and": where_clauses}

        results = self.collection.query(
            query_texts=[search_query],
            n_results=k,
            where=where_filter
        )

        search_results: List[SearchResult] = []

        if not results or not results.get("ids") or not results["ids"][0]:
            return search_results

        ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        for cid, doc, meta, dist in zip(ids, docs, metas, distances):
            if max_distance is not None and dist > max_distance:
                continue

            # Convert cosine/L2 distance to normalized relevance score (0.0 to 1.0)
            relevance = max(0.0, min(1.0, 1.0 - (dist / 2.0)))

            res = SearchResult(
                chunk_id=cid,
                text=doc,
                distance=round(dist, 4),
                relevance_score=round(relevance, 4),
                source=meta.get("source", "Unknown"),
                category=meta.get("category", "General"),
                page_number=int(meta.get("page_number", 0)),
                language=meta.get("language", "Unknown"),
                document_id=meta.get("document_id", ""),
                variety_name=meta.get("variety_name", "")
            )
            search_results.append(res)

        return search_results

    def format_context_for_rag(self, results: List[SearchResult]) -> str:
        """Format retrieved search results into an LLM-ready context block with citations."""
        if not results:
            return "No relevant agricultural knowledge documents found for this query."

        context_blocks = []
        for i, r in enumerate(results, 1):
            citation = r.citation()
            context_blocks.append(
                f"--- DOCUMENT {i} {citation} [Relevance: {r.relevance_score:.0%}] ---\n"
                f"{r.text.strip()}"
            )

        return "\n\n".join(context_blocks)


def get_retriever(config: Optional[VectorStoreConfig] = None) -> ChromaRetriever:
    """Helper factory function to instantiate a ChromaRetriever."""
    return ChromaRetriever(config=config)
