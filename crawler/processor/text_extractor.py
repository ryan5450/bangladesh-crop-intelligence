"""Multi-page text and document metadata extractor using PyPDF."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from pypdf import PdfReader

from processor.cleaner import clean_extracted_text
from utils.file_helper import clean_title
from utils.logger import get_logger

logger = get_logger("processor.text_extractor")


@dataclass
class ExtractedDocument:
    """Container holding extracted document text, structure, and embedded metadata."""
    file_path: Path
    title: str
    full_text: str
    pages: int
    word_count: int
    char_count: int
    author: Optional[str] = None
    creation_date: Optional[str] = None
    page_texts: List[str] = field(default_factory=list)
    raw_metadata: Dict[str, str] = field(default_factory=dict)


def extract_pdf_content(file_path: Path) -> ExtractedDocument:
    """Extract clean multi-page text and metadata from a validated PDF."""
    reader = PdfReader(str(file_path), strict=False)
    pages = len(reader.pages)

    page_texts: List[str] = []
    for idx, page in enumerate(reader.pages):
        try:
            raw_text = page.extract_text() or ""
            cleaned_page = clean_extracted_text(raw_text)
            if cleaned_page:
                page_texts.append(cleaned_page)
        except Exception as exc:
            logger.warning(f"Error extracting page {idx+1} in {file_path.name}: {exc}")

    full_text = "\n\n".join(page_texts).strip()

    # Read PDF internal document information if present
    raw_metadata: Dict[str, str] = {}
    embedded_title = ""
    author = None
    creation_date = None

    if reader.metadata:
        try:
            for k, v in reader.metadata.items():
                if v and isinstance(v, str):
                    raw_metadata[str(k).replace("/", "")] = v.strip()

            embedded_title = raw_metadata.get("Title", "").strip()
            author = raw_metadata.get("Author", "").strip() or None
            creation_date = raw_metadata.get("CreationDate", "").strip() or None
        except Exception:
            pass

    # Derive human-readable title:
    # 1. Use embedded PDF title if not generic
    # 2. Else derive from first significant line of page 1 text
    # 3. Else fallback to clean file name
    final_title = ""
    if embedded_title and len(embedded_title) > 3 and not embedded_title.lower().startswith("untitled"):
        final_title = clean_title(embedded_title)
    elif page_texts:
        first_page_lines = [line.strip() for line in page_texts[0].split("\n") if len(line.strip()) > 3]
        if first_page_lines:
            candidate = first_page_lines[0]
            # If line is reasonable title length (< 120 chars)
            if len(candidate) <= 120:
                final_title = clean_title(candidate)

    if not final_title:
        final_title = clean_title(file_path.stem)

    words = re.findall(r"\w+", full_text)

    return ExtractedDocument(
        file_path=file_path,
        title=final_title,
        full_text=full_text,
        pages=pages,
        word_count=len(words),
        char_count=len(full_text),
        author=author,
        creation_date=creation_date,
        page_texts=page_texts,
        raw_metadata=raw_metadata,
    )

