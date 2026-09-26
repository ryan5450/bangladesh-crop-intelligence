"""Recursive scanner for agricultural documents in knowledge_base."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import List, Optional
from document_processor.config import KNOWN_SOURCES, RESERVED_FOLDERS, VALID_CATEGORIES


@dataclass
class ScannedDocument:
    """Document discovered during filesystem scan."""
    file_path: Path
    category: str
    source: str
    title: str
    document_id: str


def infer_source_from_filename(filename: str) -> str:
    """Infer source agency from filename prefix."""
    lower = filename.lower()
    for prefix in KNOWN_SOURCES.keys():
        if lower.startswith(prefix.lower() + "_") or lower.startswith(prefix.lower() + "-"):
            return prefix
    return "Unknown"


def scan_knowledge_base(base_dir: Path) -> List[ScannedDocument]:
    """Recursively scan base_dir discovering all candidate agricultural PDFs.
    
    Args:
        base_dir: Root knowledge_base directory.
        
    Returns:
        List of ScannedDocument objects with resolved categories and sources.
    """
    discovered: List[ScannedDocument] = []
    if not base_dir.exists():
        return []

    # Recursively find all PDFs
    for pdf_path in sorted(base_dir.rglob("*.pdf")):
        # Skip files located inside reserved output folders (processed, chunks, metadata, reports, rejected)
        rel_parts = pdf_path.relative_to(base_dir).parts
        if any(part in RESERVED_FOLDERS for part in rel_parts):
            continue

        # Category is the immediate top-level folder under knowledge_base
        raw_category = rel_parts[0] if len(rel_parts) > 1 else "crops"
        category = raw_category if raw_category in VALID_CATEGORIES else "crops"

        source = "Unknown"
        title = pdf_path.stem.replace("_", " ").title()
        document_id = pdf_path.stem

        # Check if a companion metadata JSON file exists (e.g. from crawler)
        companion_json = pdf_path.with_suffix(".json")
        if companion_json.exists():
            try:
                meta = json.loads(companion_json.read_text(encoding="utf-8"))
                source = meta.get("source", source)
                title = meta.get("title", title)
                document_id = meta.get("document_id", document_id)
                if "categories" in meta and meta["categories"]:
                    cat_candidate = meta["categories"][0]
                    if cat_candidate in VALID_CATEGORIES:
                        category = cat_candidate
            except Exception:
                pass

        if source == "Unknown":
            source = infer_source_from_filename(pdf_path.name)

        discovered.append(
            ScannedDocument(
                file_path=pdf_path,
                category=category,
                source=source,
                title=title,
                document_id=document_id,
            )
        )

    return discovered
