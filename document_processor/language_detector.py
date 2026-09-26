"""Language detection for Bengali and English agricultural texts."""

import re
from typing import Tuple
from document_processor.config import LANG_BANGLA, LANG_BILINGUAL, LANG_ENGLISH

# Unicode range for Bengali script
BENGALI_CHAR_PATTERN = re.compile(r"[\u0980-\u09FF]")
LATIN_CHAR_PATTERN = re.compile(r"[a-zA-Z]")


def detect_language(text: str) -> str:
    """Analyze script character distribution and return 'Bangla', 'English', or 'Bilingual'.
    
    Args:
        text: Raw or cleaned text string.
        
    Returns:
        'Bangla', 'English', or 'Bilingual'
    """
    if not text or not text.strip():
        return LANG_ENGLISH

    bengali_chars = len(BENGALI_CHAR_PATTERN.findall(text))
    latin_chars = len(LATIN_CHAR_PATTERN.findall(text))
    total_letters = bengali_chars + latin_chars

    if total_letters == 0:
        return LANG_ENGLISH

    bn_ratio = bengali_chars / total_letters
    en_ratio = latin_chars / total_letters

    # If both languages have substantial representation (>25% each)
    if bn_ratio >= 0.25 and en_ratio >= 0.25:
        return LANG_BILINGUAL
    elif bn_ratio > 0.40:
        return LANG_BANGLA
    else:
        return LANG_ENGLISH


def get_language_metrics(text: str) -> Tuple[str, float, float]:
    """Return language label along with Bengali and English character ratios."""
    bengali_chars = len(BENGALI_CHAR_PATTERN.findall(text))
    latin_chars = len(LATIN_CHAR_PATTERN.findall(text))
    total_letters = max(1, bengali_chars + latin_chars)

    bn_ratio = round(bengali_chars / total_letters, 3)
    en_ratio = round(latin_chars / total_letters, 3)

    return detect_language(text), bn_ratio, en_ratio
