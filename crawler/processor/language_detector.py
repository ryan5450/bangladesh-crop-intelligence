"""Bilingual language detector specialized for Bengali and English agronomic text."""

import re
from typing import Literal

LanguageCode = Literal["bn", "en", "bn/en"]


def detect_language(text: str) -> LanguageCode:
    """Determine whether text is Bengali ('bn'), English ('en'), or Bilingual ('bn/en').
    
    Uses Unicode character distribution between the Bengali Unicode script block (\u0980-\u09FF)
    and Latin alphabet ([a-zA-Z]).
    """
    if not text:
        return "en"

    # Count Bengali script characters
    bengali_chars = len(re.findall(r"[\u0980-\u09FF]", text))

    # Count Latin/English alphabetic characters
    english_chars = len(re.findall(r"[a-zA-Z]", text))

    total_alpha = bengali_chars + english_chars

    if total_alpha == 0:
        return "en"

    bengali_ratio = bengali_chars / total_alpha
    english_ratio = english_chars / total_alpha

    # Classification logic
    if bengali_ratio >= 0.40 and english_ratio >= 0.20:
        return "bn/en"  # Substantial presence of both languages
    elif bengali_ratio >= 0.35:
        return "bn"     # Primarily Bengali
    elif english_ratio >= 0.65:
        return "en"     # Primarily English
    else:
        return "bn/en"  # Mixed/Bilingual

