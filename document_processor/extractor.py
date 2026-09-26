"""High-fidelity PDF text extraction powered by PyMuPDF."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import pymupdf

from document_processor.cleaner import clean_document_pages
from document_processor.language_detector import detect_language


@dataclass
class ExtractedPage:
    """Individual page extraction data."""
    page_number: int
    raw_text: str
    cleaned_text: str = ""
    char_count: int = 0


@dataclass
class ExtractedDocument:
    """Aggregated extraction result for an entire publication."""
    document_id: str
    filename: str
    file_path: Path
    category: str
    source: str
    page_count: int
    pages: List[ExtractedPage] = field(default_factory=list)
    full_cleaned_text: str = ""
    language: str = "English"
    char_count: int = 0
    word_count: int = 0


def extract_document(
    file_path: Path,
    category: str,
    source: str = "Unknown",
    document_id: Optional[str] = None,
) -> ExtractedDocument:
    """Extract and clean text across all pages of a PDF using PyMuPDF.
    
    Args:
        file_path: Absolute path to the PDF document.
        category: Agricultural taxonomy category.
        source: Trusted source agency (BRRI, BARI, DAE, etc.).
        document_id: Optional explicit document identifier.
        
    Returns:
        ExtractedDocument containing per-page cleaned text, full text, and language.
    """
    doc_id = document_id or f"{source.lower()}_{file_path.stem}"
    doc = pymupdf.open(str(file_path))

    raw_pages_text: List[str] = []
    page_objects: List[ExtractedPage] = []

    try:
        # Extract raw text per page
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            # Use 'text' extraction layout
            text = page.get_text("text") or ""
            raw_pages_text.append(text)
            page_objects.append(
                ExtractedPage(
                    page_number=page_idx + 1,
                    raw_text=text,
                    char_count=len(text),
                )
            )

        # Apply multi-page header/footer detection, page number removal, and Bangla Unicode normalization
        cleaned_pages_text = clean_document_pages(raw_pages_text)

        full_cleaned_chunks = []
        for idx, clean_txt in enumerate(cleaned_pages_text):
            page_objects[idx].cleaned_text = clean_txt
            page_objects[idx].char_count = len(clean_txt)
            if clean_txt:
                full_cleaned_chunks.append(clean_txt)

        full_text = "\n\n".join(full_cleaned_chunks)
        detected_lang = detect_language(full_text)
        word_count = len(full_text.split())

        return ExtractedDocument(
            document_id=doc_id,
            filename=file_path.name,
            file_path=file_path,
            category=category,
            source=source,
            page_count=len(doc),
            pages=page_objects,
            full_cleaned_text=full_text,
            language=detected_lang,
            char_count=len(full_text),
            word_count=word_count,
        )

    finally:
        doc.close()
