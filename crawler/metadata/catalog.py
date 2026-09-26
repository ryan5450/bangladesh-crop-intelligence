"""Catalog manager organizing knowledge_base/ storage and index generation."""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import CATALOG_PATH, KNOWLEDGE_BASE_DIR, SUMMARY_PATH, CATEGORIES
from metadata.schema import DocumentMetadata
from utils.file_helper import ensure_dir
from utils.logger import get_logger

logger = get_logger("metadata.catalog")


class CatalogManager:
    """Manages persistent document storage, per-file metadata, and master catalog index."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or KNOWLEDGE_BASE_DIR
        ensure_dir(self.base_dir)

        # Initialize all 24 category folders in knowledge_base/
        for cat in CATEGORIES:
            ensure_dir(self.base_dir / cat)

        self.catalog_path = self.base_dir / "catalog.json"
        self.summary_path = self.base_dir / "summary.json"
        self._catalog_cache: Dict[str, Dict[str, Any]] = self._load_catalog()

    def _load_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Load existing master catalog from disk."""
        if self.catalog_path.exists():
            try:
                with open(self.catalog_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return {doc["document_id"]: doc for doc in data if "document_id" in doc}
                    elif isinstance(data, dict):
                        return data
            except Exception as exc:
                logger.warning(f"Could not parse existing catalog.json: {exc}. Starting fresh.")
        return {}

    def is_already_cataloged(self, doc_hash: str) -> bool:
        """Check if a document with this hash is already present in the catalog."""
        short_hash = doc_hash[:12]
        return any(short_hash in doc_id for doc_id in self._catalog_cache.keys())

    def save_document(
        self,
        staged_pdf_path: Path,
        cleaned_text: str,
        metadata: DocumentMetadata,
        primary_category: str,
    ) -> Path:
        """Store document triplet (PDF, JSON metadata, TXT) in destination category folder."""
        cat_dir = ensure_dir(self.base_dir / primary_category)

        target_pdf_path = cat_dir / metadata.filename
        target_meta_path = cat_dir / f"{target_pdf_path.stem}.json"
        target_txt_path = cat_dir / f"{target_pdf_path.stem}.txt"

        # 1. Move PDF from staging to permanent category folder
        shutil.copy2(staged_pdf_path, target_pdf_path)

        # 2. Write per-document metadata JSON
        with open(target_meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata.model_dump(), f, ensure_ascii=False, indent=2)

        # 3. Write extracted clean text (for instant RAG chunking and embeddings)
        with open(target_txt_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        # 4. Update memory cache and write master catalog
        self._catalog_cache[metadata.document_id] = metadata.model_dump()
        self._write_catalog()
        self._write_summary()

        logger.info(
            f"[SAVED] {metadata.filename} -> {primary_category}/ | "
            f"Quality: {metadata.quality_score:.2f} | Language: {metadata.language}"
        )

        return target_pdf_path

    def _write_catalog(self) -> None:
        """Write master catalog array to catalog.json."""
        catalog_list = sorted(list(self._catalog_cache.values()), key=lambda x: x.get("title", ""))
        with open(self.catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog_list, f, ensure_ascii=False, indent=2)

    def _write_summary(self) -> None:
        """Generate and save aggregate statistical summary."""
        docs = list(self._catalog_cache.values())
        total_docs = len(docs)
        total_pages = sum(d.get("pages", 1) for d in docs)
        total_size_kb = sum(d.get("file_size_kb", 0) for d in docs)

        # Breakdowns
        by_category: Dict[str, int] = {}
        for cat in CATEGORIES:
            by_category[cat] = 0

        by_language: Dict[str, int] = {}
        by_source: Dict[str, int] = {}

        for d in docs:
            # Categories (count all assigned categories)
            cats = d.get("categories", [])
            for c in cats:
                if c in by_category:
                    by_category[c] += 1

            lang = d.get("language", "unknown")
            by_language[lang] = by_language.get(lang, 0) + 1

            src = d.get("source", "unknown")
            by_source[src] = by_source.get(src, 0) + 1

        summary = {
            "total_documents": total_docs,
            "total_pages": total_pages,
            "total_size_mb": round(total_size_kb / 1024.0, 2),
            "by_category": by_category,
            "by_language": by_language,
            "by_source": by_source,
        }

        with open(self.summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    def get_summary(self) -> Dict[str, Any]:
        """Return current knowledge base statistics."""
        if self.summary_path.exists():
            try:
                with open(self.summary_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"total_documents": len(self._catalog_cache)}

