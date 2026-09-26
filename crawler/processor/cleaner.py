"""Text cleaning and Unicode normalization for Bengali and English agronomic text."""

import re
import unicodedata


def clean_extracted_text(text: str) -> str:
    """Clean raw extracted text from PDFs, normalizing Bengali & English typography."""
    if not text:
        return ""

    # 1. Unicode NFKC Normalization (standardizes composite Bengali glyphs)
    cleaned = unicodedata.normalize("NFKC", text)

    # 2. Replace non-breaking spaces and zero-width characters
    cleaned = cleaned.replace("\u00a0", " ")
    cleaned = cleaned.replace("\u200b", "")  # zero-width space
    cleaned = cleaned.replace("\u200e", "")  # left-to-right mark
    cleaned = cleaned.replace("\u200f", "")  # right-to-left mark
    cleaned = cleaned.replace("\ufeff", "")  # byte order mark

    # 3. Remove control characters (except newline, tab, carriage return)
    cleaned = "".join(ch for ch in cleaned if unicodedata.category(ch)[0] != "C" or ch in "\n\r\t")

    # 4. Standardize Bengali punctuation and hyphens
    cleaned = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015]", "-", cleaned)
    cleaned = re.sub(r"[\u2018\u2019]", "'", cleaned)
    cleaned = re.sub(r"[\u201c\u201d]", '"', cleaned)

    # 5. Remove repeated standalone page numbers / header artifacts (e.g. "Page 12 of 45" or "--- 12 ---")
    cleaned = re.sub(r"(?m)^\s*(page\s+\d+(\s+of\s+\d+)?|\d+)\s*$", "", cleaned, flags=re.IGNORECASE)

    # 6. Normalize multiple horizontal spaces and line breaks
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()

