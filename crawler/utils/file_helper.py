"""File system operations and filename sanitization helpers."""

import re
from pathlib import Path
from typing import Union


def ensure_dir(dir_path: Union[str, Path]) -> Path:
    """Ensure directory exists, creating all intermediate directories if required."""
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """Convert an arbitrary string into a safe, clean canonical filename component.
    
    Preserves Bengali characters and alphanumeric ASCII, converts whitespace to underscores,
    and removes special punctuation.
    """
    if not name:
        return "unnamed_document"

    # Remove file extension if accidentally passed
    clean = re.sub(r"\.pdf$", "", name, flags=re.IGNORECASE)

    # Normalize whitespace
    clean = re.sub(r"\s+", "_", clean.strip())

    # Retain English alphanumeric, Bengali script (\u0980-\u09FF), dashes, and underscores
    clean = re.sub(r"[^\w\-\u0980-\u09FF]", "", clean)

    # Collapse repeated underscores
    clean = re.sub(r"_+", "_", clean).strip("_-")

    if not clean:
        return "document"

    return clean[:max_length].lower()


def clean_title(raw_title: str) -> str:
    """Normalize extracted document titles, stripping redundant boilerplate."""
    if not raw_title:
        return "Agricultural Technical Document"

    # Remove common PDF suffixes and file paths
    title = re.sub(r"\.pdf$", "", raw_title, flags=re.IGNORECASE)
    title = title.split("/")[-1].split("\\")[-1]

    # Normalize underscores and dashes to clean spaces
    title = title.replace("_", " ").replace("-", " ")

    # Strip government portal boilerplate prefixes
    title = re.sub(r"^(brri|bari|dae|barc|bamis|fao)\s*[:|-]?\s*", "", title, flags=re.IGNORECASE)

    # Capitalize cleanly
    title = re.sub(r"\s+", " ", title).strip()

    return title if title else "Agricultural Publication"

