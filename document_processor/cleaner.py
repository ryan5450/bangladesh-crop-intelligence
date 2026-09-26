"""Text cleaning module for agricultural publications.

Handles Bangla Unicode normalization, repeated header/footer elimination,
page number removal, and whitespace formatting.
"""

from collections import Counter
import re
from typing import List, Set, Tuple
import unicodedata

# Page number regex for English and Bengali numerals
PAGE_NUMBER_REGEX = re.compile(
    r"^\s*(?:(?:Page|পৃষ্ঠা|পেইজ)\s*)?(?:[-–—\[\(\.\s]*)?(?:\d+|[০-৯]+)(?:[-–—\]\)\.\s]*)?(?:\s*(?:of|/|এর)\s*(?:\d+|[০-৯]+))?\s*$",
    re.IGNORECASE,
)

# Invisible / zero-width characters to strip
ZERO_WIDTH_CHARS = re.compile(r"[\u200b\u200c\u200d\u200e\u200f\ufeff]")

# Unprintable control characters (excluding newline, tab, carriage return)
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Hyphenated word break at line ends (e.g. 'agri-\nculture' -> 'agriculture')
HYPHEN_WRAP_REGEX = re.compile(r"(\b[a-zA-Z]{2,})-\s*\n\s*([a-zA-Z]{2,}\b)")


def normalize_bangla_unicode(text: str) -> str:
    """Normalize Unicode characters using NFKC decomposition and recomposition.
    
    Ensures standard encoding for Bengali conjuncts, vowel signs (kar), and punctuation,
    while stripping harmful zero-width and control characters.
    """
    if not text:
        return ""

    # Unicode NFKC standard normalization
    normalized = unicodedata.normalize("NFKC", text)

    # Strip zero-width markers and stray control characters
    normalized = ZERO_WIDTH_CHARS.sub("", normalized)
    normalized = CONTROL_CHARS.sub("", normalized)

    # Preserve Bengali dāri (।) and double dāri (॥)
    return normalized


def is_page_number_line(line: str) -> bool:
    """Check if a line contains solely a page number or pagination pattern."""
    clean = line.strip()
    if not clean:
        return False
    return bool(PAGE_NUMBER_REGEX.match(clean))


def detect_repeated_headers_and_footers(
    pages_text: List[str], min_page_ratio: float = 0.35, min_occurrences: int = 3
) -> Tuple[Set[str], Set[str]]:
    """Scan across pages to detect repeated running headers and footers.
    
    Args:
        pages_text: List of raw text strings per page.
        min_page_ratio: Fraction of pages line must appear on.
        min_occurrences: Absolute minimum page count.
        
    Returns:
        (headers_to_remove, footers_to_remove)
    """
    total_pages = len(pages_text)
    if total_pages < min_occurrences:
        return set(), set()

    threshold = max(min_occurrences, int(total_pages * min_page_ratio))

    header_candidates: Counter[str] = Counter()
    footer_candidates: Counter[str] = Counter()

    for page_text in pages_text:
        lines = [line.strip() for line in page_text.splitlines() if line.strip()]
        if not lines:
            continue

        # Top 1-3 lines as header candidates
        top_lines = lines[: min(3, len(lines))]
        for line in top_lines:
            if not is_page_number_line(line) and len(line) >= 4:
                header_candidates[line] += 1

        # Bottom 1-3 lines as footer candidates
        bottom_lines = lines[max(0, len(lines) - 3):]
        for line in bottom_lines:
            if not is_page_number_line(line) and len(line) >= 4:
                footer_candidates[line] += 1

    headers = {line for line, count in header_candidates.items() if count >= threshold}
    footers = {line for line, count in footer_candidates.items() if count >= threshold}

    return headers, footers


def clean_whitespace(text: str) -> str:
    """Normalize whitespace, merge hyphenated wraps, and standardize paragraph breaks."""
    if not text:
        return ""

    # Rejoin words broken across line endings with hyphens
    text = HYPHEN_WRAP_REGEX.sub(r"\1\2", text)

    # Standardize non-breaking spaces and tabs
    text = text.replace("\u00a0", " ").replace("\t", " ")

    lines: List[str] = []
    blank_line_count = 0

    for raw_line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if not line:
            blank_line_count += 1
            if blank_line_count <= 1 and lines:
                lines.append("")
        else:
            blank_line_count = 0
            lines.append(line)

    result = "\n".join(lines).strip()
    # Collapse multiple consecutive newlines to maximum 2 (paragraph break)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def clean_page_text(
    raw_page_text: str,
    headers_to_remove: Set[str] = None,
    footers_to_remove: Set[str] = None,
) -> str:
    """Clean a single page of text: normalize Unicode, strip headers, footers, and page numbers."""
    raw_page_norm = normalize_bangla_unicode(raw_page_text)
    if not raw_page_norm:
        return ""

    headers = headers_to_remove or set()
    footers = footers_to_remove or set()

    lines = raw_page_norm.splitlines()
    filtered_lines: List[str] = []

    for line in lines:
        stripped = line.strip()

        # Skip empty lines in initial check
        if not stripped:
            filtered_lines.append("")
            continue

        # Skip isolated page numbers
        if is_page_number_line(stripped):
            continue

        # Skip detected running headers & footers
        if stripped in headers or stripped in footers:
            continue

        filtered_lines.append(line)

    reconstructed = "\n".join(filtered_lines)
    return clean_whitespace(reconstructed)


def clean_document_pages(raw_pages: List[str]) -> List[str]:
    """Clean all pages of a document using holistic cross-page header/footer detection."""
    headers, footers = detect_repeated_headers_and_footers(raw_pages)
    cleaned_pages = [
        clean_page_text(p, headers_to_remove=headers, footers_to_remove=footers)
        for p in raw_pages
    ]
    return cleaned_pages
