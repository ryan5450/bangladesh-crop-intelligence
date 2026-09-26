"""Document validation and corrupted file handling."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
from typing import Optional, Tuple
import pymupdf

from document_processor.config import MAX_GIBBERISH_RATIO, MIN_EXTRACTABLE_CHARS


@dataclass
class ValidationResult:
    """Document integrity and readability status."""
    is_valid: bool
    reason: str
    page_count: int = 0
    char_count: int = 0
    gibberish_ratio: float = 0.0


# Regex matching legitimate Bengali or Latin alphabetic, numeric, and standard punctuation characters
VALID_TEXT_PATTERN = re.compile(r"[\w\s\u0980-\u09FF\.,;:!?\(\)\[\]\"'/\-–—%।॥]")


def calculate_gibberish_ratio(text: str) -> float:
    """Measure the ratio of invalid, unprintable, or replacement symbols in text."""
    if not text:
        return 1.0

    total_chars = len(text)
    if total_chars == 0:
        return 1.0

    # Count replacement characters and Unicode private use area (PUA) codes
    replacement_chars = text.count("\ufffd")
    pua_chars = sum(1 for c in text if "\ue000" <= c <= "\uf8ff")
    unprintable_control = sum(1 for c in text if ord(c) < 32 and c not in "\n\r\t")

    # Count legitimate letters, digits, and common punctuation
    valid_chars = len(VALID_TEXT_PATTERN.findall(text))
    noise_chars = total_chars - valid_chars + (replacement_chars * 2) + pua_chars + unprintable_control

    ratio = min(1.0, max(0.0, noise_chars / total_chars))
    return round(ratio, 3)


def validate_pdf(file_path: Path) -> ValidationResult:
    """Validate that a PDF opens correctly, has extractable text, and is not corrupted or gibberish.
    
    Args:
        file_path: Absolute path to candidate PDF.
        
    Returns:
        ValidationResult detailing validity, page count, char count, and gibberish ratio.
    """
    if not file_path.exists():
        return ValidationResult(is_valid=False, reason="File does not exist on disk.")

    file_size = file_path.stat().st_size
    if file_size < 1024:
        return ValidationResult(is_valid=False, reason=f"File too small ({file_size} bytes). Likely empty or HTML stub.")

    # 1. Magic bytes check
    try:
        with open(file_path, "rb") as f:
            header = f.read(1024)
            if b"%PDF-" not in header:
                return ValidationResult(is_valid=False, reason="Invalid PDF header magic bytes.")
    except Exception as exc:
        return ValidationResult(is_valid=False, reason=f"Failed to read file header: {exc}")

    # 2. Test opening with PyMuPDF
    try:
        doc = pymupdf.open(str(file_path))
    except Exception as exc:
        return ValidationResult(is_valid=False, reason=f"PyMuPDF failed to open document: {exc}")

    try:
        # Check password protection
        if doc.is_encrypted:
            if not doc.authenticate(""):
                doc.close()
                return ValidationResult(is_valid=False, reason="PDF is password encrypted and cannot be decrypted.")

        page_count = len(doc)
        if page_count == 0:
            doc.close()
            return ValidationResult(is_valid=False, reason="PDF contains 0 pages.")

        # 3. Extract sample text across pages to test readability
        extracted_text_pieces = []
        for page_idx in range(min(15, page_count)):
            page = doc[page_idx]
            extracted_text_pieces.append(page.get_text("text") or "")

        full_sample = "".join(extracted_text_pieces).strip()
        char_count = len(full_sample)

        # 4. Check for extractable text layer (scanned image detection)
        if char_count < MIN_EXTRACTABLE_CHARS:
            doc.close()
            return ValidationResult(
                is_valid=False,
                reason=f"No digital text layer found ({char_count} chars). Document appears to be a scanned image or empty.",
                page_count=page_count,
                char_count=char_count,
            )

        # 5. Check for corrupted font stream or gibberish encoding
        gibberish_ratio = calculate_gibberish_ratio(full_sample)
        if gibberish_ratio > MAX_GIBBERISH_RATIO:
            doc.close()
            return ValidationResult(
                is_valid=False,
                reason=f"High corrupted text / symbol noise ratio ({gibberish_ratio:.1%} > {MAX_GIBBERISH_RATIO:.1%}). Corrupted font encoding.",
                page_count=page_count,
                char_count=char_count,
                gibberish_ratio=gibberish_ratio,
            )

        doc.close()
        return ValidationResult(
            is_valid=True,
            reason="Document is valid and readable.",
            page_count=page_count,
            char_count=char_count,
            gibberish_ratio=gibberish_ratio,
        )

    except Exception as exc:
        doc.close()
        return ValidationResult(is_valid=False, reason=f"Unexpected error while validating PDF: {exc}")


def move_to_rejected(
    file_path: Path,
    reason: str,
    rejected_dir: Path,
    category: str = "general",
) -> Path:
    """Move an invalid or corrupted file to the rejected directory and log reason."""
    target_category_dir = rejected_dir / category
    target_category_dir.mkdir(parents=True, exist_ok=True)

    dest_path = target_category_dir / file_path.name
    shutil.move(str(file_path), str(dest_path))

    # Also move corresponding .json or .txt if they exist in source folder
    for ext in [".json", ".txt"]:
        sidecar = file_path.with_suffix(ext)
        if sidecar.exists():
            shutil.move(str(sidecar), str(target_category_dir / sidecar.name))

    # Write companion rejection metadata
    meta_path = target_category_dir / f"{file_path.stem}.rejected.json"
    rejection_record = {
        "filename": file_path.name,
        "original_category": category,
        "rejected_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    }
    meta_path.write_text(json.dumps(rejection_record, indent=2, ensure_ascii=False), encoding="utf-8")

    return dest_path
