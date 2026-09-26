"""ChromaDB ingestion and indexing engine for Bangladesh agriculture knowledge chunks."""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple

import chromadb
from chromadb.api.models.Collection import Collection

from vector_store.config import VectorStoreConfig, default_config
from vector_store.embedding_service import get_embedding_function

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def sanitize_metadata(meta: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all metadata fields are ChromaDB-compatible primitives (str, int, float, bool)."""
    clean = {}
    for k, v in meta.items():
        if v is None:
            clean[k] = ""
        elif isinstance(v, (str, int, float, bool)):
            clean[k] = v
        elif isinstance(v, (list, tuple)):
            clean[k] = ", ".join(str(item) for item in v)
        elif isinstance(v, dict):
            clean[k] = json.dumps(v, ensure_ascii=False)
        else:
            clean[k] = str(v)
    return clean


def generate_variety_profile_chunks(catalog_path: Path) -> List[Dict[str, Any]]:
    """Generate high-density semantic profile chunks from the BRRI rice varieties catalog."""
    if not catalog_path.exists():
        logger.warning(f"BRRI varieties catalog not found at {catalog_path}. Skipping variety profiles.")
        return []

    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        logger.error(f"Failed to read variety catalog {catalog_path}: {exc}")
        return []

    varieties = data.get("varieties", [])
    profile_chunks = []

    for idx, v in enumerate(varieties):
        name_en = v.get("variety_name", "")
        name_bn = v.get("variety_name_bn", "")
        season = v.get("season", "")
        crop = v.get("crop", "Rice (ধান)")
        doc_id = v.get("document_id", f"brri_variety_{idx+1}")
        orig_fname = v.get("original_filename", "")

        # Rich bilingual semantic profile text
        bn_title_str = f" ({name_bn})" if name_bn else ""
        text = (
            f"বাংলাদেশ ধান গবেষণা ইনস্টিটিউট (BRRI) উদ্ভাবিত ধানের জাত: {name_en}{bn_title_str}। "
            f"ফসল: {crop}। মৌসুম: {season}। "
            f"উৎস: বাংলাদেশ ধান গবেষণা ইনস্টিটিউট (BRRI)। "
            f"জাতের তথ্যপত্র এবং চাষাবাদ নির্দেশিকা: {name_en} Fact Sheet Leaflet। "
            f"Official rice variety developed by Bangladesh Rice Research Institute (BRRI): {name_en}."
        )

        chunk_id = f"{doc_id}_profile"
        profile_chunks.append({
            "text": text,
            "source": "BRRI",
            "category": "cereals",
            "page_number": 1,
            "language": "Bangla" if name_bn else "English",
            "chunk_id": chunk_id,
            "document_id": doc_id,
            "variety_name": name_en,
            "variety_name_bn": name_bn,
            "is_variety_profile": True
        })

    logger.info(f"Generated {len(profile_chunks)} BRRI variety profile chunks.")
    return profile_chunks


class ChromaIndexer:
    """Orchestrator for indexing knowledge base chunks into ChromaDB."""

    def __init__(self, config: Optional[VectorStoreConfig] = None):
        self.config = config or default_config
        self.config.persist_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Connecting to persistent ChromaDB at: {self.config.persist_dir}")
        self.client = chromadb.PersistentClient(path=str(self.config.persist_dir))
        self.embedding_fn = get_embedding_function(self.config.embedding_provider)

        self.collection: Collection = self.client.get_or_create_collection(
            name=self.config.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "Bangladesh Crop Intelligence RAG Knowledge Base"}
        )

    def load_all_chunks(self) -> Tuple[List[Dict[str, Any]], int, int]:
        """Load document chunks and synthetic variety profiles, deduplicating by chunk_id."""
        if not self.config.chunks_path.exists():
            raise FileNotFoundError(f"Chunks file does not exist: {self.config.chunks_path}")

        logger.info(f"Reading document chunks from: {self.config.chunks_path}")
        with open(self.config.chunks_path, "r", encoding="utf-8") as f:
            doc_chunks = json.load(f)

        logger.info(f"Loaded {len(doc_chunks):,} base document chunks.")

        # Load BRRI variety profile chunks
        variety_chunks = generate_variety_profile_chunks(self.config.varieties_catalog_path)

        # Merge and deduplicate
        seen_ids = set()
        merged_chunks = []

        for c in doc_chunks + variety_chunks:
            cid = c.get("chunk_id")
            if not cid:
                continue
            if cid not in seen_ids:
                seen_ids.add(cid)
                merged_chunks.append(c)

        return merged_chunks, len(doc_chunks), len(variety_chunks)

    def index(
        self,
        reset_existing: bool = False,
        batch_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Index all loaded chunks into ChromaDB in batches.

        Args:
            reset_existing: If True, deletes existing collection documents first.
            batch_size: Batch size for ChromaDB insertion.

        Returns:
            Dictionary containing indexing performance and metrics.
        """
        start_time = time.time()
        bsize = batch_size or self.config.batch_size

        if reset_existing:
            logger.warning(f"Resetting existing collection: {self.config.collection_name}")
            self.client.delete_collection(name=self.config.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.config.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"description": "Bangladesh Crop Intelligence RAG Knowledge Base"}
            )

        chunks, doc_chunks_count, variety_chunks_count = self.load_all_chunks()
        total_chunks = len(chunks)

        logger.info(f"Starting batch indexing for {total_chunks:,} chunks (Batch size: {bsize})...")

        total_batches = (total_chunks + bsize - 1) // bsize

        for b_idx in range(total_batches):
            b_start = b_idx * bsize
            b_end = min(b_start + bsize, total_chunks)
            batch = chunks[b_start:b_end]

            ids = [c["chunk_id"] for c in batch]
            documents = [c["text"] for c in batch]
            metadatas = [
                sanitize_metadata({
                    "source": c.get("source", ""),
                    "category": c.get("category", ""),
                    "page_number": c.get("page_number", 0),
                    "language": c.get("language", ""),
                    "document_id": c.get("document_id", ""),
                    "variety_name": c.get("variety_name", ""),
                    "is_variety_profile": c.get("is_variety_profile", False)
                })
                for c in batch
            ]

            # Upsert into ChromaDB
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

            progress_pct = (b_end / total_chunks) * 100
            elapsed = time.time() - start_time
            rate = b_end / elapsed if elapsed > 0 else 0
            logger.info(
                f"Batch [{b_idx + 1}/{total_batches}] | Indexed {b_end:,}/{total_chunks:,} "
                f"({progress_pct:.1f}%) | Speed: {rate:.1f} chunks/sec"
            )

        duration = round(time.time() - start_time, 2)
        final_count = self.collection.count()

        summary = {
            "status": "success",
            "collection_name": self.config.collection_name,
            "total_chunks_indexed": total_chunks,
            "doc_chunks_indexed": doc_chunks_count,
            "variety_profiles_indexed": variety_chunks_count,
            "final_collection_count": final_count,
            "duration_seconds": duration,
            "avg_speed_chunks_per_sec": round(total_chunks / duration, 1) if duration > 0 else 0,
            "persist_directory": str(self.config.persist_dir),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Save indexing report
        report_path = self.config.persist_dir.parent / "reports" / "vector_indexing_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info(f"Indexing completed in {duration}s. Final Chroma collection count: {final_count:,}.")
        logger.info(f"Report saved to: {report_path}")
        return summary
